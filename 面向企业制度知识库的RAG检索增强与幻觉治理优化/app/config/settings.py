from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    # LLM配置
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL")
    MODEL_NAME: str = os.getenv("MODEL_NAME")

    # embedding
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER")

    OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL")

    LOCAL_EMBEDDING_MODEL: str = os.getenv(
        "LOCAL_EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5"
    )
    LOCAL_EMBEDDING_DEVICE: str = os.getenv("LOCAL_EMBEDDING_DEVICE")
    NORMALIZE_EMBEDDINGS: bool = bool(os.getenv("NORMALIZE_EMBEDDINGS"))

    # 生成参数
    TEMPERATURE: float = float(os.getenv("TEMPERATURE"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS"))

    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP"))
    SPLIT_STRATEGY: str = os.getenv("SPLIT_STRATEGY")

    VECTOR_TOP_K: int = int(os.getenv("VECTOR_TOP_K"))
    KEYWORD_TOP_K: int = int(os.getenv("KEYWORD_TOP_K"))
    FINAL_TOP_K: int = int(os.getenv("FINAL_TOP_K"))

    VECTOR_WEIGHT: float = float(os.getenv("VECTOR_WEIGHT"))
    KEYWORD_WEIGHT: float = float(os.getenv("KEYWORD_WEIGHT"))
    RRF_K: int = int(os.getenv("RRF_K", "60"))
    RERANKER_MODEL: str = os.getenv("RERANKER_MODEL", "BAAI/bge-reranker-base")
    RERANKER_DEVICE: str = os.getenv("RERANKER_DEVICE", "cpu")

    # 知识库目录
    DOCS_DIR: str = "data/docs"
    VECTOR_STORE_DIR: str = "data/vector_store"

    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
