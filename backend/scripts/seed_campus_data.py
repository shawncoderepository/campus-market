"""初始化演示数据：

1. 重置 admin 密码为 123456，并补全资料。
2. 为 student1 / student2 补全真实感资料与头像。
3. 删除其余普通用户及其商品、收藏、浏览、议价、订单、评价等关联数据。
4. 为 student1 / student2 发布不同类别的商品（带本地图片）。

直接运行：
    python scripts/seed_campus_data.py
"""
from __future__ import annotations

import asyncio
import random
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

import aiomysql
import bcrypt

DB = dict(host="localhost", port=3306, user="root", password="123456",
          db="campus_market", charset="utf8mb4")

KEEP_USERNAMES = {"admin", "student1", "student2"}
PASSWORD = "123456"

# ---- 用户资料（编的但看起来像真的） ----
PROFILES = {
    "admin": dict(nickname="校园小助手", avatar="/uploads/avatar_admin.jpg",
                  phone="13800138000", student_no="2023000001"),
    "student1": dict(nickname="林晚晴", avatar="/uploads/avatar_student1.jpg",
                     phone="13912345678", student_no="2023010521"),
    "student2": dict(nickname="陈屿", avatar="/uploads/avatar_student2.jpg",
                     phone="13787654321", student_no="2022041336"),
}

# ---- 商品数据（参考真实校园二手信息） ----
# (category_id, title, description, original_price, sell_price, condition_level, images)
PRODUCTS_STUDENT1 = [
    (1, "出自用 MacBook Air M1 8+256 银色",
     "21 年官网购入，平时只用来写论文和看视频，无拆无修，电池循环 180 次左右。"
     "机身成色很好，一直带壳使用，配件齐全（原装充电器+盒子都在）。"
     "毕业换新电脑所以出掉，支持当面验机，非诚勿扰。",
     "7999", "4200", 4, ["/uploads/p_macbook_1.jpg", "/uploads/p_macbook_2.jpg"]),
    (2, "iPhone 13 128G 星光色 全原无拆修",
     "去年考研时换的备用机，主力机一直用安卓所以这台基本闲置。"
     "外观 95 新，屏幕无划痕，电池健康 89%，爱思全绿，序列号可查。"
     "送原装数据线和两个手机壳，可走验机。",
     "5999", "3300", 4, ["/uploads/p_iphone_1.jpg", "/uploads/p_iphone_2.jpg"]),
    (3, "全新未拆 王道408考研复习全书 一套四本",
     "24 考研买的，后来决定保研了用不上，塑封都没拆。"
     "数据结构+计组+操作系统+计算机网络四本一套，不单出。"
     "校内可以送到图书馆或宿舍楼下。",
     "218", "120", 5, ["/uploads/p_textbook_1.jpg", "/uploads/p_textbook_2.jpg"]),
    (4, "优衣库连帽卫衣 浅灰色 L码",
     "去年双十一买的，只穿过两三次，洗过一次，无起球无污渍。"
     "尺码偏大，适合 170-178 穿。换季整理衣柜出掉，可小刀。",
     "199", "65", 4, ["/uploads/p_hoodie_1.jpg"]),
    (5, "美的宿舍护眼台灯 充插两用",
     "大三时买的，三档调光，充一次电能用一周。"
     "功能完好，灯头无发黄，毕业带不走便宜出。",
     "89", "30", 3, ["/uploads/p_desklamp_1.jpg"]),
]

PRODUCTS_STUDENT2 = [
    (6, "斯伯丁篮球 7号 室外水泥地耐磨",
     "上学期体育课买的，打了不到十次，表皮纹路还很清晰。"
     "气密性没问题，送打气筒和球针。适合外场日常使用。",
     "159", "70", 3, ["/uploads/p_basketball_1.jpg"]),
    (8, "卡马民谣吉他 41寸 原木色 送包",
     "大一社团招新时买的，学了半年就闲置了。"
     "琴颈直，弦距低，适合新手入门。面板有一条轻微划痕不影响音色，"
     "送加厚琴包、变调夹、备用琴弦和拨片。",
     "569", "260", 3, ["/uploads/p_guitar_1.jpg", "/uploads/p_guitar_2.jpg"]),
    (7, "科颜氏高保湿面霜 125ml 全新",
     "去年双十二旗舰店买的，囤多了用不完，出一瓶。"
     "保质期到 2027 年，防伪码可查，塑封完好。"
     "适合干皮秋冬使用，校内面交。",
     "315", "230", 5, ["/uploads/p_skincare_1.jpg"]),
    (1, "雷蛇黑寡妇机械键盘 87键 绿轴",
     "打游戏的键盘，按键灵敏无连击，RGB 灯效正常。"
     "键帽有轻微打油，已经清理过，送拔键器和备用键帽。"
     "换 60% 配列所以出掉。",
     "499", "220", 3, ["/uploads/p_keyboard_1.jpg", "/uploads/p_keyboard_2.jpg"]),
    (5, "宿舍懒人沙发椅 可折叠 灰色",
     "买来放宿舍追剧用的，靠背五档可调，能平躺。"
     "钢架结实，布套可拆洗，用了半年无塌陷。"
     "体积有点大，建议自提，可以帮忙搬到楼下。",
     "129", "45", 3, ["/uploads/p_chair_1.jpg"]),
]


def hash_password(raw: str) -> str:
    return bcrypt.hashpw(raw.encode("utf-8")[:72], bcrypt.gensalt()).decode("utf-8")


