# 文本切词器
import re


class TextSplitter:
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 80,
        strategy: str = "recursive",
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.strategy = strategy

        if self.chunk_size <= self.chunk_overlap:
            raise ValueError("chunk_overlap必须小于chun_size")

    def split_text(self, text: str) -> list[str]:
        if not text:
            return []

        if self.strategy == "fixed":
            return self.fixed_split(text)
        elif self.strategy == "paragraph":
            return self.paragraph_split(text)
        elif self.strategy == "sentence":
            return self.sentence_split(text)
        elif self.strategy == "recursive":
            return self.recursive_split(text)
        else:
            raise ValueError("没有该策略")

    def fixed_split(self, text: str) -> list[str]:
        """
        固定字符切片
        """
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + self.chunk_size
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start += self.chunk_size - self.chunk_overlap

        return chunks

    def paragraph_split(self, text: str) -> list[str]:
        """
        按段落切片  保留段落完整
        """
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        return self.merge_units(paragraphs)

    def sentence_split(self, text: str) -> list[str]:
        """
        按句子切片 适合中文制度 说明书 FAQ
        """
        sentences = re.split(r"(?<=[。！？；.!?;])", text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return self.merge_units(sentences)

    def recursive_split(self, text: str) -> list[str]:
        """
        递归切片 先按大结构切 再按小结构 段落->句子->固定大小
        段落或句子过长会二次切分
        """
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        units = []
        for paragraph in paragraphs:
            if len(paragraph) <= self.chunk_size:
                # 段落较小
                units.append(paragraph)
            else:
                sentences = re.split(r"(?<=[。！？；.!?;])", paragraph)
                sentences = [s.strip() for s in sentences if s.strip()]
                for sentence in sentences:
                    if len(sentence) <= self.chunk_size:
                        units.append(sentence)
                    else:
                        units.extend(self.fixed_split(sentence))
        return self.merge_units(units)

    def merge_units(self, units: list[str]) -> list[str]:
        """
        合并成尽量少的<=chunk_size的块
        """
        chunks = []
        current = ""
        for unit in units:
            if not current:
                current = unit
                continue
            if len(current) + len(unit) + 1 <= self.chunk_size:
                current += "\n" + unit
            else:
                chunks.append(current.strip())
                if self.chunk_overlap > 0:
                    overlap_text = current[-self.chunk_overlap]
                    current = overlap_text + "\n" + unit
                else:
                    current = unit
        if current.strip():
            chunks.append(current.strip())
        return chunks

    def split_documents(self, doucuments: list[dict]) -> list[dict]:
        """
        输入documents,输出chunks
        """
        all_chunks = []

        # 遍历所有文件的内容,一个文件内容对应一个doc
        for doc in doucuments:
            source = doc["source"]
            content = doc["content"]
            file_type = doc.get("file_type", "unknown")

            chunks = self.split_text(content)

            # 索引，元素一起拿
            for index, chunk in enumerate(chunks):
                all_chunks.append(
                    {
                        "id": f"{source}_{index}",
                        "source": source,
                        "file_type": file_type,
                        "chunk_index": index,
                        "chunk_size": len(chunk),
                        "strategy": self.strategy,
                        "content": chunk,
                    }
                )
        return all_chunks
