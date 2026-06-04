class EmbeddingEvaluator:
    def evaluate_hit(
        self,
        retrieved_chunks: list[dict],
        expected_words: list[str],
        expected_source: str,
    ) -> dict:
        expected_words = expected_words or []

        contents = [item.get("content", "") for item in retrieved_chunks]
        sources = [item.get("source", "") for item in retrieved_chunks]

        keyword_hits = {}

        for keyword in expected_words:
            keyword_hits[keyword] = any(keyword in content for content in contents)

        source_hit = None

        if expected_source:
            source_hit = expected_source in sources

        all_keyword_hit = all(keyword_hits.values()) if keyword_hits else None

        return {
            "expected_source": expected_source,
            "source_hit": source_hit,
            "expected_keywords": expected_words,
            "keyword_hits": keyword_hits,
            "all_keyword_hit": all_keyword_hit,
            "retrieved_sources": sources,
        }

    def summarize_scores(self, retrieved_chunks: list[dict]) -> dict:
        if not retrieved_chunks:
            return {
                "count": 0,
                "max_vector_score": None,
                "min_vector_score": None,
                "avg_vector_score": None,
            }
        scores = [item.get("vector_score", 0.0) for item in retrieved_chunks]
        return {
            "count": len(retrieved_chunks),
            "max_vector_score": max(scores),
            "min_vector_score": min(scores),
            "avg_vector_score": round(sum(scores) / len(scores), 4),
        }
