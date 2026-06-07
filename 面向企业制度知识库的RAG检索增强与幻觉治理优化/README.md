## Day10 Local Embedding RAG

这是 2026 AI Agent 工程师 30 天实战计划的 Day10 项目。

## 项目目标

将 RAG 系统中的 Embedding 模块本地化，支持 BGE、m3e、text2vec 等本地中文 Embedding 模型，同时保留 OpenAI Embedding 兼容模式。

## 功能

- 支持 OpenAI Embedding
- 支持本地 Embedding
- 支持 BGE
- 支持 m3e
- 支持 text2vec
- 支持 FAISS 向量库
- 支持向量检索
- 支持混合检索
- 支持 Embedding 效果评估接口
- 支持 RAG 问答

## 安装依赖

```bash
pip install -r requirements.txt
```

## 环境变量

复制 `.env.example` 为 `.env`：
    EMBEDDING_PROVIDER=local
    LOCAL_EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5
    LOCAL_EMBEDDING_DEVICE=cpu
    NORMALIZE_EMBEDDINGS=true

## 启动

    python -m app.main

访问：
    http://127.0.0.1:8000/docs

## 查看 Embedding 配置

    GET /embedding/info

## 构建知识库

    POST /knowledge/build

## 向量检索

    POST /retrieve/vector
    
    {
      "question": "一线城市住宿费可以报销多少钱？",
      "top_k": 5
    }

## Embedding 评估

    POST /embedding/evaluate
    
    {
      "question": "一线城市住宿费可以报销多少钱？",
      "expected_source": "company_policy.txt",
      "expected_keywords": ["一线城市", "住宿", "500"],
      "top_k": 5
    }

## RAG 问答

    POST /ask
    
    {
      "question": "公司内部敏感信息可以上传外部平台吗？"
    }

## 支持模型示例

| 模型                               | 说明                  |
| -------------------------------- | ------------------- |
| BAAI/bge-small-zh-v1.5           | 智源，推荐入门，中文效果好       |
| moka-ai/m3e-small                | MOKA，中文语义检索常用       |
| shibing624/text2vec-base-chinese | text2vec,中文句向量经典模型  |
| text-embedding-3-small           | OpenAI 云端 Embedding |

## 注意事项

切换 Embedding 模型后必须重建向量库：
    rm -rf data/vector_store/*

然后重新调用：
    POST /knowledge/build

## Day10 学习重点

* Embedding 是 RAG 检索的语义基础

* 本地 Embedding 可降低成本并增强数据安全

* 不同 Embedding 模型不能混用同一个向量库

* 切换模型后必须重建索引

* Embedding 效果需要用 Recall@K、Hit Rate 等方式评估

## 

## 本地模型部署无法下载

```bash
$env:HF_ENDPOINT="https://hf-mirror.com"
python -m app.main
```




