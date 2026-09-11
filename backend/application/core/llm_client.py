"""LLM 客户端：按脚手架"扩展基础设施"模式实现。

- 配置了 api_key 时，通过 OpenAI 兼容接口调用真实大模型；
- 未配置时 has_llm() 返回 False，上层自动降级为本地规则策略。
"""
import logging

import httpx

from application.common.config import config

logger = logging.getLogger(__name__)


def has_llm() -> bool:
    return bool(config.llm.enabled and config.llm.api_key)


async def chat(system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
    """调用 OpenAI 兼容的 chat completions 接口，返回文本内容。"""
    if not has_llm():
        raise RuntimeError("LLM 未配置 api_key")
    url = f"{config.llm.api_base.rstrip('/')}/chat/completions"
    headers = {"Authorization": f"Bearer {config.llm.api_key}", "Content-Type": "application/json"}
    payload = {
        "model": config.llm.model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
    }
    async with httpx.AsyncClient(timeout=config.llm.timeout_seconds) as client:
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
