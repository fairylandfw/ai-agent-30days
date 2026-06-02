from app.config.settings import settings
from app.core.logger import logger

from app.rag.document_loader import DocumentLoader
from app.rag.text_splitter import TextSplitter
from app.rag.embedding import EmbeddingClient
from app.rag.vector_store import FaissVectorStore
from app.rag.evaluator import ChunkEvaluator
from app.llm.client import LLMClient


class RAGPipeline:
    def __init__(self):
        self.loader = DocumentLoader(settings.DOCS_DIR)
        self.embedding_client = EmbeddingClient()
        self.vector_store = FaissVectorStore(settings.VECTOR_STORE_DIR)
        self.llm = LLMClient()
        self.evaluator = ChunkEvaluator()

    def create_splitter(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
        strategy: str | None = None,
    ) -> TextSplitter:
        return TextSplitter(
            chunk_size=chunk_size or settings.CHUNK_SIZE,
            chunk_overlap=(
                chunk_overlap if chunk_overlap is not None else settings.CHUNK_OVERLAP
            ),
            strategy=strategy,
        )

    def preview_chunks(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
        strategy: str | None = None,
    ) -> dict:
        """
        提前查看chunk
        """
        documents = self.loader.load_doucuments()

        splitter = self.create_splitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            strategy=strategy,
        )

        chunks = splitter.split_documents(documents)
        summary = self.evaluator.summarize_chunks(chunks)
        return {
            "config": {
                "chunk_size": splitter.chunk_size,
                "chunk_overlap": splitter.chunk_overlap,
                "strategy": splitter.strategy,
            },
            "summary": summary,
            "chunks": chunks[:10],
        }

    def build_knowledge_base(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
        strategy: str | None = None,
    ) -> dict:
        logger.info("开始构建 Chunk 优化版知识库")
        doucuments = self.loader.load_doucuments()

        if not doucuments:
            return {"doucuments": 0, "chunks": 0, "message": "没有找到可用的文档"}

        splitter = self.create_splitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            strategy=strategy,
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

        summary = self.evaluator.summarize_chunks(chunks)

        return {
            "doucument": len(doucuments),
            "chunks": len(chunks),
            "config": {
                "chunk_size": splitter.chunk_size,
                "chunk_overlap": splitter.chunk_overlap,
                "strategy": splitter.strategy,
            },
            "summary": summary,
            "message": "多格式知识库构建完成",
        }

    def retrieve(self, question: str, top_k: int | None = None) -> list[dict]:
        query_embedding = self.embedding_client.embed_text(question)
        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k or settings.TOP_K,
        )
        return results

    def answer(self, question: str) -> dict:
        logger.info("收到RAG问题:%s", question)

        retrieved_chunks = self.retrieve(question)

        context_lines = []
        for item in retrieved_chunks:
            line = f"来源:{item['source']},类型:{item['file_type']},片段:{item['chunk_index']}\n内容:{item['content']}"
            context_lines.append(line)
        # 保证每个dict间有空格
        context = "\n\n".join(context_lines)

        messages = [
            {
                "role": "system",
                "content": """
你是一个企业知识库问答助手。

你必须遵守：
1. 只能根据知识库上下文回答
2. 如果上下文没有答案，回答：“根据当前知识库资料，我无法确定。”
3. 不要编造
4. 回答时尽量说明来源文件
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
            "retrieved_chunks": retrieved_chunks,
        }

    def run_chunk_experiment(
        self,
        question: str,
        expected_source: str | None,
        chunk_size: int,
        chunk_overlap: int,
        strategy: str,
    ) -> dict:
        build_result = self.build_knowledge_base(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            strategy=strategy,
        )

        retrieved_chunks = self.retrieve(question)

        hit_result = self.evaluator.evaluate_retrieval_hit(
            retrieved_chunks=retrieved_chunks,
            expected_source=expected_source,
        )

        return {
            "question": question,
            "expected_source": expected_source,
            "build_result": build_result,
            "retrieval_result": {
                "top_chunks": retrieved_chunks,
                "hit_result": hit_result,
            },
        }
