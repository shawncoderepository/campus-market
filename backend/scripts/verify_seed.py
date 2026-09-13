"""验证种子数据结果（UTF-8 安全输出）。"""
import asyncio
import json
import sys

import aiomysql


async def main() -> None:
    conn = await aiomysql.connect(
        host="localhost", port=3306, user="root", password="123456",
        db="campus_market", charset="utf8mb4",
    )
    cur = await conn.cursor()
    out = {}

    await cur.execute(
        "SELECT id, username, nickname, avatar, phone, student_no, role, status FROM user"
    )
    out["users"] = [
        dict(zip(["id", "username", "nickname", "avatar", "phone", "student_no", "role", "status"], r))
        for r in await cur.fetchall()
    ]

    await cur.execute(
        "SELECT p.id, p.title, u.nickname AS seller, c.name AS category, "
        "p.original_price, p.sell_price, p.condition_level, p.images, p.view_count "
        "FROM product p JOIN user u ON p.seller_id = u.id "
        "JOIN category c ON p.category_id = c.id ORDER BY p.id"
    )
    out["products"] = [
        dict(zip(["id", "title", "seller", "category", "original_price", "sell_price",
                  "condition_level", "images", "view_count"], r))
        for r in await cur.fetchall()
    ]

    for t in ["bargain_record", "browse_history", "favorite", "message", "orders", "review", "report"]:
        await cur.execute(f"SELECT COUNT(*) FROM {t}")
        out.setdefault("counts", {})[t] = (await cur.fetchone())[0]

    conn.close()
    sys.stdout.buffer.write(json.dumps(out, ensure_ascii=False, indent=2, default=str).encode("utf-8"))
    print()


asyncio.run(main())
