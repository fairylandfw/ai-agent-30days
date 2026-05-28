# Day1 AI Chatbot

这是我的第一个AI聊天机器人项目。

## 功能

- 调用gpt5.5大模型接口

- 支持命令行聊天

- 支持system prompt 人设

- 使用环境变量管理配置

## 项目结构

```textile
DAY1_AI_CHATBOT
├── main.py
├── config.py
├── .env
├── .env.example
├── .gitignore
├── .requirements.txt
├── README.md
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置环境变量

复制`.env.example`为`.env`，然后填写自己的API Key：

```Env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4o-mini
```

## 运行

```bash
python main.py
```

## 退出

输入：

```textile
exit
```

或者：

```textile
quit
```
