from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    # LLM配置
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
    MODEL_NAME = os.getenv("MODEL_NAME")
    # 生成参数
    TEMPERATURE = float(os.getenv("TEMPERATURE", 0.3))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", 1000))
    MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", 10))

    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # 数据目录
    CONVERSATION_DIR: str = "data/conversations"


settings = Settings()
