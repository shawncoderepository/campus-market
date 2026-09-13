"""用户端 + 管理端 全接口覆盖测试（真实写库）。

在 e2e_real_accounts.py 已覆盖核心交易流的基础上，补齐所有剩余端点，
确保用户端与管理端每一个 API 都被真实调用并写入数据库。

覆盖清单：
  用户端 user: register / login / me / profile / password(改后改回)
  商品   goods: publish / list / detail / edit / my/list / upload / delete(下架)
  收藏   favorite: toggle / list
  消息   message: send / conversations / history / unread
  议价   bargain: offer / reply / respond / session / my
  订单   order: create / pay / ship / confirm / cancel / my
  评价   review: create / received
  举报   report: create / my
  分类   category: list
  管理端 admin: stats / users / users status / users credit /
                categories 增改删 / reports 列表+处理 / goods 列表+status / orders 列表

运行（先确保后端在 8001）：
    uv run python scripts/e2e_full_coverage.py
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
        with urllib.request.urlopen(req, timeout=20) as resp:
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
    step("U0. 用户注册 + 登录 + me")
    import time
    ts = int(time.time()) % 100000
    reg = api("POST", "/user/register", {"username": f"cover_{ts}", "password": "123456", "nickname": "覆盖测试号"})
    check("注册新用户", reg.get("code") == OK)
    seller, sid = login("student1")
    buyer, bid = login("student2")
    admin, aid = login("admin")
    me = api("GET", "/user/me", token=seller)
    check("me 获取当前用户", me["data"]["id"] == sid)

    step("U1. 修改资料 + 修改密码(改后改回)")
    p = api("PUT", "/user/profile", {"nickname": "林晚晴", "phone": "13800000000"}, seller)
    check("修改资料", p.get("code") == OK)
    pw = api("PUT", "/user/password", {"old_password": "123456", "new_password": "654321"}, seller)
    check("修改密码", pw.get("code") == OK)
    relog = api("POST", "/user/login", {"username": "student1", "password": "654321"})
    check("新密码可登录", relog.get("code") == OK)
    back = api("PUT", "/user/password", {"old_password": "654321", "new_password": "123456"}, seller)
    check("改回原密码", back.get("code") == OK)

    step("U2. 商品：发布 / 列表 / 详情 / 编辑 / 我的列表 / 上传 / 下架")
    cats = api("GET", "/category/list")["data"]
    cat_map = {c["name"]: c["id"] for c in cats}
    g = api("POST", "/goods/publish", {
        "category_id": cat_map.get("生活百货") or cats[0]["id"],
        "title": "覆盖测试 收纳箱 大号", "description": "毕业出清，干净无异味。",
        "original_price": 59, "sell_price": 25, "condition_level": 4, "images": [],
    }, seller)
    pid = g["data"]["id"]
    check("发布商品", g.get("code") == OK, f"(id={pid})")
    lst = api("GET", f"/goods/list?keyword={urllib.parse.quote('收纳箱')}&page=1&page_size=10")
    check("商品列表(搜索)", any(i["id"] == pid for i in lst["data"]["list"]))
    det = api("GET", f"/goods/detail/{pid}", token=buyer)
    check("商品详情", det["data"]["id"] == pid and "related" in det["data"])
    ed = api("PUT", f"/goods/{pid}", {"title": "覆盖测试 收纳箱 大号(已小刀)", "sell_price": 22}, seller)
    check("编辑商品", ed.get("code") == OK and ed["data"]["sell_price"] == 22)
    my = api("GET", "/goods/my/list?page=1&page_size=20", token=seller)
    check("我的商品列表", any(i["id"] == pid for i in my["data"]["list"]))
    # 上传图片（multipart）
    up_ok = False
    try:
        import io as _io
        boundary = "----pytestboundary1234567"
        png = bytes.fromhex("89504e470d0a1a0a0000000d4948445200000001000000010806000000" "1f15c4890000000d49444154789c626001000000ffff030000060005" "57bfabd40000000049454e44ae426082")
        body = b""
        body += f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"t.png\"\r\nContent-Type: image/png\r\n\r\n".encode()
        body += png + f"\r\n--{boundary}--\r\n".encode()
        req = urllib.request.Request(BASE + "/goods/upload", data=body, method="POST")
        req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
        req.add_header("Authorization", f"Bearer {seller}")
        with urllib.request.urlopen(req, timeout=20) as resp:
            upd = json.loads(resp.read().decode("utf-8"))
        up_ok = upd.get("code") == OK and bool(upd["data"].get("url"))
    except Exception as exc:  # noqa: BLE001
        print(f"    (上传异常: {exc})")
    check("上传图片", up_ok)

    step("U3. 收藏：toggle / list")
    fav = api("POST", "/favorite/toggle", {"product_id": pid}, buyer)
    check("收藏", fav["data"]["is_favorited"] is True)
    favs = api("GET", "/favorite/list?page=1&page_size=20", token=buyer)
    check("收藏列表", any(i["id"] == pid for i in favs["data"]["list"]))

    step("U4. 消息：send / conversations / history / unread")
    api("POST", "/message/send", {"receiver_id": sid, "product_id": pid, "content": "这个还在吗？"}, buyer)
    conv = api("GET", "/message/conversations", token=seller)
    check("会话列表", any(c["peer_id"] == bid for c in conv["data"]))
    unread = api("GET", "/message/unread", token=seller)
    check("未读消息数", unread.get("code") == OK and unread["data"].get("count", 0) >= 1, f"(count={unread['data'].get('count')})")
    hist = api("GET", f"/message/history?peer_id={bid}&product_id={pid}", token=seller)
    check("聊天记录", hist.get("code") == OK and len(hist["data"]["list"]) >= 1)

    step("U5. 议价：offer / reply / session / my / respond(拒绝)")
    off = api("POST", "/bargain/offer", {"product_id": pid, "offer_price": 18, "message": "18 行吗"}, buyer)
    check("买家出价", off.get("code") == OK)
    sess = api("GET", f"/bargain/session?product_id={pid}&buyer_id={bid}", token=seller)
    check("议价会话", sess.get("code") == OK)
    rep = api("POST", "/bargain/reply", {"product_id": pid, "buyer_id": bid, "offer_price": 20, "message": "最低 20"}, seller)
    check("卖家还价", rep.get("code") == OK)
    rid = rep["data"]["id"]
    myb = api("GET", "/bargain/my", token=buyer)
    check("我的议价列表", myb.get("code") == OK and len(myb["data"]) >= 1)
    rej = api("POST", "/bargain/respond", {"record_id": rid, "accept": False}, buyer)
    check("买家拒绝还价", rej.get("code") == OK)

    step("U6. 订单：create / cancel / my（取消流程）")
    oc = api("POST", "/order/create", {"product_id": pid, "address": "校内", "remark": "测试取消"}, buyer)
    oid_c = oc["data"]["id"]
    check("下单(待取消)", oc.get("code") == OK)
    cc = api("POST", "/order/cancel", {"order_id": oid_c}, buyer)
    check("取消订单", cc.get("code") == OK and cc["data"]["status"] == 5)
    myo = api("GET", "/order/my?role=buyer", token=buyer)
    check("我的订单列表", any(o["id"] == oid_c for o in myo["data"]["list"]))

    step("U7. 完整成交：出价→接受→下单→付款→发货→确认→评价")
    o2 = api("POST", "/bargain/offer", {"product_id": pid, "offer_price": 20}, buyer)
    r2 = api("POST", "/bargain/reply", {"product_id": pid, "buyer_id": bid, "offer_price": 21}, seller)
    acc = api("POST", "/bargain/respond", {"record_id": r2["data"]["id"], "accept": True}, buyer)
    check("议价成交", acc["data"]["offer_price"] == 21)
    od = api("POST", "/order/create", {"product_id": pid, "bargain_record_id": r2["data"]["id"], "address": "校内 6 号楼"}, buyer)
    oid = od["data"]["id"]
    check("下单", od.get("code") == OK and od["data"]["deal_price"] == 21)
    check("付款", api("POST", "/order/pay", {"order_id": oid}, buyer)["data"]["status"] == 2)
    check("发货", api("POST", "/order/ship", {"order_id": oid}, seller)["data"]["status"] == 3)
    check("确认收货", api("POST", "/order/confirm", {"order_id": oid}, buyer)["data"]["status"] == 4)
    rv = api("POST", "/review/create", {"order_id": oid, "rating": 4, "content": "东西不错。", "tags": ["物流快"]}, buyer)
    check("发表评价", rv.get("code") == OK)
    rec = api("GET", f"/review/received/{sid}")
    check("收到的评价", any(r["order_id"] == oid for r in rec["data"]["list"]))

    step("U8. 举报：create / my")
    rp = api("POST", "/report/create", {"product_id": pid, "reason": "覆盖测试：描述与实物不符。"}, buyer)
    check("提交举报", rp.get("code") == OK)
    rep_id = rp["data"]["id"]
    myrep = api("GET", "/report/my?page=1&page_size=20", token=buyer)
    check("我的举报列表", any(r["id"] == rep_id for r in myrep["data"]["list"]))

    # ---------- 管理端 ----------
    step("A1. 仪表盘统计")
    st = api("GET", "/admin/stats", token=admin)
    check("数据概览", st.get("code") == OK and "user_total" in st["data"], f"(users={st['data'].get('user_total')}, goods={st['data'].get('goods_total')}, deal={st['data'].get('deal_amount')})")

    step("A2. 用户管理：列表 / 调整信用分 / 禁用 / 启用")
    us = api("GET", "/admin/users?page=1&page_size=50", token=admin)
    check("用户列表", us.get("code") == OK and us["data"]["total"] >= 1)
    cr = api("PUT", f"/admin/users/{bid}/credit", {"credit_score": 95}, admin)
    check("调整信用分", cr.get("code") == OK and cr["data"]["credit_score"] == 95)
    ds = api("PUT", f"/admin/users/{bid}/status", {"status": 0}, admin)
    check("禁用用户", ds.get("code") == OK and ds["data"]["status"] == 0)
    en = api("PUT", f"/admin/users/{bid}/status", {"status": 1}, admin)
    check("启用用户", en.get("code") == OK and en["data"]["status"] == 1)

    step("A3. 分类管理：新增 / 编辑 / 删除")
    nc = api("POST", "/admin/categories", {"name": f"测试分类{ts}", "icon": "🧪", "sort": 99}, admin)
    check("新增分类", nc.get("code") == OK)
    cid = nc["data"]["id"]
    uc = api("PUT", f"/admin/categories/{cid}", {"name": f"测试分类改{ts}", "icon": "✅"}, admin)
    check("编辑分类", uc.get("code") == OK and uc["data"]["name"] == f"测试分类改{ts}")
    cl = api("GET", "/admin/categories", token=admin)
    check("分类列表(含商品数)", any(c["id"] == cid for c in cl["data"]))
    dc = api("DELETE", f"/admin/categories/{cid}", token=admin)
    check("删除分类", dc.get("code") == OK)

    step("A4. 举报处理：列表 / 处理")
    rl = api("GET", "/admin/reports?status=1&page=1&page_size=20", token=admin)
    check("举报列表(待处理)", any(r["id"] == rep_id for r in rl["data"]["list"]))
    hd = api("PUT", f"/admin/reports/{rep_id}", {"status": 3, "handler_result": "经核实不成立，予以驳回。"}, admin)
    check("处理举报(驳回)", hd.get("code") == OK and hd["data"]["status"] == 3)

    step("A5. 商品管理：全站列表 / 上/下架")
    gl = api("GET", "/admin/goods?page=1&page_size=50", token=admin)
    check("全站商品列表", gl.get("code") == OK and gl["data"]["total"] >= 1)
    offs = api("PUT", f"/admin/goods/{pid}/status", {"status": 3}, admin)
    check("管理员下架商品", offs.get("code") == OK and offs["data"]["status"] == 3)
    on = api("PUT", f"/admin/goods/{pid}/status", {"status": 1}, admin)
    check("管理员上架商品", on.get("code") == OK and on["data"]["status"] == 1)

    step("A6. 订单管理：全站订单列表")
    ol = api("GET", "/admin/orders?page=1&page_size=50", token=admin)
    check("全站订单列表", ol.get("code") == OK and ol["data"]["total"] >= 1, f"(total={ol['data'].get('total')})")

    step("U9. 商品下架（卖家自主 delete）")
    gd = api("DELETE", f"/goods/{pid}", token=seller)
    check("卖家下架商品", gd.get("code") == OK)

    print(f"\n{'='*44}\n全覆盖测试完成：通过 {PASS} 项，失败 {FAIL} 项。")
    if FAIL:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
