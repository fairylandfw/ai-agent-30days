from fastapi import FastAPI, HTTPException

from app.rag.rag_pipeline import RAGPipeline
from app.schemas.rag import (
    AskRequest,
    AskResponse,
    BuildRequest,
    PreviewChunkRequest,
    ChunkExperimentRequest,
)
from app.utils.response import success_response
from app.core.logger import logger

app = FastAPI(
    title="Day8 Chunk Optimization RAG",
    description="用于实验 chunk_size、chunk_overlap 和切片策略的 RAG 系统",
    version="1.0.0",
)

rag = RAGPipeline()


@app.get("/")
def root():
    return success_response(
        data={
            "project": "Day8 Chunk Optimization RAG",
            "docs": "http://127.0.0.1:8000/docs",
        }
    )


@app.get("/health")
def health_check():
    return success_response(data={"status": "ok"})


@app.post("/chunks/preview")
def preview_chunks(request: PreviewChunkRequest):
    """
    预览不同切片配置下的chunk结果。
    不构建向量库，不消耗 embedding。
    """
    try:
        result = rag.preview_chunks(
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
            strategy=request.strategy,
        )
        return success_response(data=result)
    except Exception as e:
        logger.error("预览chunk失败:%s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/knowledge/build")
def build_knowledge_base(request: BuildRequest):
    """
    构建知识库
    读取data/docs下的txt文件 切片 生成embedding 存入faiss
    """
    try:
        result = rag.build_knowledge_base(
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
            strategy=request.strategy,
        )
        return success_response(data=result, message="知识库构建完成")
    except Exception as e:
        logger.error(f"构建知识库失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/retrieve")
def retrieve(request: AskRequest):
    """
    只检索，不生成答案。
    用于观察向量检索结果。
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="question 不能为空")
    try:
        results = rag.retrieve(request.question)
        return success_response(data=results)
    except Exception as e:
        logger.error(f"检索失败: {e}")
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


@app.post("/experiments/chunks")
def chunk_experiment(request: ChunkExperimentRequest):
    """
    运行一次 chunk 实验：
    1. 按指定配置重新构建知识库
    2. 检索问题
    3. 判断是否命中 expected_source
    """
    try:
        result = rag.run_chunk_experiment(
            question=request.question,
            expected_source=request.expected_source,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
            strategy=request.strategy,
        )
        return success_response(data=result)
    except Exception as e:
        logger.error(f"chunk 实验失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
