from pydantic import BaseModel, Field

# FastAPI专用的数据模具    严格定义接口数据长什么样，自动检查对错


class ChatRequest(BaseModel):
    """
    前端请求的数据格式
    """

    # 第一个字段是传进来的参数 第二个字段是说明
    session_id: str = Field(
        default="default",
        description="会话 ID",
    )
    message: str = Field(
        # 没有默认值，必须传参
        ...,
        description="用户输入",
    )
    # 做提示和默认值
    prompt_type: str = Field(
        default="default",
        description="Prompt类型:default/json_assistant/markdown_teacher/code_reviewer",
    )


class ChatResponse(BaseModel):
    """
    后端返回的数据格式
    """

    session_id: str
    prompt_type: str
    reply: str
