# 文本切词器
import re


class TextSplitter:
    def __init__(
        self,
        chunk_size: int = 100,
        chunk_overlap: int = 20,
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
        elif self.strategy == "section":
            return self.section_split(text)
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
                    overlap_text = current[-self.chunk_overlap :]
                    current = overlap_text + "\n" + unit
                else:
                    current = unit
        if current.strip():
            chunks.append(current.strip())
        return chunks

    def is_primary_section_title(self, line: str) -> bool:
        line = line.strip()
        if not line:
            return False

        patterns = [
            r"^[一二三四五六七八九十百千万]+、.*$",
            r"^第[一二三四五六七八九十百千万0-9]+章.*$",
        ]
        return any(re.match(pattern, line) for pattern in patterns)

    def is_subsection_title(self, line: str) -> bool:
        line = line.strip()
        if not line:
            return False

        patterns = [
            r"^第[一二三四五六七八九十百千万0-9]+条.*$",
            # r"^[（(][一二三四五六七八九十百千万]+[）)].*$",
            r"^[0-9]+[.．、)）].*$",
        ]
        return any(re.match(pattern, line) for pattern in patterns)

    def section_split(self, text: str) -> list[str]:
        """
        按一级标题分开
        """
        if not text:
            return []

        lines = text.splitlines()
        sections = []  # list[str] 一段一段
        current_section = []  # 一行一行

        for line in lines:
            if self.is_primary_section_title(line):
                if current_section:
                    sections.append("\n".join(current_section).strip())
                current_section = [line]
            elif current_section:
                current_section.append(line)

        if current_section:
            sections.append("\n".join(current_section).strip())

        if not sections:
            return self.recursive_split(text)

        # listp[list[str]]   一行 一个 一级标题段
        chunks = []
        for section in sections:
            chunks.extend(self.split_long_section(section))
        return chunks

    def split_long_section(
        self, section_text: str, section_title: str | None = None
    ) -> list[str]:
        if len(section_text) <= self.chunk_size:
            return [section_text]

        lines = section_text.splitlines()
        if section_title is None:
            # 有标题 或 无标题
            section_title = lines[0].strip() if lines else ""
        else:
            section_title = section_title.strip()

        def ensure_section_title(chunk: str) -> str:
            """
            确保段落有标题
            """
            chunk = chunk.strip()
            if section_title and section_title not in chunk:
                return f"{section_title}\n{chunk}".strip()
            return chunk

        # 用二级标题划分 每段
        subsections = []
        current_subsection = []
        has_subsection_title = False

        # 从第二行开始
        for line in lines[1:]:
            if self.is_subsection_title(line):
                has_subsection_title = True
                if current_subsection:
                    subsections.append("\n".join(current_subsection).strip())
                current_subsection = [line]
            else:
                current_subsection.append(line)

        if current_subsection:
            subsections.append("\n".join(current_subsection).strip())

        # 没二级标题就采用recursive
        if not has_subsection_title:
            return [
                ensure_section_title(chunk)
                for chunk in self.recursive_split(section_text)
                if chunk.strip()
            ]

        #
        chunks = []
        current_chunk = section_title

        # 遍历二级标题分后的 每块
        for subsection in subsections:
            subsection = subsection.strip()
            if not subsection:
                continue

            # 之前加当前块比较小 就更新加入current_chunk 继续循环
            candidate = f"{current_chunk}\n{subsection}".strip()
            if len(candidate) <= self.chunk_size:
                current_chunk = candidate
                continue

            # current_chunk先加到chunks
            if current_chunk.strip() and current_chunk.strip() != section_title:
                chunks.append(ensure_section_title(current_chunk))

            # current_chunk更新为当前块 加入一级标题
            prefixed_subsection = f"{section_title}\n{subsection}".strip()
            if len(prefixed_subsection) <= self.chunk_size:
                current_chunk = prefixed_subsection
                continue

            # 长度比较大 就切 依次加标题到chunk里
            for chunk in self.recursive_split(subsection):
                if chunk.strip():
                    chunks.append(ensure_section_title(chunk))
            current_chunk = section_title

        if current_chunk.strip() and current_chunk.strip() != section_title:
            chunks.append(ensure_section_title(current_chunk))

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
