import logging
from pathlib import Path
from app.config.settings import settings


def setup_logger(name: str = "ai_app") -> logging.Logger:
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    # 创建日志器
    logger = logging.getLogger(name)
    logger.setLevel(settings.LOG_LEVEL)

    # 该日志器已经配置过处理器
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        # 定义日志的输出格式 生成时间|日志级别|日志器的名字|自制内容
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        # 定义时间显示格式
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 创建控制台日志处理器 打印到终端里
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # 创建文件日志处理器 存到日志文件中
    file_handler = logging.FileHandler(log_dir / "app.log", encoding="utf-8")
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger


logger = setup_logger()
