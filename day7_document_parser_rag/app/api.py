from fastapi import FastAPI, HTTPException

from app.rag.rag_pipeline import RAGPipeline
from app.schemas.rag import AskRequest, AskResponse
from app.utils.response import success_response
from app.core.logger import logger

app = FastAPI(
    title="Day7 Document Parser RAG",
    description="支持 PDF / Word / TXT / Markdown 的企业文档知识库",
    version="1.0.0",
)

rag = RAGPipeline()


@app.get("/")
def root():
    return success_response(
        data={
            "project": "Day7 Document Parser RAG",
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
    读取data/docs下的txt文件 切片 生成embedding 存入faiss
    """
    try:
        result = rag.build_knowledge_base()
        return success_response(data=result, message="知识库构建完成")
    except Exception as e:
        logger.error(f"构建知识库失败: {e}")
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
