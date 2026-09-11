"""FastAPI 依赖项：获取当前登录用户。"""
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from application.common.constants import HttpErrorCodeEnum
from application.common.exception.exception import HttpBusinessException
from application.common.helper.security_helper import decode_access_token
from application.common.models import User

# tokenUrl 仅用于 Swagger 文档的授权入口
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login", auto_error=False)


async def get_current_user(token: str | None = Depends(oauth2_scheme)) -> User:
    if not token:
        raise HttpBusinessException(HttpErrorCodeEnum.UNAUTHORIZED, "请先登录")
    user_id = decode_access_token(token)
    if user_id is None:
        raise HttpBusinessException(HttpErrorCodeEnum.UNAUTHORIZED, "登录已过期，请重新登录")
    user = await User.get_or_none(id=user_id)
    if user is None or user.status != 1:
        raise HttpBusinessException(HttpErrorCodeEnum.UNAUTHORIZED, "账号不存在或已被禁用")
    return user


async def get_current_user_optional(token: str | None = Depends(oauth2_scheme)) -> User | None:
    try:
        return await get_current_user(token)
    except HttpBusinessException:
        return None


async def get_current_admin(current: User = Depends(get_current_user)) -> User:
    if current.role != 2:
        raise HttpBusinessException(HttpErrorCodeEnum.FORBIDDEN, "需要管理员权限")
    return current
