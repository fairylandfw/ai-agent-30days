from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., description="用户问题")


class BuildRequest(BaseModel):
    chunk_size: int | None = Field(default=None, description="chunk大小")
    chunk_overlap: int | None = Field(default=None, description="chunk 重叠")
    strategy: str | None = Field(
        default=None, description="切片策略 fixed/paragraph/sentence/recursive"
    )


class PreviewChunkRequest(BaseModel):
    chunk_size: int | None = None
    chunk_overlap: int | None = None
    strategy: str | None = None


class ChunkExperimentRequest(BaseModel):
    question: str
    expected_source: str | None = None
    chunk_size: int = 500
    chunk_overlap: int = 80
    strategy: str = "recursive"


class AskResponse(BaseModel):
    question: str
    answer: str
    retrieved_chunks: list[dict]
