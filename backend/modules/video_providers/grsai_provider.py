# -*- coding: utf-8 -*-
"""
GRSAI video provider.

Submit API:
- auth: Bearer
- body: JSON

Query API:
- POST /v1/draw/result
- body: {"id": "<task_id>"}
"""

import os
from typing import Any, Dict, Optional
from urllib.parse import urlparse, urlunparse

import requests

from .base import BaseVideoProvider
from .common import extract_progress, extract_task_id, extract_video_url, safe_text, validate_start_image_url


DEFAULT_QUERY_PATH = "/v1/draw/result"


def _pick_api_key(config: Dict[str, Any], context: Dict[str, Any]) -> str:
    return (
        safe_text(context.get("grsai_api_key"))
        or safe_text(context.get("api_key"))
        or safe_text(config.get("api_key"))
        or safe_text(os.getenv("GRSAI_API_KEY"))
    )


def _pick_submit_url(config: Dict[str, Any], context: Dict[str, Any]) -> str:
    return (
        safe_text(context.get("grsai_base_url"))
        or safe_text(context.get("base_url"))
        or safe_text(config.get("base_url"))
        or safe_text(os.getenv("GRSAI_BASE_URL"))
    )


def _derive_query_url(source_url: str) -> str:
    parsed = urlparse(safe_text(source_url))
    if not parsed.scheme or not parsed.netloc:
        return ""
    return urlunparse((parsed.scheme, parsed.netloc, DEFAULT_QUERY_PATH, "", "", ""))


def _pick_query_url(config: Dict[str, Any], provider_options: Dict[str, Any], submit_url: str = "") -> str:
    explicit = (
        safe_text(provider_options.get("query_url"))
        or safe_text(provider_options.get("status_url"))
        or safe_text(config.get("query_url"))
        or safe_text(os.getenv("GRSAI_QUERY_URL"))
    )
    if explicit:
        return explicit

    fallback_source = submit_url or safe_text(config.get("base_url")) or safe_text(os.getenv("GRSAI_BASE_URL"))
    return _derive_query_url(fallback_source)


def _pick_query_method(config: Dict[str, Any], provider_options: Dict[str, Any]) -> str:
    return (
        safe_text(provider_options.get("query_method"))
        or safe_text(config.get("query_method"))
        or safe_text(os.getenv("GRSAI_QUERY_METHOD"))
        or "POST"
    ).upper()


def _extract_query_url(payload: Dict[str, Any]) -> str:
    if not isinstance(payload, dict):
        return ""

    keys = ("query_url", "queryUrl", "status_url", "statusUrl", "task_url", "taskUrl")
    for key in keys:
        value = safe_text(payload.get(key))
        if value:
            return value

    data = payload.get("data")
    if isinstance(data, dict):
        for key in keys:
            value = safe_text(data.get(key))
            if value:
                return value
    return ""


def _extract_business_code(payload: Dict[str, Any]) -> Optional[int]:
    if not isinstance(payload, dict):
        return None
    try:
        value = payload.get("code")
        if value in (None, ""):
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _extract_message(payload: Dict[str, Any]) -> str:
    if not isinstance(payload, dict):
        return ""

    for key in ("msg", "message"):
        value = safe_text(payload.get(key))
        if value:
            return value

    error_obj = payload.get("error")
    if isinstance(error_obj, dict):
        value = safe_text(error_obj.get("message"))
        if value:
            return value
    if isinstance(error_obj, str) and error_obj.strip():
        return error_obj.strip()

    data = payload.get("data")
    if isinstance(data, dict):
        for key in ("failure_reason", "error", "message"):
            value = safe_text(data.get(key))
            if value:
                return value

    return ""


def _map_aspect_ratio(value: Any) -> str:
    ratio = safe_text(value) or "16:9"
    if ratio == "adaptive":
        return "16:9"
    if ratio in {"16:9", "9:16", "1:1", "4:3", "3:4"}:
        return ratio
    return "16:9"


def _normalize_status(raw_status: Any, has_video: bool = False) -> str:
    status = safe_text(raw_status).lower()
    if not status:
        return "succeeded" if has_video else "processing"
    if status in {"success", "succeeded", "done", "finished", "complete", "completed"}:
        return "succeeded"
    if status in {"failed", "error", "cancelled", "canceled", "timeout", "not_found"}:
        return "failed"
    if status in {"submitted", "pending", "queued", "running", "processing", "generating", "in_progress"}:
        return "processing"
    return "succeeded" if has_video else "processing"


def _extract_result_url(data: Dict[str, Any]) -> str:
    if not isinstance(data, dict):
        return ""

    results = data.get("results")
    if isinstance(results, list):
        for item in results:
            if isinstance(item, dict):
                value = safe_text(item.get("url"))
                if value:
                    return value
    return extract_video_url(data)


