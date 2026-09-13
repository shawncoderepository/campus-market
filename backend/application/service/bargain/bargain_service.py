"""议价域业务逻辑：议价状态机。

议价会话由 (product_id, buyer_id) 唯一确定。
状态流转：买家出价(待响应) -> 卖家 接受/拒绝/还价 -> ...
接受后可将该成交价用于下单（deal_price）。
"""
from tortoise.expressions import Q

from application.common.constants import HttpErrorCodeEnum
from application.common.exception.exception import HttpBusinessException
from application.common.models import BargainRecord, Product, User

STATUS_PENDING = 1
STATUS_ACCEPTED = 2
STATUS_REJECTED = 3


def to_record_res(r: BargainRecord) -> dict:
    return {
        "id": r.id,
        "product_id": r.product_id,
        "product_title": getattr(r.product, "title", "") if hasattr(r, "product") else "",
        "product_image": (r.product.images[0] if hasattr(r, "product") and r.product.images else ""),
        "buyer_id": r.buyer_id,
        "buyer_nickname": getattr(r.buyer, "nickname", "") if hasattr(r, "buyer") else "",
        "seller_id": r.seller_id,
        "seller_nickname": getattr(r.seller, "nickname", "") if hasattr(r, "seller") else "",
        "round": r.round,
        "offer_price": float(r.offer_price) if r.offer_price is not None else None,
        "role": r.role,
        "message": r.message,
        "status": r.status,
        "created_at": r.created_at,
    }


async def _get_product(product_id: int, prefetch_seller: bool = False) -> Product:
    qs = Product.get_or_none(id=product_id)
    if prefetch_seller:
        qs = qs.prefetch_related("seller")
    product = await qs
    if product is None:
        raise HttpBusinessException(HttpErrorCodeEnum.NOT_FOUND, "商品不存在")
    return product


async def _current_round(product_id: int, buyer_id: int) -> int:
    count = await BargainRecord.filter(product_id=product_id, buyer_id=buyer_id).count()
    return count // 2 + 1 if count else 1


async def buyer_offer(buyer: User, product_id: int, offer_price: float, message: str) -> BargainRecord:
    product = await _get_product(product_id)
    if product.seller_id == buyer.id:
        raise HttpBusinessException(HttpErrorCodeEnum.PARAM_INVALID, "不能对自己发布的商品议价")
    if product.status != 1:
        raise HttpBusinessException(HttpErrorCodeEnum.PARAM_INVALID, "商品不在售")
    # 最近一条若是买家待响应，则不允许重复出价
    last = (
        await BargainRecord.filter(product_id=product_id, buyer_id=buyer.id)
        .order_by("-id")
        .first()
    )
    if last and last.role == "buyer" and last.status == STATUS_PENDING:
        raise HttpBusinessException(HttpErrorCodeEnum.PARAM_INVALID, "请等待卖家响应后再出价")
    round_no = await _current_round(product_id, buyer.id)
    record = await BargainRecord.create(
        product=product,
        buyer=buyer,
        seller_id=product.seller_id,
        round=round_no,
        offer_price=offer_price,
        role="buyer",
        message=message,
        status=STATUS_PENDING,
    )
    record.product = product
    record.buyer = buyer
    return record


async def seller_reply(
    seller: User, product_id: int, buyer_id: int, offer_price: float, message: str
) -> BargainRecord:
    product = await _get_product(product_id)
    if product.seller_id != seller.id:
        raise HttpBusinessException(HttpErrorCodeEnum.FORBIDDEN, "无权操作该商品议价")
    last = (
        await BargainRecord.filter(product_id=product_id, buyer_id=buyer_id)
        .order_by("-id")
        .first()
    )
    if last is None or last.role != "buyer" or last.status != STATUS_PENDING:
        raise HttpBusinessException(HttpErrorCodeEnum.PARAM_INVALID, "当前无待响应的买家出价")
    # 拒绝买家上一轮后，卖家还价
    last.status = STATUS_REJECTED
    await last.save()
    round_no = last.round
    record = await BargainRecord.create(
        product=product,
        buyer_id=buyer_id,
        seller=seller,
        round=round_no,
        offer_price=offer_price,
        role="seller",
        message=message,
        status=STATUS_PENDING,
    )
    record.product = product
    record.seller = seller
    return record


async def respond(user: User, record_id: int, accept: bool) -> BargainRecord:
    record = await BargainRecord.get_or_none(id=record_id).prefetch_related("product", "buyer", "seller")
    if record is None:
        raise HttpBusinessException(HttpErrorCodeEnum.NOT_FOUND, "议价记录不存在")
    if record.status != STATUS_PENDING:
        raise HttpBusinessException(HttpErrorCodeEnum.PARAM_INVALID, "该出价已响应")
    # 权限：买家出价的响应方是卖家；卖家出价的响应方是买家
    if record.role == "buyer" and user.id != record.seller_id:
        raise HttpBusinessException(HttpErrorCodeEnum.FORBIDDEN, "只有卖家能响应买家出价")
    if record.role == "seller" and user.id != record.buyer_id:
        raise HttpBusinessException(HttpErrorCodeEnum.FORBIDDEN, "只有买家能响应卖家出价")
    record.status = STATUS_ACCEPTED if accept else STATUS_REJECTED
    await record.save()
    return record


async def session(user: User, product_id: int, buyer_id: int | None) -> dict:
    """获取某商品某买家的议价会话。买家看自己，卖家可指定 buyer_id。"""
    product = await _get_product(product_id, prefetch_seller=True)
    if buyer_id is None:
        buyer_id = product.seller_id if user.id != product.seller_id else user.id
        # 买家查询时 buyer_id 应为自己
        if user.id != product.seller_id:
            buyer_id = user.id
    records = (
        await BargainRecord.filter(product_id=product_id, buyer_id=buyer_id)
        .prefetch_related("product", "buyer", "seller")
        .order_by("id")
    )
    pending = next((r for r in reversed(records) if r.status == STATUS_PENDING), None)
    turn = "none"
    if pending is not None:
        turn = "seller" if pending.role == "buyer" else "buyer"
    return {
        "product_id": product.id,
        "product_title": product.title,
        "product_image": product.images[0] if product.images else "",
        "sell_price": float(product.sell_price),
        "buyer_id": buyer_id,
        "buyer_nickname": records[0].buyer.nickname if records else "",
        "seller_id": product.seller_id,
        "seller_nickname": getattr(product, "seller", None) and product.seller.nickname or "",
        "records": [to_record_res(r) for r in records],
        "pending_record_id": pending.id if pending else None,
        "turn": turn,
    }


async def my_sessions(user: User) -> list[dict]:
    """我参与的所有议价会话（按商品分组，取每个会话最新一条）。"""
    qs = BargainRecord.filter(Q(buyer_id=user.id) | Q(seller_id=user.id))
    records = await qs.prefetch_related("product", "buyer", "seller").order_by("-id")
    seen: set[tuple[int, int]] = set()
    sessions = []
    for r in records:
        key = (r.product_id, r.buyer_id)
        if key in seen:
            continue
        seen.add(key)
        sessions.append(to_record_res(r))
    return sessions
