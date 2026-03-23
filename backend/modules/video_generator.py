# -*- coding: utf-8 -*-
"""
视频生成统一入口。

说明：
- 具体 API 调用逻辑由不同 Provider 类负责；
- 本文件只负责根据 provider 做分发，保持对外函数签名兼容。
"""

from typing import Any, Dict, Optional

from modules.video_providers import create_video_provider, resolve_video_provider
from modules.video_providers.common import safe_text


def generate_video(
    start_frame,
    end_frame=None,
    mode="keyframe-interpolation",
    context=None,
    llm_config=None,
    provider: Optional[str] = None,
):
    context = context if isinstance(context, dict) else {}
    config = llm_config or {}
    normalized_start_frame = start_frame if isinstance(start_frame, dict) else {}
    normalized_end_frame = end_frame if isinstance(end_frame, dict) else None

    # provider 解析优先级：显式参数 > context > llm_config > 默认值
    resolved_provider = resolve_video_provider(provider, context, config)
    client = create_video_provider(resolved_provider, llm_config=config)
    print(f"Using video provider: {client}")
    return client.generate(
        start_frame=normalized_start_frame,
        end_frame=normalized_end_frame,
        mode=mode,
        context=context,
    )


def query_video_task(
    task_id: str,
    llm_config=None,
    provider: Optional[str] = None,
    provider_options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    normalized_task_id = safe_text(task_id)
    if not normalized_task_id:
        return {"status": "error", "error": "task_id is required"}

    config = llm_config or {}
    options = provider_options if isinstance(provider_options, dict) else {}

    # 查询时可通过 provider_options 传入 provider 相关附加参数（例如 req_key）
    resolved_provider = resolve_video_provider(provider, options, config)
    client = create_video_provider(resolved_provider, llm_config=config)
    return client.query_task(task_id=normalized_task_id, provider_options=options)
