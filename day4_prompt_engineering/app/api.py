from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from app.llm.client import LLMClient
from app.config.settings import settings
from app.schemas.chat import ChatRequest, ChatResponse
from app.memory.json_memory import JsonMemory
from app.prompts.prompt_manager import PromptManager

app = FastAPI(
    title="Day4 Prompt Engineering Assistant",
    description="一个支持 Prompt 模板切换、结构化输出和多轮记忆的 AI 助手",
    version="1.0.0",
)

llm = LLMClient()
prompt_manager = PromptManager()


def build_message(
    systemp_prompt: str, history: list[dict], user_input: str
) -> list[dict]:
    """
    给大模型的message=system prompt+历史消息+当前用户输入
    """
    recent_history = history[-settings.MAX_HISTORY_MESSAGES :]
    messages = [{"role": "system", "content": systemp_prompt}]
    messages.extend(recent_history)
    messages.append({"role": "user", "content": user_input})
    return messages


# 访问根目录时会运行下面的函数
@app.get("/")
def root():
    """
    网页根地址
    """
    return {
        "message": "Day4 Prompt Engineering Assistant is running.",
        "prompt_types": [
            "default",
            "json_assistant",
            "markdown_teacher",
            "code_reviewer",
        ],
    }


# 强制这个接口返回的数据格式  |一次性|返回JSON结构化数据
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    聊天
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="message不能为空")

    systemp_prompt = prompt_manager.load_prompt(request.prompt_type)
    memory = JsonMemory(session_id=request.session_id)
    history = memory.load_history()

    messages = build_message(
        systemp_prompt=systemp_prompt, history=history, user_input=request.message
    )
    try:
        reply = llm.chat(messages=messages)
        memory.add_message("user", request.message)
        memory.add_message("assistant", reply)
        return ChatResponse(
            session_id=request.session_id, prompt_type=request.prompt_type, reply=reply
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 不是一次性返回所以没法加返回类型
@app.post("/chat/stream")
def stream_chat(request: ChatRequest):
    """
    流式聊天
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="message不能为空")

    systemp_prompt = prompt_manager.load_prompt(request.prompt_type)
    memory = JsonMemory(session_id=request.session_id)
    history = memory.load_history()

    messages = build_message(
        systemp_prompt=systemp_prompt, history=history, user_input=request.message
    )

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


@app.post("/prompts")
def list_prompts():
    return {
        "available_prompt_types": [
            "default",
            "json_assistant",
            "markdown_teacher",
            "code_reviewer",
        ]
    }
