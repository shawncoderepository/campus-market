from fastapi import APIRouter, Depends

from application.apis.user.schema import (
    ChangePasswordReq,
    LoginReq,
    LoginRes,
    RegisterReq,
    UpdateProfileReq,
    UserRes,
)
from application.common.dependency import get_current_user
from application.common.helper.response_helper import ResponseHelper
from application.common.models import User
from application.common.schema.response_schema import BaseResponse
from application.service.user import user_service

user_router = APIRouter(prefix="/user", tags=["User"])


@user_router.post("/register", response_model=BaseResponse[UserRes], summary="注册")
async def register(req: RegisterReq) -> object:
    user = await user_service.register(req.username, req.password, req.nickname, req.student_no)
    return ResponseHelper.success(UserRes(**user_service.to_user_res(user)), message="注册成功")


@user_router.post("/login", response_model=BaseResponse[LoginRes], summary="登录")
async def login(req: LoginReq) -> object:
    token, user = await user_service.login(req.username, req.password)
    data = LoginRes(token=token, user=UserRes(**user_service.to_user_res(user)))
    return ResponseHelper.success(data, message="登录成功")


@user_router.get("/me", response_model=BaseResponse[UserRes], summary="获取当前用户")
async def me(current: User = Depends(get_current_user)) -> object:
    return ResponseHelper.success(UserRes(**user_service.to_user_res(current)))


@user_router.put("/profile", response_model=BaseResponse[UserRes], summary="修改资料")
async def update_profile(
    req: UpdateProfileReq, current: User = Depends(get_current_user)
) -> object:
    user = await user_service.update_profile(current, req.model_dump(exclude_none=True))
    return ResponseHelper.success(UserRes(**user_service.to_user_res(user)), message="修改成功")


@user_router.put("/password", summary="修改密码")
async def change_password(
    req: ChangePasswordReq, current: User = Depends(get_current_user)
) -> object:
    await user_service.change_password(current, req.old_password, req.new_password)
    return ResponseHelper.success(message="密码修改成功")
