from datetime import datetime, timedelta

from fastapi import APIRouter, Depends

from application.apis.admin.schema import (
    AdminActivity,
    AdminCategoryReq,
    AdminCategoryRes,
    AdminCategoryShare,
    AdminGoodsStatusReq,
    AdminReportHandleReq,
    AdminStatsRes,
    AdminUserCreditReq,
    AdminUserRes,
    AdminUserStatusReq,
)
from application.apis.goods.schema import GoodsItemRes
from application.apis.order.schema import OrderRes
from application.apis.report.report_api import _to_res as report_to_res
from application.apis.report.schema import ReportRes
from application.common.constants import HttpErrorCodeEnum
from application.common.dependency import get_current_admin
from application.common.exception.exception import HttpBusinessException
from application.common.helper.response_helper import ResponseHelper
from application.common.models import Category, Order, Product, Report, Review, User
from application.common.schema.response_schema import BaseResponse, PageResult
from application.service.goods.goods_service import to_item_res as goods_to_item_res
from application.service.goods.goods_service import update_goods as goods_update_goods
from application.service.notification.notification_service import notify_report_handled
from application.service.order.order_service import to_order_res as order_to_res

admin_router = APIRouter(prefix="/admin", tags=["Admin"])


def _wow(current: float, previous: float) -> float | None:
    """计算周环比增长率（%）。上周为 0 时无法计算返回 None。"""
    if previous == 0:
        return None
    return round((current - previous) / previous * 100, 1)


# ---------- 数据概览 ----------
@admin_router.get("/stats", response_model=BaseResponse[AdminStatsRes], summary="数据概览")
async def stats(_: User = Depends(get_current_admin)) -> object:
    now = datetime.now()
    week_start = now - timedelta(days=7)
    prev_week_start = now - timedelta(days=14)

    user_total = await User.all().count()
    goods_total = await Product.all().count()
    goods_on_sale = await Product.filter(status=1).count()
    order_total = await Order.all().count()
    order_done = await Order.filter(status=4).count()
    done_prices = await Order.filter(status=4).values_list("deal_price", flat=True)
    deal_amount = float(sum(done_prices))
    report_pending = await Report.filter(status=1).count()
    category_total = await Category.all().count()
    review_total = await Review.all().count()

    # 本周新增
    user_cur = await User.filter(created_at__gte=week_start).count()
    goods_cur = await Product.filter(created_at__gte=week_start).count()
    order_cur = await Order.filter(created_at__gte=week_start).count()
    review_cur = await Review.filter(created_at__gte=week_start).count()
    report_cur = await Report.filter(created_at__gte=week_start).count()
    deal_cur_prices = await Order.filter(status=4, updated_at__gte=week_start).values_list("deal_price", flat=True)
    deal_cur = float(sum(deal_cur_prices))

    # 上周新增（14 天前 ~ 7 天前）
    user_prev = await User.filter(created_at__gte=prev_week_start, created_at__lt=week_start).count()
    goods_prev = await Product.filter(created_at__gte=prev_week_start, created_at__lt=week_start).count()
    order_prev = await Order.filter(created_at__gte=prev_week_start, created_at__lt=week_start).count()
    review_prev = await Review.filter(created_at__gte=prev_week_start, created_at__lt=week_start).count()
    report_prev = await Report.filter(created_at__gte=prev_week_start, created_at__lt=week_start).count()
    deal_prev_prices = await Order.filter(
        status=4, updated_at__gte=prev_week_start, updated_at__lt=week_start
    ).values_list("deal_price", flat=True)
    deal_prev = float(sum(deal_prev_prices))

    return ResponseHelper.success(
        AdminStatsRes(
            user_total=user_total,
            goods_total=goods_total,
            goods_on_sale=goods_on_sale,
            order_total=order_total,
            order_done=order_done,
            deal_amount=round(deal_amount, 2),
            report_pending=report_pending,
            category_total=category_total,
            review_total=review_total,
            user_wow=_wow(user_cur, user_prev),
            goods_wow=_wow(goods_cur, goods_prev),
            order_wow=_wow(order_cur, order_prev),
            deal_amount_wow=_wow(deal_cur, deal_prev),
            report_wow=_wow(report_cur, report_prev),
            review_wow=_wow(review_cur, review_prev),
        )
    )


