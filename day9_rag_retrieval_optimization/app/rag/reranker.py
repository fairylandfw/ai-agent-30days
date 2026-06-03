import jieba
import re

from app.config.settings import settings


class SimpleReranker:
    def rerank(self, query: str, candidates: list[dict], top_k: int) -> list[dict]:
        if not candidates:
            return []

        query_terms = self.extract_terms(query)
        reranked = []

        # 每一个候选块的加权打分
        for item in candidates:
            vector_score = item.get("vector_score", 0.0)
            keyword_score = item.get("keyword_score", 0.0)
            keyword_overlap_score = self.keyword_overlap_score(
                query_terms, item["content"]
            )
            keyword_exact_match_score = self.keyword_exact_match_score(
                query, item["content"]
            )

            final_score = (
                vector_score * settings.VECTOR_WEIGHT
                + keyword_score * settings.KEYWORD_WEIGHT
                + keyword_overlap_score * 0.2
                + keyword_exact_match_score * 0.2
            )
            newitem = item.copy()
            newitem["rerank_score"] = float(final_score)
            newitem["keyword_overlap_score"] = keyword_overlap_score
            newitem["keyword_exact_match_score"] = keyword_exact_match_score
            reranked.append(newitem)

        reranked.sort(
            key=lambda x: (x["rerank_score"]),
            reverse=True,
        )
        return reranked[:top_k]

    def extract_terms(self, text: str) -> list[str]:
        # 分词返回列表
        tokens = jieba.lcut(text)
        return [
            token.strip()
            for token in tokens
            if token.strip() and len(token.strip()) > 1
        ]

    def keyword_overlap_score(self, query_terms: list[str], content: str) -> float:
        """
        重叠得分  问题分词在知识库块内容中出现 的次数/问题分词数
        """
        hit_count = 0
        for term in query_terms:
            if term in content:
                hit_count += 1
        return float(hit_count) / len(query_terms)

    def keyword_exact_match_score(self, query: str, content: str) -> float:
        """
        基于规则的精确匹配打分
        """
        numbers = re.findall(r"\d+", query)
        score = 0.0

        for number in numbers:
            if number in content:
                score += 0.5

        important_terms = [
            "一线城市",
            "普通城市",
            "住宿",
            "餐饮",
            "交通",
            "远程办公",
            "试用期",
        ]
        for term in important_terms:
            if term in query and term in content:
                score += 0.3

        return min(1.0, score)
