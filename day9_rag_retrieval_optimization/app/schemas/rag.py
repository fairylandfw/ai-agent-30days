from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., description="用户问题")


class RetrieveRequest(BaseModel):
    question: str = Field(..., description="用户问题")
    top_k: int | None = Field(default=None, description="返回数量")


class HybridRetrieveRequset(BaseModel):
    question: str
    vector_top_k: int | None = None
    keyword_top_k: int | None = None
    final_top_k: int | None = None
    use_rerank: bool = True


class AskResponse(BaseModel):
    question: str
    answer: str
    retrieved_chunks: list[dict]
