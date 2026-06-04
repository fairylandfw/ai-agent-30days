from app.config.settings import settings
from app.core.logger import logger

from app.rag.document_loader import DocumentLoader
from app.rag.text_splitter import TextSplitter
from app.rag.embedding import create_embedding_client
from app.rag.embedding_evaluator import EmbeddingEvaluator
from app.rag.vector_store import FaissVectorStore
from app.rag.retrieval_pipeline import RetrievalPipeline
from app.llm.client import LLMClient


class RAGPipeline:
    def __init__(self):
        self.loader = DocumentLoader(settings.DOCS_DIR)
        self.embedding_client = create_embedding_client()
        self.evaluator = EmbeddingEvaluator()
        self.vector_store = FaissVectorStore(settings.VECTOR_STORE_DIR)
        self.retrieve_pipline = RetrievalPipeline(
            embedding_client=self.embedding_client,
            vector_store=self.vector_store,
        )
        self.llm = LLMClient()
        chunks = []

    def build_knowledge_base(self) -> dict:
        logger.info("开始构建本地 Embedding 知识库")
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

        # info = {"embedding": self.embedding_info()}

        self.vector_store.build(embeddings, chunks)
        self.vector_store.save()

        self.chunks = chunks
        self.retrieve_pipline.build_keyword_index(chunks)

        return {
            "doucument": len(doucuments),
            "chunks": len(chunks),
            "message": "知识库构建完成",
        }

    def ensure_keyword_index(self):
        if self.retrieve_pipline.chunks:
            return

        self.vector_store.load()
        chunks = self.vector_store.metadata
        self.chunks = chunks
        self.retrieve_pipline.build_keyword_index(chunks)

    def retrieve_vector(self, question: str, top_k: int | None = None) -> list[dict]:
        return self.retrieve_pipline.vector_search(question, top_k=top_k)

    def retrieve_keyword(self, question: str, top_k: int | None = None) -> list[dict]:
        self.ensure_keyword_index()
        return self.retrieve_pipline.keyword_search(question, top_k=top_k)

    def retrieve_hybrid(
        self,
        question: str,
        vector_top_k: int | None = None,
        keyword_top_k: int | None = None,
        final_top_k: int | None = None,
        use_rerank: bool = True,
    ) -> dict:
        self.ensure_keyword_index()
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
            片段：{item['chunk_index']}
            召回来源：{item.get('retrieval_source')}
            向量分数: {item.get('vector_score')}
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

    def embedding_info(self) -> dict:
        return {
            "embedding_provider": settings.EMBEDDING_PROVIDER,
            "openai_embedding_model": settings.OPENAI_EMBEDDING_MODEL,
            "local_embedding_model": settings.LOCAL_EMBEDDING_MODEL,
            "local_embedding_device": settings.LOCAL_EMBEDDING_DEVICE,
            "normalize_embeddings": settings.NORMALIZE_EMBEDDINGS,
        }

    def evaluate_embedding(
        self,
        question: str,
        expected_words: list[str] | None = None,
        expected_source: str | None = None,
        top_k: int | None = None,
    ) -> dict:
        results = self.retrieve_vector(
            question=question,
            top_k=top_k or settings.VECTOR_TOP_K,
        )
        hit_result = self.evaluator.evaluate_hit(
            retrieved_chunks=results,
            expected_words=expected_words,
            expected_source=expected_source,
        )
        score_summary = self.evaluator.summarize_scores(results)

        return {
            "question": question,
            "embedding_info": self.embedding_info(),
            "score_summary": score_summary,
            "hit_result": hit_result,
            "retrieved_chunks": results,
        }
