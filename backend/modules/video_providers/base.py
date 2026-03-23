# -*- coding: utf-8 -*-
"""
视频 Provider 抽象基类。
后续新增模型时，只需要继承该类并实现 generate/query_task。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseVideoProvider(ABC):
    provider_name = "base"

    def __init__(self, llm_config: Optional[Dict[str, Any]] = None):
        self.llm_config = llm_config or {}

    @abstractmethod
    def generate(
        self,
        start_frame: Optional[Dict[str, Any]],
        end_frame: Optional[Dict[str, Any]] = None,
        mode: str = "keyframe-interpolation",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def query_task(self, task_id: str, provider_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        raise NotImplementedError
