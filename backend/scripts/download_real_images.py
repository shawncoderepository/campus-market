"""从 Unsplash 下载真实商品图片并替换现有占位图。

使用方法：
    python scripts/download_real_images.py

注意：Unsplash 免费版无需 API key，通过 source.unsplash.com 直接下载。
"""
from __future__ import annotations

import asyncio
import io
import random
import sys
import urllib.request
from pathlib import Path

import aiomysql

UPLOAD_ROOT = Path(__file__).resolve().parents[1] / "uploads"
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
}

# Unsplash 图片映射：商品关键词 -> (文件名, 备用关键词)
# 使用 source.unsplash.com 直接获取相关图片
IMAGE_MAP = {
    # 现有商品图片替换
    "p_macbook_1.jpg": ("macbook-laptop-silver", "laptop-computer-apple"),
    "p_macbook_2.jpg": ("macbook-screen-closeup", "laptop-keyboard-apple"),
    "p_iphone_1.jpg": ("iphone-13-starlight", "iphone-smartphone-white"),
    "p_iphone_2.jpg": ("iphone-back-camera", "iphone-smartphone-apple"),
    "p_textbook_1.jpg": ("textbook-books-stack", "books-study-education"),
    "p_textbook_2.jpg": ("computer-science-books", "programming-books-stack"),
    "p_hoodie_1.jpg": ("hoodie-gray-casual", "sweatshirt-clothes-gray"),
    "p_desklamp_1.jpg": ("desk-lamp-modern-led", "table-lamp-study-light"),
    "p_basketball_1.jpg": ("basketball-ball-orange", "spalding-basketball-sport"),
    "p_guitar_1.jpg": ("acoustic-guitar-wooden", "guitar-instrument-music"),
    "p_guitar_2.jpg": ("guitar-closeup-strings", "acoustic-guitar-detail"),
    "p_skincare_1.jpg": ("skincare-cream-jar", "cosmetic-product-lotion"),
    "p_keyboard_1.jpg": ("mechanical-keyboard-rgb", "keyboard-gaming-computer"),
    "p_keyboard_2.jpg": ("keyboard-closeup-keys", "mechanical-keyboard-detail"),
    "p_chair_1.jpg": ("bean-bag-chair-gray", "lounge-chair-comfortable"),
}

# 用户头像（用更真实的头像）
AVATAR_MAP = {
    "avatar_admin.jpg": ("avatar-professional-business", "person-portrait-face"),
    "avatar_student1.jpg": ("student-girl-asian", "woman-portrait-young"),
    "avatar_student2.jpg": ("student-boy-asian", "man-portrait-young"),
}


def fetch_unsplash(keyword: str, dest: Path, size: str = "800x800") -> bool:
    """从 Unsplash 下载指定关键词的图片。"""
    # source.unsplash.com 支持关键词直接获取
    urls = [
        f"https://source.unsplash.com/featured/?{keyword}",
        f"https://source.unsplash.com/{size}/?{keyword}",
        f"https://source.unsplash.com/featured/{size}/?{keyword}",
    ]
    for url in urls:
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as resp:
                # 检查重定向后的最终 URL
                final_url = resp.geturl()
                if "images.unsplash.com" in final_url or "source.unsplash.com" in final_url:
                    data = resp.read()
                    if len(data) > 5000:  # 确保是有效图片
                        dest.write_bytes(data)
                        print(f"  [OK] {dest.name} <- {keyword}")
                        return True
        except Exception as exc:
            continue
    return False


def fallback_placeholder(dest: Path, text: str, color: tuple[int, int, int]) -> None:
    """下载失败时生成带文字的占位图。"""
    try:
        from PIL import Image, ImageDraw, ImageFont

        img = Image.new("RGB", (800, 800), color)
        d = ImageDraw.Draw(img)
        # 尝试使用系统字体
        try:
            font = ImageFont.truetype("arial.ttf", 48)
        except OSError:
            try:
                font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 48)
            except OSError:
                font = ImageFont.load_default()

        # 计算文字位置（居中）
        bbox = d.textbbox((0, 0), text, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        d.text(((800 - w) // 2, (800 - h) // 2), text, fill=(255, 255, 255), font=font)

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=90)
        dest.write_bytes(buf.getvalue())
        print(f"  [占位] {dest.name}")
    except Exception as exc:
        print(f"  [失败] {dest.name}: {exc}")


async def update_product_images() -> None:
    """更新数据库中商品的图片路径。"""
    conn = await aiomysql.connect(
        host="localhost", port=3306, user="root", password="123456",
        db="campus_market", charset="utf8mb4",
    )
    cur = await conn.cursor()

    # 商品图片映射（数据库中的商品 ID -> 图片列表）
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
        print(f"  更新商品 {pid} 图片")

    await conn.commit()
    conn.close()


async def update_user_avatars() -> None:
    """更新用户头像。"""
    conn = await aiomysql.connect(
        host="localhost", port=3306, user="root", password="123456",
        db="campus_market", charset="utf8mb4",
    )
    cur = await conn.cursor()

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
        print(f"  更新用户 {username} 头像")

    await conn.commit()
    conn.close()


async def main() -> None:
    random.seed(20260912)

    print("=" * 50)
    print("开始下载真实商品图片...")
    print("=" * 50)

    # 下载商品图片
    print("\n[1/3] 下载商品图片...")
    success, fail = 0, 0
    colors = [
        (99, 102, 241), (16, 185, 129), (245, 158, 11),
        (236, 72, 153), (6, 182, 212), (139, 92, 246),
    ]
    for i, (fname, (kw1, kw2)) in enumerate(IMAGE_MAP.items()):
        dest = UPLOAD_ROOT / fname
        # 优先用第一个关键词，失败用第二个
        if fetch_unsplash(kw1, dest) or fetch_unsplash(kw2, dest):
            success += 1
        else:
            fallback_placeholder(dest, fname.replace("p_", "").replace("_", " ").replace(".jpg", ""), colors[i % len(colors)])
            fail += 1

    # 下载头像
    print("\n[2/3] 下载用户头像...")
    for fname, (kw1, kw2) in AVATAR_MAP.items():
        dest = UPLOAD_ROOT / fname
        if fetch_unsplash(kw1, dest) or fetch_unsplash(kw2, dest):
            success += 1
        else:
            fallback_placeholder(dest, fname.replace("avatar_", "").replace(".jpg", ""), (100, 116, 139))
            fail += 1

    # 更新数据库
    print("\n[3/3] 更新数据库图片路径...")
    await update_product_images()
    await update_user_avatars()

    print("\n" + "=" * 50)
    print(f"完成！成功 {success} 张，占位 {fail} 张")
    print(f"图片目录: {UPLOAD_ROOT}")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
