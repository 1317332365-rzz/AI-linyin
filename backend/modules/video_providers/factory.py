# -*- coding: utf-8 -*-
"""
视频 Provider 工厂：
- 负责解析 provider 名称
- 负责实例化具体 API 调用类
"""

from typing import Any, Dict, Optional, Type

from .base import BaseVideoProvider
from .common import normalize_provider, resolve_provider
from .grsai_provider import GrsAIVideoProvider
from .jimeng_provider import JiMengVideoProvider
from .openai_provider import OpenAICompatibleVideoProvider


PROVIDER_MAP: Dict[str, Type[BaseVideoProvider]] = {
    "openai": OpenAICompatibleVideoProvider,
    "jimeng": JiMengVideoProvider,
    "grsai": GrsAIVideoProvider,
}


def create_video_provider(provider_name: str, llm_config: Optional[Dict[str, Any]] = None) -> BaseVideoProvider:
    normalized = normalize_provider(provider_name)
    provider_cls = PROVIDER_MAP.get(normalized, OpenAICompatibleVideoProvider)
    return provider_cls(llm_config=llm_config or {})


def resolve_video_provider(explicit_provider: Any, context: Optional[Dict[str, Any]], llm_config: Optional[Dict[str, Any]]) -> str:
    return resolve_provider(explicit_provider, context, llm_config)
