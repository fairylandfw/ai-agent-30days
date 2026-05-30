from pydantic import BaseModel

# FastAPI专用的数据模具    严格定义接口数据长什么样，自动检查对错


class ChatRequest(BaseModel):
    """
    前端请求的数据格式
    """

    session_id: str = "default"
    message: str


class ChatResponse(BaseModel):
    """
    后端返回的数据格式
    """

    session_id: str
    reply: str
