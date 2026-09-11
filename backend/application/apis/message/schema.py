from pydantic import Field

from application.common.schema import SnakeCaseModel


class SendMessageReq(SnakeCaseModel):
    receiver_id: int
    product_id: int | None = None
    content: str = Field(min_length=1, max_length=1024)


class MessageRes(SnakeCaseModel):
    id: int
    sender_id: int
    sender_nickname: str
    sender_avatar: str
    receiver_id: int
    product_id: int | None
    content: str
    msg_type: int
    is_read: bool
    created_at: object = None


class ConversationRes(SnakeCaseModel):
    peer_id: int
    peer_nickname: str
    peer_avatar: str
    product_id: int | None
    last_content: str
    last_time: object = None
    unread_count: int = 0
