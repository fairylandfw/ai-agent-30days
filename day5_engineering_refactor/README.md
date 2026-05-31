# Day5 Engineering Refactor AI Assistant

这是 2026 AI Agent 工程师 30 天实战计划的 Day5 项目。

本项目是在 Day1~Day4 基础上的第一阶段工程化重构版本。

## 项目目标

将一个基础 AI 聊天助手整理成更规范的工程项目，加入配置管理、日志系统、工具函数、Prompt 模板管理和 GitHub 发布准备。

## 功能特性

- OpenAI 兼容接口调用大模型
- FastAPI 后端服务
- 普通聊天接口
- 流式聊天接口
- 多轮对话记忆
- session 会话隔离
- Prompt 模板管理
- JSON 结构化输出
- Markdown 教学输出
- 代码审查助手
- logger 日志系统
- 配置文件管理
- 统一响应工具

## 项目结构

```txt
day5_engineering_refactor/
├── app/
│   ├── main.py
│   ├── api.py
│   ├── config/
│   │   └── settings.py
│   ├── core/
│   │   └── logger.py
│   ├── llm/
│   │   └── client.py
│   ├── memory/
│   │   └── json_memory.py
│   ├── prompts/
│   │   ├── prompt_manager.py
│   │   └── templates/
│   │       ├── default.txt
│   │       ├── json_assistant.txt
│   │       ├── markdown_teacher.txt
│   │       └── code_reviewer.txt
│   ├── schemas/
│   │   └── chat.py
│   └── utils/
│       └── response.py
├── data/
│   └── conversations/
├── logs/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

环境要求

* Python 3.10+
* OpenAI 兼容模型 API

## 安装依赖

    pip install -r requirements.txt

## 配置环境变量

复制 `.env.example` 为 `.env`：

```bash
cp .env.example .env
```

Windows 可以手动复制文件。

配置内容：

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4o-mini

TEMPERATURE=0.3
MAX_TOKENS=1000
MAX_HISTORY_MESSAGES=10

LOG_LEVEL=INFO
```

## 启动服务

    python -m app.main

服务地址：
    http://127.0.0.1:8000

接口文档：
    http://127.0.0.1:8000/docs

## 接口说明

### 健康检查

    GET /health

### 查看 Prompt 类型

    GET /prompts

### 普通聊天

    POST /chat

请求示例：
    {
      "session_id": "default",
      "message": "你好",
      "prompt_type": "default"
    }

### 流式聊天

    POST /chat/stream

请求示例：
    {
      "session_id": "default",
      "message": "请解释什么是流式输出",
      "prompt_type": "markdown_teacher"
    }

### 清空记忆

    POST /chat/clear

请求示例：
    {
      "session_id": "default",
      "message": "clear",
      "prompt_type": "default"
    }

## Prompt 类型

| prompt_type      | 说明            |
| ---------------- | ------------- |
| default          | 默认助手          |
| json_assistant   | JSON 结构化输出助手  |
| markdown_teacher | Markdown 教学助手 |
| code_reviewer    | 代码审查助手        |

## 日志

项目日志会输出到：

```textile
logs/app.log
```

## Day5 学习重点

* 工程化项目结构
* 配置集中管理
* logger 日志系统
* utils 工具模块
* README 编写
* Git 基础操作
* GitHub 项目发布
