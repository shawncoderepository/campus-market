"""端到端真实账号全流程测试：用现存账号完整走一遍真实交易并把数据写入数据库。

卖家 student1 / 买家 student2 / 管理员 admin（密码均为 123456）。

流程：登录 → 双方改资料 → 卖家上架两件商品 → 买家搜索/看详情/收藏 →
私信往返 → 多轮议价 → 按成交价下单 → 付款 → 发货 → 确认收货 → 评价 →
买家举报另一件商品 → 管理员处理举报（违规下架）→ 校验状态。

运行方式（先确保后端在 8001 端口运行，在 backend 目录）：
    uv run python scripts/e2e_real_accounts.py
"""
from __future__ import annotations

import io
import json
import sys
import urllib.request
import urllib.error
import urllib.parse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE = "http://localhost:8001/api"
OK = 0

PASS = 0
FAIL = 0


def api(method: str, path: str, body: dict | None = None, token: str | None = None) -> dict:
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
        payload = json.loads(e.read().decode("utf-8") or "{}")
        raise RuntimeError(f"{method} {path} -> HTTP {e.code}: {payload}")


def check(name: str, cond: bool, extra: str = "") -> None:
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  [PASS] {name} {extra}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} {extra}")


def step(title: str) -> None:
    print(f"\n=== {title} ===")


def login(username: str, password: str = "123456") -> tuple[str, int]:
    r = api("POST", "/user/login", {"username": username, "password": password})
    return r["data"]["token"], r["data"]["user"]["id"]


