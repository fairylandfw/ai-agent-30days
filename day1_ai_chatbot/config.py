from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
    MODEL_NAME = os.getenv("MODEL_NAME")
    # 优先找配置里的参数，找不到默认0.7
    TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", 800))


settings = Settings()
