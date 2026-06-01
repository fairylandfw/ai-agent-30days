from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., description="用户问题")


class AskResponse(BaseModel):
    question: str
    answer: str
    retrieved_chunks: list[dict]
