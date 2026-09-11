"""种子数据脚本：初始化分类、管理员、测试用户与示例商品。

运行方式（在 backend 目录）：
    uv run python scripts/seed.py
"""
import asyncio

from application.common.helper.security_helper import hash_password
from application.common.models import Category, Product, User
from application.core.database import connect_database, disconnect_database

_CATEGORIES = [
    ("数码电子", "💻"),
    ("手机平板", "📱"),
    ("图书教材", "📚"),
    ("服饰鞋包", "👟"),
    ("生活家居", "🛏️"),
    ("运动户外", "⚽"),
    ("美妆护肤", "💄"),
    ("乐器", "🎸"),
    ("其他", "📦"),
]

_PRODUCTS = [
    ("九成新 iPad 9 64G", "考研结束出，无磕碰，功能完好，带保护壳。", 2499, 1500, 4, "手机平板"),
    ("计算机网络第七版", "谢希仁版教材，少量笔记，适合期末复习。", 49, 15, 3, "图书教材"),
    ("机械键盘 87键", "青轴，敲击手感好，换静电容故出。", 399, 180, 3, "数码电子"),
    ("全新未拆封 蓝牙耳机", "双十一囤货多的一副，塑封未拆。", 199, 120, 5, "数码电子"),
    ("耐克跑步鞋 42码", "穿过几次，成色不错，运动款。", 599, 220, 3, "服饰鞋包"),
    ("宿舍小电锅", "煮面煮火锅都行，毕业出。", 89, 30, 3, "生活家居"),
    ("瑜伽垫 加厚", "几乎全新，买来没怎么用。", 69, 25, 4, "运动户外"),
    ("尤克里里 23寸", "入门款，附调音器和教程。", 299, 130, 3, "乐器"),
]


async def seed() -> None:
    await connect_database()

    # 分类
    category_map: dict[str, Category] = {}
    for index, (name, icon) in enumerate(_CATEGORIES):
        category, _ = await Category.get_or_create(
            name=name, defaults={"icon": icon, "sort": index}
        )
        category_map[name] = category
    print(f"categories: {await Category.all().count()}")

    # 管理员
    admin, created = await User.get_or_create(
        username="admin",
        defaults={
            "password_hash": hash_password("admin123"),
            "nickname": "管理员",
            "role": 2,
        },
    )
    print(f"admin: {'created' if created else 'exists'}")

    # 测试卖家
    seller, _ = await User.get_or_create(
        username="seller",
        defaults={
            "password_hash": hash_password("123456"),
            "nickname": "学长的小店",
            "student_no": "2021001",
        },
    )
    # 测试买家
    await User.get_or_create(
        username="buyer",
        defaults={
            "password_hash": hash_password("123456"),
            "nickname": "爱捡漏的同学",
            "student_no": "2023002",
        },
    )

    # 示例商品
    created_count = 0
    for title, desc, original, sell, condition, cat_name in _PRODUCTS:
        exists = await Product.get_or_none(title=title, seller_id=seller.id)
        if exists:
            continue
        await Product.create(
            seller=seller,
            category=category_map[cat_name],
            title=title,
            description=desc,
            original_price=original,
            sell_price=sell,
            condition_level=condition,
            images=[],
        )
        created_count += 1
    print(f"products created: {created_count}, total: {await Product.all().count()}")

    await disconnect_database()
    print("seed done.")


if __name__ == "__main__":
    asyncio.run(seed())
