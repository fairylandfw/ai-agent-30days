import re


class DoucumentCleaner:
    def clean(self, text: str) -> str:
        if not text:
            return ""
        text = self.normalize_newlines(text)
        text = self.remove_extra_spaces(text)
        text = self.remove_repeated_blank_lines(text)
        text = self.remove_page_numbers(text)
        return text.strip()

    def normalize_newlines(self, text: str) -> str:
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")
        return text

    def remove_extra_spaces(self, text: str) -> str:
        text = re.sub(r"[ \t]+", " ", text)
        return text

    def remove_repeated_blank_lines(self, text: str) -> str:
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text

    def remove_page_numbers(self, text: str) -> set:
        text = re.sub(r"\n\s*\d+\s*\n", "\n", text)
        text = re.sub(r"\n\s*-\s*\d+\s*-\s*\n", "\n", text)
        return text
