"""举报域共享常量：违规类型、处理结论、通知与理由模板。

前后端约定一致的违规类型编码（reason_type），
用于举报提交时的类型选择、后台处理时的理由模板与系统通知文案。
"""
from __future__ import annotations

# 举报状态
REPORT_STATUS_PENDING = 1  # 待处理
REPORT_STATUS_APPROVED = 2  # 已处理（举报成立）
REPORT_STATUS_REJECTED = 3  # 已驳回（举报不成立）

# 违规类型：code -> 名称（与前端举报类型选项一一对应）
REPORT_REASON_TYPES: dict[str, str] = {
    "counterfeit": "假冒/盗版商品",
    "false_info": "虚假信息/描述不符",
    "prohibited": "违禁/违规物品",
    "fraud": "涉嫌诈骗/诱导线下交易",
    "price_abuse": "价格异常/恶意抬价",
    "spam": "垃圾广告/重复刷屏",
    "other": "其他违规",
}

# 处理为“举报成立”时，按违规类型给出的处理理由模板（管理员可再编辑）
APPROVE_REASON_TEMPLATES: dict[str, str] = {
    "counterfeit": "经核实，该商品为假冒/盗版物品，违反平台规定，已予以下架处理。",
    "false_info": "经核实，该商品描述与实物严重不符，存在误导，已予以下架处理。",
    "prohibited": "经核实，该商品属于平台禁售的违禁/违规物品，已予以下架处理。",
    "fraud": "经核实，该商品涉嫌诈骗或诱导线下交易，存在安全风险，已予以下架处理。",
    "price_abuse": "经核实，该商品价格异常、涉嫌恶意抬价，扰乱交易秩序，已予以下架处理。",
    "spam": "经核实，该商品为垃圾广告/恶意刷屏，已予以下架处理。",
    "other": "经核实，该商品存在违规行为，违反平台规定，已予以下架处理。",
}

# 处理为“举报不成立（驳回）”时的默认理由模板
REJECT_REASON_TEMPLATE = "经核实，暂未发现该商品存在违规行为，举报不成立，商品保持正常在售。"


def reason_type_name(code: str) -> str:
    return REPORT_REASON_TYPES.get(code, "其他违规")


def approve_template(code: str) -> str:
    return APPROVE_REASON_TEMPLATES.get(code, APPROVE_REASON_TEMPLATES["other"])
