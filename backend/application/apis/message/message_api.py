from fastapi import APIRouter, Depends
from tortoise.expressions import Q

from application.apis.message.schema import ConversationRes, MessageRes, SendMessageReq
from application.common.dependency import get_current_user
from application.common.helper.response_helper import ResponseHelper
from application.common.models import Message, User
from application.common.schema.response_schema import BaseResponse, PageResult

message_router = APIRouter(prefix="/message", tags=["Message"])


def _to_res(m: Message) -> dict:
    return {
        "id": m.id,
        "sender_id": m.sender_id,
        "sender_nickname": getattr(m.sender, "nickname", "") if hasattr(m, "sender") else "",
        "sender_avatar": getattr(m.sender, "avatar", "") if hasattr(m, "sender") else "",
        "receiver_id": m.receiver_id,
        "product_id": m.product_id,
        "content": m.content,
        "msg_type": m.msg_type,
        "is_read": m.is_read,
        "created_at": m.created_at,
    }


@message_router.post("/send", response_model=BaseResponse[MessageRes], summary="发送消息")
async def send(req: SendMessageReq, current: User = Depends(get_current_user)) -> object:
    message = await Message.create(
        sender=current,
        receiver_id=req.receiver_id,
        product_id=req.product_id,
        content=req.content,
    )
    message.sender = current
    return ResponseHelper.success(MessageRes(**_to_res(message)), message="发送成功")


@message_router.get("/conversations", response_model=BaseResponse[list[ConversationRes]], summary="会话列表")
async def conversations(current: User = Depends(get_current_user)) -> object:
    # 与当前用户相关的所有消息，按对方 + 商品分组取最新
    messages = (
        await Message.filter(Q(sender_id=current.id) | Q(receiver_id=current.id))
        .prefetch_related("sender", "receiver")
        .order_by("-id")
    )
    peers: dict[tuple[int, int | None], dict] = {}
    for m in messages:
        peer_id = m.receiver_id if m.sender_id == current.id else m.sender_id
        key = (peer_id, m.product_id)
        if key in peers:
            continue
        peer = m.receiver if m.sender_id == current.id else m.sender
        unread = await Message.filter(
            sender_id=peer_id, receiver_id=current.id, product_id=m.product_id, is_read=False
        ).count()
        peers[key] = {
            "peer_id": peer_id,
            "peer_nickname": peer.nickname,
            "peer_avatar": peer.avatar,
            "product_id": m.product_id,
            "last_content": m.content,
            "last_time": m.created_at,
            "unread_count": unread,
        }
    return ResponseHelper.success([ConversationRes(**v) for v in peers.values()])


@message_router.get("/history", response_model=BaseResponse[PageResult[MessageRes]], summary="聊天记录")
async def history(
    peer_id: int,
    product_id: int | None = None,
    page: int = 1,
    page_size: int = 50,
    current: User = Depends(get_current_user),
) -> object:
    cond = (
        (Q(sender_id=current.id) & Q(receiver_id=peer_id))
        | (Q(sender_id=peer_id) & Q(receiver_id=current.id))
    )
    if product_id is not None:
        cond &= Q(product_id=product_id)
    qs = Message.filter(cond).prefetch_related("sender")
    total = await qs.count()
    messages = await qs.order_by("-id").offset((page - 1) * page_size).limit(page_size)
    # 标记对方发给我的为已读
    await Message.filter(sender_id=peer_id, receiver_id=current.id, is_read=False).update(is_read=True)
    items = [MessageRes(**_to_res(m)) for m in reversed(messages)]
    return ResponseHelper.success(
        PageResult[MessageRes](list=items, total=total, page=page, page_size=page_size)
    )


@message_router.get("/unread", summary="未读消息数")
async def unread(current: User = Depends(get_current_user)) -> object:
    count = await Message.filter(receiver_id=current.id, is_read=False).count()
    from application.common.schema import SnakeCaseModel

    class UnreadRes(SnakeCaseModel):
        count: int

    return ResponseHelper.success(UnreadRes(count=count))
