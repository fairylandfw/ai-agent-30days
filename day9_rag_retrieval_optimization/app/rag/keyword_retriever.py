import jieba
import math
from collections import Counter
from app.core.logger import logger


class KeywordRetriever:
    def __init__(self):
        self.chunks = []
        self.chunk_tokens = []
        self.idf = {}

    def build(self, chunks: list[dict]):
        """
        给文档
        """
        self.chunks = chunks
        self.chunk_tokens = []

        # 包含某个词的文档片段数量
        document_frequency = Counter()

        # 遍历文档的分块
        for chunk in chunks:
            # 提取当前文档分词 list[str]
            tokens = self.tokenize(chunk["content"])
            # list[list[str]]
            self.chunk_tokens.append(tokens)

            unique_tokens = set(tokens)
            for token in unique_tokens:
                document_frequency[token] += 1

        total_docs = len(chunks)

        # 关键词的IDF分数 dict
        self.idf = {
            # +1让结果不太小
            token: math.log((total_docs + 1) / (df + 1)) + 1
            for token, df in document_frequency.items()
        }

    def tokenize(self, text: str) -> list[str]:
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
        if not self.chunks:
            return []

        query_tokens = self.tokenize(query)
        # 加划分的关键词自动统计
        query_counter = Counter(query_tokens)
        keyword_results = []

        # 遍历文档库中的每一个文档
        for doc_index, doc_tokens in enumerate(self.chunk_tokens):

            # 当前文档的关键词计数
            doc_counter = Counter(doc_tokens)
            # 当前文档的打分
            score = 0.0
            # 当前文档匹配的关键词
            matched_terms = []

            for q_token, q_count in query_counter.items():
                # 遍历问题中的 关键词和出现次数
                if q_token in doc_counter:
                    # tf = 当前文档这个问题关键词出现次数 / 当前文档关键词数量
                    tf = doc_counter[q_token] / max(len(doc_tokens), 1)
                    # 这个关键词的在文档中的idf
                    idf = self.idf.get(q_token, 1.0)
                    score += q_count * tf * idf
                    matched_terms.append(q_token)

            if score > 0:
                item = self.chunks[doc_index].copy()
                item["keyword_score"] = float(score)
                item["matched_terms"] = matched_terms
                item["retrieval_source"] = ["keyword"]
                keyword_results.append(item)
            elif score < 0:
                logger.error("score不应该<0")

        keyword_results.sort(key=lambda x: x["keyword_score"], reverse=True)
        return keyword_results[:top_k]
