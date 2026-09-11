"""密码哈希与 JWT 签发/校验。

使用官方 bcrypt 库直接封装，避免 passlib 与新版 bcrypt 后端的兼容问题。
JWT 载荷中 sub 存放用户 ID（字符串）。
"""
from datetime import UTC, datetime, timedelta

import bcrypt
from jose import JWTError, jwt

from application.common.config import config


def hash_password(raw: str) -> str:
    # bcrypt 限制密码最长 72 字节，超长需截断
    pwd_bytes = raw.encode("utf-8")[:72]
    return bcrypt.hashpw(pwd_bytes, bcrypt.gensalt()).decode("utf-8")


def verify_password(raw: str, hashed: str) -> bool:
    try:
        pwd_bytes = raw.encode("utf-8")[:72]
        return bcrypt.checkpw(pwd_bytes, hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(user_id: int) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=config.jwt.access_token_expire_minutes)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, config.secret_key, algorithm=config.jwt.algorithm)


def decode_access_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, config.secret_key, algorithms=[config.jwt.algorithm])
        return int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        return None
