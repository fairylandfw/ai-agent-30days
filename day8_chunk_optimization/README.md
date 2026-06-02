# Day8 Chunk Optimization RAG

这是 2026 AI Agent 工程师 30 天实战计划的 Day8 项目。

## 项目目标

实验并优化 RAG 中的 chunk 切片策略，理解 chunk_size、chunk_overlap 和不同切片方式对召回率、上下文完整性和幻觉率的影响。

## 功能

- 支持 fixed 固定长度切片
- 支持 paragraph 段落切片
- 支持 sentence 句子切片
- 支持 recursive 递归切片
- 支持 chunk 预览接口
- 支持指定 chunk 参数构建知识库
- 支持检索观察
- 支持简单 chunk 实验接口

## 启动

```bash
pip install -r requirements.txtpython -m app.main
```

访问：
    http://127.0.0.1:8000/docs

## 预览 Chunk

```
POST /chunks/preview
```

示例：

```
{ "chunk_size": 300, "chunk_overlap": 50, "strategy": "recursive" }
```

## 构建知识库

    POST /knowledge/build

示例：

```
{
  "chunk_size": 300,
  "chunk_overlap": 50,
  "strategy": "recursive"
}
```

## 检索

    POST /retrieve

示例：
    {
      "question": "一线城市住宿费标准是多少？"
    }

## Chunk 实验

    POST /experiments/chunk

示例：
    {
      "question": "一线城市住宿费标准是多少？",
      "expected_source": "company_policy.txt",
      "chunk_size": 300,
      "chunk_overlap": 50,
      "strategy": "recursive"
    }

## 支持的切片策略

| strategy  | 说明               |
| --------- | ---------------- |
| fixed     | 固定字符长度切片         |
| paragraph | 按段落切片            |
| sentence  | 按句子切片            |
| recursive | 段落 → 句子 → 字符递归切片 |

## Day8 学习重点

* chunk 是 RAG 检索的基本单位

* chunk 太小会导致语义不完整

* chunk 太大会导致语义稀释和成本升高

* overlap 可以缓解边界截断问题

* 不同文档类型需要不同切片策略