class GrsAIVideoProvider(BaseVideoProvider):
    provider_name = "grsai"

    def generate(
        self,
        start_frame: Optional[Dict[str, Any]],
        end_frame: Optional[Dict[str, Any]] = None,
        mode: str = "keyframe-interpolation",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        context = context or {}
        config = self.llm_config or {}

        api_key = _pick_api_key(config, context)
        if not api_key:
            return {"status": "error", "error": "grsai api_key is required"}
        print(f"Using grsai api_key: {api_key[:4]}***{api_key[-4:]}")
        submit_url = _pick_submit_url(config, context)
        if not submit_url:
            return {"status": "error", "error": "grsai base_url is required"}

        ok, error_msg, start_image_url = validate_start_image_url(start_frame)
        if not ok:
            return {"status": "error", "error": error_msg}

        end_image_url = safe_text((end_frame or {}).get("image_url"))
        model = safe_text(context.get("grsai_model") or context.get("model") or config.get("model")) or "veo3.1-fast"
        prompt = (
            safe_text(context.get("prompt"))
            or safe_text((start_frame or {}).get("enhanced_prompt"))
            or safe_text((start_frame or {}).get("description"))
            or "东方动漫风电影镜头，主体清晰，动作自然，运镜流畅，保持当前片段内动作连续与人物关系稳定。"
        )

        raw_urls = "https://grsai.dakka.com.cn/v1/video/sora-video"
        urls = raw_urls if isinstance(raw_urls, list) else []
        payload = {
            "model": model,
            "prompt": prompt,
            "urls": urls[0],
            "aspectRatio": _map_aspect_ratio(context.get("ratio") or context.get("aspectRatio")),
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        try:
            response = requests.post(submit_url, headers=headers, json=payload, timeout=90)
        except Exception as exc:
            return {"status": "error", "error": f"request failed: {exc}"}
        print(response.json())
        try:
            response_payload = response.json()
            
        except ValueError:
            response_payload = {"raw": response.text}

        if response.status_code >= 400:
            message = _extract_message(response_payload) or "unknown error"
            return {
                "status": "error",
                "error": f"grsai api error {response.status_code} | {message}",
                "details": response_payload,
            }

        business_code = _extract_business_code(response_payload)
        if business_code not in (None, 0):
            message = _extract_message(response_payload) or "unknown error"
            return {
                "status": "error",
                "error": f"grsai api error code={business_code} | {message}",
                "details": response_payload,
            }

        data = response_payload.get("data") if isinstance(response_payload.get("data"), dict) else {}
        task_id = (
            extract_task_id(response_payload)
            or safe_text(response_payload.get("taskId"))
            or safe_text(response_payload.get("recordId"))
            or safe_text(data.get("taskId"))
            or safe_text(data.get("recordId"))
        )
        video_url = _extract_result_url(data) or extract_video_url(response_payload)
        query_url = _extract_query_url(response_payload) or _pick_query_url(config, {}, submit_url)
        progress = extract_progress(data) or extract_progress(response_payload)
        status = _normalize_status(data.get("status") or response_payload.get("status"), has_video=bool(video_url))
        if progress is None:
            progress = 100 if status == "succeeded" else 8

        message = _extract_message(response_payload) or ("grsai 视频已生成" if video_url else "grsai 视频任务已提交")
        query_method = _pick_query_method(config, {})

        return {
            "status": status,
            "message": message,
            "mode": mode,
            "task_id": task_id,
            "video_url": video_url,
            "progress": progress,
            "provider": self.provider_name,
            "query_url": query_url,
            "query_method": query_method,
            "raw_response": response_payload,
        }

    def query_task(self, task_id: str, provider_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        provider_options = provider_options or {}
        config = self.llm_config or {}
        normalized_task_id = safe_text(task_id)
        if not normalized_task_id:
            return {"status": "error", "error": "task_id is required"}

        api_key = _pick_api_key(config, provider_options)
        if not api_key:
            return {"status": "error", "error": "grsai api_key is required"}

        submit_url = _pick_submit_url(config, provider_options)
        query_url = "https://grsai.dakka.com.cn/v1/draw/result"

        payload={
            "id": normalized_task_id
        }
        # if not query_url:
        #     return {
        #         "status": "failed",
        #         "task_id": normalized_task_id,
        #         "message": "grsai query_url is not configured",
        #         "provider": self.provider_name,
        #         "progress": 0,
        #     }

        # method = _pick_query_method(config, provider_options)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        try:
           response = requests.post(query_url, headers=headers, json={"id": normalized_task_id}, timeout=45)
        except Exception as exc:
            return {"status": "error", "error": f"request failed: {exc}"}

        try:
            response_payload = response.json()
        except ValueError:
            response_payload = {"raw": response.text}

        if response.status_code >= 400:
            message = _extract_message(response_payload) or "unknown error"
            return {
                "status": "failed",
                "task_id": normalized_task_id,
                "message": f"grsai query http {response.status_code} | {message}",
                "provider": self.provider_name,
                "details": response_payload,
                "progress": 0,
                "query_url": query_url,
            }

        business_code = _extract_business_code(response_payload)
        data = response_payload.get("data") if isinstance(response_payload.get("data"), dict) else {}
        video_url = _extract_result_url(data)
        status = _normalize_status(data.get("status"), has_video=bool(video_url))
        progress = extract_progress(data) or extract_progress(response_payload)

        message = _extract_message(response_payload)
        failure_reason = safe_text(data.get("failure_reason") or data.get("error"))
        if business_code == -22:
            status = "failed"
            message = message or "任务不存在"
        elif business_code not in (None, 0):
            status = "failed"
            message = message or failure_reason or f"code={business_code}"
        elif status == "failed":
            message = message or failure_reason or "视频生成失败"
        elif status == "succeeded":
            message = message or "视频生成完成"
        else:
            message = message or "视频任务处理中"

        if progress is None:
            progress = 100 if status == "succeeded" else (0 if status == "failed" else 15)

        result: Dict[str, Any] = {
            "status": status,
            "task_id": normalized_task_id,
            "video_url": video_url,
            "progress": progress,
            "message": message,
            "provider": self.provider_name,
            "query_url": query_url,
            "query_method": method,
            "raw_response": response_payload,
        }

        if business_code is not None:
            result["api_code"] = business_code
        if failure_reason:
            result["failure_reason"] = failure_reason
        if business_code not in (None, 0):
            result["details"] = response_payload

        return result
