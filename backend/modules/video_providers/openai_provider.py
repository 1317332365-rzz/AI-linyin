# -*- coding: utf-8 -*-
"""
OpenAI-compatible video provider (mainly Ark /contents/generations/tasks).
"""

from typing import Any, Dict, Optional

import requests

from .base import BaseVideoProvider
from .common import (
    build_text_prompt,
    extract_progress,
    extract_task_id,
    extract_video_url,
    normalize_ark_base_url,
    normalize_task_status,
    parse_duration_seconds,
    pick_ark_api_key,
    pick_video_model,
    safe_text,
    validate_start_image_url,
)


class OpenAICompatibleVideoProvider(BaseVideoProvider):
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

        model = safe_text(context.get("model") or pick_video_model(config))
        if not model or model == "doubao-seedance-1-5-pro-251215":
            model = "veo3-fast-frames"
        elif model.lower() in {"veo_3_1", "veo3.1", "veo-3.1", "veo3_1", "veo3-fast"}:
            model = "veo3-fast-frames"
        endpoint = (
            safe_text(context.get("video_submit_endpoint") or config.get("video_submit_endpoint"))
            or "https://api.vectorengine.ai/v1/video/create"
        )

        ok, error_msg, start_image_url = validate_start_image_url(start_frame)
        if not ok:
            return {"status": "error", "error": error_msg}

        end_image_url = safe_text((end_frame or {}).get("image_url"))
        text_prompt = build_text_prompt(start_frame or {}, context)
        images = [start_image_url]
        if end_image_url:
            images.append(end_image_url)

        aspect_ratio = safe_text(context.get("aspect_ratio") or context.get("aspectRatio") or context.get("ratio")) or "16:9"
        if aspect_ratio == "adaptive":
            aspect_ratio = "16:9"
        requested_duration = parse_duration_seconds(
            context.get("shot_duration") or context.get("duration"),
            fallback=5,
        )

        headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            }
        # veo 3
        # payload = {
        #     "prompt": text_prompt,
        #     "model": 'veo_3_1-fast',
        #     "images": images,
        #     "seconds": requested_duration,
        #     "enhance_prompt": bool(context.get("enhance_prompt", True)),
        #     "enable_upsample": bool(context.get("enable_upsample", True)),
        #     "aspect_ratio": aspect_ratio,
             
        # }

        #grok

        # veo 3
        payload = {
            "prompt": text_prompt,
            "model": 'grok-video-3',
            "images": images,
            "seconds": 12,
            "aspect_ratio": "3:2",
            "size": "720P",
        }

        # sora2 

        payload = {
            "prompt": text_prompt,
            "model": 'sora-2-all',
            "images": images,
            "duration": 4,
            "size":"small",
            "orientation": "portrait",
            "watermark": False,
            "private": True
        }

        # # veo 3
        # payload = {
        #     "prompt": text_prompt,
        #     "model": 'grok-video-3',
        #     "images": images,
        #     "aspect_ratio": "3:2",
        #     "size": "720P",
        # }

        # veo 3
        payload = {
            "prompt": text_prompt,
            "model": 'veo_3_1-fast',
            "images": images,
            "seconds": requested_duration,
            "enhance_prompt": bool(context.get("enhance_prompt", True)),
            "enable_upsample": bool(context.get("enable_upsample", True)),
            "aspect_ratio": aspect_ratio,
             
        }
        print(f"Using video duration seconds: {requested_duration}")
        print(f"Submitting video generation task to {endpoint} with payload: {payload}")
        if context.get("watermark") is not None:
            payload["watermark"] = bool(context.get("watermark"))

        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
            print(response.text)
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
                "error": f"video api error {response.status_code}{suffix}{req_text}",
                "details": response_payload,
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
            "duration_requested": requested_duration,
            "duration_applied": requested_duration,
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
        endpoint = f"https://api.vectorengine.ai/v1/video/query?id={task_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        print(endpoint)
        try:
            response = requests.get(endpoint, headers=headers, timeout=30)
        except Exception as e:
            return {"status": "error", "error": f"request failed: {e}"}
        
        try:
            response_payload = response.json()
            print(f"query_task response_payload: {response_payload}")
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
