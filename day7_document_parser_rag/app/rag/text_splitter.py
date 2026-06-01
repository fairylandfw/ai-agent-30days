# 文本切词器


class TextSplitter:
    def __init__(self, chunk_size, chunk_overlap):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> list[str]:
        """
        简单字符级分片
        """

        chunks = []

        if not text:
            return chunks

        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + self.chunk_size
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start += self.chunk_size - self.chunk_overlap

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
                        "content": chunk,
                    }
                )
        return all_chunks
