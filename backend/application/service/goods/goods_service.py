"""商品域业务逻辑。"""
from tortoise.expressions import Q

from application.common.constants import HttpErrorCodeEnum
from application.common.exception.exception import HttpBusinessException
from application.common.models import BrowseHistory, Category, Favorite, Product, User


def to_item_res(p: Product) -> dict:
    return {
        "id": p.id,
        "title": p.title,
        "description": p.description,
        "original_price": float(p.original_price),
        "sell_price": float(p.sell_price),
        "condition_level": p.condition_level,
        "images": p.images or [],
        "status": p.status,
        "view_count": p.view_count,
        "category_id": p.category_id,
        "category_name": getattr(p.category, "name", "") if hasattr(p, "category") else "",
        "seller_id": p.seller_id,
        "seller_nickname": getattr(p.seller, "nickname", "") if hasattr(p, "seller") else "",
        "seller_avatar": getattr(p.seller, "avatar", "") if hasattr(p, "seller") else "",
        "created_at": p.created_at,
    }


async def publish(seller: User, data: dict) -> Product:
    category = await Category.get_or_none(id=data["category_id"])
    if category is None:
        raise HttpBusinessException(HttpErrorCodeEnum.PARAM_INVALID, "分类不存在")
    product = await Product.create(
        seller=seller,
        category=category,
        title=data["title"],
        description=data.get("description", ""),
        original_price=data.get("original_price", 0),
        sell_price=data["sell_price"],
        condition_level=data.get("condition_level", 3),
        images=data.get("images", []),
    )
    return product


async def list_goods(query: dict, viewer: User | None = None) -> tuple[list[Product], int]:
    cond = Q(status=1)  # 只展示在售
    if viewer is not None:
        cond &= ~Q(seller_id=viewer.id)  # 不展示自己发布的商品
    if query.get("keyword"):
        kw = query["keyword"]
        cond &= Q(title__icontains=kw) | Q(description__icontains=kw)
    if query.get("category_id"):
        cond &= Q(category_id=query["category_id"])
    if query.get("min_price") is not None:
        cond &= Q(sell_price__gte=query["min_price"])
    if query.get("max_price") is not None:
        cond &= Q(sell_price__lte=query["max_price"])
    if query.get("condition_level"):
        cond &= Q(condition_level=query["condition_level"])

    order_field = {
        "latest": "-created_at",
        "price_asc": "sell_price",
        "price_desc": "-sell_price",
        "hot": "-view_count",
    }.get(query.get("sort", "latest"), "-created_at")

    qs = Product.filter(cond).prefetch_related("category", "seller")
    total = await qs.count()
    page, page_size = query["page"], query["page_size"]
    items = await qs.order_by(order_field).offset((page - 1) * page_size).limit(page_size)
    return items, total


async def get_detail(product_id: int, viewer: User | None) -> Product:
    product = await Product.get_or_none(id=product_id).prefetch_related("category", "seller")
    if product is None:
        raise HttpBusinessException(HttpErrorCodeEnum.NOT_FOUND, "商品不存在")
    # 浏览量 +1
    product.view_count += 1
    await product.save()
    # 记录浏览历史（登录用户）
    if viewer is not None:
        await BrowseHistory.create(user=viewer, product=product)
    return product


async def is_favorited(user: User | None, product_id: int) -> bool:
    if user is None:
        return False
    return await Favorite.get_or_none(user=user, product_id=product_id) is not None


async def update_goods(product_id: int, seller: User, data: dict) -> Product:
    product = await Product.get_or_none(id=product_id)
    if product is None:
        raise HttpBusinessException(HttpErrorCodeEnum.NOT_FOUND, "商品不存在")
    if product.seller_id != seller.id and seller.role != 2:
        raise HttpBusinessException(HttpErrorCodeEnum.FORBIDDEN, "无权操作该商品")
    for key in ("category_id", "title", "description", "original_price", "sell_price",
                "condition_level", "images", "status"):
        value = data.get(key)
        if value is not None:
            setattr(product, key, value)
    await product.save()
    return product


async def my_goods(seller: User, page: int, page_size: int) -> tuple[list[Product], int]:
    qs = Product.filter(seller_id=seller.id).prefetch_related("category", "seller")
    total = await qs.count()
    items = await qs.order_by("-created_at").offset((page - 1) * page_size).limit(page_size)
    return items, total


async def related_goods(product: Product, limit: int = 6) -> list[Product]:
    return (
        await Product.filter(Q(category_id=product.category_id) & Q(status=1) & ~Q(id=product.id))
        .prefetch_related("category", "seller")
        .order_by("-view_count")
        .limit(limit)
    )
