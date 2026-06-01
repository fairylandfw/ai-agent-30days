from app.config.settings import settings
from app.core.logger import logger

from app.rag.document_loader import DocumentLoader
from app.rag.text_splitter import TextSplitter
from app.rag.embedding import EmbeddingClient
from app.rag.vector_store import FaissVectorStore
from app.llm.client import LLMClient


class RAGPipeline:
    def __init__(self):
        self.loader = DocumentLoader(settings.DOCS_DIR)
        self.splitter = TextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )

        self.embedding_client = EmbeddingClient()
        self.vector_store = FaissVectorStore(settings.VECTOR_STORE_DIR)
        self.llm = LLMClient()

    def build_knowledge_base(self) -> dict:
        logger.info("开始构建知识库")
        doucuments = self.loader.load_txt_files()

        if not doucuments:
            return {"doucuments": 0, "chunks": 0, "message": "没有找到可用的文档"}

        chunks = self.splitter.split_documents(doucuments)
        texts = [chunk["content"] for chunk in chunks]
        embeddings = self.embedding_client.embed_texts(texts)

        self.vector_store.build(embeddings, chunks)
        self.vector_store.save()

        return {
            "doucument": len(doucuments),
            "chunks": len(chunks),
            "message": "知识库构建完成",
        }

    def retrieve(self, question: str) -> list[dict]:
        query_embedding = self.embedding_client.embed_text(question)
        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=settings.TOP_K,
        )
        return results

    def answer(self, question: str) -> dict:
        logger.info("收到RAG问题:%s", question)

        retrieved_chunks = self.retrieve(question)

        context_lines = []
        for item in retrieved_chunks:
            line = f"来源:{item['source']},片段:{item['chunk_index']}\n内容:{item['content']}"
            context_lines.append(line)
        # 保证每个dict间有空格
        context = "\n\n".join(context_lines)

        messages = [
            {
                "role": "system",
                "content": """
你是一个严谨的企业知识库问答助手。

你必须遵守以下规则：
1. 只能根据提供的【知识库上下文】回答问题
2. 如果上下文中没有答案，就回答：“根据当前知识库资料，我无法确定。”
3. 不要编造知识库中不存在的信息
4. 回答要简洁、准确
5. 如果能找到依据，请说明信息来源
""",
            },
            {
                "role": "user",
                "content": f"""
【知识库上下文】
{context}

【用户问题】
{question}

请基于知识库上下文回答用户问题。
""",
            },
        ]

        answer = self.llm.chat(messages)

        return {
            "question": question,
            "answer": answer,
            "retrieved_chunks": retrieved_chunks,
        }
