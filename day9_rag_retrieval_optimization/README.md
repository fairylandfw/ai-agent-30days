# Day9 RAG Retrieval Optimization

这是 2026 AI Agent 工程师 30 天实战计划的 Day9 项目。

## 项目目标

优化 RAG 检索召回阶段，实现 TopK、关键词召回、多路召回、去重和简单 Rerank。

## 功能

- 向量检索
- 关键词检索
- 混合检索
- 多路召回融合
- 检索结果去重
- 简单 Rerank 重排序
- RAG 问答接口
- 检索调试接口

## 安装依赖

```bash
pip install -r requirements.txt
```

## 环境变量

复制 `.env.example` 为 `.env`：

    OPENAI_API_KEY=your_api_key_here
    OPENAI_BASE_URL=https://api.openai.com/v1
    MODEL_NAME=gpt-4o-mini
    EMBEDDING_MODEL=text-embedding-3-small
    
    CHUNK_SIZE=400
    CHUNK_OVERLAP=80
    SPLIT_STRATEGY=recursive
    
    VECTOR_TOP_K=8
    KEYWORD_TOP_K=8
    FINAL_TOP_K=4
    
    VECTOR_WEIGHT=0.7
    KEYWORD_WEIGHT=0.3

## 启动

    python -m app.main

访问：
    http://127.0.0.1:8000/docs

## 构建知识库

    POST /knowledge/build

## 向量检索

    POST /retrieve/vector
    
    {
      "question": "一线城市住宿费可以报销多少钱？",
      "top_k": 5
    }

## 关键词检索

    POST /retrieve/keyword
    
    {
      "question": "一线城市住宿费 500 元",
      "top_k": 5
    }

## 混合检索

    POST /retrieve/hybrid
    
    {
      "question": "员工每周可以远程办公几天？",
      "vector_top_k": 8,
      "keyword_top_k": 8,
      "final_top_k": 4,
      "use_rerank": true
    }

## RAG 问答

    POST /ask
    
    {
      "question": "敏感信息传输必须使用什么通道？"
    }

## Day9 学习重点

* TopK 太小会漏召回，太大会引入噪音

* 向量检索擅长语义相似

* 关键词检索擅长数字、专有名词、精确匹配

* 多路召回可以提高召回率

* 去重可以减少重复上下文

* Rerank 可以提高最终上下文质量
