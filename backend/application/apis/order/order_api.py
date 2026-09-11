from fastapi import APIRouter, Depends

from application.apis.order.schema import CreateOrderReq, OrderActionReq, OrderRes
from application.common.dependency import get_current_user
from application.common.helper.response_helper import ResponseHelper
from application.common.models import User
from application.common.schema.response_schema import BaseResponse, PageResult
from application.service.order import order_service

order_router = APIRouter(prefix="/order", tags=["Order"])


@order_router.post("/create", response_model=BaseResponse[OrderRes], summary="下单")
async def create(req: CreateOrderReq, current: User = Depends(get_current_user)) -> object:
    order = await order_service.create_order(
        current, req.product_id, req.bargain_record_id, req.address, req.remark
    )
    return ResponseHelper.success(OrderRes(**order_service.to_order_res(order)), message="下单成功")


@order_router.post("/pay", response_model=BaseResponse[OrderRes], summary="付款")
async def pay(req: OrderActionReq, current: User = Depends(get_current_user)) -> object:
    order = await order_service.pay(current, req.order_id)
    return ResponseHelper.success(OrderRes(**order_service.to_order_res(order)), message="付款成功")


@order_router.post("/ship", response_model=BaseResponse[OrderRes], summary="发货")
async def ship(req: OrderActionReq, current: User = Depends(get_current_user)) -> object:
    order = await order_service.ship(current, req.order_id)
    return ResponseHelper.success(OrderRes(**order_service.to_order_res(order)), message="已发货")


@order_router.post("/confirm", response_model=BaseResponse[OrderRes], summary="确认收货")
async def confirm(req: OrderActionReq, current: User = Depends(get_current_user)) -> object:
    order = await order_service.confirm(current, req.order_id)
    return ResponseHelper.success(OrderRes(**order_service.to_order_res(order)), message="交易完成")


@order_router.post("/cancel", response_model=BaseResponse[OrderRes], summary="取消订单")
async def cancel(req: OrderActionReq, current: User = Depends(get_current_user)) -> object:
    order = await order_service.cancel(current, req.order_id)
    return ResponseHelper.success(OrderRes(**order_service.to_order_res(order)), message="订单已取消")


@order_router.get("/my", response_model=BaseResponse[PageResult[OrderRes]], summary="我的订单")
async def my_orders(
    role: str = "buyer",
    page: int = 1,
    page_size: int = 20,
    current: User = Depends(get_current_user),
) -> object:
    items, total = await order_service.my_orders(current, role, page, page_size)
    return ResponseHelper.success(
        PageResult[OrderRes](
            list=[OrderRes(**d) for d in items], total=total, page=page, page_size=page_size
        )
    )
