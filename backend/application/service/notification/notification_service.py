"""系统通知服务：以管理员身份向用户发送站内系统消息（msg_type=2）。

复用站内消息表，前端消息页将管理员会话展示为“系统通知”。
"""
from __future__ import annotations

from application.common.models import Message, Product, Report, User


async def send_system_notification(
    sender: User, receiver_id: int, content: str, product_id: int | None = None
) -> Message:
    """以系统/管理员名义给指定用户发一条系统消息。"""
    return await Message.create(
        sender_id=sender.id,
        receiver_id=receiver_id,
        product_id=product_id,
        content=content,
        msg_type=2,
    )


async def notify_report_handled(admin: User, report: Report, product: Product) -> None:
    """举报处理完成后，按结论向相关方发送系统通知。

    - 举报成立(违规)：通知举报者(感谢+结果) + 通知被举报者(告知违规+处罚+理由)
    - 举报不成立(驳回)：仅通知举报者(说明为何不成立)，不打扰被举报者
    """
    product_title = product.title
    reason_name = report.reason_type
    result = report.handler_result or ""

    if report.status == 2:  # 举报成立
        await send_system_notification(
            admin,
            report.reporter_id,
            f"【举报处理结果】您举报的商品「{product_title}」经核实存在违规（{reason_name}）。"
            f"处理结果：{result} 感谢您的监督，共同维护校园交易环境。",
            product_id=product.id,
        )
        await send_system_notification(
            admin,
            product.seller_id,
            f"【违规处理通知】您的商品「{product_title}」因被举报并经核实存在违规（{reason_name}），"
            f"已被平台下架。处理说明：{result} 如有疑问请联系平台客服申诉。",
            product_id=product.id,
        )
    elif report.status == 3:  # 举报不成立，仅通知举报者
        await send_system_notification(
            admin,
            report.reporter_id,
            f"【举报处理结果】您举报的商品「{product_title}」经核实暂未发现违规。"
            f"处理说明：{result} 感谢您的反馈，若有更多证据欢迎再次举报。",
            product_id=product.id,
        )
