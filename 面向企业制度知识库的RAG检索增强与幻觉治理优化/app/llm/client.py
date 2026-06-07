from openai import OpenAI
from app.config.settings import settings
from app.core.logger import logger


class LLMClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
        )

    def chat(self, messages: list[dict]) -> str:
        logger.info("调用聊天模型:%s", settings.MODEL_NAME)

        response = self.client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=messages,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS,
        )
        return response.choices[0].message.content
