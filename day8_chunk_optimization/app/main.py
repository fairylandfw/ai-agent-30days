import uvicorn
from app.core.logger import logger

if __name__ == "__main__":
    logger.info("启动 Day7 Document Parser RAG")

    uvicorn.run(
        "app.api:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
