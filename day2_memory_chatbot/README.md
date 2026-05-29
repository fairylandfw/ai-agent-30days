# Day2 Memory Chatbot

这是 2026 AI Agent 工程师 30 天实战计划的 Day2 项目。

## 项目目标

实现一个带上下文记忆的命令行 AI 聊天助手。

## 功能

- 支持多轮对话
- 支持本地 JSON 保存聊天历史
- 支持 session 会话隔离
- 支持清空当前会话记忆
- 支持历史消息截断，控制 token 成本
- 使用 OpenAI 兼容接口调用大模型

## 项目结构

```txt
day2_memory_chatbot/
├── app/
│   ├── main.py
│   ├── llm/
│   │   └── client.py
│   ├── memory/
│   │   └── json_memory.py
│   └── config/
│       └── settings.py
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

复制`.env.example`为 `.env`，填写自己的模型配置

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4o-mini
TEMPERATURE=0.7
MAX_TOKENS=800
MAX_HISTORY_MESSAGES=10
```

## 运行

```bash
python -m app.main
```

## 使用方式

启动后输入 session_id。

如果直接回车，默认使用：

```textile
default
```

支持命令：

```textile
exit
quit
clear
```

- `exit` / `quit`：退出程序
- `clear`：清空当前会话记忆

Day2 学习重点
---------

* 大模型 API 是无状态的
* 多轮记忆是通过 history 拼接实现的
* 每次请求都要把历史消息重新传给模型
* 历史消息不能无限增长，需要截断
* session 可以实现不同用户的会话隔离


