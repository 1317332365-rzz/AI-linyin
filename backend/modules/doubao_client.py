import json
import re

import httpx


MIN_PIXELS = 3686400


def _normalize_size(size, width=1024, height=1024):
    text = str(size or "").strip().lower().replace("*", "x")
    if not text and width and height:
        text = f"{int(width)}x{int(height)}"

    if text in {"2k", "3k"}:
        return text

    match = re.match(r"^(\d{2,5})x(\d{2,5})$", text)
    if match:
        w = int(match.group(1))
        h = int(match.group(2))
        if w * h < MIN_PIXELS:
            return "2k"
        return f"{w}x{h}"

    return "2k"


def _normalize_base_url(base_url):
    text = str(base_url or "https://ark.cn-beijing.volces.com/api/v3").strip().rstrip("/")
    if not text:
        text = "https://ark.cn-beijing.volces.com/api/v3"

    if text.endswith("/images/generations"):
        return text
    if text.endswith("/images"):
        return f"{text}/generations"
    if text.endswith("/api/v3"):
        return f"{text}/images/generations"
    return f"{text}/images/generations"


def _normalize_reference_image(reference_image=None, reference_images=None):
    candidates = []
    if isinstance(reference_images, (list, tuple)):
        candidates.extend(reference_images)
    if reference_image:
        candidates.insert(0, reference_image)

    for item in candidates:
        text = str(item or "").strip()
        if text.startswith("http://") or text.startswith("https://"):
            return text
    return ""


def _extract_image_url(payload):
    data = payload.get("data")
    if not isinstance(data, list):
        return ""

    for item in data:
        if not isinstance(item, dict):
            continue
        url = str(item.get("url") or "").strip()
        if url:
            return url
    return ""


def _extract_error_message(response, payload):
    if isinstance(payload, dict):
        err = payload.get("error")
        if isinstance(err, dict):
            message = str(err.get("message") or "").strip()
            if message:
                return message
        message = str(payload.get("message") or "").strip()
        if message:
            return message
    return response.text.strip()


def _clone_payload(payload):
    if not isinstance(payload, dict):
        return {}
    return dict(payload)


def _find_unsupported_optional_field(error_message):
    text = str(error_message or "").strip().lower()
    if not text:
        return ""
    if "parameter `output_format`" in text and "not supported" in text:
        return "output_format"
    if "parameter `watermark`" in text and "not supported" in text:
        return "watermark"
    return ""


def _post_generation(http_client, endpoint, api_key, payload):
    response = http_client.post(
        endpoint,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json; charset=utf-8",
        },
        json=payload,
    )
    try:
        payload_json = response.json()
    except json.JSONDecodeError:
        payload_json = {}
    return response, payload_json
def generate_nonoImage( api_key,
    model,
    prompt,):
    endPoint='https://api.vectorengine.ai/fal-ai/nano-banana'
    playLoad={
        "num_images": 1,
        "prompt": prompt,
    }
    import requests
    headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }    
    try:
        response = requests.post(endPoint, headers=headers, json=playLoad, timeout=60)
        response=response.json()
        return {"success": True, "image_url": response.get("response_url")}
    except Exception as e:        
        return {"success": False, "error": str(e)}
def generate_image(
    api_key,
    model,
    prompt,
    size="2k",
    width=1920,
    height=1920,
    base_url=None,
    output_format="png",
    watermark=False,
    reference_image=None,
    reference_images=None,
):
    """
    Generate an image with Ark image generation API.
    Supports optional image-to-image generation via the `image` field.
    """
    if not api_key:
        return {"success": False, "error": "Missing api_key"}
    if not model:
        return {"success": False, "error": "Missing model"}
    if not prompt:
        return {"success": False, "error": "Missing prompt"}

    normalized_size = _normalize_size(size, width=width, height=height)
    endpoint = _normalize_base_url(base_url)
    primary_reference = _normalize_reference_image(reference_image, reference_images)
    payload = {
        "model": model,
        "messages": prompt,
        "size": normalized_size,
        "output_format": str(output_format or "png").strip() or "png",
        "watermark": bool(watermark),
    }
    
    if primary_reference:
        payload["image"] = primary_reference
        
    try:
        with httpx.Client(
            timeout=90.0,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        ) as http_client:
            request_payload = _clone_payload(payload)
            response, payload_json = _post_generation(http_client, endpoint, api_key, request_payload)

            if not response.is_success:
                error_message = _extract_error_message(response, payload_json)
                unsupported_field = _find_unsupported_optional_field(error_message)
                if unsupported_field and unsupported_field in request_payload:
                    fallback_payload = _clone_payload(request_payload)
                    fallback_payload.pop(unsupported_field, None)
                    response, payload_json = _post_generation(http_client, endpoint, api_key, fallback_payload)
                    if response.is_success:
                        payload = fallback_payload
                    else:
                        payload = fallback_payload

        if response.is_success:
            image_url = _extract_image_url(payload_json)
            if image_url:
                result = {"success": True, "image_url": image_url}
                if primary_reference:
                    result["reference_image_used"] = primary_reference
                    result["generation_mode"] = "image-to-image"
                else:
                    result["generation_mode"] = "text-to-image"
                if "output_format" not in payload:
                    result["request_compat_mode"] = "without_output_format"
                return result
            return {"success": False, "error": "No image URL returned", "raw_response": payload_json or response.text}

        error_message = _extract_error_message(response, payload_json)
        detail = f"ark image api error {response.status_code}"
        if error_message:
            detail = f"{detail} | {error_message}"
        result = {"success": False, "error": detail}
        if payload_json:
            result["raw_response"] = payload_json
        return result

    except Exception as e:
        return {"success": False, "error": str(e)}
