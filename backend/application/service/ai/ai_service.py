"""AI 服务：文案生成 / 智能估价 / 议价话术。

每个能力都优先调用 LLM，未配置 Key 或调用失败时降级为本地规则策略，
保证演示与答辩时功能始终可用。
"""
import logging

from application.core import llm_client

logger = logging.getLogger(__name__)

# 品类贬值曲线：每年贬值比例（原创规则模型）
_CATEGORY_DEPRECIATION: dict[str, float] = {
    "数码电子": 0.25,
    "手机平板": 0.28,
    "电脑配件": 0.24,
    "图书教材": 0.10,
    "服饰鞋包": 0.20,
    "生活家居": 0.15,
    "运动户外": 0.16,
    "美妆护肤": 0.22,
    "乐器": 0.12,
    "其他": 0.15,
}

# 成色系数
_CONDITION_FACTOR: dict[int, float] = {5: 0.95, 4: 0.85, 3: 0.70, 2: 0.50, 1: 0.30}


async def generate_copy(title_keywords: str, category_name: str, condition_level: int,
                        original_price: float) -> dict:
    """AI 帮写商品文案：返回 {title, description}。"""
    condition_text = {5: "全新", 4: "几乎全新", 3: "明显使用痕迹", 2: "成色一般", 1: "成色较差"}.get(
        condition_level, "成色一般"
    )
    if llm_client.has_llm():
        try:
            system = "你是校园二手交易平台的文案助手，擅长写出吸引学生买家的真实、简洁商品文案。"
            user = (
                f"请根据以下信息生成二手商品文案：\n关键词：{title_keywords}\n品类：{category_name}\n"
                f"成色：{condition_text}\n原价：{original_price}元\n"
                "输出格式：第一行是标题（不超过30字），空一行后是描述（80-150字，口语化、突出卖点和成色，可适当加emoji）。"
            )
            text = await llm_client.chat(system, user)
            parts = text.split("\n", 1)
            title = parts[0].strip().lstrip("标题：").strip()
            desc = parts[1].strip().lstrip("描述：").strip() if len(parts) > 1 else text
            return {"title": title, "description": desc, "source": "llm"}
        except Exception as exc:  # noqa: BLE001
            logger.warning("LLM 文案生成失败，降级本地策略: %s", exc)
    # 降级：模板拼接
    title = f"{condition_text}{title_keywords}"[:30]
    desc = (
        f"毕业/换新高性价比出 {title_keywords}，{condition_text}，"
        f"原价 {original_price:.0f} 元，现诚意转让。功能完好，实物如图，"
        f"支持当面交易/验货，价格可小刀，喜欢的同学欢迎私聊～"
    )
    return {"title": title, "description": desc, "source": "local"}


async def estimate_price(category_name: str, original_price: float, condition_level: int,
                         used_years: float) -> dict:
    """智能估价：规则模型给基础价与区间，LLM 可结合描述微调。"""
    depreciation = _CATEGORY_DEPRECIATION.get(category_name, 0.15)
    condition_factor = _CONDITION_FACTOR.get(condition_level, 0.7)
    # 基础价 = 原价 * 成色系数 * (1 - 年贬值率)^年限
    base = original_price * condition_factor * max(0.0, (1 - depreciation) ** max(0.0, used_years))
    base = max(1.0, round(base, 2))
    low = round(base * 0.85, 2)
    high = round(base * 1.15, 2)

    result = {
        "suggested_price": base,
        "price_low": low,
        "price_high": high,
        "source": "local",
        "reason": f"原价{original_price:.0f}元，成色系数{condition_factor}，"
                  f"按{category_name}年贬值{int(depreciation * 100)}%、使用{used_years}年折算",
    }

    if llm_client.has_llm():
        try:
            system = "你是二手交易估价师，给出合理的人民币建议售价，只输出一个数字。"
            user = (
                f"品类：{category_name}，原价：{original_price}元，成色等级(1-5)：{condition_level}，"
                f"使用年限：{used_years}年。规则模型给出的参考价为{base}元，"
                f"请结合市场行情给出你认为更合理的建议售价，只输出数字。"
            )
            text = await llm_client.chat(system, user, temperature=0.3)
            llm_price = float("".join(ch for ch in text if ch.isdigit() or ch == ".") or base)
            llm_price = max(1.0, round(llm_price, 2))
            # LLM 与规则取折中，避免偏差过大
            final = round((base + llm_price) / 2, 2)
            result.update({
                "suggested_price": final,
                "price_low": round(final * 0.85, 2),
                "price_high": round(final * 1.15, 2),
                "source": "llm",
                "reason": f"规则模型{base}元，AI参考{llm_price}元，综合建议{final}元",
            })
        except Exception as exc:  # noqa: BLE001
            logger.warning("LLM 估价失败，使用规则模型: %s", exc)
    return result


# 议价话术降级模板库
_BARGAIN_FALLBACK = [
    "同学好，这个价格还能再优惠一点吗？诚心要～",
    "看成色还不错，方便的话便宜 {delta} 元我现在就拍？",
    "预算有限，{price} 元可以出吗？可以的话马上下单。",
    "能小刀吗？我们同校可以当面交易，省你邮费。",
]


async def bargain_assist(product_title: str, sell_price: float, buyer_offer: float,
                         buyer_message: str, round_no: int, side: str) -> dict:
    """AI 议价助手：给出一方（默认卖家）的回复建议与建议价。"""
    if llm_client.has_llm():
        try:
            system = (
                f"你是校园二手交易中的{('卖家' if side == 'seller' else '买家')}议价助手，"
                "语气友好、接地气，目标是促成交易同时不吃亏。"
            )
            user = (
                f"商品：{product_title}，标价：{sell_price}元。\n"
                f"对方第{round_no}轮出价：{buyer_offer}元，留言：{buyer_message or '（无）'}。\n"
                "请给出：1) 一句回复话术（不超过60字）；2) 一个建议的成交价（数字）。"
                "输出两行，第一行话术，第二行只写数字。"
            )
            text = await llm_client.chat(system, user, temperature=0.7)
            lines = [line for line in text.split("\n") if line.strip()]
            reply = lines[0].strip() if lines else text[:60]
            counter = None
            if len(lines) > 1:
                digits = "".join(ch for ch in lines[1] if ch.isdigit() or ch == ".")
                counter = float(digits) if digits else None
            return {"reply": reply, "counter_price": counter, "source": "llm"}
        except Exception as exc:  # noqa: BLE001
            logger.warning("LLM 议价失败，降级模板: %s", exc)
    # 降级：简单策略，给买家与卖家中间价的还价建议
    gap = sell_price - buyer_offer
    counter = round(buyer_offer + gap * 0.5, 2) if side == "seller" else round(buyer_offer + gap * 0.3, 2)
    counter = max(1.0, counter)
    if side == "seller":
        reply = f"同学，{buyer_offer} 有点低啦，最低 {counter} 元给你吧，诚心要就出这个价～"
    else:
        reply = f"老板，{counter} 元我现在就下单，可以的话成交？"
    return {"reply": reply, "counter_price": counter, "source": "local"}
