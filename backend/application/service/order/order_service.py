"""订单域业务逻辑：订单状态机。

状态：1待付款 2待发货 3待收货 4已完成 5已取消。
流转：create(1) -> pay(2) -> ship(3) -> confirm(4)；任意阶段可 cancel(5)（部分限制）。
"""
import time
import uuid

from application.common.constants import HttpErrorCodeEnum
from application.common.exception.exception import HttpBusinessException
from application.common.models import BargainRecord, Order, Product, Review, User

STATUS_PENDING_PAY = 1
STATUS_PENDING_SHIP = 2
STATUS_PENDING_RECEIVE = 3
STATUS_DONE = 4
STATUS_CANCELLED = 5


def to_order_res(o: Order, has_review: bool = False) -> dict:
    return {
        "id": o.id,
        "order_no": o.order_no,
        "product_id": o.product_id,
        "product_title": getattr(o.product, "title", "") if hasattr(o, "product") else "",
        "product_image": (o.product.images[0] if hasattr(o, "product") and o.product.images else ""),
        "buyer_id": o.buyer_id,
        "buyer_nickname": getattr(o.buyer, "nickname", "") if hasattr(o, "buyer") else "",
        "seller_id": o.seller_id,
        "seller_nickname": getattr(o.seller, "nickname", "") if hasattr(o, "seller") else "",
        "deal_price": float(o.deal_price),
        "status": o.status,
        "address": o.address,
        "remark": o.remark,
        "has_review": has_review,
        "created_at": o.created_at,
    }


def _gen_order_no() -> str:
    return f"{time.strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8].upper()}"


async def create_order(
    buyer: User, product_id: int, bargain_record_id: int | None, address: str, remark: str
) -> Order:
    product = await Product.get_or_none(id=product_id)
    if product is None:
        raise HttpBusinessException(HttpErrorCodeEnum.NOT_FOUND, "商品不存在")
    if product.seller_id == buyer.id:
        raise HttpBusinessException(HttpErrorCodeEnum.PARAM_INVALID, "不能购买自己的商品")
    if product.status != 1:
        raise HttpBusinessException(HttpErrorCodeEnum.PARAM_INVALID, "商品已售出或下架")

    deal_price = float(product.sell_price)
    if bargain_record_id is not None:
        record = await BargainRecord.get_or_none(id=bargain_record_id)
        if record is None or record.product_id != product_id or record.buyer_id != buyer.id:
            raise HttpBusinessException(HttpErrorCodeEnum.PARAM_INVALID, "议价记录无效")
        if record.status != 2:
            raise HttpBusinessException(HttpErrorCodeEnum.PARAM_INVALID, "议价未被接受")
        deal_price = float(record.offer_price)

    # 标记商品已售，防止重复下单
    product.status = 2
    await product.save()

    order = await Order.create(
        order_no=_gen_order_no(),
        product=product,
        buyer=buyer,
        seller_id=product.seller_id,
        deal_price=deal_price,
        status=STATUS_PENDING_PAY,
        address=address,
        remark=remark,
    )
    order.product = product
    order.buyer = buyer
    return order


async def _get_order_for_action(order_id: int) -> Order:
    order = await Order.get_or_none(id=order_id).prefetch_related("product", "buyer", "seller")
    if order is None:
        raise HttpBusinessException(HttpErrorCodeEnum.NOT_FOUND, "订单不存在")
    return order


async def pay(buyer: User, order_id: int) -> Order:
    order = await _get_order_for_action(order_id)
    if order.buyer_id != buyer.id:
        raise HttpBusinessException(HttpErrorCodeEnum.FORBIDDEN, "无权操作")
    if order.status != STATUS_PENDING_PAY:
        raise HttpBusinessException(HttpErrorCodeEnum.PARAM_INVALID, "订单状态不正确")
    order.status = STATUS_PENDING_SHIP
    await order.save()
    return order


async def ship(seller: User, order_id: int) -> Order:
    order = await _get_order_for_action(order_id)
    if order.seller_id != seller.id:
        raise HttpBusinessException(HttpErrorCodeEnum.FORBIDDEN, "无权操作")
    if order.status != STATUS_PENDING_SHIP:
        raise HttpBusinessException(HttpErrorCodeEnum.PARAM_INVALID, "订单状态不正确")
    order.status = STATUS_PENDING_RECEIVE
    await order.save()
    return order


async def confirm(buyer: User, order_id: int) -> Order:
    order = await _get_order_for_action(order_id)
    if order.buyer_id != buyer.id:
        raise HttpBusinessException(HttpErrorCodeEnum.FORBIDDEN, "无权操作")
    if order.status != STATUS_PENDING_RECEIVE:
        raise HttpBusinessException(HttpErrorCodeEnum.PARAM_INVALID, "订单状态不正确")
    order.status = STATUS_DONE
    await order.save()
    return order


async def cancel(user: User, order_id: int) -> Order:
    order = await _get_order_for_action(order_id)
    if user.id not in (order.buyer_id, order.seller_id):
        raise HttpBusinessException(HttpErrorCodeEnum.FORBIDDEN, "无权操作")
    if order.status in (STATUS_DONE, STATUS_CANCELLED):
        raise HttpBusinessException(HttpErrorCodeEnum.PARAM_INVALID, "订单已结束")
    # 取消后恢复商品在售
    order.status = STATUS_CANCELLED
    await order.save()
    product = order.product
    product.status = 1
    await product.save()
    return order


async def my_orders(user: User, role: str, page: int, page_size: int) -> tuple[list[dict], int]:
    qs = Order.filter(buyer_id=user.id) if role == "buyer" else Order.filter(seller_id=user.id)
    qs = qs.prefetch_related("product", "buyer", "seller")
    total = await qs.count()
    orders = await qs.order_by("-id").offset((page - 1) * page_size).limit(page_size)
    result = []
    for o in orders:
        has_review = await Review.get_or_none(order_id=o.id) is not None
        result.append(to_order_res(o, has_review))
    return result, total
