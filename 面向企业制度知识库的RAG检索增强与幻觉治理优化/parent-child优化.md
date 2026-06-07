

**加入 parent-child 和 metadata**

请继续修改文件：
D:\project\agent\面向企业制度知识库的 RAG 检索增强与幻觉治理优化\app\rag\text_splitter.py

目标：
在上一版条款级切分方法基础上，新增 parent-child 分块输出能力。不要删除已有方法。可以新增方法；只有在必要时才最小修改 split_documents，使它可以在 strategy="section" 时输出带 parent-child metadata 的 chunks。

设计：
一级制度条款作为 parent。
长 parent 内部切出的片段作为 child。
短 parent 可以 parent 和 child 同内容。

请新增方法：

def section_split_with_metadata(self, text: str, source: str, file_type: str = "unknown") -> list[dict]:
    ...

输出每个 child chunk 的 dict，字段包括：

- id: 唯一 chunk id，例如 "{source}_section_{section_index}_child_{child_index}"
  
  - source
  - file_type
  - chunk_index
  - chunk_size
  - strategy: "section"
  - content: 用于生成阶段的原文内容，必须包含 parent_title
  - raw_text: 不额外拼接检索上下文的原始 chunk 内容
  - index_text: 用于 embedding/BM25 建索引的文本
  - parent_id
  - parent_index
  - parent_title
  - child_index
  - chunk_type: "section_child"
  
  index_text 规则：
  
  - 用于检索索引，可以比 content 多一些上下文。
  - 至少包含：
    文档来源、parent_title、raw_text。
  - 示例：
    "来源文件：company_policy.txt\n所属条款：三、住宿费报销制度\n内容：普通城市住宿标准为每日不超过 300 元。"
  
  parent-child 规则：
  
  - section_split_with_metadata 内部按一级标题切 parent。
  - 如果 parent 不长，输出一个 child，child_index=0。
  - 如果 parent 太长，调用 split_long_section 切成多个 child。
  - 每个 child 的 content 和 index_text 都必须包含 parent_title。
  - 不同 parent 之间不 overlap。
  - child 可以在同一个 parent 内部 overlap。
  
  split_documents 修改要求：
  
  - 只在 self.strategy == "section" 时使用 section_split_with_metadata。
  - 其他 strategy 的行为必须保持不变。
  - 原有字段 id、source、file_type、chunk_index、chunk_size、strategy、content 仍然保留，避免影响下游代码。
  - 如果 section_split_with_metadata 没识别到一级标题，可以回退到原 split_documents 当前逻辑。
  
  限制：
  
  - 不要修改其他文件。
  - 不要改动已有非 section 策略的输出。
  - 不要引入第三方依赖。
    
    

**版本 3：检索 child，生成时补同 parent 相邻 child**

请修改 RAG 检索相关代码，实现“检索 child，生成时可补充同 parent 下相邻 child”的轻量 parent-child retrieval。

目标：
不推翻现有 vector / keyword / hybrid / rerank 逻辑，只在已有结果基础上增加上下文扩展能力。

背景：
section 策略下，每个 chunk 可能带有：

- parent_id
- parent_title
- child_index
- raw_text
- index_text

检索时应该使用更适合召回的 index_text；生成时应该使用 content/raw_text，并可补充同 parent 下相邻 child，避免 child 太短丢上下文。

请按以下步骤修改：

1. 修改向量构建使用 index_text

找到构建 embedding 的地方，例如 RAGPipeline.build_knowledge_base 中：

texts = [chunk["content"] for chunk in chunks]

改为优先使用 index_text：

texts = [chunk.get("index_text", chunk["content"]) for chunk in chunks]

要求：

- 没有 index_text 的旧 chunk 仍然正常工作。
2. 修改关键词索引使用 index_text

找到 KeywordRetriever.build 中 tokenize 的文本来源。

改为优先使用 index_text：

tokens = self.tokenize(chunk.get("index_text", chunk["content"]))

要求：

- 返回结果仍然保留原 chunk dict，不要把 content 替换成 index_text。

- 没有 index_text 的旧 chunk 仍然正常工作。
3. 新增同 parent 相邻 child 扩展

在 RetrievalPipeline 或 RAGPipeline 中新增方法，例如：

def expand_with_neighbor_children(self, retrieved_chunks: list[dict], window: int = 1) -> list[dict]:
    ...

功能：

- 对每个检索结果，如果包含 parent_id 和 child_index，则在当前知识库 chunks 中找到同 parent_id 下 child_index 前后 window 个 child。
- 默认 window=1，即补前一个和后一个 child。
- 去重，保持稳定顺序。
- 不跨 parent。
- 如果 chunk 没有 parent_id/child_index，则原样保留。
- 扩展出来的 neighbor chunk 标记：
  "expanded_from": 原始命中 chunk id
  "retrieval_source": 原 retrieval_source + ["neighbor"] 或单独标记为 ["neighbor"]

注意：

- 用于生成上下文扩展，不用于改变原始召回指标。

- 最终 answer 返回中最好能区分 retrieved_chunks 和 context_chunks：
  retrieved_chunks: 原始检索命中的 chunk
  context_chunks: 扩展后用于 prompt 的 chunk
4. 修改 RAGPipeline.answer

当前 answer 中 retrieved_chunks 直接来自 retrieval_result["final_results"]。

请改成：

- retrieved_chunks 仍然表示原始 final_results。

- context_chunks = expand_with_neighbor_children(retrieved_chunks, window=1)

- prompt 拼接使用 context_chunks。

- 返回结果中同时包含 retrieved_chunks 和 context_chunks。

- 旧字段 retrieved_chunks 不要删除，避免影响已有接口。
5. prompt 中展示 parent_title

拼接上下文时，如果 chunk 有 parent_title，加入：
所属条款：{parent_title}

如果有 raw_text，优先展示 raw_text；否则展示 content。

6. 限制
- 不要重写现有检索流程。
- 不要改变 vector_search / keyword_search / hybrid_search 的核心排序逻辑。
- 不要引入新依赖。
- 没有 parent-child metadata 的旧数据必须继续可用。
