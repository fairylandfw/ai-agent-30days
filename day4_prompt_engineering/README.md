# Day4 Prompt Engineering Assistant

这是 2026 AI Agent 工程师 30 天实战计划的 Day4 项目。

## 项目目标

实现一个支持 Prompt 模板切换的 AI 助手，用于练习 System Prompt、Few-shot、输出约束和结构化输出。

## 功能

- FastAPI 后端服务
- 多轮对话记忆
- 流式输出
- Prompt 模板管理
- JSON 结构化输出
- Markdown 教学输出
- 代码审查助手

## Prompt 类型

| prompt_type      | 说明            |
| ---------------- | ------------- |
| default          | 默认助手          |
| json_assistant   | JSON 结构化输出助手  |
| markdown_teacher | Markdown 教学助手 |
| code_reviewer    | 代码审查助手        |

## 项目结构

```txt
day4_prompt_engineering/
├── app/
│   ├── main.py
│   ├── api.py
│   ├── llm/
│   │   └── client.py
│   ├── memory/
│   │   └── json_memory.py
│   ├── config/
│   │   └── settings.py
│   ├── schemas/
│   │   └── chat.py
│   └── prompts/
│       ├── prompt_manager.py
│       └── templates/
│           ├── default.txt
│           ├── json_assistant.txt
│           ├── markdown_teacher.txt
│           └── code_reviewer.txt
├── data/
│   └── conversations/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

安装依赖
    pip install -r requirements.txt

## 配置环境变量

复制 `.env.example` 为 `.env`，填写自己的模型配置。
    OPENAI_API_KEY=your_api_key_here
    OPENAI_BASE_URL=https://api.openai.com/v1
    MODEL_NAME=gpt-4o-mini

    TEMPERATURE=0.3
    MAX_TOKENS=1000
    MAX_HISTORY_MESSAGES=10

## 启动服务

    python -m app.main

访问：
    http://127.0.0.1:8000

接口文档：
    http://127.0.0.1:8000/docs

## 请求示例

### 默认助手

    {
      "session_id": "default_user",
      "message": "什么是 Prompt 工程？",
      "prompt_type": "default"
    }

### JSON 助手

    {
      "session_id": "json_user",
      "message": "什么是 FastAPI？",
      "prompt_type": "json_assistant"
    }

### Markdown 教学助手

    {
      "session_id": "teacher_user",
      "message": "请教我什么是流式输出",
      "prompt_type": "markdown_teacher"
    }

### 代码审查助手

    {
      "session_id": "review_user",
      "message": "请审查这段 Python 代码：\n\ndef add(a,b):\n    return a+b",
      "prompt_type": "code_reviewer"
    }

## Day4 学习重点

* Prompt 不是一句话

* System Prompt 可以控制模型角色和行为

* Few-shot 可以提升输出稳定性

* 输出约束可以减少格式错误

* Prompt 应该像配置一样管理
