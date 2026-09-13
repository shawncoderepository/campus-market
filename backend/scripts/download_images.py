"""下载头像与商品图片到 uploads 目录。

图片来源：picsum.photos（占位图，稳定可下载）。
如果 picsum 不可用，脚本会退化为生成带颜色块的占位图。
"""
from __future__ import annotations

import io
import random
import urllib.request
from pathlib import Path

UPLOAD_ROOT = Path(__file__).resolve().parents[1] / "uploads"
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def fetch(url: str, dest: Path) -> bool:
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read()
        dest.write_bytes(data)
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"  下载失败 {url}: {exc}")
        return False


def fallback_image(dest: Path, text: str = "") -> None:
    """下载失败时生成一张纯色占位图（避免引用失效链接）。"""
    try:
        from PIL import Image, ImageDraw

        color = (
            random.randint(80, 200),
            random.randint(80, 200),
            random.randint(80, 200),
        )
        img = Image.new("RGB", (600, 600), color)
        d = ImageDraw.Draw(img)
        if text:
            d.text((40, 280), text, fill=(255, 255, 255))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        dest.write_bytes(buf.getvalue())
    except Exception as exc:  # noqa: BLE001
        print(f"  占位图生成失败: {exc}")


# (文件名, picsum seed)
AVATARS = [
    ("avatar_admin.jpg", "campus-avatar-admin"),
    ("avatar_student1.jpg", "campus-avatar-student1"),
    ("avatar_student2.jpg", "campus-avatar-student2"),
]

# 商品图：每个商品给 1~3 张
PRODUCT_IMAGES = [
    # student1
    ("p_macbook_1.jpg", "macbook-laptop"),
    ("p_macbook_2.jpg", "macbook-screen"),
    ("p_iphone_1.jpg", "iphone-phone"),
    ("p_iphone_2.jpg", "iphone-back"),
    ("p_textbook_1.jpg", "textbook-books"),
    ("p_textbook_2.jpg", "textbook-stack"),
    ("p_hoodie_1.jpg", "hoodie-clothes"),
    ("p_desklamp_1.jpg", "desk-lamp"),
    # student2
    ("p_basketball_1.jpg", "basketball-ball"),
    ("p_guitar_1.jpg", "guitar-instrument"),
    ("p_guitar_2.jpg", "guitar-closeup"),
    ("p_skincare_1.jpg", "skincare-cream"),
    ("p_keyboard_1.jpg", "keyboard-computer"),
    ("p_keyboard_2.jpg", "keyboard-rgb"),
    ("p_chair_1.jpg", "chair-dorm"),
]


def main() -> None:
    random.seed(20260911)
    ok, fail = 0, 0
    for fname, seed in AVATARS + PRODUCT_IMAGES:
        dest = UPLOAD_ROOT / fname
        if dest.exists() and dest.stat().st_size > 0:
            print(f"  已存在，跳过 {fname}")
            ok += 1
            continue
        url = f"https://picsum.photos/seed/{seed}/800/800"
        print(f"下载 {fname} ...")
        if fetch(url, dest) and dest.stat().st_size > 1000:
            ok += 1
        else:
            fallback_image(dest, text=fname)
            fail += 1
    print(f"完成：成功 {ok}，占位 {fail}，目录 {UPLOAD_ROOT}")


if __name__ == "__main__":
    main()
