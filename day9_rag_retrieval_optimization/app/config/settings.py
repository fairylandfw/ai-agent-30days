from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    # LLM配置
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL")

    MODEL_NAME: str = os.getenv("MODEL_NAME")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL")

    # 生成参数
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", 0.2))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", 1000))

    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", 100))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", 20))
    SPLIT_STRATEGY: str = os.getenv("SPLIT_STRATEGY", "recrusive")

    VECTOR_TOP_K: int = int(os.getenv("VECTOR_TOP_K", 8))
    KEYWORD_TOP_K: int = int(os.getenv("KEYWORD_TOP_K", 8))
    FINAL_TOP_K: int = int(os.getenv("FINAL_TOP_K", 4))

    VECTOR_WEIGHT: float = float(os.getenv("VECTOR_WEIGHT", 0.7))
    KEYWORD_WEIGHT: float = float(os.getenv("KEYWORD_WEIGHT", 0.3))

    # 知识库目录
    DOCS_DIR: str = "data/docs"
    VECTOR_STORE_DIR: str = "data/vector_store"

    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
