from app.config.settings import settings
from app.core.logger import logger

from app.rag.document_loader import DocumentLoader
from app.rag.text_splitter import TextSplitter
from app.rag.embedding import EmbeddingClient
from app.rag.vector_store import FaissVectorStore
from app.rag.retrieval_pipeline import RetrievalPipeline
from app.llm.client import LLMClient


class RAGPipeline:
    def __init__(self):
        self.loader = DocumentLoader(settings.DOCS_DIR)
        self.embedding_client = EmbeddingClient()
        self.vector_store = FaissVectorStore(settings.VECTOR_STORE_DIR)
        self.retrieve_pipline = RetrievalPipeline(
            embedding_client=self.embedding_client,
            vector_store=self.vector_store,
        )
        self.llm = LLMClient()
        chunks = []

    def build_knowledge_base(self) -> dict:
        logger.info("开始构建 Chunk 优化版知识库")
        doucuments = self.loader.load_doucuments()

        if not doucuments:
            return {"doucuments": 0, "chunks": 0, "message": "没有找到可用的文档"}

        splitter = TextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            strategy=settings.SPLIT_STRATEGY,
        )

        chunks = splitter.split_documents(doucuments)
        if not chunks:
            return {
                "documents": len(doucuments),
                "chunks": 0,
                "msessage": "文档解析成功,但没有生成有效chunk",
            }
        texts = [chunk["content"] for chunk in chunks]
        embeddings = self.embedding_client.embed_texts(texts)

        self.vector_store.build(embeddings, chunks)
        self.vector_store.save()

        self.chunks = chunks
        self.retrieve_pipline.build_keyword_index(chunks)

        return {
            "doucument": len(doucuments),
            "chunks": len(chunks),
            "config": {
                "chunk_size": splitter.chunk_size,
                "chunk_overlap": splitter.chunk_overlap,
                "strategy": splitter.strategy,
                "vector_top_k": settings.VECTOR_TOP_K,
                "keyword_top_k": settings.KEYWORD_TOP_K,
                "final_top_k": settings.FINAL_TOP_K,
            },
            "message": "知识库构建完成",
        }

    def retrieve_vector(self, question: str, top_k: int | None = None) -> list[dict]:
        return self.retrieve_pipline.vector_search(question, top_k=top_k)

    def retrieve_keyword(self, question: str, top_k: int | None = None) -> list[dict]:
        return self.retrieve_pipline.keyword_search(question, top_k=top_k)

    def retrieve_hybrid(
        self,
        question: str,
        vector_top_k: int | None = None,
        keyword_top_k: int | None = None,
        final_top_k: int | None = None,
        use_rerank: bool = True,
    ) -> dict:
        return self.retrieve_pipline.hybrid_search(
            question=question,
            vector_top_k=vector_top_k,
            keyword_top_k=keyword_top_k,
            final_top_k=final_top_k,
            use_rerank=use_rerank,
        )

    def answer(self, question: str) -> dict:
        logger.info("收到RAG问题:%s", question)

        retrieval_result = self.retrieve_hybrid(
            question=question,
            use_rerank=True,
        )
        retrieved_chunks = retrieval_result["final_results"]

        context_lines = []
        for item in retrieved_chunks:
            line = f"""来源：{item['source']},
            片段：{item['chunk_index']},
            召回来源：{item.get('retrieval_source')}
            重排分数：{item.get('rerank_score')}
            内容：{item['content']}"""
            context_lines.append(line)
        # 保证每个dict间有空格
        context = "\n\n".join(context_lines)

        messages = [
            {
                "role": "system",
                "content": """
你是一个严谨的企业知识库问答助手。

你必须遵守：
1. 只能根据知识库上下文回答
2. 如果上下文没有答案，回答：“根据当前知识库资料，我无法确定。”
3. 不要编造
4. 回答要简洁准确
5. 尽量说明来源文件
""",
            },
            {
                "role": "user",
                "content": f"""
【知识库上下文】
{context}

【用户问题】
{question}

请基于上下文回答。
""",
            },
        ]

        answer = self.llm.chat(messages)

        return {
            "question": question,
            "answer": answer,
            "retrieval_result": retrieval_result,
            "retrieved_chunks": retrieved_chunks,
        }
