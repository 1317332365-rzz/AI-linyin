# -*- coding: utf-8 -*-
"""
OpenAI-compatible video provider (mainly Ark /contents/generations/tasks).
"""

from typing import Any, Dict, Optional

import requests

from .base import BaseVideoProvider
from .common import (
    build_duration_candidates,
    build_text_prompt,
    extract_progress,
    extract_task_id,
    extract_video_url,
    is_invalid_duration_response,
    normalize_ark_base_url,
    normalize_duration_for_model,
    normalize_task_status,
    parse_duration_seconds,
    pick_ark_api_key,
    pick_video_model,
    safe_text,
    validate_start_image_url,
)


class doubaoAICompatibleVideoProvider(BaseVideoProvider):
    provider_name = "openai"

    @staticmethod
    def _extract_api_message(payload: Dict[str, Any]) -> str:
        if not isinstance(payload, dict):
            return ""
        error_obj = payload.get("error")
        if isinstance(error_obj, dict):
            message = safe_text(error_obj.get("message"))
            if message:
                return message
        return safe_text(payload.get("message"))

    @staticmethod
    def _extract_request_id(payload: Dict[str, Any]) -> str:
        if not isinstance(payload, dict):
            return ""
        return (
            safe_text(payload.get("request_id"))
            or safe_text(payload.get("requestId"))
            or safe_text(payload.get("RequestId"))
        )

    def generate(
        self,
        start_frame: Optional[Dict[str, Any]],
        end_frame: Optional[Dict[str, Any]] = None,
        mode: str = "keyframe-interpolation",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        context = context or {}
        config = self.llm_config or {}

        api_key = pick_ark_api_key(config)
        if not api_key:
            return {"status": "error", "error": "video api_key is required"}

        model = pick_video_model(config)
        # base_url = normalize_ark_base_url(config.get("base_url"))

        endpoint = f"https://api.vectorengine.ai/v1/video/create"

        ok, error_msg, start_image_url = validate_start_image_url(start_frame)
        if not ok:
            return {"status": "error", "error": error_msg}

        end_image_url = safe_text((end_frame or {}).get("image_url"))
        text_prompt = build_text_prompt(start_frame or {}, context)

        content = [{"type": "text", "text": text_prompt}]
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": start_image_url},
                "role": "first_frame",
            }
        )
        if end_image_url:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": end_image_url},
                    "role": "last_frame",
                }
            )

        requested_duration_raw = parse_duration_seconds(
            context.get("shot_duration") or context.get("duration"),
            fallback=5,
        )
        # 即刻约束：所有分镜时长上限 12s（兼容 flf2v 模型）。
        requested_duration = max(1, min(12, requested_duration_raw))

        duration_seconds = normalize_duration_for_model(
            model=model,
            mode=mode,
            duration_seconds=requested_duration,
            has_end_frame=bool(end_image_url),
        )
        duration_seconds = max(1, min(12, int(duration_seconds)))

        duration_candidates = build_duration_candidates(
            model=model,
            mode=mode,
            requested_duration=duration_seconds,
            has_end_frame=bool(end_image_url),
        )
        # 兜底候选，确保 duration 报错时可自动降级。
        for value in [12, 10, 8, 6, 5, 4, 3, 2, 1]:
            if value <= duration_seconds and value not in duration_candidates:
                duration_candidates.append(value)

        headers = {
            'Accept': 'application/json',
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        print(headers)

        response = None
        response_payload: Dict[str, Any] = {}
        applied_duration = duration_seconds
        last_error_payload: Dict[str, Any] = {}

        for candidate in duration_candidates:
            generate_audio = bool(context.get("generate_audio", True))
            # 用户侧要求默认有音频：当存在对白细节时强制开启音频。
            if safe_text(context.get("dialogue_details")) or safe_text(context.get("detailed_plot")):
                generate_audio = True
            payload = {
                "model": model,
                "prompt": content,
                "enhance_prompt": True,
                "enable_upsample": True,
                "aspect_ratio": "16:9",
                # "watermark": bool(context.get("watermark", False)),
            }
            print(endpoint)
            try:
                response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
            except Exception as e:
                return {"status": "error", "error": f"request failed: {e}"}

            try:
                response_payload = response.json()
            except ValueError:
                response_payload = {"raw": response.text}

            if response.status_code < 400:
                applied_duration = candidate
                break

            last_error_payload = response_payload
            if (response.status_code == 400) and is_invalid_duration_response(response_payload):
                continue

            detail_message = self._extract_api_message(response_payload)
            request_id = self._extract_request_id(response_payload)
            suffix = f" | {detail_message}" if detail_message else ""
            req_text = f" | Request id: {request_id}" if request_id else ""
            return {
                "status": "error",
                "error": f"ark api error {response.status_code}{suffix}{req_text}",
                "details": response_payload,
                "request_id": request_id,
            }

        if response is None or response.status_code >= 400:
            detail_message = self._extract_api_message(last_error_payload or response_payload)
            request_id = self._extract_request_id(last_error_payload or response_payload)
            status_code = response.status_code if response is not None else "unknown"
            suffix = f" | {detail_message}" if detail_message else ""
            req_text = f" | Request id: {request_id}" if request_id else ""
            return {
                "status": "error",
                "error": f"ark api error {status_code}{suffix}{req_text}",
                "details": last_error_payload or response_payload,
                "request_id": request_id,
            }

        task_id = extract_task_id(response_payload)
        video_url = extract_video_url(response_payload)
        status = normalize_task_status(response_payload)
        progress = extract_progress(response_payload)
        if progress is None:
            if status == "succeeded":
                progress = 100
            elif status in ("submitted", "processing", "unknown"):
                progress = 10

        message = "视频任务已提交，若未返回视频地址请稍后查询任务状态。"
        if applied_duration != requested_duration_raw:
            message = (
                f"视频任务已提交（请求时长 {requested_duration_raw}s，"
                f"模型兼容后使用 {applied_duration}s），若未返回视频地址请稍后查询任务状态。"
            )

        normalized_status = status if status != "unknown" else "submitted"
        if not task_id and video_url and normalized_status == "submitted":
            normalized_status = "succeeded"

        return {
            "status": normalized_status,
            "message": message,
            "mode": mode,
            "task_id": task_id,
            "video_url": video_url,
            "progress": progress,
            "duration_requested": requested_duration_raw,
            "duration_applied": applied_duration,
            "provider": self.provider_name,
            "raw_response": response_payload,
        }

    def query_task(self, task_id: str, provider_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        task_id = safe_text(task_id)
        if not task_id:
            return {"status": "error", "error": "task_id is required"}

        config = self.llm_config or {}
        api_key = pick_ark_api_key(config)
        if not api_key:
            return {"status": "error", "error": "video api_key is required"}

        base_url = normalize_ark_base_url(config.get("base_url"))
        endpoint = f"{base_url}/contents/generations/tasks/{task_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        try:
            response = requests.get(endpoint, headers=headers, timeout=30)
        except Exception as e:
            return {"status": "error", "error": f"request failed: {e}"}

        try:
            response_payload = response.json()
        except ValueError:
            response_payload = {"raw": response.text}

        if response.status_code >= 400:
            detail_message = self._extract_api_message(response_payload)
            request_id = self._extract_request_id(response_payload)
            suffix = f" | {detail_message}" if detail_message else ""
            req_text = f" | Request id: {request_id}" if request_id else ""
            return {
                "status": "error",
                "error": f"ark api error {response.status_code}{suffix}{req_text}",
                "details": response_payload,
                "request_id": request_id,
            }

        status = normalize_task_status(response_payload)
        video_url = extract_video_url(response_payload)
        progress = extract_progress(response_payload)
        if progress is None:
            if status == "succeeded":
                progress = 100
            elif status == "failed":
                progress = 0
            elif status in ("submitted", "processing", "unknown"):
                progress = 10

        message = safe_text(response_payload.get("message"))
        if not message:
            if status == "succeeded":
                message = "视频生成完成"
            elif status == "failed":
                message = "视频生成失败"
            else:
                message = "视频任务处理中"

        return {
            "status": status,
            "task_id": task_id,
            "video_url": video_url,
            "progress": progress,
            "message": message,
            "provider": self.provider_name,
            "raw_response": response_payload,
        }
