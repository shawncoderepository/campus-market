from fastapi import APIRouter, FastAPI

from application.apis.ai import ai_router
from application.apis.bargain import bargain_router
from application.apis.category import category_router
from application.apis.favorite import favorite_router
from application.apis.goods import goods_router
from application.apis.message import message_router
from application.apis.order import order_router
from application.apis.report import report_router
from application.apis.review import review_router
from application.apis.system import system_router
from application.apis.user import user_router
from application.common.config import config


def register_routes(app: FastAPI) -> None:
    api_router = APIRouter()
    api_router.include_router(system_router)
    api_router.include_router(user_router)
    api_router.include_router(category_router)
    api_router.include_router(goods_router)
    api_router.include_router(favorite_router)
    api_router.include_router(bargain_router)
    api_router.include_router(order_router)
    api_router.include_router(review_router)
    api_router.include_router(message_router)
    api_router.include_router(report_router)
    api_router.include_router(ai_router)
    app.include_router(api_router, prefix=config.prefix)


__all__ = ["register_routes"]
