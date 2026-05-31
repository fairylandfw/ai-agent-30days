from openai import OpenAI
from app.config.settings import settings
from app.core.logger import logger


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
        接收完整的message,返回模型回复文本
        """
        logger.info(
            "调用模型:model=%s,messages_count=%d",
            settings.MODEL_NAME,
            len(messages),
        )

        response = self.client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=messages,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS,
        )

        reply = response.choices[0].message.content
        logger.info("模型调用完成")

        return reply

    def stream_chat(self, messages: list[dict]):
        """
        流式输出
        """
        logger.info(
            "流式调用模型:model=%s,meessage_count=%d",
            settings.MODEL_NAME,
            len(messages),
        )
        stream = self.client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=messages,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS,
            # 开启流式输出
            stream=True,
        )

        # stream类似一个传送带
        for chunk in stream:
            if not chunk.choices:
                continue

            # 本次新增的内容
            delta = chunk.choices[0].delta

            if delta and delta.content:
                # 一点点返回
                yield delta.content