async def exec_sql(cur, sql: str, args=()) -> int:
    await cur.execute(sql, args)
    return cur.rowcount


async def main() -> None:
    random.seed(20260911)
    conn = await aiomysql.connect(**DB, autocommit=False)
    cur = await conn.cursor()

    # 1. 找出要删除的普通用户（保留 admin / student1 / student2）
    await cur.execute("SELECT id, username FROM user")
    rows = await cur.fetchall()
    keep_ids, delete_ids = [], []
    for uid, uname in rows:
        (keep_ids if uname in KEEP_USERNAMES else delete_ids).append(uid)
    print(f"保留用户 id={keep_ids}，删除用户 id={delete_ids}")

    if delete_ids:
        ph = ",".join(["%s"] * len(delete_ids))
        # 先拿到要删除用户的商品 id
        await cur.execute(f"SELECT id FROM product WHERE seller_id IN ({ph})", delete_ids)
        del_pids = [r[0] for r in await cur.fetchall()]
        print(f"将删除商品 id={del_pids}")

        # 删除商品相关的所有引用（不限于这些用户的商品，防止别的用户下过单）
        if del_pids:
            pph = ",".join(["%s"] * len(del_pids))
            # review 通过 order 关联商品，先删 review 再删 orders
            await exec_sql(
                cur,
                f"DELETE r FROM review r JOIN orders o ON r.order_id = o.id "
                f"WHERE o.product_id IN ({pph})",
                del_pids,
            )
            for tbl, col in [
                ("bargain_record", "product_id"),
                ("favorite", "product_id"),
                ("browse_history", "product_id"),
                ("orders", "product_id"),
                ("report", "product_id"),
            ]:
                n = await exec_sql(cur, f"DELETE FROM {tbl} WHERE {col} IN ({pph})", del_pids)
                if n:
                    print(f"  {tbl}: 删除 {n} 行（按商品）")

        # 再删除与这些用户直接相关的剩余数据
        for tbl, cols in [
            ("bargain_record", ("buyer_id", "seller_id")),
            ("favorite", ("user_id",)),
            ("browse_history", ("user_id",)),
            ("orders", ("buyer_id", "seller_id")),
            ("review", ("reviewer_id", "target_id")),
            ("message", ("sender_id", "receiver_id")),
            ("report", ("reporter_id",)),
            ("product", ("seller_id",)),
        ]:
            for col in cols:
                n = await exec_sql(cur, f"DELETE FROM {tbl} WHERE {col} IN ({ph})", delete_ids)
                if n:
                    print(f"  {tbl}.{col}: 删除 {n} 行")

        n = await exec_sql(cur, f"DELETE FROM user WHERE id IN ({ph})", delete_ids)
        print(f"  user: 删除 {n} 行")

    # 2. 更新保留用户的资料 + 重置密码
    pwd_hash = hash_password(PASSWORD)
    for uname, prof in PROFILES.items():
        n = await exec_sql(
            cur,
            "UPDATE user SET nickname=%s, avatar=%s, phone=%s, student_no=%s, password_hash=%s "
            "WHERE username=%s",
            (prof["nickname"], prof["avatar"], prof["phone"], prof["student_no"], pwd_hash, uname),
        )
        print(f"更新 {uname}: {n} 行")

    # 3. 为 student1 / student2 发布商品（先清掉他们已有的，保证可重复执行）
    await cur.execute("SELECT id, username FROM user WHERE username IN ('student1','student2')")
    uid_map = {uname: uid for uid, uname in await cur.fetchall()}

    for uname, products in (("student1", PRODUCTS_STUDENT1), ("student2", PRODUCTS_STUDENT2)):
        uid = uid_map[uname]
        await cur.execute("SELECT id FROM product WHERE seller_id=%s", (uid,))
        old_pids = [r[0] for r in await cur.fetchall()]
        if old_pids:
            pph = ",".join(["%s"] * len(old_pids))
            await exec_sql(
                cur,
                f"DELETE r FROM review r JOIN orders o ON r.order_id = o.id "
                f"WHERE o.product_id IN ({pph})",
                old_pids,
            )
            for tbl, col in [
                ("bargain_record", "product_id"),
                ("favorite", "product_id"),
                ("browse_history", "product_id"),
                ("orders", "product_id"),
                ("report", "product_id"),
            ]:
                await exec_sql(cur, f"DELETE FROM {tbl} WHERE {col} IN ({pph})", old_pids)
            await exec_sql(cur, f"DELETE FROM product WHERE id IN ({pph})", old_pids)
            print(f"清空 {uname} 旧商品 {len(old_pids)} 个")

        for cat_id, title, desc, orig, sell, cond, images in products:
            view = random.randint(15, 320)
            created = datetime.now() - timedelta(days=random.randint(1, 45),
                                                 hours=random.randint(0, 23))
            await exec_sql(
                cur,
                "INSERT INTO product (seller_id, category_id, title, description, original_price,"
                " sell_price, condition_level, images, status, view_count, created_at, updated_at)"
                " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,1,%s,%s,%s)",
                (uid, cat_id, title, desc, Decimal(orig), Decimal(sell), cond,
                 str(images).replace("'", '"'), view, created, created),
            )
        print(f"已为 {uname} 发布 {len(products)} 个商品")

    await conn.commit()
    conn.close()
    print("完成")


asyncio.run(main())
