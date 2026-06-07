from sentence_transformers import CrossEncoder

from app.config.settings import settings
from app.core.logger import logger


class Reranker:
    def __init__(self):
        self.model = None

    def rerank(self, query: str, candidates: list[dict], top_k: int) -> list[dict]:
        if not candidates:
            return []

        model = self._load_model()
        pairs = [(query, item.get("content", "")) for item in candidates]
        scores = model.predict(pairs)

        reranked = []
        for item, score in zip(candidates, scores):
            new_item = item.copy()
            new_item["rerank_score"] = float(score)
            reranked.append(new_item)

        reranked.sort(
            key=lambda x: x.get("rerank_score", 0.0),
            reverse=True,
        )
        return reranked[:top_k]

    def _load_model(self):
        if self.model is None:
            logger.info("Loading cross-encoder reranker: %s", settings.RERANKER_MODEL)
            self.model = CrossEncoder(
                settings.RERANKER_MODEL,
                device=settings.RERANKER_DEVICE,
            )
        return self.model
