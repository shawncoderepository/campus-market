from enum import Enum


class HttpErrorCodeEnum(Enum):
    SUCCESS = (0, "成功")
    ERROR = (40000, "系统错误")
    UNAUTHORIZED = (40100, "未认证")
    FORBIDDEN = (40300, "无权访问")
    NOT_FOUND = (40400, "资源不存在")
    PARAM_INVALID = (41000, "参数校验错误")

    def __init__(self, code: int, message: str) -> None:
        self.code = code
        self.message = message
