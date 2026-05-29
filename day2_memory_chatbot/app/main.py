from app.llm.client import LLMClient
from app.config.settings import settings
from app.memory.json_memory import JsonMemory

SYSTEM_PROMPT = """
你是一个 AI Agent 工程师导师，专门帮助零基础学生学习 AI 应用开发。
你的要求：
1. 回答要通俗易懂
2. 尽量给出具体例子
3. 如果用户问编程问题，要给出可运行代码
4. 不要一次讲太多理论
5. 引导用户通过项目学习
"""


def build_messages(history: list[dict], user_input: str) -> list[dict]:
    """
    给大模型的message=system prompt+历史消息+当前用户输入
    """
    # 只保留最后settings.MAX_HISTORY_MESSAGES条消息
    recent_history = history[-settings.MAX_HISTORY_MESSAGES :]
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(recent_history)
    messages.append({"role": "user", "content": user_input})
    return messages


def main():
    print("欢迎使用 Day2 多轮记忆聊天助手")
    print("输入 exit 或 quit 退出程序")
    print("输入 clear 清空当前会话记忆")
    print("-" * 50)

    # 新会话要有一个session_id 用来保留对应的记忆
    session_id = input("请输入session_id,直接回车使用default:").strip()
    if not session_id:
        session_id = "default"
    memory = JsonMemory(session_id=session_id)
    llm = LLMClient()
    print(f"当前对话：{session_id}")
    print("-" * 50)
    while True:
        user_input = input("你：").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("AI:再见,明天我们继续升级流式输出和FastAPI")
            break
        if user_input.lower() == "clear":
            memory.clear()
            print("AI:当前会话已清空")
            continue
        if not user_input:
            print("AI:请输入内容")
            continue
        try:
            history = memory.load_history()
            messages = build_messages(history=history, user_input=user_input)
            answer = llm.chat(messages=messages)
            print(f"\nAI:{answer}\n")
            # 保存会话
            memory.add_message("user", user_input)
            memory.add_message("assistant", answer)
        except Exception as e:
            print("调用模型失败:", e)


if __name__ == "__main__":
    main()