@admin_router.get("/stats/category-share", response_model=BaseResponse[list[AdminCategoryShare]], summary="商品分类占比")
async def category_share(_: User = Depends(get_current_admin)) -> object:
    goods_total = await Product.all().count()
    categories = await Category.all()
    shares: list[AdminCategoryShare] = []
    for c in categories:
        count = await Product.filter(category_id=c.id).count()
        percent = round(count / goods_total * 100, 1) if goods_total else 0.0
        shares.append(AdminCategoryShare(name=c.name, count=count, percent=percent))
    shares.sort(key=lambda x: x.count, reverse=True)
    return ResponseHelper.success(shares)


@admin_router.get("/stats/activities", response_model=BaseResponse[list[AdminActivity]], summary="最新动态")
async def activities(_: User = Depends(get_current_admin)) -> object:
    """聚合最近的商品、订单、举报、注册事件，按时间倒序取前 8 条。"""
    events: list[tuple[datetime, AdminActivity]] = []

    def _naive(dt: datetime) -> datetime:
        # MySQL 带时区时 created_at 为 offset-aware，统一转成本地 naive 便于相减与排序
        return dt.replace(tzinfo=None) if dt.tzinfo is not None else dt

    def _rel_time(dt: datetime) -> str:
        diff = datetime.now() - _naive(dt)
        if diff < timedelta(minutes=1):
            return "刚刚"
        if diff < timedelta(hours=1):
            return f"{int(diff.total_seconds() // 60)} 分钟前"
        if diff < timedelta(days=1):
            return f"{int(diff.total_seconds() // 3600)} 小时前"
        return f"{diff.days} 天前"

    recent_products = await Product.all().prefetch_related("seller").order_by("-id").limit(3)
    for p in recent_products:
        events.append((p.created_at, AdminActivity(
            id=f"product-{p.id}",
            user=getattr(p.seller, "nickname", "") or "用户",
            action="发布了新商品",
            target=p.title,
            time=_rel_time(p.created_at),
            color="#6366f1",
        )))

    # 订单事件：按状态细分（创建 / 付款待面议 / 完成 / 取消），每类取最近几条
    order_status_meta = {
        1: ("创建了订单", "#10b981", "buyer"),
        3: ("付款成功，待面议", "#0ea5e9", "buyer"),
        4: ("完成了订单", "#16a34a", "buyer"),
        5: ("取消了订单", "#f97316", "buyer"),
    }
    for status, (action, color, _) in order_status_meta.items():
        rows = await Order.filter(status=status).prefetch_related("buyer").order_by("-updated_at").limit(3)
        for o in rows:
            events.append((o.updated_at, AdminActivity(
                id=f"order-{o.id}-s{status}",
                user=getattr(o.buyer, "nickname", "") or "用户",
                action=action,
                target=f"订单 #{o.id}",
                time=_rel_time(o.updated_at),
                color=color,
            )))

    recent_reports = await Report.all().order_by("-id").limit(3)
    for r in recent_reports:
        events.append((r.created_at, AdminActivity(
            id=f"report-{r.id}",
            user="系统",
            action="收到新举报",
            target=r.reason[:20] if r.reason else "",
            time=_rel_time(r.created_at),
            color="#ef4444",
        )))

    recent_users = await User.all().order_by("-id").limit(3)
    for u in recent_users:
        events.append((u.created_at, AdminActivity(
            id=f"user-{u.id}",
            user=u.nickname or u.username,
            action="注册了账号",
            target="",
            time=_rel_time(u.created_at),
            color="#8b5cf6",
        )))

    events.sort(key=lambda x: _naive(x[0]), reverse=True)
    return ResponseHelper.success([e[1] for e in events[:8]])


# ---------- 用户管理 ----------
@admin_router.get("/users", response_model=BaseResponse[PageResult[AdminUserRes]], summary="用户列表")
async def users(
    keyword: str = "",
    role: int | None = None,
    status: int | None = None,
    page: int = 1,
    page_size: int = 20,
    _: User = Depends(get_current_admin),
) -> object:
    qs = User.all()
    if keyword:
        qs = qs.filter(username__icontains=keyword) | qs.filter(nickname__icontains=keyword)
    if role is not None:
        qs = qs.filter(role=role)
    if status is not None:
        qs = qs.filter(status=status)
    total = await qs.count()
    items = await qs.order_by("-id").offset((page - 1) * page_size).limit(page_size)
    data = [
        AdminUserRes(
            id=u.id, username=u.username, nickname=u.nickname, avatar=u.avatar,
            phone=u.phone, student_no=u.student_no, credit_score=u.credit_score,
            role=u.role, status=u.status, created_at=u.created_at,
        )
        for u in items
    ]
    return ResponseHelper.success(
        PageResult[AdminUserRes](list=data, total=total, page=page, page_size=page_size)
    )


