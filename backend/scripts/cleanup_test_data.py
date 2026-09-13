"""清理 e2e 测试残留的账号、商品及关联数据，并删除 uploads 中未被引用的文件。"""
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

import pymysql

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")

conn = pymysql.connect(
    host="127.0.0.1", port=3306, user="root", password="123456",
    database="campus_market", charset="utf8mb4",
)
cur = conn.cursor()

# 1. 测试用户
cur.execute(
    "SELECT id, username FROM user WHERE username LIKE 'seller_hong%' "
    "OR username LIKE 'buyer_ming%' OR username LIKE 'cover_%'"
)
test_users = [r[0] for r in cur.fetchall()]
print("测试用户:", test_users)

if test_users:
    fmt = ",".join(["%s"] * len(test_users))
    cur.execute(f"SELECT id FROM product WHERE seller_id IN ({fmt})", test_users)
    test_products = [r[0] for r in cur.fetchall()]
    print("测试商品:", test_products)
    if test_products:
        pfmt = ",".join(["%s"] * len(test_products))
        cur.execute(f"DELETE r FROM review r JOIN orders o ON r.order_id=o.id WHERE o.product_id IN ({pfmt})", test_products)
        cur.execute(f"DELETE FROM orders WHERE product_id IN ({pfmt})", test_products)
        cur.execute(f"DELETE FROM bargain_record WHERE product_id IN ({pfmt})", test_products)
        cur.execute(f"DELETE FROM favorite WHERE product_id IN ({pfmt})", test_products)
        cur.execute(f"DELETE FROM report WHERE product_id IN ({pfmt})", test_products)
        cur.execute(f"DELETE FROM product WHERE id IN ({pfmt})", test_products)
    cur.execute(f"DELETE FROM orders WHERE buyer_id IN ({fmt})", test_users)
    cur.execute(f"DELETE FROM bargain_record WHERE buyer_id IN ({fmt})", test_users)
    cur.execute(f"DELETE FROM favorite WHERE user_id IN ({fmt})", test_users)
    cur.execute(f"DELETE FROM report WHERE reporter_id IN ({fmt})", test_users)
    cur.execute(f"DELETE FROM message WHERE sender_id IN ({fmt}) OR receiver_id IN ({fmt})", test_users + test_users)
    cur.execute(f"DELETE FROM user WHERE id IN ({fmt})", test_users)

# 2. 孤儿测试商品
cur.execute(
    "SELECT id FROM product WHERE title LIKE '%测试%' OR title LIKE '%闭环%' "
    "OR title LIKE '%覆盖%' OR title LIKE '%UI模板%'"
)
orphans = [r[0] for r in cur.fetchall()]
print("孤儿测试商品:", orphans)
if orphans:
    ofmt = ",".join(["%s"] * len(orphans))
    cur.execute(f"DELETE r FROM review r JOIN orders o ON r.order_id=o.id WHERE o.product_id IN ({ofmt})", orphans)
    cur.execute(f"DELETE FROM orders WHERE product_id IN ({ofmt})", orphans)
    cur.execute(f"DELETE FROM bargain_record WHERE product_id IN ({ofmt})", orphans)
    cur.execute(f"DELETE FROM favorite WHERE product_id IN ({ofmt})", orphans)
    cur.execute(f"DELETE FROM report WHERE product_id IN ({ofmt})", orphans)
    cur.execute(f"DELETE FROM product WHERE id IN ({ofmt})", orphans)

conn.commit()

cur.execute("SELECT COUNT(*) FROM product")
print("剩余商品数:", cur.fetchone()[0])
cur.execute("SELECT id, username FROM user")
print("剩余用户:", cur.fetchall())

# 3. 收集数据库中所有被引用的图片路径
referenced = set()
cur.execute("SELECT images FROM product")
for (imgs,) in cur.fetchall():
    if imgs:
        import json
        for u in (imgs if isinstance(imgs, list) else json.loads(imgs)):
            referenced.add(u.lstrip("/").replace("uploads/", ""))
cur.execute("SELECT avatar FROM user WHERE avatar != ''")
for (av,) in cur.fetchall():
    referenced.add(av.lstrip("/").replace("uploads/", ""))
print("被引用文件:", sorted(referenced))

conn.close()

# 4. 删除未被引用的文件
removed = []
for fname in os.listdir(UPLOAD_DIR):
    if fname not in referenced:
        os.remove(os.path.join(UPLOAD_DIR, fname))
        removed.append(fname)
print("已删除文件:", removed)
