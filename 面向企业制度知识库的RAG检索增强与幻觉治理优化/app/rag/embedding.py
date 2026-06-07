from typing import Protocol

from openai import OpenAI
from sentence_transformers import SentenceTransformer

from app.config.settings import settings
from app.core.logger import logger


class BaseEmbeddingClient(Protocol):
    def embed_text(self, text: str) -> list[float]:
        pass

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        pass


class OpenAIEmbeddingClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )
        self.model = settings.OPENAI_EMBEDDING_MODEL

    def embed_text(self, text: str) -> list[float]:
        response = self.client.embeddings.create(
            model=self.model,
            input=text,
        )

        return response.data[0].embedding

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        logger.info("开始生成embeddings,文本数量:%d", len(texts))

        response = self.client.embeddings.create(
            model=self.model,
            input=texts,
        )

        return [item.embedding for item in response.data]


class LocalEmbeddingClient:
    def __init__(self):
        self.model_name = settings.LOCAL_EMBEDDING_MODEL
        self.device = settings.LOCAL_EMBEDDING_DEVICE

        logger.info(
            f"正在加载本地 Embedding 模型: {self.model_name}, device={self.device}"
        )

        self.model = SentenceTransformer(
            model_name_or_path=self.model_name,
            device=self.device,
        )
        logger.info("本地 Embedding 模型加载完成")

    def embed_text(self, text: str) -> list[float]:
        embedding = self.model.encode(
            text,
            normalize_embeddings=settings.NORMALIZE_EMBEDDINGS,
        ).tolist()
        return embedding

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        logger.info(f"本地 Embedding 批量生成，数量: {len(texts)}")

        embeddings = self.model.encode(
            texts,
            # 每次处理多少文本
            batch_size=32,
            # 显示处理进度条
            show_progress_bar=True,
            normalize_embeddings=settings.NORMALIZE_EMBEDDINGS,
        ).tolist()

        return embeddings


def create_embedding_client() -> BaseEmbeddingClient:
    # 决定使用哪种模型
    provider = settings.EMBEDDING_PROVIDER.lower()

    if provider == "openai":
        return OpenAIEmbeddingClient()
    if provider == "local":
        return LocalEmbeddingClient()

    raise ValueError(f"不支持的 EMBEDDING_PROVIDER: {settings.EMBEDDING_PROVIDER}")