@admin_router.put("/users/{user_id}/status", response_model=BaseResponse[AdminUserRes], summary="启用/禁用用户")
async def set_user_status(
    user_id: int, req: AdminUserStatusReq, admin: User = Depends(get_current_admin)
) -> object:
    if user_id == admin.id:
        raise HttpBusinessException(HttpErrorCodeEnum.PARAM_INVALID, "不能操作自己的账号")
    user = await User.get_or_none(id=user_id)
    if user is None:
        raise HttpBusinessException(HttpErrorCodeEnum.NOT_FOUND, "用户不存在")
    user.status = req.status
    await user.save()
    return ResponseHelper.success(
        AdminUserRes(
            id=user.id, username=user.username, nickname=user.nickname, avatar=user.avatar,
            phone=user.phone, student_no=user.student_no, credit_score=user.credit_score,
            role=user.role, status=user.status, created_at=user.created_at,
        ),
        message="已禁用" if req.status == 0 else "已启用",
    )


@admin_router.put("/users/{user_id}/credit", response_model=BaseResponse[AdminUserRes], summary="调整信用分")
async def set_user_credit(
    user_id: int, req: AdminUserCreditReq, _: User = Depends(get_current_admin)
) -> object:
    user = await User.get_or_none(id=user_id)
    if user is None:
        raise HttpBusinessException(HttpErrorCodeEnum.NOT_FOUND, "用户不存在")
    user.credit_score = req.credit_score
    await user.save()
    return ResponseHelper.success(
        AdminUserRes(
            id=user.id, username=user.username, nickname=user.nickname, avatar=user.avatar,
            phone=user.phone, student_no=user.student_no, credit_score=user.credit_score,
            role=user.role, status=user.status, created_at=user.created_at,
        ),
        message="信用分已更新",
    )


# ---------- 分类管理 ----------
@admin_router.get("/categories", response_model=BaseResponse[list[AdminCategoryRes]], summary="分类列表(含商品数)")
async def categories(_: User = Depends(get_current_admin)) -> object:
    cats = await Category.all().order_by("sort", "id")
    data = []
    for c in cats:
        count = await Product.filter(category_id=c.id).count()
        data.append(AdminCategoryRes(id=c.id, name=c.name, icon=c.icon, sort=c.sort, goods_count=count))
    return ResponseHelper.success(data)


@admin_router.post("/categories", response_model=BaseResponse[AdminCategoryRes], summary="新增分类")
async def create_category(req: AdminCategoryReq, _: User = Depends(get_current_admin)) -> object:
    if await Category.get_or_none(name=req.name):
        raise HttpBusinessException(HttpErrorCodeEnum.PARAM_INVALID, "分类名已存在")
    c = await Category.create(name=req.name, icon=req.icon, sort=req.sort)
    return ResponseHelper.success(
        AdminCategoryRes(id=c.id, name=c.name, icon=c.icon, sort=c.sort, goods_count=0), message="已新增"
    )


@admin_router.put("/categories/{category_id}", response_model=BaseResponse[AdminCategoryRes], summary="编辑分类")
async def update_category(
    category_id: int, req: AdminCategoryReq, _: User = Depends(get_current_admin)
) -> object:
    c = await Category.get_or_none(id=category_id)
    if c is None:
        raise HttpBusinessException(HttpErrorCodeEnum.NOT_FOUND, "分类不存在")
    c.name, c.icon, c.sort = req.name, req.icon, req.sort
    await c.save()
    count = await Product.filter(category_id=c.id).count()
    return ResponseHelper.success(
        AdminCategoryRes(id=c.id, name=c.name, icon=c.icon, sort=c.sort, goods_count=count), message="已保存"
    )


