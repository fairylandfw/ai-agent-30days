from fastapi import FastAPI, HTTPException

from app.rag.rag_pipeline import RAGPipeline
from app.schemas.rag import (
    AskRequest,
    AskResponse,
    RetrieveRequest,
    HybridRetrieveRequset,
    EmbeddingEvaluateRequest,
)
from app.utils.response import success_response
from app.core.logger import logger

app = FastAPI(
    title="Day10 Local Embedding RAG",
    description="支持 BGE / m3e / text2vec 本地 Embedding 的 RAG 系统",
    version="1.0.0",
)

rag = RAGPipeline()


@app.get("/")
def root():
    return success_response(
        data={
            "project": "Day9 RAG Retrieval Optimization",
            "docs": "http://127.0.0.1:8000/docs",
        }
    )


@app.get("/health")
def health_check():
    return success_response(data={"status": "ok"})


@app.post("/knowledge/build")
def build_knowledge_base():
    """
    构建知识库
    """
    try:
        result = rag.build_knowledge_base()
        return success_response(data=result, message="知识库构建完成")
    except Exception as e:
        logger.error(f"构建知识库失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/retrieve/vector")
def retrieve_vector(request: RetrieveRequest):
    """
    向量检索
    只检索，不生成答案。
    用于观察向量检索结果。
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="question 不能为空")
    try:
        results = rag.retrieve_vector(
            question=request.question,
            top_k=request.top_k,
        )
        return success_response(data=results)
    except Exception as e:
        logger.error("向量检索失败:%s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/retrieve/hybrid")
def retrieve_hybrid(request: HybridRetrieveRequset):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="question 不能为空")
    try:
        results = rag.retrieve_hybrid(
            question=request.question,
            vector_top_k=request.vector_top_k,
            keyword_top_k=request.keyword_top_k,
            final_top_k=request.final_top_k,
            use_rerank=request.use_rerank,
        )
        return success_response(data=results)
    except Exception as e:
        logger.error("混合检索失败:%s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    """
    RAG问答接口
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="question 不能为空")
    try:
        result = rag.answer(request.question)
        return AskResponse(
            question=result["question"],
            answer=result["answer"],
            retrieved_chunks=result["retrieved_chunks"],
        )
    except Exception as e:
        logger.error(f"RAG 问答失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/embedding/info")
def embedding_info():
    return success_response(data=rag.embedding_info())


@app.post("/embedding/evaluate")
def evaluate_embedding(request: EmbeddingEvaluateRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="question不能为空")
    try:
        result = rag.evaluate_embedding(
            question=request.question,
            expected_words=request.expected_keywords,
            expected_source=request.expected_source,
            top_k=request.top_k,
        )
        return success_response(data=result)
    except Exception as e:
        logger.error("Embedding评估失败:%s", e)
        raise HTTPException(status_code=500, detail=str(e))
