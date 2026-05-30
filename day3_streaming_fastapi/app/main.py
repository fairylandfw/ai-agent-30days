import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        # 运行服务
        # 文件夹.文件名：实例名 （api.py里写的app=FastAPI()）
        "app.api:app",
        # 本机回环地址
        host="127.0.0.1",
        # 端口号
        port=8000,
        # 修改代码后保存，服务器自动重启，适合开发的时候，上线时不要用
        reload=True,
    )
