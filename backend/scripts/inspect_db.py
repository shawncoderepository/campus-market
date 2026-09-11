"""查看数据库中的用户、分类、商品（UTF-8 安全输出）。"""
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
    await cur.execute("SELECT id, username, nickname, role, status FROM user")
    out["users"] = [
        {"id": r[0], "username": r[1], "nickname": r[2], "role": r[3], "status": r[4]}
        for r in await cur.fetchall()
    ]
    await cur.execute("SELECT id, name FROM category ORDER BY sort")
    out["categories"] = [{"id": r[0], "name": r[1]} for r in await cur.fetchall()]
    await cur.execute("SELECT id, title, seller_id, category_id, status FROM product")
    out["products"] = [
        {"id": r[0], "title": r[1], "seller_id": r[2], "category_id": r[3], "status": r[4]}
        for r in await cur.fetchall()
    ]
    conn.close()
    sys.stdout.buffer.write(json.dumps(out, ensure_ascii=False, indent=2).encode("utf-8"))
    print()


asyncio.run(main())
