from openai import OpenAI
from app.config.settings import settings
from app.core.logger import logger


class EmbeddingClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )

    def embed_text(self, text: str) -> list[float]:
        response = self.client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=text,
        )

        return response.data[0].embedding

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        logger.info("开始生成embeddings,文本数量:%d", len(texts))

        response = self.client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=texts,
        )

        embeddings = []
        for item in response.data:
            embeddings.append(item.embedding)

        return embeddings
