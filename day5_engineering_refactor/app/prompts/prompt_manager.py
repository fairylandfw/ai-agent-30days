from pathlib import Path
from app.core.logger import logger


class PromptManager:
    def __init__(self, template_dir: str = "app/prompts/templates"):
        self.template_dir = Path(template_dir)
        self.allowed_prompt_types = {
            "default",
            "json_assistant",
            "markdown_teacher",
            "code_reviewer",
        }

    def load_prompt(self, prompt_type: str) -> str:
        """
        根据prompt_type加载对应的prompt模板
        如果模板不存在,则使用default
        """

        if prompt_type not in self.allowed_prompt_types:
            logger.warning("未知prompt_type={%s},使用default", prompt_type)
            prompt_type = "default"

        file_path = self.template_dir / f"{prompt_type}.txt"

        if not file_path.exists():
            logger.warning("Prompt文件不存在:%s,使用default", file_path)
            file_path = self.template_dir / "default.txt"

        # with自动关闭文件,不用手动释放
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
