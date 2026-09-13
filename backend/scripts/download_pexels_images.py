"""从 Pexels 下载真实商品图片（使用固定图片链接）。

Pexels 图片链接格式：https://images.pexels.com/photos/{id}/pexels-photo-{id}.jpeg
以下链接均为免费商用图片，与商品类型匹配。
"""
from __future__ import annotations

import asyncio
import io
import sys
import urllib.request
from pathlib import Path

import aiomysql

UPLOAD_ROOT = Path(__file__).resolve().parents[1] / "uploads"
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

# Pexels 真实图片链接（已验证可访问）
# 格式: (文件名, Pexels 图片 URL, 描述)
PEXELS_IMAGES = [
    # 数码产品
    ("p_macbook_1.jpg", "https://images.pexels.com/photos/303383/pexels-photo-303383.jpeg?auto=compress&cs=tinysrgb&w=800", "MacBook 笔记本"),
    ("p_macbook_2.jpg", "https://images.pexels.com/photos/1181244/pexels-photo-1181244.jpeg?auto=compress&cs=tinysrgb&w=800", "MacBook 屏幕"),
    ("p_iphone_1.jpg", "https://images.pexels.com/photos/699122/pexels-photo-699122.jpeg?auto=compress&cs=tinysrgb&w=800", "iPhone 手机"),
    ("p_iphone_2.jpg", "https://images.pexels.com/photos/5082579/pexels-photo-5082579.jpeg?auto=compress&cs=tinysrgb&w=800", "iPhone 背面"),
    # 书籍教材
    ("p_textbook_1.jpg", "https://images.pexels.com/photos/159866/books-book-pages-read-literature-159866.jpeg?auto=compress&cs=tinysrgb&w=800", "书籍堆叠"),
    ("p_textbook_2.jpg", "https://images.pexels.com/photos/590493/pexels-photo-590493.jpeg?auto=compress&cs=tinysrgb&w=800", "计算机教材"),
    # 服饰
    ("p_hoodie_1.jpg", "https://images.pexels.com/photos/6311392/pexels-photo-6311392.jpeg?auto=compress&cs=tinysrgb&w=800", "灰色连帽卫衣"),
    # 生活家居
    ("p_desklamp_1.jpg", "https://images.pexels.com/photos/1112598/pexels-photo-1112598.jpeg?auto=compress&cs=tinysrgb&w=800", "现代台灯"),
    ("p_chair_1.jpg", "https://images.pexels.com/photos/4352247/pexels-photo-4352247.jpeg?auto=compress&cs=tinysrgb&w=800", "懒人沙发"),
    # 运动户外
    ("p_basketball_1.jpg", "https://images.pexels.com/photos/358042/pexels-photo-358042.jpeg?auto=compress&cs=tinysrgb&w=800", "篮球"),
    # 乐器
    ("p_guitar_1.jpg", "https://images.pexels.com/photos/1407322/pexels-photo-1407322.jpeg?auto=compress&cs=tinysrgb&w=800", "木吉他"),
    ("p_guitar_2.jpg", "https://images.pexels.com/photos/164821/pexels-photo-164821.jpeg?auto=compress&cs=tinysrgb&w=800", "吉他特写"),
    # 美妆
    ("p_skincare_1.jpg", "https://images.pexels.com/photos/4465124/pexels-photo-4465124.jpeg?auto=compress&cs=tinysrgb&w=800", "面霜护肤品"),
    # 键盘
    ("p_keyboard_1.jpg", "https://images.pexels.com/photos/1714208/pexels-photo-1714208.jpeg?auto=compress&cs=tinysrgb&w=800", "机械键盘"),
    ("p_keyboard_2.jpg", "https://images.pexels.com/photos/841228/pexels-photo-841228.jpeg?auto=compress&cs=tinysrgb&w=800", "键盘特写"),
    # 头像
    ("avatar_admin.jpg", "https://images.pexels.com/photos/2379004/pexels-photo-2379004.jpeg?auto=compress&cs=tinysrgb&w=400", "管理员头像"),
    ("avatar_student1.jpg", "https://images.pexels.com/photos/733872/pexels-photo-733872.jpeg?auto=compress&cs=tinysrgb&w=400", "学生头像-女"),
    ("avatar_student2.jpg", "https://images.pexels.com/photos/1222271/pexels-photo-1222271.jpeg?auto=compress&cs=tinysrgb&w=400", "学生头像-男"),
]


def fetch_image(url: str, dest: Path) -> bool:
    """下载图片到本地。"""
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        if len(data) > 3000:  # 确保是有效图片
            dest.write_bytes(data)
            return True
    except Exception as exc:
        print(f"    下载失败: {exc}")
    return False


async def update_database() -> None:
    """更新数据库中的图片路径。"""
    conn = await aiomysql.connect(
        host="localhost", port=3306, user="root", password="123456",
        db="campus_market", charset="utf8mb4",
    )
    cur = await conn.cursor()

    # 商品图片映射
    product_images = {
        12: ["/uploads/p_macbook_1.jpg", "/uploads/p_macbook_2.jpg"],
        13: ["/uploads/p_iphone_1.jpg", "/uploads/p_iphone_2.jpg"],
        14: ["/uploads/p_textbook_1.jpg", "/uploads/p_textbook_2.jpg"],
        15: ["/uploads/p_hoodie_1.jpg"],
        16: ["/uploads/p_desklamp_1.jpg"],
        17: ["/uploads/p_basketball_1.jpg"],
        18: ["/uploads/p_guitar_1.jpg", "/uploads/p_guitar_2.jpg"],
        19: ["/uploads/p_skincare_1.jpg"],
        20: ["/uploads/p_keyboard_1.jpg", "/uploads/p_keyboard_2.jpg"],
        21: ["/uploads/p_chair_1.jpg"],
    }

    for pid, images in product_images.items():
        await cur.execute(
            "UPDATE product SET images=%s WHERE id=%s",
            (str(images).replace("'", '"'), pid),
        )

    # 用户头像
    avatars = {
        "admin": "/uploads/avatar_admin.jpg",
        "student1": "/uploads/avatar_student1.jpg",
        "student2": "/uploads/avatar_student2.jpg",
    }
    for username, avatar in avatars.items():
        await cur.execute(
            "UPDATE user SET avatar=%s WHERE username=%s",
            (avatar, username),
        )

    await conn.commit()
    conn.close()


async def main() -> None:
    print("=" * 50)
    print("从 Pexels 下载真实商品图片")
    print("=" * 50)

    success, fail = 0, 0
    for fname, url, desc in PEXELS_IMAGES:
        dest = UPLOAD_ROOT / fname
        print(f"[{success + fail + 1}/{len(PEXELS_IMAGES)}] {desc} -> {fname}")
        if fetch_image(url, dest):
            size = dest.stat().st_size / 1024
            print(f"  成功 ({size:.1f} KB)")
            success += 1
        else:
            fail += 1

    print(f"\n下载完成: 成功 {success} 张, 失败 {fail} 张")

    if success > 0:
        print("\n更新数据库图片路径...")
        await update_database()
        print("数据库已更新")

    print(f"\n图片目录: {UPLOAD_ROOT}")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
