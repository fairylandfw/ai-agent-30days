import json
from pathlib import Path
from app.config.settings import settings
from app.core.logger import logger


class JsonMemory:
    """
    使用JSON文件保存聊天历史
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.storage_dir = Path(settings.CONVERSATION_DIR)
        # parents=True 允许多层创建 xxx/xxx/xxx   exist_ok=True 允许存在
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.file_path = self.storage_dir / f"{session_id}.json"

    def load_history(self) -> list[dict]:
        """
        读取历史消息
        如果文件不存在 返回空列表
        """
        if not self.file_path.exists():
            return []

        # with自动关文件  r只读  打开后的文件对象为f
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                # 读取f返回list[dict]
                return json.load(f)
        except Exception as e:
            logger.error("加载历史记录失败:session_id=%s,error=%s", self.session_id, e)
            return []

    def save_history(self, history: list[dict]) -> None:
        """
        保存完整历史消息
        """
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                # ensure保证中文不乱码，indent每行锁紧2个字符
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error("保存历史记录失败:session_id=%s,error=%s", self.session_id, e)

    def add_message(self, role: str, content: str) -> None:
        """
        添加信息,只能是user或assitant
        """
        history = self.load_history()
        history.append({"role": role, "content": content})
        self.save_history(history)

    def clear(self) -> None:
        """清空"""
        self.save_history([])
        logger.info("清空会话记录:seession_id=%s", self.session_id)
