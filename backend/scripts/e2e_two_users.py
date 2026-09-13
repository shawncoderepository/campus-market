"""端到端功能测试：模拟两个真实用户完整交易流程。

场景：卖家小红上架商品并完善资料，买家小明注册登录、修改资料、
浏览搜索、收藏、私信、议价（多轮还价）、按成交价下单、付款、
卖家发货、买家确认收货、买家评价卖家。

运行方式（先确保后端在 8000 端口运行，在 backend 目录）：
    uv run python scripts/e2e_two_users.py
"""
from __future__ import annotations

import io
import json
import sys
import time
import urllib.request
import urllib.error

# 统一控制台 UTF-8 输出，避免中文乱码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

BASE = "http://localhost:8001/api"
OK = 0  # 后端成功码为 0

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
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        payload = json.loads(e.read().decode("utf-8") or "{}")
        raise RuntimeError(f"{method} {path} -> HTTP {e.code}: {payload}")
    return payload


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


def main() -> None:
    ts = int(time.time()) % 100000
    seller_name = f"seller_hong_{ts}"
    buyer_name = f"buyer_ming_{ts}"

    step("1. 注册两个真实用户（卖家小红 / 买家小明）")
    r1 = api("POST", "/user/register", {"username": seller_name, "password": "123456", "nickname": "小红学姐", "student_no": "2021001"})
    check("卖家注册", r1.get("code") == OK)
    r2 = api("POST", "/user/register", {"username": buyer_name, "password": "123456", "nickname": "小明同学", "student_no": "2023002"})
    check("买家注册", r2.get("code") == OK)

    step("2. 双方登录拿 token")
    ls = api("POST", "/user/login", {"username": seller_name, "password": "123456"})
    seller_token = ls["data"]["token"]
    seller_id = ls["data"]["user"]["id"]
    check("卖家登录", bool(seller_token))
    lb = api("POST", "/user/login", {"username": buyer_name, "password": "123456"})
    buyer_token = lb["data"]["token"]
    buyer_id = lb["data"]["user"]["id"]
    check("买家登录", bool(buyer_token))

    step("3. 双方修改自己的资料")
    ps = api("PUT", "/user/profile", {"nickname": "小红学姐", "phone": "13800000001", "student_no": "2021001"}, seller_token)
    check("卖家改资料", ps.get("code") == OK and ps["data"]["phone"] == "13800000001")
    pb = api("PUT", "/user/profile", {"nickname": "爱捡漏的小明", "phone": "13900000002"}, buyer_token)
    check("买家改昵称", pb.get("code") == OK and pb["data"]["nickname"] == "爱捡漏的小明")

    step("4. 卖家上架两件商品")
    cats = api("GET", "/category/list")["data"]
    cat_map = {c["name"]: c["id"] for c in cats}
    g1 = api("POST", "/goods/publish", {
        "category_id": cat_map.get("数码电子"),
        "title": "九成新 iPad 9 64G 深空灰",
        "description": "考研结束出，无磕碰无拆修，电池健康，带原装保护壳和充电器。",
        "original_price": 2499, "sell_price": 1500, "condition_level": 4, "images": [],
    }, seller_token)
    check("上架商品1", g1.get("code") == OK)
    pid = g1["data"]["id"]
    g2 = api("POST", "/goods/publish", {
        "category_id": cat_map.get("图书教材"),
        "title": "计算机网络 第七版 谢希仁",
        "description": "少量笔记，适合期末复习。",
        "original_price": 49, "sell_price": 15, "condition_level": 3, "images": [],
    }, seller_token)
    check("上架商品2", g2.get("code") == OK)
    pid2 = g2["data"]["id"]

    step("5. 买家浏览 / 搜索 / 查看详情")
    lst = api("GET", "/goods/list?keyword=iPad&page=1&page_size=10")
    check("关键词搜索", any(i["id"] == pid for i in lst["data"]["list"]))
    detail = api("GET", f"/goods/detail/{pid}", token=buyer_token)
    check("查看详情", detail["data"]["id"] == pid and detail["data"]["seller"]["id"] == seller_id)

    step("6. 买家收藏")
    fav = api("POST", "/favorite/toggle", {"product_id": pid2}, buyer_token)
    check("收藏商品2", fav["data"]["is_favorited"] is True)
    favs = api("GET", "/favorite/list", token=buyer_token)
    check("收藏列表", any(i["id"] == pid2 for i in favs["data"]["list"]))

    step("7. 买家私信卖家")
    m1 = api("POST", "/message/send", {"receiver_id": seller_id, "product_id": pid, "content": "学姐好，iPad 还在吗？能看看实物吗？"}, buyer_token)
    check("买家发私信", m1.get("code") == OK)
    m2 = api("POST", "/message/send", {"receiver_id": buyer_id, "product_id": pid, "content": "在的，随时可以看实物～"}, seller_token)
    check("卖家回私信", m2.get("code") == OK)
    convs = api("GET", "/message/conversations", token=seller_token)
    check("卖家会话列表", any(c["peer_id"] == buyer_id for c in convs["data"]))

    step("8. 议价：买家出价 → 卖家还价 → 买家接受")
    offer = api("POST", "/bargain/offer", {"product_id": pid, "offer_price": 1300, "message": "诚心要，1300 行吗？"}, buyer_token)
    check("买家出价 1300", offer.get("code") == OK)
    reply = api("POST", "/bargain/reply", {"product_id": pid, "buyer_id": buyer_id, "offer_price": 1400, "message": "最低 1400，真的很新"}, seller_token)
    check("卖家还价 1400", reply.get("code") == OK)
    reply_record_id = reply["data"]["id"]
    accept = api("POST", "/bargain/respond", {"record_id": reply_record_id, "accept": True}, buyer_token)
    check("买家接受 1400", accept.get("code") == OK)
    final_price = accept["data"]["offer_price"]
    check("成交价为 1400", final_price == 1400, f"(实际 {final_price})")

    step("9. 买家按成交价下单 → 付款")
    order = api("POST", "/order/create", {"product_id": pid, "bargain_record_id": reply_record_id, "address": "校内 3 号宿舍楼", "remark": "下课后来取"}, buyer_token)
    check("下单", order.get("code") == OK)
    oid = order["data"]["id"]
    check("订单金额=成交价", order["data"]["deal_price"] == 1400, f"(实际 {order['data']['deal_price']})")
    pay = api("POST", "/order/pay", {"order_id": oid}, buyer_token)
    check("买家付款", pay.get("code") == OK and pay["data"]["status"] == 2)

    step("10. 卖家发货 → 买家确认收货")
    ship = api("POST", "/order/ship", {"order_id": oid}, seller_token)
    check("卖家发货", ship["data"]["status"] == 3)
    confirm = api("POST", "/order/confirm", {"order_id": oid}, buyer_token)
    check("买家确认收货", confirm["data"]["status"] == 4)

    step("11. 买家评价卖家")
    review = api("POST", "/review/create", {"order_id": oid, "rating": 5, "content": "学姐人很好，iPad 成色和描述一致，交易愉快！", "tags": ["成色符合", "沟通愉快"]}, buyer_token)
    check("买家评价", review.get("code") == OK)
    received = api("GET", f"/review/received/{seller_id}")
    check("卖家收到评价", any(r["order_id"] == oid for r in received["data"]["list"]))

    step("12. 校验双方订单列表")
    bo = api("GET", "/order/my?role=buyer", token=buyer_token)
    check("买家订单", any(o["id"] == oid for o in bo["data"]["list"]))
    so = api("GET", "/order/my?role=seller", token=seller_token)
    check("卖家订单", any(o["id"] == oid for o in so["data"]["list"]))

    step("13. 校验商品状态变为已售")
    final = api("GET", f"/goods/detail/{pid}")
    check("商品已售出(状态2)", final["data"]["status"] == 2, f"(实际 status={final['data']['status']})")

    print(f"\n{'='*40}\n测试完成：通过 {PASS} 项，失败 {FAIL} 项。")
    if FAIL:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
