class ChunkEvaluator:
    def summarize_chunks(self, chunks: list[dict]) -> dict:
        if not chunks:
            return {
                "chunk_count": 0,
                "avg_chunk_size": 0,
                "min_chunk_size": 0,
                "max_chunk_size": 0,
            }

        sizes = [len(chunk["content"]) for chunk in chunks]

        return {
            "chunk_count": len(chunks),
            "avg_chunk_size": round(sum(sizes) / len(sizes), 2),
            "min_chunk_size": min(sizes),
            "max_chunk_size": max(sizes),
        }

    def evaluate_retrieval_hit(
        self,
        retrieved_chunks: list[dict],
        expected_source: str | None = None,
    ) -> dict:
        if not expected_source:
            return {
                "expected_source": None,
                "hit": None,
            }

        sources = [item.get("source") for item in retrieved_chunks]
        hit = expected_source in sources
        return {
            "expected_source": expected_source,
            "retrieved_sources": sources,
            "hit": hit,
        }
