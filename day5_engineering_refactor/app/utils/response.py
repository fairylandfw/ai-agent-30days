# 统一响应工具
def success_response(data=None, message: str = "sucesss"):
    return {"success": True, "message": message, "data": data}


def error_response(message: str = "error", data=None):
    return {"success": False, "message": message, "data": data}
