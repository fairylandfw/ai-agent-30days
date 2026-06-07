import json
import re

from app.llm.client import LLMClient


class QueryRewriter:
    def __init__(self, llm: LLMClient | None = None):
        self.llm = llm or LLMClient()

    def query_decompose(self, query: str) -> list[str]:
        if not query or not query.strip():
            return []

        messages = [
            {
                "role": "system",
                "content": (
                    "你是企业制度知识库 RAG 检索的查询拆解助手。"
                    "你的任务是把用户一次输入中的多个独立问题拆成若干个可单独检索的问题。"
                    "只输出 JSON 字符串数组，不要输出 Markdown、解释或额外字段。"
                ),
            },
            {
                "role": "user",
                "content": f"""
请拆解下面的用户问题。

要求：
1. 如果只有一个问题，返回只包含原问题的数组。
2. 每个子问题必须语义完整，保留关键主体、制度名称、时间、条件和限制。
3. 不要回答问题，不要补充用户没有问到的新问题。
4. 输出格式示例：["问题1", "问题2"]
5. 严格按要求输出格式，不要输出多余的东西

用户问题：
{query.strip()}
""",
            },
        ]

        content = self.llm.chat(messages)
        questions = self._parse_question_list(content)
        return questions or [query.strip()]

    def query_vector_adapt(self, query: str) -> str:
        if not query or not query.strip():
            return ""

        messages = [
            {
                "role": "system",
                "content": (
                    "你是企业制度知识库 RAG 检索的 HyDE 查询改写助手。"
                    "你需要根据用户的单个问题生成一段可能出现在企业制度文档中的假设性答案文本，"
                    "用于向量检索召回相关制度片段。"
                    "只输出改写后的检索文本，不要输出 Markdown、标题、解释或免责声明。"
                ),
            },
            {
                "role": "user",
                "content": f"""
请使用 HyDE 方法改写下面的单个问题。

要求：
1. 生成一段适合做向量检索的假设性制度文本，而不是直接回答用户。
2. 文本应包含用户问题中的核心实体、关键词、同义表达和可能的制度表述。
3. 不要编造具体数值、日期、审批人、文件名或条款编号。
4. 控制在 120 字以内。

用户问题：
{query.strip()}
""",
            },
        ]

        content = self.llm.chat(messages)
        adapted_query = self._clean_text(content)
        return adapted_query or query.strip()

    @staticmethod
    def _parse_question_list(content: str) -> list[str]:
        if not content:
            return []

        cleaned = QueryRewriter._clean_text(content)
        parsed = QueryRewriter._loads_json_array(cleaned)

        # 解析失败 清理各种情况
        if parsed is None:
            match = re.search(r"\[[\s\S]*\]", cleaned)
            if match:
                parsed = QueryRewriter._loads_json_array(match.group(0))

        if parsed is not None:
            return QueryRewriter._normalize_questions(parsed)

        lines = re.split(r"[\n；;]+", cleaned)
        questions = []
        for line in lines:
            line = re.sub(r"^\s*(?:[-*]|\d+[.)、])\s*", "", line).strip()
            if line:
                questions.append(line)
        return QueryRewriter._dedupe(questions)

    @staticmethod
    def _loads_json_array(content: str) -> list[str] | None:
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            return None
        return parsed if isinstance(parsed, list) else None

    @staticmethod
    def _normalize_questions(items: list) -> list[str]:
        questions = []
        for item in items:
            if isinstance(item, str):
                question = item.strip()
            elif isinstance(item, dict):
                question = str(
                    item.get("question")
                    or item.get("query")
                    or item.get("content")
                    or ""
                ).strip()
            else:
                question = str(item).strip()

            if question:
                questions.append(question)
        return QueryRewriter._dedupe(questions)

    @staticmethod
    def _dedupe(items: list[str]) -> list[str]:
        result = []
        seen = set()
        for item in items:
            key = item.strip()
            if key and key not in seen:
                result.append(key)
                seen.add(key)
        return result

    @staticmethod
    def _clean_text(content: str) -> str:
        text = (content or "").strip()
        text = re.sub(r"^```(?:json|JSON)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        return text.strip()
