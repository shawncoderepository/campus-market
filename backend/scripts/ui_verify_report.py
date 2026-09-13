"""举报闭环 UI 验证：管理员处理页（模板+被举报者）、用户消息页（系统通知）。截图存 ui_shots/。"""
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


def check(name, cond, extra=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {extra}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {extra}")


def login(page, u, p="123456"):
    page.goto(f"{BASE}/login", wait_until="networkidle")
    page.wait_for_timeout(600)
    page.locator('input[type="text"]').first.fill(u)
    page.locator('input[type="password"]').first.fill(p)
    page.locator('input[type="password"]').first.press("Enter")
    page.wait_for_url(lambda x: "/login" not in x, timeout=10000)
    page.wait_for_load_state("networkidle")


def main():
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        ctx = b.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
        page = ctx.new_page()

        print("\n=== 管理员：举报处理页 ===")
        login(page, "admin")
        page.goto(f"{BASE}/admin/report", wait_until="networkidle")
        page.wait_for_timeout(1000)
        txt = page.locator("body").inner_text()
        check("举报列表含违规类型列", "违规类型" in txt or "假冒" in txt or "虚假" in txt)
        check("举报列表含被举报者列", "被举报者" in txt)
        page.screenshot(path=str(SHOTS / "20_admin_report_list.png"), full_page=True)
        # 打开一条待处理举报看模板
        handled = page.locator("button:has-text('处理')")
        if handled.count() > 0:
            handled.first.click()
            page.wait_for_timeout(600)
            mt = page.locator("body").inner_text()
            check("处理弹窗显示被举报者", "被举报者" in mt)
            check("处理弹窗显示违规类型", "违规类型" in mt)
            check("处理弹窗自动填模板", "经核实" in mt)
            page.screenshot(path=str(SHOTS / "21_admin_report_handle.png"), full_page=True)
            page.keyboard.press("Escape")
        else:
            check("有待处理举报可打开", False, "(当前无待处理举报)")

        print("\n=== 买家 student2：消息页系统通知 ===")
        ctx2 = b.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
        p2 = ctx2.new_page()
        login(p2, "student2")
        p2.goto(f"{BASE}/message", wait_until="networkidle")
        p2.wait_for_timeout(1000)
        t2 = p2.locator("body").inner_text()
        has_sys = "系统通知" in t2 or "举报处理结果" in t2 or "校园小助手" in t2
        check("消息页能看到系统通知", has_sys)
        # 点开管理员会话
        conv = p2.locator(".message__conv", has_text="系统")
        if conv.count() == 0:
            conv = p2.locator(".message__conv").first
        if conv.count() > 0:
            conv.first.click()
            p2.wait_for_timeout(800)
        p2.screenshot(path=str(SHOTS / "22_buyer_message_sys.png"), full_page=True)
        bt = p2.locator("body").inner_text()
        check("系统气泡带'系统通知'标记", "系统通知" in bt)

        b.close()

    print(f"\n{'='*40}\n举报闭环 UI 验证完成：通过 {PASS} 项，失败 {FAIL} 项。")
    if FAIL:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
