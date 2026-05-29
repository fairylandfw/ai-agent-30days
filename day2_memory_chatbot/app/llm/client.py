from openai import OpenAI
from app.config.settings import settings


class LLMClient:
    """
    大模型客户端
    """

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            default_headers={"User-Agent": "Mozilla/5.0"},
        )

    def chat(self, messages: list[dict]) -> str:
        """
        接收完整messages,返回模型回复文本
        """
        response = self.client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=messages,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS,
        )
        return response.choices[0].message.content
