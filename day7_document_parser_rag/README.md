# Day7 Document Parser RAG

这是 2026 AI Agent 工程师 30 天实战计划的 Day7 项目。

## 项目目标

在 Day6 极简 RAG 系统基础上，升级文档解析能力，支持 PDF / Word / TXT / Markdown 多格式企业文档知识库。

## 功能

- 支持 TXT 文档解析
- 支持 Markdown 文档解析
- 支持 PDF 文档解析
- 支持 Word docx 文档解析
- 支持 Word 表格文本提取
- 文档基础清洗
- chunk 切片
- embedding 向量化
- FAISS 向量库
- RAG 问答接口

## 支持格式

| 文件类型                             | 后缀    |
| -------------------------------- | ----- |
| TXT                              | .txt  |
| Markdown                         | .md   |
| PDF/暂未完善                         | .pdf  |
| Word | .docx |

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置环境变量

复制 `.env.example` 为 `.env`：

```.env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small 
TEMPERATURE=0.2 
MAX_TOKENS=1000 
CHUNK_SIZE=500 CHUNK_OVERLAP=80 
TOP_K=4 
LOG_LEVEL=INFO   
```

## 启动服务

    python -m app.main

访问接口文档：
    http://127.0.0.1:8000/docs

## 构建知识库

把文档放入：data/docs/

然后调用：POST /knowledge/build

## 检索

    POST /retrieve

请求：

```txt
{ 
    "question": "一线城市住宿费标准是多少？"
 }
```

## 问答

    POST /ask

请求：




```textile
{
  "question": "星河 AI 知识库平台适合哪些场景？"
}
```

## OCR 说明

如果 PDF 是扫描件，普通 PDF 解析库无法提取文字，需要使用 OCR 技术。

常见 OCR 方案：

* PaddleOCR
* Tesseract
* 百度 OCR
* 腾讯 OCR
* 阿里 OCR
* MinerU

Day7 只理解 OCR 概念，不强制实现。

## Day7 学习重点

* 文档解析是 RAG 的入口

* PDF、Word、Markdown、TXT 解析方式不同

* Word 表格需要单独处理

* 扫描 PDF 需要 OCR

* 文档清洗会影响 chunk 和检索质量


