# 文档加载器

from pathlib import Path
from app.core.logger import logger


class DocumentLoader:
    def __init__(self, docs_dir: str):
        self.docs_dir = Path(docs_dir)

    def load_txt_files(self) -> list[dict]:
        """
        返回docs_dir下的所有txt文件
        返回格式：
        [
            {
                "source":"文件名",
                "content":"文件内容"
            }
        ]
        """

        document = []

        if not self.docs_dir.exists():
            logger.warning("文档目录不存在：%s", self.docs_dir)

        # 循环遍历知识库文件夹下的所有文件
        for file_path in self.docs_dir.glob("*.txt"):
            try:
                content = file_path.read_text(encoding="utf-8")
                document.append(
                    {
                        "source": file_path.name,
                        "content": content,
                    }
                )

                logger.info("加载文档成功:%s", file_path.name)

            except Exception as e:
                logger.error("加载文档失败:%s,error=%s", file_path.name, e)

        return document
