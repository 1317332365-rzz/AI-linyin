# -*- coding: utf-8 -*-
"""
JiMeng video provider using Volcengine Visual API Signature V4.
Reference flow:
- POST https://visual.volcengineapi.com/?Action=...&Version=...
- Canonical headers: content-type;host;x-content-sha256;x-date
- Authorization: HMAC-SHA256 Credential=..., SignedHeaders=..., Signature=...
"""

import datetime
import hashlib
import hmac
import json
import os
import time
from typing import Any, Dict, Optional
from urllib.parse import parse_qsl, urlencode, urlparse

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException, SSLError
from urllib3.util.retry import Retry

from .base import BaseVideoProvider
from .common import (
    build_action_endpoint,
    build_jimeng_payload_candidates,
    build_text_prompt,
    extract_progress,
    extract_task_id,
    extract_video_url,
    is_invalid_parameter_response,
    normalize_jimeng_base_url,
    normalize_task_status,
    parse_duration_seconds,
    pick_jimeng_req_key,
    pick_jimeng_submit_action,
    pick_jimeng_version,
    safe_text,
    validate_start_image_url,
)

DEFAULT_SERVICE = "cv"
DEFAULT_REGION = "cn-north-1"
QUERY_ACTION_FIXED = "CVSync2AsyncGetResult"
VERSION_FIXED = "2022-08-31"
QUERY_REQ_KEY_FIXED = "jimeng_ti2v_v30_pro"
DEFAULT_SUBMIT_API_RETRIES = 2
DEFAULT_QUERY_API_RETRIES = 3


