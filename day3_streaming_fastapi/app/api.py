from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from app.llm.client import LLMClient
from app.config.settings import settings
from app.schemas.chat import ChatRequest, ChatResponse
from app.memory.json_memory import JsonMemory

app = FastAPI(
    title="Day3 Streaming FastAPI Chatbot",
    description="一个支持多轮记忆和流式输出的ai聊天接口",
    version="1.0.0",
)

llm = LLMClient()

SYSTEM_PROMPT = """
你是一个 AI Agent 工程师导师，专门帮助零基础学生学习 AI 应用开发。

你的要求：
1. 回答要通俗易懂
2. 尽量给出具体例子
3. 如果用户问编程问题，要给出可运行代码
4. 不要一次讲太多理论
5. 引导用户通过项目学习
"""


def build_message(history: list[dict], user_input: str) -> list[dict]:
    """
    给大模型的message=system prompt+历史消息+当前用户输入
    """
    recent_history = history[-settings.MAX_HISTORY_MESSAGES :]
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(recent_history)
    messages.append({"role": "user", "content": user_input})
    return messages


# 访问根目录时会运行下面的函数
@app.get("/")
def root():
    """
    网页根地址
    """
    return {"message": "Day3 Streaming FastAPI Chatbot is running."}


# 强制这个接口返回的数据格式
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    聊天
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="message不能为空")

    memory = JsonMemory(session_id=request.session_id)
    history = memory.load_history()

    messages = build_message(history=history, user_input=request.message)
    try:
        reply = llm.chat(messages=messages)
        memory.add_message("user", request.message)
        memory.add_message("assistant", reply)
        return ChatResponse(session_id=request.session_id, reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/stream")
def stream_chat(request: ChatRequest):
    """
    流式聊天
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="message不能为空")

    memory = JsonMemory(session_id=request.session_id)
    history = memory.load_history()

    messages = build_message(history=history, user_input=request.message)

    def generate():
        full_reply = ""

        try:
            # 那边每yield一次，这边就循环一次
            for chunk in llm.stream_chat(messages):
                full_reply += chunk
                yield chunk

            memory.add_message("user", request.message)
            memory.add_message("assistant", full_reply)

        except Exception as e:
            yield f"\n[ERROR] {str(e)}"

    # 流式类型，让前端显示出流式
    return StreamingResponse(generate(), media_type="text/plain; charset=utf-8")


@app.post("/chat/clear")
def clear_chat(request: ChatRequest):
    """
    清空会话记录
    """
    memory = JsonMemory(session_id=request.session_id)
    memory.clear()

    return {"session_id": request.session_id, "message": "当前会话记忆已清空"}