@admin_router.delete("/categories/{category_id}", summary="删除分类")
async def delete_category(category_id: int, _: User = Depends(get_current_admin)) -> object:
    c = await Category.get_or_none(id=category_id)
    if c is None:
        raise HttpBusinessException(HttpErrorCodeEnum.NOT_FOUND, "分类不存在")
    used = await Product.filter(category_id=category_id).count()
    if used > 0:
        raise HttpBusinessException(HttpErrorCodeEnum.PARAM_INVALID, f"该分类下还有 {used} 件商品，不能删除")
    await c.delete()
    return ResponseHelper.success(message="已删除")


# ---------- 举报处理 ----------
@admin_router.get("/reports", response_model=BaseResponse[PageResult[ReportRes]], summary="举报列表")
async def reports(
    status: int | None = None,
    page: int = 1,
    page_size: int = 20,
    _: User = Depends(get_current_admin),
) -> object:
    qs = Report.all().prefetch_related("reporter", "product__seller")
    if status is not None:
        qs = qs.filter(status=status)
    total = await qs.count()
    items = await qs.order_by("-id").offset((page - 1) * page_size).limit(page_size)
    return ResponseHelper.success(
        PageResult[ReportRes](
            list=[ReportRes(**report_to_res(r)) for r in items],
            total=total, page=page, page_size=page_size,
        )
    )


@admin_router.put("/reports/{report_id}", response_model=BaseResponse[ReportRes], summary="处理举报")
async def handle_report(
    report_id: int, req: AdminReportHandleReq, admin: User = Depends(get_current_admin)
) -> object:
    report = await Report.get_or_none(id=report_id).prefetch_related("reporter", "product")
    if report is None:
        raise HttpBusinessException(HttpErrorCodeEnum.NOT_FOUND, "举报不存在")
    report.status = req.status
    report.handler_result = req.handler_result
    await report.save()

    product = await Product.get_or_none(id=report.product_id)
    if product is not None:
        # 举报成立：联动下架商品（若仍在售）
        if req.status == 2 and product.status == 1:
            product.status = 3
            await product.save()
        # 发送系统通知（成立→通知举报者与被举报者；驳回→仅通知举报者）
        await notify_report_handled(admin, report, product)

    return ResponseHelper.success(ReportRes(**report_to_res(report)), message="处理完成")


# ---------- 商品管理（全站，含所有状态） ----------
@admin_router.get("/goods", response_model=BaseResponse[PageResult[GoodsItemRes]], summary="全站商品列表")
async def admin_goods(
    keyword: str = "",
    status: int | None = None,
    page: int = 1,
    page_size: int = 20,
    _: User = Depends(get_current_admin),
) -> object:
    qs = Product.all().prefetch_related("category", "seller")
    if keyword:
        qs = qs.filter(title__icontains=keyword)
    if status is not None:
        qs = qs.filter(status=status)
    total = await qs.count()
    items = await qs.order_by("-id").offset((page - 1) * page_size).limit(page_size)
    return ResponseHelper.success(
        PageResult[GoodsItemRes](
            list=[GoodsItemRes(**goods_to_item_res(p)) for p in items],
            total=total, page=page, page_size=page_size,
        )
    )


@admin_router.put("/goods/{product_id}/status", response_model=BaseResponse[GoodsItemRes], summary="管理员上/下架商品")
async def admin_set_goods_status(
    product_id: int, req: AdminGoodsStatusReq, admin: User = Depends(get_current_admin)
) -> object:
    product = await goods_update_goods(product_id, admin, {"status": req.status})
    product = await Product.get_or_none(id=product_id).prefetch_related("category", "seller")
    return ResponseHelper.success(
        GoodsItemRes(**goods_to_item_res(product)),
        message="已下架" if req.status == 3 else "已上架",
    )


# ---------- 订单管理（全站） ----------
@admin_router.get("/orders", response_model=BaseResponse[PageResult[OrderRes]], summary="全站订单列表")
async def admin_orders(
    status: int | None = None,
    page: int = 1,
    page_size: int = 20,
    _: User = Depends(get_current_admin),
) -> object:
    qs = Order.all().prefetch_related("product", "buyer", "seller")
    if status is not None:
        qs = qs.filter(status=status)
    total = await qs.count()
    items = await qs.order_by("-id").offset((page - 1) * page_size).limit(page_size)
    return ResponseHelper.success(
        PageResult[OrderRes](
            list=[OrderRes(**order_to_res(o)) for o in items],
            total=total, page=page, page_size=page_size,
        )
    )
