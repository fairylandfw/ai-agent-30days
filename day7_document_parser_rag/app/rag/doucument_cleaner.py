import re


class DoucumentCleaner:
    def clean(self, text: str) -> str:
        """
        数据清洗
        """
        if not text:
            return ""
        text = self.normalize_newlines(text)
        text = self.remove_extra_spaces(text)
        text = self.remove_repeated_blank_lines(text)
        text = self.remove_page_numbers(text)
        return text.strip()

    def normalize_newlines(self, text: str) -> str:
        """
        统一换行符
        """
        # windows换行
        text = text.replace("\r\n", "\n")
        # 老Mac换行  都统一为Linux换行标准
        text = text.replace("\r", "\n")
        return text

    def remove_extra_spaces(self, text: str) -> str:
        """
        多空格 Tab TAb和空格混合 都替换为一个标准空格
        """
        # re.sub正则替换(匹配规则 替换成什么 要处理的文本) r代表原始字符串 不处理\
        text = re.sub(r"[ \t]+", " ", text)
        return text

    def remove_repeated_blank_lines(self, text: str) -> str:
        """
        3个及以上换行统一为两个换行
        """
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text

    def remove_page_numbers(self, text: str) -> set:
        """
        去除页码
        """
        # \s* 0或多个空白   \d+ 1个及以上数字 页码
        text = re.sub(r"\n\s*\d+\s*\n", "\n", text)
        text = re.sub(r"\n\s*-\s*\d+\s*-\s*\n", "\n", text)
        return text
