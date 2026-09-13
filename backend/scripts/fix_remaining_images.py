"""删除重复商品，给剩余无图商品下载并填充图片。"""
import json
import sys
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

import pymysql

UPLOAD_ROOT = Path(__file__).resolve().parents[1] / "uploads"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

# 需要下载的新图
NEW_IMAGES = [
    ("p_headphone_1.jpg", "https://images.pexels.com/photos/3394650/pexels-photo-3394650.jpeg?auto=compress&cs=tinysrgb&w=800", "头戴式降噪耳机"),
    ("p_headphone_2.jpg", "https://images.pexels.com/photos/1649771/pexels-photo-1649771.jpeg?auto=compress&cs=tinysrgb&w=800", "耳机特写"),
    ("p_mathbook_1.jpg", "https://images.pexels.com/photos/6238050/pexels-photo-6238050.jpeg?auto=compress&cs=tinysrgb&w=800", "数学教材"),
    ("p_mathbook_2.jpg", "https://images.pexels.com/photos/5905445/pexels-photo-5905445.jpeg?auto=compress&cs=tinysrgb&w=800", "高等数学"),
]


def fetch(url: str, dest: Path) -> bool:
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        if len(data) > 3000:
            dest.write_bytes(data)
            return True
    except Exception as exc:
        print(f"  下载失败: {exc}")
    return False


def main() -> None:
    # 1. 下载图片
    for fname, url, desc in NEW_IMAGES:
        dest = UPLOAD_ROOT / fname
        if dest.exists() and dest.stat().st_size > 3000:
            print(f"[跳过] {desc} 已存在")
            continue
        print(f"[下载] {desc} -> {fname}")
        ok = fetch(url, dest)
        print(f"  {'成功' if ok else '失败'}")

    conn = pymysql.connect(
        host="127.0.0.1", port=3306, user="root", password="123456",
        database="campus_market", charset="utf8mb4",
    )
    cur = conn.cursor()

    # 2. 删除重复商品（保留每组 id 较小者）
    dup_ids = [28, 29]
    fmt = ",".join(["%s"] * len(dup_ids))
    cur.execute(f"DELETE r FROM review r JOIN orders o ON r.order_id=o.id WHERE o.product_id IN ({fmt})", dup_ids)
    cur.execute(f"DELETE FROM orders WHERE product_id IN ({fmt})", dup_ids)
    cur.execute(f"DELETE FROM bargain_record WHERE product_id IN ({fmt})", dup_ids)
    cur.execute(f"DELETE FROM favorite WHERE product_id IN ({fmt})", dup_ids)
    cur.execute(f"DELETE FROM report WHERE product_id IN ({fmt})", dup_ids)
    cur.execute(f"DELETE FROM product WHERE id IN ({fmt})", dup_ids)
    print(f"已删除重复商品: {dup_ids}")

    # 3. 给 26/27 填充图片
    mapping = {
        26: ["/uploads/p_headphone_1.jpg", "/uploads/p_headphone_2.jpg"],
        27: ["/uploads/p_mathbook_1.jpg", "/uploads/p_mathbook_2.jpg"],
    }
    for pid, imgs in mapping.items():
        cur.execute("UPDATE product SET images=%s WHERE id=%s", (json.dumps(imgs, ensure_ascii=False), pid))
        print(f"商品 {pid} 已填充图片: {imgs}")

    conn.commit()

    cur.execute("SELECT id, title, images FROM product ORDER BY id")
    for row in cur.fetchall():
        print(row)
    conn.close()


if __name__ == "__main__":
    main()
