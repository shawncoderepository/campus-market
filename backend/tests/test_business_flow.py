"""核心业务链路冒烟测试：注册→登录→发布→搜索→议价→下单→收货→评价。

使用独立的 MySQL 测试库或临时配置；此处直接对开发库操作，
通过唯一用户名避免与种子数据冲突。需保证 config.yaml 已启用数据库。
"""
import os

os.environ.setdefault("CONFIG_FILE", "config.yaml")

import uuid

from fastapi.testclient import TestClient

from application import create_app

app = create_app()


def _auth(client: TestClient, username: str, password: str) -> dict:
    client.post("/api/user/register", json={"username": username, "password": password, "nickname": username})
    resp = client.post("/api/user/login", json={"username": username, "password": password})
    token = resp.json()["data"]["token"]
    return {"Authorization": f"Bearer {token}"}


def test_full_business_flow() -> None:
    suffix = uuid.uuid4().hex[:8]
    seller_name, buyer_name = f"seller_{suffix}", f"buyer_{suffix}"
    pwd = "123456"

    with TestClient(app) as client:
        seller = _auth(client, seller_name, pwd)
        buyer = _auth(client, buyer_name, pwd)

        # 分类列表
        cat = client.get("/api/category/list").json()["data"]
        assert len(cat) >= 1
        category_id = cat[0]["id"]

        # 卖家发布商品
        publish = client.post(
            "/api/goods/publish",
            json={
                "category_id": category_id,
                "title": f"测试商品{suffix}",
                "description": "冒烟测试用",
                "original_price": 100,
                "sell_price": 60,
                "condition_level": 3,
                "images": [],
            },
            headers=seller,
        ).json()
        assert publish["code"] == 0, publish
        product_id = publish["data"]["id"]

        # 商品列表能搜到
        listed = client.get("/api/goods/list", params={"keyword": suffix}).json()
        assert listed["data"]["total"] >= 1

        # 商品详情
        detail = client.get(f"/api/goods/detail/{product_id}", headers=buyer).json()
        assert detail["code"] == 0 and detail["data"]["id"] == product_id

        # 收藏
        fav = client.post("/api/favorite/toggle", json={"product_id": product_id}, headers=buyer).json()
        assert fav["data"]["is_favorited"] is True

        # 买家出价
        offer = client.post(
            "/api/bargain/offer",
            json={"product_id": product_id, "offer_price": 50, "message": "便宜点"},
            headers=buyer,
        ).json()
        assert offer["code"] == 0, offer
        record_id = offer["data"]["id"]

        # 卖家接受出价
        respond = client.post(
            "/api/bargain/respond", json={"record_id": record_id, "accept": True}, headers=seller
        ).json()
        assert respond["data"]["status"] == 2

        # 买家按议价成交价下单
        order = client.post(
            "/api/order/create",
            json={"product_id": product_id, "bargain_record_id": record_id, "address": "1号宿舍楼"},
            headers=buyer,
        ).json()
        assert order["code"] == 0, order
        order_id = order["data"]["id"]
        assert order["data"]["deal_price"] == 50.0

        # 付款 -> 发货 -> 确认收货
        pay = client.post("/api/order/pay", json={"order_id": order_id}, headers=buyer).json()
        assert pay["data"]["status"] == 2
        ship = client.post("/api/order/ship", json={"order_id": order_id}, headers=seller).json()
        assert ship["data"]["status"] == 3
        confirm = client.post("/api/order/confirm", json={"order_id": order_id}, headers=buyer).json()
        assert confirm["data"]["status"] == 4

        # 买家评价卖家
        review = client.post(
            "/api/review/create",
            json={"order_id": order_id, "rating": 5, "content": "很好", "tags": ["靠谱"]},
            headers=buyer,
        ).json()
        assert review["code"] == 0, review

        # AI 降级（无 Key 时本地策略仍可用）
        copy_res = client.post(
            "/api/ai/copy",
            json={"keywords": "机械键盘", "category_name": "数码电子", "condition_level": 3, "original_price": 399},
            headers=seller,
        ).json()
        assert copy_res["code"] == 0 and copy_res["data"]["title"]

        estimate = client.post(
            "/api/ai/estimate",
            json={"category_name": "数码电子", "original_price": 399, "condition_level": 3, "used_years": 1},
            headers=seller,
        ).json()
        assert estimate["data"]["suggested_price"] > 0