def main() -> None:
    step("1. 三方登录（卖家 student1 / 买家 student2 / 管理员 admin）")
    seller_token, seller_id = login("student1")
    check("卖家 student1 登录", bool(seller_token), f"(id={seller_id})")
    buyer_token, buyer_id = login("student2")
    check("买家 student2 登录", bool(buyer_token), f"(id={buyer_id})")
    admin_token, admin_id = login("admin")
    check("管理员 admin 登录", bool(admin_token), f"(id={admin_id})")

    step("2. 双方修改自己的资料")
    ps = api("PUT", "/user/profile", {"nickname": "林晚晴学姐", "phone": "13811112222", "student_no": "2021001"}, seller_token)
    check("卖家改资料", ps.get("code") == OK and ps["data"]["phone"] == "13811112222")
    pb = api("PUT", "/user/profile", {"nickname": "爱捡漏的陈屿", "phone": "13933334444"}, buyer_token)
    check("买家改资料", pb.get("code") == OK and pb["data"]["nickname"] == "爱捡漏的陈屿")

    step("3. 卖家上架两件商品")
    cats = api("GET", "/category/list")["data"]
    cat_map = {c["name"]: c["id"] for c in cats}
    g1 = api("POST", "/goods/publish", {
        "category_id": cat_map.get("数码电子"),
        "title": "自用降噪耳机 头戴式 蓝牙",
        "description": "毕业出清，续航正常，附赠收纳包。诚心可小刀。",
        "original_price": 899, "sell_price": 420, "condition_level": 4, "images": [],
    }, seller_token)
    check("上架商品1（议价对象）", g1.get("code") == OK)
    pid = g1["data"]["id"]
    g2 = api("POST", "/goods/publish", {
        "category_id": cat_map.get("图书教材"),
        "title": "高等数学 同济第七版 上下册",
        "description": "少量笔记，正版。",
        "original_price": 68, "sell_price": 20, "condition_level": 3, "images": [],
    }, seller_token)
    check("上架商品2（被举报对象）", g2.get("code") == OK)
    pid2 = g2["data"]["id"]

    step("4. 买家搜索 / 查看详情 / 收藏")
    kw = urllib.parse.quote("耳机")
    lst = api("GET", f"/goods/list?keyword={kw}&page=1&page_size=10")
    check("关键词搜索", any(i["id"] == pid for i in lst["data"]["list"]))
    detail = api("GET", f"/goods/detail/{pid}", token=buyer_token)
    check("查看详情", detail["data"]["id"] == pid and detail["data"]["seller"]["id"] == seller_id)
    fav = api("POST", "/favorite/toggle", {"product_id": pid}, buyer_token)
    check("收藏商品1", fav["data"]["is_favorited"] is True)

    step("5. 买家与卖家私信往返")
    api("POST", "/message/send", {"receiver_id": seller_id, "product_id": pid, "content": "学姐好，耳机还在吗？能试听吗？"}, buyer_token)
    m2 = api("POST", "/message/send", {"receiver_id": buyer_id, "product_id": pid, "content": "在的，随时来试听～"}, seller_token)
    check("私信往返", m2.get("code") == OK)
    convs = api("GET", "/message/conversations", token=buyer_token)
    check("买家会话列表", any(c["peer_id"] == seller_id for c in convs["data"]))

    step("6. 议价：买家出价 → 卖家还价 → 买家接受")
    api("POST", "/bargain/offer", {"product_id": pid, "offer_price": 360, "message": "学生党，360 行吗？"}, buyer_token)
    reply = api("POST", "/bargain/reply", {"product_id": pid, "buyer_id": buyer_id, "offer_price": 400, "message": "最低 400，成色很好"}, seller_token)
    check("卖家还价 400", reply.get("code") == OK)
    record_id = reply["data"]["id"]
    accept = api("POST", "/bargain/respond", {"record_id": record_id, "accept": True}, buyer_token)
    check("买家接受 400", accept.get("code") == OK and accept["data"]["offer_price"] == 400)

    step("7. 买家按成交价下单 → 付款")
    order = api("POST", "/order/create", {"product_id": pid, "bargain_record_id": record_id, "address": "校内 5 号宿舍楼", "remark": "晚上来取"}, buyer_token)
    check("下单", order.get("code") == OK)
    oid = order["data"]["id"]
    check("订单金额=成交价400", order["data"]["deal_price"] == 400)
    pay = api("POST", "/order/pay", {"order_id": oid}, buyer_token)
    check("买家付款", pay.get("code") == OK and pay["data"]["status"] == 2)

    step("8. 卖家发货 → 买家确认收货")
    ship = api("POST", "/order/ship", {"order_id": oid}, seller_token)
    check("卖家发货", ship["data"]["status"] == 3)
    confirm = api("POST", "/order/confirm", {"order_id": oid}, buyer_token)
    check("买家确认收货", confirm["data"]["status"] == 4)

    step("9. 买家评价卖家")
    review = api("POST", "/review/create", {"order_id": oid, "rating": 5, "content": "学姐人很好，耳机成色和描述一致，交易愉快！", "tags": ["成色符合", "沟通愉快"]}, buyer_token)
    check("买家评价", review.get("code") == OK)
    received = api("GET", f"/review/received/{seller_id}")
    check("卖家收到评价", any(r["order_id"] == oid for r in received["data"]["list"]))

    step("10. 买家举报卖家的另一件商品（商品2）")
    rep = api("POST", "/report/create", {"product_id": pid2, "reason": "疑似盗版影印教材，价格异常偏低，请核实。"}, buyer_token)
    check("提交举报", rep.get("code") == OK)
    rid = rep["data"]["id"]

    step("11. 管理员处理举报（判定违规 → 商品下架）")
    pend = api("GET", "/admin/reports?status=1", token=admin_token)
    check("管理员看到待处理举报", any(r["id"] == rid for r in pend["data"]["list"]))
    handle = api("PUT", f"/admin/reports/{rid}", {"status": 2, "handler_result": "核实为违规商品，已下架处理。"}, admin_token)
    check("管理员处理举报", handle.get("code") == OK and handle["data"]["status"] == 2)
    off = api("PUT", f"/admin/goods/{pid2}/status", {"status": 3}, admin_token)
    check("管理员下架违规商品", off.get("code") == OK)

    step("12. 最终校验")
    final = api("GET", f"/goods/detail/{pid}")
    check("议价商品已售(状态2)", final["data"]["status"] == 2, f"(实际 {final['data']['status']})")
    off_detail = api("GET", f"/goods/detail/{pid2}")
    check("被举报商品已下架(状态3)", off_detail["data"]["status"] == 3, f"(实际 {off_detail['data']['status']})")
    bo = api("GET", "/order/my?role=buyer", token=buyer_token)
    check("买家订单含本单", any(o["id"] == oid for o in bo["data"]["list"]))

    print(f"\n{'='*40}\n真实账号全流程测试完成：通过 {PASS} 项，失败 {FAIL} 项。")
    print(f"卖家 student1(id={seller_id}) / 买家 student2(id={buyer_id}) / 订单 id={oid} / 举报 id={rid}")
    if FAIL:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
