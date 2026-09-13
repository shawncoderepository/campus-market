"""举报闭环验证：类型化举报 → 管理员处理(违规/驳回) → 自动下架 + 系统通知。

验证点：
1. 举报提交支持 reason_type（违规类型）
2. 处理为“举报成立”→ 商品自动下架 + 举报者与被举报者都收到系统通知
3. 处理为“举报不成立”→ 商品保持 + 仅举报者收到通知
运行：uv run python scripts/verify_report_loop.py
"""
from __future__ import annotations

import io
import json
import sys
import urllib.request
import urllib.error

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
BASE = "http://localhost:8001/api"
OK = 0
PASS = 0
FAIL = 0


def api(method, path, body=None, token=None):
    url = BASE + path
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{method} {path} -> HTTP {e.code}: {e.read().decode('utf-8')}")


def check(name, cond, extra=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {extra}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {extra}")


def login(u, p="123456"):
    r = api("POST", "/user/login", {"username": u, "password": p})
    return r["data"]["token"], r["data"]["user"]["id"]


def step(t):
    print(f"\n=== {t} ===")


def main():
    seller, sid = login("student1")
    buyer, bid = login("student2")
    admin, aid = login("admin")

    step("1. 卖家上架两件商品（一件判违规、一件判不违规）")
    cats = api("GET", "/category/list")["data"]
    cid = cats[0]["id"]
    g1 = api("POST", "/goods/publish", {"category_id": cid, "title": "闭环测试 违规商品", "description": "x", "original_price": 100, "sell_price": 50, "condition_level": 4, "images": []}, seller)
    bad_pid = g1["data"]["id"]
    g2 = api("POST", "/goods/publish", {"category_id": cid, "title": "闭环测试 正常商品", "description": "x", "original_price": 100, "sell_price": 50, "condition_level": 4, "images": []}, seller)
    good_pid = g2["data"]["id"]
    check("上架两件商品", g1.get("code") == OK and g2.get("code") == OK)

    step("2. 买家类型化举报两件商品")
    r1 = api("POST", "/report/create", {"product_id": bad_pid, "reason_type": "counterfeit", "reason": "明显是盗版"}, buyer)
    check("举报违规商品(类型counterfeit)", r1.get("code") == OK and r1["data"]["reason_type"] == "counterfeit", f"(类型名:{r1['data'].get('reason_type_name')})")
    rid1 = r1["data"]["id"]
    check("举报响应含被举报者", r1["data"].get("seller_nickname") != "", f"(卖家:{r1['data'].get('seller_nickname')})")
    r2 = api("POST", "/report/create", {"product_id": good_pid, "reason_type": "false_info", "reason": "我觉得不符"}, buyer)
    rid2 = r2["data"]["id"]
    check("举报正常商品(类型false_info)", r2.get("code") == OK)
    # 不能举报自己的商品
    try:
        api("POST", "/report/create", {"product_id": bad_pid, "reason_type": "other", "reason": "x"}, seller)
        check("自己不能举报自己", False)
    except RuntimeError:
        check("自己不能举报自己", True)

    step("3. 管理员处理：商品1 判违规(自动下架+双方通知)")
    h1 = api("PUT", f"/admin/reports/{rid1}", {"status": 2, "handler_result": "经核实为盗版，已下架。"}, admin)
    check("处理为违规", h1.get("code") == OK and h1["data"]["status"] == 2)
    d1 = api("GET", f"/goods/detail/{bad_pid}")
    check("违规商品自动下架(状态3)", d1["data"]["status"] == 3, f"(实际 {d1['data']['status']})")

    step("4. 验证双方收到系统通知")
    bn = api("GET", "/message/conversations", token=buyer)
    buyer_admin = [c for c in bn["data"] if c["peer_id"] == aid]
    check("举报者收到管理员会话", len(buyer_admin) >= 1)
    bh = api("GET", f"/message/history?peer_id={aid}", token=buyer)
    buyer_msgs = [m for m in bh["data"]["list"] if m["msg_type"] == 2 and "举报处理结果" in m["content"]]
    check("举报者收到系统通知(msg_type=2)", len(buyer_msgs) >= 1, f"(内容:{buyer_msgs[-1]['content'][:30]}...)" if buyer_msgs else "")

    sn = api("GET", "/message/conversations", token=seller)
    seller_admin = [c for c in sn["data"] if c["peer_id"] == aid]
    check("被举报者收到管理员会话", len(seller_admin) >= 1)
    sh = api("GET", f"/message/history?peer_id={aid}", token=seller)
    seller_msgs = [m for m in sh["data"]["list"] if m["msg_type"] == 2 and "违规处理通知" in m["content"]]
    check("被举报者收到违规通知(msg_type=2)", len(seller_msgs) >= 1, f"(内容:{seller_msgs[-1]['content'][:30]}...)" if seller_msgs else "")

    step("5. 管理员处理：商品2 判不成立(保持+仅举报者通知)")
    before = len(seller_msgs)
    h2 = api("PUT", f"/admin/reports/{rid2}", {"status": 3, "handler_result": "经核实未发现违规。"}, admin)
    check("处理为不成立", h2.get("code") == OK and h2["data"]["status"] == 3)
    d2 = api("GET", f"/goods/detail/{good_pid}")
    check("正常商品保持在售(状态1)", d2["data"]["status"] == 1, f"(实际 {d2['data']['status']})")
    bh2 = api("GET", f"/message/history?peer_id={aid}", token=buyer)
    buyer_reject = [m for m in bh2["data"]["list"] if m["msg_type"] == 2 and "暂未发现违规" in m["content"]]
    check("举报者收到驳回通知", len(buyer_reject) >= 1)
    sh2 = api("GET", f"/message/history?peer_id={aid}", token=seller)
    seller_new = [m for m in sh2["data"]["list"] if m["msg_type"] == 2]
    check("被举报者未收到新通知(驳回不打扰)", len(seller_new) == before, f"(卖家通知数 {before}->{len(seller_new)})")

    print(f"\n{'='*40}\n举报闭环验证完成：通过 {PASS} 项，失败 {FAIL} 项。")
    if FAIL:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