class JiMengVideoProvider(BaseVideoProvider):
    provider_name = "jimeng"

    @staticmethod
    def _sign(key: bytes, msg: str) -> bytes:
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    def _get_signature_key(self, secret_key: str, datestamp: str, region: str, service: str) -> bytes:
        k_date = self._sign(secret_key.encode("utf-8"), datestamp)
        k_region = self._sign(k_date, region)
        k_service = self._sign(k_region, service)
        return self._sign(k_service, "request")

    def _resolve_credentials(self, context: Dict[str, Any], config: Dict[str, Any]) -> tuple[str, str]:
        access_key = (
            safe_text(context.get("jimeng_access_key"))
            or safe_text(config.get("access_key"))
            or safe_text(config.get("jimeng_access_key"))
            or safe_text(os.getenv("JIMENG_ACCESS_KEY"))
            or safe_text(os.getenv("VOLCENGINE_ACCESS_KEY"))
        )
        secret_key = (
            safe_text(context.get("jimeng_secret_key"))
            or safe_text(config.get("secret_key"))
            or safe_text(config.get("jimeng_secret_key"))
            or safe_text(os.getenv("JIMENG_SECRET_KEY"))
            or safe_text(os.getenv("VOLCENGINE_SECRET_KEY"))
        )
        return access_key, secret_key

    def _resolve_region_service(self, context: Dict[str, Any]) -> tuple[str, str]:
        region = safe_text(context.get("jimeng_region")) or safe_text(os.getenv("JIMENG_REGION")) or DEFAULT_REGION
        service = safe_text(context.get("jimeng_service")) or safe_text(os.getenv("JIMENG_SERVICE")) or DEFAULT_SERVICE
        return region, service

    @staticmethod
    def _extract_request_id(payload: Dict[str, Any]) -> str:
        return safe_text(payload.get("request_id")) or safe_text(payload.get("RequestId")) or ""

    @staticmethod
    def _normalize_jimeng_query_status(code_value: Any, raw_status: str, video_url: str) -> str:
        # Official contract: code==10000 means success at API layer.
        if str(code_value) != "10000":
            return "failed"

        text = (raw_status or "").strip().lower()
        if text == "in_queue":
            return "submitted"
        if text == "generating":
            return "processing"
        if text == "done":
            return "succeeded" if video_url else "failed"
        if text in {"not_found", "expired"}:
            return "failed"
        if video_url:
            return "succeeded"
        return "processing"

    def _resolve_transport_options(self, context: Dict[str, Any]) -> tuple[bool, int]:
        raw_verify = safe_text(context.get("jimeng_verify_ssl")) or safe_text(os.getenv("JIMENG_VERIFY_SSL"))
        verify_ssl = raw_verify.lower() not in {"0", "false", "no", "off"} if raw_verify else True

        raw_retries = safe_text(context.get("jimeng_network_retries")) or safe_text(os.getenv("JIMENG_NETWORK_RETRIES"))
        try:
            network_retries = max(0, min(5, int(raw_retries))) if raw_retries else 2
        except ValueError:
            network_retries = 2

        return verify_ssl, network_retries

    def _resolve_submit_api_retries(self, context: Dict[str, Any]) -> int:
        raw_retries = (
            safe_text(context.get("jimeng_submit_api_retries"))
            or safe_text(os.getenv("JIMENG_SUBMIT_API_RETRIES"))
        )
        try:
            retries = int(raw_retries) if raw_retries else DEFAULT_SUBMIT_API_RETRIES
        except ValueError:
            retries = DEFAULT_SUBMIT_API_RETRIES
        return max(0, min(5, retries))

    def _resolve_query_api_retries(self, context: Dict[str, Any]) -> int:
        raw_retries = (
            safe_text(context.get("jimeng_query_api_retries"))
            or safe_text(os.getenv("JIMENG_QUERY_API_RETRIES"))
        )
        try:
            retries = int(raw_retries) if raw_retries else DEFAULT_QUERY_API_RETRIES
        except ValueError:
            retries = DEFAULT_QUERY_API_RETRIES
        return max(0, min(8, retries))

    @staticmethod
    def _is_retryable_submit_error(status_code: int, response_payload: Dict[str, Any]) -> bool:
        if status_code >= 500:
            return True
        code_text = safe_text(response_payload.get("code"))
        if code_text in {"50000", "50501"}:
            return True
        message = safe_text(response_payload.get("message")).lower()
        retry_signals = (
            "internal rpc error",
            "rpc internal error",
            "internal error",
            "retry final failed",
            "upstream",
            "temporarily unavailable",
            "timeout",
        )
        return any(token in message for token in retry_signals)

    def _canonical_query(self, endpoint: str) -> str:
        parsed = urlparse(endpoint)
        pairs = parse_qsl(parsed.query, keep_blank_values=True)
        return urlencode(sorted(pairs, key=lambda x: (x[0], x[1])))

    def _sign_v4_headers(
        self,
        access_key: str,
        secret_key: str,
        endpoint: str,
        body_json: str,
        region: str,
        service: str,
    ) -> Dict[str, str]:
        parsed = urlparse(endpoint)
        host = parsed.netloc
        canonical_uri = "/"
        canonical_query = self._canonical_query(endpoint)

        now = datetime.datetime.utcnow()
        x_date = now.strftime("%Y%m%dT%H%M%SZ")
        datestamp = now.strftime("%Y%m%d")

        payload_hash = hashlib.sha256(body_json.encode("utf-8")).hexdigest()
        signed_headers = "content-type;host;x-content-sha256;x-date"
        content_type = "application/json"

        canonical_headers = (
            f"content-type:{content_type}\n"
            f"host:{host}\n"
            f"x-content-sha256:{payload_hash}\n"
            f"x-date:{x_date}\n"
        )

        canonical_request = (
            "POST\n"
            f"{canonical_uri}\n"
            f"{canonical_query}\n"
            f"{canonical_headers}\n"
            f"{signed_headers}\n"
            f"{payload_hash}"
        )

        algorithm = "HMAC-SHA256"
        credential_scope = f"{datestamp}/{region}/{service}/request"
        string_to_sign = (
            f"{algorithm}\n"
            f"{x_date}\n"
            f"{credential_scope}\n"
            f"{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
        )

        signing_key = self._get_signature_key(secret_key, datestamp, region, service)
        signature = hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

        authorization = (
            f"{algorithm} "
            f"Credential={access_key}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, "
            f"Signature={signature}"
        )

        return {
            "X-Date": x_date,
            "Authorization": authorization,
            "X-Content-Sha256": payload_hash,
            "Content-Type": content_type,
            "Host": host,
        }

    def _signed_post(
        self,
        endpoint: str,
        payload: Dict[str, Any],
        access_key: str,
        secret_key: str,
        region: str,
        service: str,
        timeout: int = 60,
        verify_ssl: bool = True,
        network_retries: int = 2,
    ) -> requests.Response:
        body_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        body_bytes = body_json.encode("utf-8")
        headers = self._sign_v4_headers(
            access_key=access_key,
            secret_key=secret_key,
            endpoint=endpoint,
            body_json=body_json,
            region=region,
            service=service,
        )
        # Avoid sticky keep-alive sockets that may cause intermittent EOF on some gateways.
        headers["Connection"] = "close"

        retry = Retry(
            total=network_retries,
            connect=network_retries,
            read=network_retries,
            backoff_factor=0.6,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"POST"}),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        last_error: Optional[Exception] = None

        with requests.Session() as session:
            session.mount("https://", adapter)
            session.mount("http://", adapter)
            for attempt in range(network_retries + 1):
                try:
                    return session.post(
                        endpoint,
                        headers=headers,
                        data=body_bytes,
                        timeout=timeout,
                        verify=verify_ssl,
                    )
                except SSLError as e:
                    last_error = e
                    if attempt >= network_retries:
                        raise
                    time.sleep(0.4 * (attempt + 1))
                except RequestException as e:
                    last_error = e
                    if attempt >= network_retries:
                        raise
                    time.sleep(0.4 * (attempt + 1))

        if last_error:
            raise last_error
        raise RuntimeError("request failed without response")

    def generate(
        self,
        start_frame: Optional[Dict[str, Any]],
        end_frame: Optional[Dict[str, Any]] = None,
        mode: str = "keyframe-interpolation",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        context = context or {}
        config = self.llm_config or {}
        print(f"JiMeng generate_video called with context: {json.dumps(context, ensure_ascii=False)}")
        access_key, secret_key = self._resolve_credentials(context, config)
        if not access_key or not secret_key:
            return {
                "status": "error",
                "error": "jimeng access_key/secret_key is required (context/config/env)",
            }
        req_key = pick_jimeng_req_key(config, context)
        req_key_text = req_key.lower()
        if (not req_key) or ("seedance" in req_key_text) or ("doubao" in req_key_text):
            req_key = QUERY_REQ_KEY_FIXED
        if not req_key:
            return {
                "status": "error",
                "error": "jimeng req_key is required (set video.model as req_key, or provide context.jimeng_req_key)",
            }

        region, service = self._resolve_region_service(context)
        verify_ssl, network_retries = self._resolve_transport_options(context)
        submit_api_retries = self._resolve_submit_api_retries(context)
        base_url = normalize_jimeng_base_url(context.get("jimeng_base_url") or config.get("base_url"))
        submit_action = pick_jimeng_submit_action(context)
        version = pick_jimeng_version(context)
        endpoint = build_action_endpoint(base_url, submit_action, version)

        ok, error_msg, start_image_url = validate_start_image_url(start_frame)
        if not ok:
            return {"status": "error", "error": error_msg}

        end_image_url = safe_text((end_frame or {}).get("image_url"))
        text_prompt = build_text_prompt(start_frame or {}, context)
        requested_duration = parse_duration_seconds(context.get("shot_duration") or context.get("duration"), fallback=5)
        ratio = safe_text(context.get("ratio"))

        base_payload: Dict[str, Any] = {
            "req_key": req_key,
            "prompt": text_prompt,
        }

        image_urls = [start_image_url]
        if end_image_url:
            image_urls.append(end_image_url)
        if image_urls:
            base_payload["image_urls"] = image_urls

        payload_candidates = build_jimeng_payload_candidates(base_payload, requested_duration, ratio)

        response = None
        response_payload: Dict[str, Any] = {}
        submitted_payload: Dict[str, Any] = {}
        last_error_payload: Dict[str, Any] = {}
        for candidate in payload_candidates:
            submitted_payload = candidate
            should_try_next_candidate = False
            for api_attempt in range(submit_api_retries + 1):
                try:
                    response = self._signed_post(
                        endpoint=endpoint,
                        payload=candidate,
                        access_key=access_key,
                        secret_key=secret_key,
                        region=region,
                        service=service,
                        timeout=60,
                        verify_ssl=verify_ssl,
                        network_retries=network_retries,
                    )
                except Exception as e:
                    return {"status": "error", "error": f"request failed: {e}"}

                try:
                    response_payload = response.json()
                except ValueError:
                    response_payload = {"raw": response.text}

                if response.status_code < 400:
                    break

                last_error_payload = response_payload
                if response.status_code == 400 and is_invalid_parameter_response(response_payload):
                    should_try_next_candidate = True
                    break

                retryable = self._is_retryable_submit_error(response.status_code, response_payload)
                if retryable and api_attempt < submit_api_retries:
                    time.sleep(0.8 * (api_attempt + 1))
                    continue

                request_id = self._extract_request_id(response_payload)
                message = safe_text(response_payload.get("message")) or "request rejected"
                hint = ""
                if response.status_code == 401:
                    hint = " | check access_key/secret_key, region=cn-north-1, service=cv, and API permissions"
                elif retryable:
                    hint = " | upstream algorithm internal error, retry later"
                return {
                    "status": "error",
                    "error": f"jimeng api error {response.status_code} | {message}{hint}",
                    "request_id": request_id,
                    "details": response_payload,
                }

            if response is not None and response.status_code < 400:
                break
            if should_try_next_candidate:
                continue

        if response is None or response.status_code >= 400:
            return {
                "status": "error",
                "error": f"jimeng api error {response.status_code if response is not None else 'unknown'}",
                "details": last_error_payload or response_payload,
            }

        task_id = extract_task_id(response_payload)
        video_url = extract_video_url(response_payload)
        status = normalize_task_status(response_payload)
        progress = extract_progress(response_payload)

        if status == "unknown":
            if video_url:
                status = "succeeded"
            elif task_id:
                status = "submitted"

        if progress is None:
            if status == "succeeded":
                progress = 100
            elif status in ("submitted", "processing", "unknown"):
                progress = 10

        result= {
            "status": status,
            "message": "jimeng video task submitted",
            "mode": mode,
            "task_id": task_id,
            "video_url": video_url,
            "progress": progress,
            "duration_requested": requested_duration,
            "duration_applied": submitted_payload.get("duration") if isinstance(submitted_payload, dict) else None,
            "provider": self.provider_name,
            "req_key": req_key,
            "raw_response": response_payload,
        }
        print(f"JiMeng generate_video result: {json.dumps(result, ensure_ascii=False)}")
        return result

    def query_task(self, task_id: str, provider_options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        task_id = safe_text(task_id)
        if not task_id:
            return {"status": "error", "error": "task_id is required"}
        provider_options = provider_options or {}
        config = self.llm_config or {}

        access_key, secret_key = self._resolve_credentials(provider_options, config)
        if not access_key or not secret_key:
            return {
                "status": "error",
                "error": "jimeng access_key/secret_key is required (provider_options/config/env)",
            }

        req_key = safe_text(provider_options.get("req_key")) or QUERY_REQ_KEY_FIXED
        base_url = normalize_jimeng_base_url(provider_options.get("jimeng_base_url") or config.get("base_url"))
        query_action = QUERY_ACTION_FIXED
        version = VERSION_FIXED
        endpoint = build_action_endpoint(base_url, query_action, version)

        region, service = self._resolve_region_service(provider_options)
        verify_ssl, network_retries = self._resolve_transport_options(provider_options)
        query_api_retries = self._resolve_query_api_retries(provider_options)

        payload: Dict[str, Any] = {"task_id": task_id}
        if req_key:
            payload["req_key"] = req_key

        response = None
        response_payload: Dict[str, Any] = {}
        for api_attempt in range(query_api_retries + 1):
            try:
                response = self._signed_post(
                    endpoint=endpoint,
                    payload=payload,
                    access_key=access_key,
                    secret_key=secret_key,
                    region=region,
                    service=service,
                    timeout=30,
                    verify_ssl=verify_ssl,
                    network_retries=network_retries,
                )
            except Exception as e:
                return {"status": "error", "error": f"request failed: {e}"}

            try:
                response_payload = response.json()
            except ValueError:
                response_payload = {"raw": response.text}
            if response.status_code < 400:
                break

            retryable = self._is_retryable_submit_error(response.status_code, response_payload)
            if retryable and api_attempt < query_api_retries:
                time.sleep(0.8 * (api_attempt + 1))
                continue

            request_id = self._extract_request_id(response_payload)
            message = safe_text(response_payload.get("message")) or "request rejected"
            code_value = response_payload.get("code")
            if retryable:
                return {
                    "status": "processing",
                    "task_id": task_id,
                    "video_url": "",
                    "progress": 50,
                    "message": f"jimeng query temporary upstream error | http={response.status_code} | code={code_value} | {message}",
                    "request_id": request_id,
                    "api_code": code_value,
                    "provider": self.provider_name,
                    "req_key": req_key,
                    "raw_response": response_payload,
                    "details": response_payload,
                    "transient_error": True,
                }
            print(response.status_code)

            return {
                "status": "failed",
                "task_id": task_id,
                "video_url": "",
                "progress": 0,
                "message": f"jimeng query http {response.status_code} | code={code_value} | {message}",
                "request_id": request_id,
                "api_code": code_value,
                "provider": self.provider_name,
                "req_key": req_key,
                "raw_response": response_payload,
                "details": response_payload,
            }

        code_value = response_payload.get("code")
        message = safe_text(response_payload.get("message"))
        request_id = self._extract_request_id(response_payload)
        data = response_payload.get("data") if isinstance(response_payload.get("data"), dict) else {}
        raw_status = safe_text(data.get("status"))
        video_url = safe_text(data.get("video_url")) or extract_video_url(response_payload)
        progress = extract_progress(data) or extract_progress(response_payload)
        status = self._normalize_jimeng_query_status(code_value, raw_status, video_url)
        print(progress)
        if progress is None:
            if raw_status == "in_queue":
                progress = 10
            elif raw_status == "generating":
                progress = 50
            elif status == "succeeded":
                progress = 100
            elif status == "failed":
                progress = 0
            else:
                progress = 10

        if not message:
            message = f"task status: {raw_status or status}"

        if str(code_value) != "10000":
            retryable = self._is_retryable_submit_error(200, response_payload)
            if retryable:
                return {
                    "status": "processing",
                    "task_id": task_id,
                    "video_url": video_url,
                    "progress": max(20, int(progress or 0)),
                    "message": f"jimeng query temporary upstream error | code={code_value} | {message}",
                    "request_id": request_id,
                    "api_code": code_value,
                    "raw_task_status": raw_status,
                    "provider": self.provider_name,
                    "req_key": req_key,
                    "raw_response": response_payload,
                    "details": response_payload,
                    "transient_error": True,
                }
            return {
                "status": "failed",
                "task_id": task_id,
                "video_url": video_url,
                "progress": 0,
                "message": f"jimeng query failed | code={code_value} | {message}",
                "request_id": request_id,
                "api_code": code_value,
                "raw_task_status": raw_status,
                "provider": self.provider_name,
                "req_key": req_key,
                "raw_response": response_payload,
            }

        return {
            "status": status,
            "task_id": task_id,
            "video_url": video_url,
            "progress": progress,
            "message": message,
            "request_id": request_id,
            "api_code": code_value,
            "raw_task_status": raw_status,
            "provider": self.provider_name,
            "req_key": req_key,
            "raw_response": response_payload,
        }
