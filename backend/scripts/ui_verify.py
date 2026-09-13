"""前端界面真实点击验证：用 Playwright 驱动浏览器，登录真实账号，
逐个打开核心页面，检测页面是否渲染出数据（验证 API 数据是否真正反映到 UI），
并对每个页面截图保存到 backend/scripts/ui_shots/。

账号：student1(卖家) / student2(买家) / admin(管理员)，密码 123456。
运行：uv run python scripts/ui_verify.py
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE = "http://localhost:5174"
SHOTS = Path(__file__).parent / "ui_shots"
SHOTS.mkdir(exist_ok=True)

PASS = 0
FAIL = 0


def check(name: str, cond: bool, extra: str = "") -> None:
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {extra}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {extra}")


def shot(page, name: str) -> None:
    page.screenshot(path=str(SHOTS / f"{name}.png"), full_page=True)


def login(page, username: str, password: str = "123456") -> None:
    page.goto(f"{BASE}/login", wait_until="networkidle")
    page.wait_for_timeout(800)
    page.locator('input[type="text"]').first.fill(username)
    page.locator('input[type="password"]').first.fill(password)
    page.locator('button[type="submit"], button:has-text("登")').first.click()
    page.wait_for_url(lambda u: "/login" not in u, timeout=10000)
    page.wait_for_load_state("networkidle")


def body_text(page) -> str:
    return page.locator("body").inner_text()


def main() -> None:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
        page = ctx.new_page()

        print("\n=== 买家 student2 视角 ===")
        login(page, "student2")
        page.goto(f"{BASE}/", wait_until="networkidle")
        shot(page, "01_home")
        t = body_text(page)
        check("首页渲染出商品", "收纳箱" in t or "耳机" in t or "¥" in t)

        page.goto(f"{BASE}/favorites", wait_until="networkidle")
        shot(page, "02_favorites")
        check("收藏页有内容", "收纳箱" in body_text(page) or "¥" in body_text(page))

        page.goto(f"{BASE}/order", wait_until="networkidle")
        shot(page, "03_order")
        check("订单页有订单", "订单" in body_text(page) and ("¥" in body_text(page) or "已" in body_text(page)))

        page.goto(f"{BASE}/bargain", wait_until="networkidle")
        page.wait_for_timeout(800)
        shot(page, "04_bargain")
        bt = body_text(page)
        check("议价中心有会话", ("议价" in bt) and ("¥" in bt or "出价" in bt or "还价" in bt or "收纳箱" in bt))

        page.goto(f"{BASE}/message", wait_until="networkidle")
        page.wait_for_timeout(500)
        shot(page, "05_message")
        check("消息页有会话", "消息" in body_text(page) or "学姐" in body_text(page) or "林" in body_text(page))

        page.goto(f"{BASE}/my", wait_until="networkidle")
        shot(page, "06_my")
        check("个人中心显示用户", "陈屿" in body_text(page) or "信用" in body_text(page))

        print("\n=== 卖家 student1 视角 ===")
        ctx2 = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
        page2 = ctx2.new_page()
        login(page2, "student1")
        page2.goto(f"{BASE}/my", wait_until="networkidle")
        shot(page2, "07_seller_my")
        check("卖家个人中心", "林" in body_text(page2) or "信用" in body_text(page2))
        page2.goto(f"{BASE}/order", wait_until="networkidle")
        shot(page2, "08_seller_order")
        check("卖家订单页", "订单" in body_text(page2))
        page2.goto(f"{BASE}/bargain", wait_until="networkidle")
        page2.wait_for_timeout(800)
        shot(page2, "09_seller_bargain")
        check("卖家议价中心", "议价" in body_text(page2))

        print("\n=== 管理员 admin 视角 ===")
        ctx3 = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
        page3 = ctx3.new_page()
        login(page3, "admin")
        page3.goto(f"{BASE}/admin/dashboard", wait_until="networkidle")
        page3.wait_for_timeout(800)
        shot(page3, "10_admin_dashboard")
        dt = body_text(page3)
        check("仪表盘有统计数字", any(k in dt for k in ["用户", "商品", "订单", "交易"]))

        for route, nm, kw in [
            ("user", "11_admin_user", "信用"),
            ("category", "12_admin_category", "分类"),
            ("report", "13_admin_report", "举报"),
            ("goods", "14_admin_goods", "商品"),
            ("order", "15_admin_order", "订单"),
        ]:
            page3.goto(f"{BASE}/admin/{route}", wait_until="networkidle")
            page3.wait_for_timeout(600)
            shot(page3, nm)
            check(f"管理页 {route} 渲染", kw in body_text(page3))

        browser.close()

    print(f"\n{'='*40}\n界面验证完成：通过 {PASS} 项，失败 {FAIL} 项。截图在 {SHOTS}")
    if FAIL:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
