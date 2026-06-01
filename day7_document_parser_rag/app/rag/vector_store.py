import json
from pathlib import Path

import faiss
import numpy as np

from app.core.logger import logger
from app.config.settings import settings


class FaissVectorStore:
    def __init__(self, store_dir: str):
        self.store_dir = Path(store_dir)
        self.store_dir.mkdir(parents=True, exist_ok=True)

        # 定义FAISS索引文件的保存路径 向量写入index.faiss
        self.index_path = self.store_dir / "index.faiss"
        # 定义元数据文件的保存路劲  文本,来源写入metadata.json
        self.meta_path = self.store_dir / "metadata.json"

        self.index = None
        self.metadata = []

    def build(self, embeddings: list[list[float]], chunks: list[dict]):
        if not embeddings:
            raise ValueError("embeddings 不能为空")

        # 把向量列表转换成 numpy数组 float32节省内存,检索速度快,符合faiss格式要求
        vectors = np.array(embeddings).astype("float32")
        # vectors.shape[0/1] 0是有多少个向量,1单个向量有几维
        dimension = vectors.shape[1]

        # 归一化(单位向量)后 向量内积=余弦相似度
        faiss.normalize_L2(vectors)

        # 创建一个FAISS向量检索索引  IP=Inner Product 内积   Flat暴力精准检索
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(vectors)

        self.metadata = chunks

        logger.info("FAISS向量库构建完成,向量数量:%d,维度:%d", len(chunks), dimension)

    def save(self):
        if self.index is None:
            raise ValueError("index为空 无法保存")

        faiss.write_index(self.index, str(self.index_path))

        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)

        logger.info("向量库已保存到:%s", self.store_dir)

    def load(self):
        if not self.index_path.exists() or not self.meta_path.exists():
            raise FileNotFoundError("向量库文件不存在，请先构建知识库")

        self.index = faiss.read_index(str(self.index_path))

        with open(self.meta_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

    def search(
        self, query_embedding: list[float], top_k: int = settings.TOP_K
    ) -> list[dict]:
        """
        对单个问题 查找top_k个相似信息
        返回top_k条信息和分数
        """
        if self.index is None:
            self.load()

        query_vector = np.array([query_embedding]).astype("float32")
        faiss.normalize_L2(query_vector)

        scores, indices = self.index.search(query_vector, top_k)

        results = []

        # scores 和 indices都是二维数组，行数代表问题数，列数代表top_k
        # zip 分数和索引配对
        for score, index in zip(scores[0], indices[0]):
            if index == -1:
                continue

            item = self.metadata[index].copy()
            item["score"] = float(score)
            results.append(item)

        return results
