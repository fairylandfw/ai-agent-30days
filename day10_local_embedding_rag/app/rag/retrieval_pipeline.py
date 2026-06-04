from app.rag.embedding import BaseEmbeddingClient
from app.rag.vector_store import FaissVectorStore
from app.rag.keyword_retriever import KeywordRetriever
from app.rag.reranker import SimpleReranker

from app.core.logger import logger

from app.config.settings import settings


class RetrievalPipeline:
    def __init__(
        self,
        embedding_client: BaseEmbeddingClient,
        vector_store: FaissVectorStore,
    ):
        self.embedding_client = embedding_client
        self.vector_store = vector_store
        self.keyword_retriever = KeywordRetriever()
        self.reranker = SimpleReranker()
        self.chunks = []

    def build_keyword_index(self, chunks: list[dict]):
        self.chunks = chunks
        self.keyword_retriever.build(chunks)
        logger.info("关键词索引构建完成,chunk 数量: %d", len(chunks))

    def vector_search(self, question: str, top_k: int | None = None) -> list[dict]:
        query_embedding = self.embedding_client.embed_text(question)
        return self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k or settings.VECTOR_TOP_K,
        )

    def keyword_search(self, question: str, top_k: int | None = None) -> list[dict]:
        return self.keyword_retriever.search(
            query=question,
            top_k=top_k or settings.KEYWORD_TOP_K,
        )

    def hybrid_search(
        self,
        question: str,
        vector_top_k: int | None = None,
        keyword_top_k: int | None = None,
        final_top_k: int | None = None,
        use_rerank: bool = True,
    ) -> dict:
        vector_results = self.vector_search(
            question=question,
            top_k=vector_top_k,
        )

        keyword_results = self.keyword_search(
            question=question,
            top_k=keyword_top_k,
        )

        merged_results = self.merge_and_deduplicate(vector_results, keyword_results)

        if use_rerank:
            final_results = self.reranker.rerank(
                query=question,
                candidates=merged_results,
                top_k=final_top_k or settings.FINAL_TOP_K,
            )
        else:
            final_results = merged_results[: final_top_k or settings.FINAL_TOP_K]
        return {
            "final_results": final_results,
            "merged_count": len(merged_results),
        }

    def merge_and_deduplicate(
        self,
        vector_results: list[dict],
        keyword_results: list[dict],
    ) -> list[dict]:
        merged_map = {}
        for item in vector_results:
            chunk_id = item["id"]
            merged_map[chunk_id] = item.copy()
            # 后续可添加为 ["vector","keyword"]
            merged_map[chunk_id]["retrieval_source"] = ["vector"]

        # 用dict 去重
        for item in keyword_results:
            chunk_id = item["id"]
            if chunk_id in merged_map:
                merged_map[chunk_id]["keyword_score"] = item.get("keyword_score", 0.0)
                merged_map[chunk_id]["matched_term"] = item.get("matched_term", [])
                merged_map[chunk_id]["retrieval_source"].append("keyword")
            else:
                merged_map[chunk_id] = item.copy()
                merged_map[chunk_id]["vector_score"] = 0.0
                merged_map[chunk_id]["retrieval_source"] = ["keyword"]

        # 把 dict中的chunk_id对应的值转换成list
        merged_results = list(merged_map.values())
        merged_results.sort(
            key=lambda x: (
                len(x.get("retrieval", [])),
                x.get("vector_score", 0.0),
                x.get("keyword_score", 0.0),
            ),
            reverse=True,
        )
        return merged_results
