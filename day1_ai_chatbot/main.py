from openai import OpenAI
from config import settings

# 创建客户端  OpenAI是一个类
client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL,
    # 伪装浏览器请求
    default_headers={"User-Agent": "Mozilla/5.0"},
)


def chat_once(user_input: str) -> str:
    """单次对话函数,接收用户输入返回AI回答"""
    # 调用大模型
    response = client.chat.completions.create(
        model=settings.MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "你是一个耐心、专业、适合初学者的AI编程学习助手。",
            },
            {"role": "user", "content": user_input},
        ],
        temperature=settings.TEMPERATURE,
        max_tokens=settings.MAX_TOKENS,
    )
    return response.choices[0].message.content


def main():
    """主函数"""
    print("欢迎使用day1 AI聊天助手")
    print("输入exit或quit退出程序")
    print("-" * 40)
    while True:
        user_input = input("你：").strip()  # 输入，删除空格
        if user_input.lower() in ["exit", "quit"]:  # 转成小写
            print("AI:再见，今天继续加油！")
            break
        if not user_input:  # 空内容
            print("AI:请输入内容。")
            continue

        # 正常调用
        try:
            answer = chat_once(user_input)
            print(f"AI:{answer}")  # print(f"  ")  把{变量}嵌入到字符串里输出
        except Exception as e:  # 所有报错存进e里
            print("调用模型失败:", e)


if __name__ == "__main__":  # 只有直接运行，才启动主函数
    main()
