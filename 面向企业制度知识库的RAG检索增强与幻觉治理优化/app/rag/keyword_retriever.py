import jieba
from rank_bm25 import BM25Okapi
from app.core.logger import logger


class KeywordRetriever:
    def __init__(self):
        self.chunks = []
        self.chunk_tokens = []
        self.bm25 = None

    def build(self, chunks: list[dict]):
        """
        构建BM25关键词索引
        """
        self.chunks = chunks
        self.chunk_tokens = [self.tokenize(chunk["content"]) for chunk in chunks]

        if not self.chunk_tokens:
            self.bm25 = None
            return

        # 关键词索引
        self.bm25 = BM25Okapi(self.chunk_tokens)
        logger.info("BM25索引构建完成,chunk数量:%d", len(chunks))

    def tokenize(self, text: str) -> list[str]:
        """
        划分关键词
        """
        tokens = jieba.lcut(text)

        stop_words = {
            "的",
            "了",
            "和",
            "是",
            "在",
            "为",
            "可以",
            "需要",
            "进行",
            "一个",
            "以及",
            "或者",
            "如果",
            "与",
            "及",
        }

        return [
            token.strip()
            for token in tokens
            if token.strip() and token.strip() not in stop_words
        ]

    def search(self, query: str, top_k: int = 8) -> list[dict]:
        if not self.chunks or self.bm25 is None:
            return []

        query_tokens = self.tokenize(query)
        # 加划分的关键词自动统计
        scores = self.bm25.get_scores(query_tokens)

        # 根据分数排序  保留下标的顺序
        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True,
        )

        keyword_results = []

        for doc_index in ranked_indices[:top_k]:
            score = float(scores[doc_index])

            if score <= 0:
                continue

            doc_tokens = set(self.chunk_tokens[doc_index])

            matched_terms = [token for token in query_tokens if token in doc_tokens]

            item = self.chunks[doc_index].copy()
            item["keyword_score"] = score
            item["matched_terms"] = matched_terms
            item["retrieval_source"] = ["keyword"]
            keyword_results.append(item)

        return keyword_results
