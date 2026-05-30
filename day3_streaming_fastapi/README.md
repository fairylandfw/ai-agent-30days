# Day3 Streaming FastAPI Chatbot

这是 2026 AI Agent 工程师 30 天实战计划的 Day3 项目。

## 项目目标

实现一个支持多轮记忆和流式输出的 AI 后端聊天服务。

## 功能

- FastAPI 后端接口
- 普通聊天接口 `POST /chat`
- 流式聊天接口 `POST /chat/stream`
- 清空会话接口 `POST /chat/clear`
- 多轮对话记忆
- session 会话隔离
- OpenAI 兼容接口调用大模型

## 项目结构

```txt
day3_streaming_fastapi/
├── app/
│   ├── main.py
│   ├── api.py
│   ├── llm/
│   │   └── client.py
│   ├── memory/
│   │   └── json_memory.py
│   ├── config/
│   │   └── settings.py
│   └── schemas/
│       └── chat.py
├── data/
│   └── conversations/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```




## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置环境变量

复制 `.env.example` 为 `.env`，填写自己的模型配置。

## 启动服务

    python -m app.main

访问：
    http://127.0.0.1:8000

接口文档：
    http://127.0.0.1:8000/docs

## 普通聊天接口

    POST /chat

请求示例：
    {
      "session_id": "default",
      "message": "你好"
    }

响应示例：
    {
      "session_id": "default",
      "reply": "你好，我是 AI 助手。"
    }

## 流式聊天接口

    POST /chat/stream

curl 测试：
    curl -N -X POST "http://127.0.0.1:8000/chat/stream" \
    -H "Content-Type: application/json" \
    -d '{"session_id":"default","message":"请解释什么是流式输出"}'

## 清空会话

    POST /chat/clear

请求示例：
    {
      "session_id": "default",
      "message": "clear"
    }

## Day3 学习重点

* AI 应用需要封装成后端接口

* FastAPI 可以快速开发 AI 后端服务

* 普通响应是一次性返回完整答案

* 流式响应是生成一点返回一点

* chunk 是流式返回中的小片段

* StreamingResponse 可以实现基础流式输出
