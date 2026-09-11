"""用户域业务逻辑。"""
from application.common.constants import HttpErrorCodeEnum
from application.common.exception.exception import HttpBusinessException
from application.common.helper.security_helper import (
    create_access_token,
    hash_password,
    verify_password,
)
from application.common.models import User


def to_user_res(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "nickname": user.nickname,
        "avatar": user.avatar,
        "phone": user.phone,
        "student_no": user.student_no,
        "credit_score": user.credit_score,
        "role": user.role,
        "status": user.status,
        "created_at": user.created_at,
    }


async def register(username: str, password: str, nickname: str, student_no: str) -> User:
    exists = await User.get_or_none(username=username)
    if exists:
        raise HttpBusinessException(HttpErrorCodeEnum.PARAM_INVALID, "用户名已存在")
    user = await User.create(
        username=username,
        password_hash=hash_password(password),
        nickname=nickname or username,
        student_no=student_no,
    )
    return user


async def login(username: str, password: str) -> tuple[str, User]:
    user = await User.get_or_none(username=username)
    if user is None or not verify_password(password, user.password_hash):
        raise HttpBusinessException(HttpErrorCodeEnum.PARAM_INVALID, "用户名或密码错误")
    if user.status != 1:
        raise HttpBusinessException(HttpErrorCodeEnum.FORBIDDEN, "账号已被禁用")
    token = create_access_token(user.id)
    return token, user


async def update_profile(user: User, data: dict) -> User:
    for key in ("nickname", "avatar", "phone", "student_no"):
        value = data.get(key)
        if value is not None:
            setattr(user, key, value)
    await user.save()
    return user


async def change_password(user: User, old_password: str, new_password: str) -> None:
    if not verify_password(old_password, user.password_hash):
        raise HttpBusinessException(HttpErrorCodeEnum.PARAM_INVALID, "原密码错误")
    user.password_hash = hash_password(new_password)
    await user.save()
