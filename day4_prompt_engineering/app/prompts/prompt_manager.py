from pathlib import Path


class PromptManager:
    def __init__(self, template_dir: str = "app/prompts/templates"):
        self.template_dir = Path(template_dir)

    def load_prompt(self, prompt_type: str) -> str:
        """
        根据prompt_type加载对应的prompt模板
        如果模板不存在,则使用default
        """

        allowed_prompt_types = {
            "default",
            "json_assistant",
            "markdown_teacher",
            "code_reviewer",
        }

        if prompt_type not in allowed_prompt_types:
            prompt_type = "default"

        file_path = self.template_dir / f"{prompt_type}.txt"

        if not file_path.exists():
            file_path = self.template_dir / "default.txt"

        # with自动关闭文件,不用手动释放
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
