import time

import httpx

from modules.llm_config import get_llm_config

_HTTP_CLIENTS = {}
_OPENAI_CLIENTS = {}


def _normalize_base_url(base_url):
    if not base_url:
        return None
    value = str(base_url).strip()
    return value or None


def _normalize_timeout_seconds(value, default=60.0):
    try:
        timeout = float(value)
    except (TypeError, ValueError):
        timeout = float(default)
    if timeout <= 0:
        timeout = float(default)
    return max(10.0, min(600.0, timeout))


def _is_timeout_error(error):
    text = str(error or "").lower()
    if not text:
        return False
    return any(
        token in text
        for token in (
            "request timed out",
            "timed out",
            "timeout",
            "read timeout",
            "connect timeout",
            "operation timed out",
        )
    )


def _normalize_image_generation_endpoint(base_url=None):
    value = str(base_url or "https://api.openai.com/v1").strip().rstrip("/")
    if not value:
        value = "https://api.openai.com/v1"

    for suffix in ("/chat/completions", "/responses", "/completions"):
        if value.endswith(suffix):
            value = value[: -len(suffix)]
            break

    if value.endswith("/images/generations"):
        return value
    if value.endswith("/images"):
        return f"{value}/generations"
    if value.endswith("/v1"):
        return f"{value}/images/generations"
    return f"{value}/images/generations"


def _normalize_chat_completion_endpoint(base_url=None):
    value = str(base_url or "https://api.openai.com/v1").strip().rstrip("/")
    if not value:
        value = "https://api.openai.com/v1"

    for suffix in ("/images/generations", "/responses", "/completions", "/chat/completions", "/images"):
        if value.endswith(suffix):
            value = value[: -len(suffix)]
            break

    if value.endswith("/v1"):
        return f"{value}/chat/completions"
    return f"{value}/chat/completions"


def _normalize_image_size(size):
    text = str(size or "").strip().lower().replace("*", "x")
    if not text:
        return "1024x1024"
    if text == "2k":
        return "1024x1024"
    if text == "3k":
        return "1536x1024"
    return text


def _normalize_reference_image(reference_image=None, reference_images=None):
    candidates = []
    if reference_image:
        candidates.append(reference_image)
    if isinstance(reference_images, (list, tuple)):
        candidates.extend(reference_images)

    for item in candidates:
        text = str(item or "").strip()
        if text.startswith("http://") or text.startswith("https://"):
            return text
    return ""


def _extract_image_url(payload):
    if not isinstance(payload, dict):
        return ""

    data = payload.get("data")
    if not isinstance(data, list):
        return ""

    for item in data:
        if not isinstance(item, dict):
            continue
        url = str(item.get("url") or "").strip()
        if url:
            return url
        b64_json = str(item.get("b64_json") or "").strip()
        if b64_json:
            return f"data:image/png;base64,{b64_json}"
    return ""


def _extract_error_message(response, payload):
    if isinstance(payload, dict):
        error_obj = payload.get("error")
        if isinstance(error_obj, dict):
            message = str(error_obj.get("message") or "").strip()
            if message:
                return message
        message = str(payload.get("message") or "").strip()
        if message:
            return message
    return str(getattr(response, "text", "") or "").strip()


def _post_image_generation(http_client, endpoint, api_key, payload):
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
    except Exception:
        payload_json = {}
    return response, payload_json


def _uses_chat_image_generation(model, base_url=None):
    model_text = str(model or "").strip().lower()
    base_text = str(base_url or "").strip().lower()
    if ("gemini" in model_text) and ("image" in model_text):
        return True
    if ("vectorengine.ai" in base_text) and ("gemini" in model_text):
        return True
    return False


def _collect_generated_image_urls(node, urls):
    if node is None:
        return
    if isinstance(node, str):
        text = node.strip()
        if text.startswith("data:image/") or text.startswith("https://") or text.startswith("http://"):
            urls.append(text)
        return
    if isinstance(node, list):
        for item in node:
            _collect_generated_image_urls(item, urls)
        return
    if isinstance(node, dict):
        for key, value in node.items():
            key_text = str(key).lower()
            if key_text in {"url", "image_url"}:
                if isinstance(value, dict):
                    nested_url = str(value.get("url") or "").strip()
                    if nested_url.startswith("data:image/") or nested_url.startswith("https://") or nested_url.startswith("http://"):
                        urls.append(nested_url)
                        continue
                elif isinstance(value, str):
                    text = value.strip()
                    if text.startswith("data:image/") or text.startswith("https://") or text.startswith("http://"):
                        urls.append(text)
                        continue
            _collect_generated_image_urls(value, urls)


def _extract_chat_image_url(payload):
    if not isinstance(payload, dict):
        return ""

    urls = []
    choices = payload.get("choices")
    if isinstance(choices, list):
        for choice in choices:
            if not isinstance(choice, dict):
                continue
            message = choice.get("message")
            if not isinstance(message, dict):
                continue
            images = message.get("images")
            if isinstance(images, list):
                _collect_generated_image_urls(images, urls)
            content = message.get("content")
            _collect_generated_image_urls(content, urls)

    if not urls:
        _collect_generated_image_urls(payload.get("data"), urls)

    return urls[0] if urls else ""


def generate_image(
    api_key,
    model,
    prompt,
    size="1920x1080",
    base_url=None,
    reference_image=None,
    reference_images=None,
):
    if not api_key:
        return {"success": False, "error": "Missing api_key"}
    if not model:
        return {"success": False, "error": "Missing model"}
    if not prompt:
        return {"success": False, "error": "Missing prompt"}

    primary_reference = _normalize_reference_image(reference_image, reference_images)
    use_chat_image_generation = _uses_chat_image_generation(model, base_url)
    if use_chat_image_generation:
        endpoint = _normalize_chat_completion_endpoint(base_url)
        content = [{"type": "text", "text": prompt}]
        if primary_reference:
            content.append({"type": "image_url", "image_url": {"url": primary_reference}})
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": content}],
            "max_tokens": 4096,
        }
    else:
        endpoint = _normalize_image_generation_endpoint(base_url)
        normalized_size = _normalize_image_size(size)
        payload = {
            "model": model,
            "prompt": prompt,
            "size": normalized_size,
        }
        if primary_reference:
            payload["image"] = primary_reference

    try:
        with httpx.Client(
            timeout=90.0,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        ) as http_client:
            response, payload_json = _post_image_generation(http_client, endpoint, api_key, payload)

            if not response.is_success and primary_reference:
                error_message = _extract_error_message(response, payload_json).lower()
                if use_chat_image_generation and any(
                    token in error_message
                    for token in ("image_url", "image", "unsupported", "invalid", "not supported", "unknown parameter")
                ):
                    fallback_payload = dict(payload)
                    fallback_messages = list(fallback_payload.get("messages") or [])
                    if fallback_messages:
                        first_message = dict(fallback_messages[0] or {})
                        content = [
                            item
                            for item in list(first_message.get("content") or [])
                            if not (isinstance(item, dict) and str(item.get("type") or "").lower() == "image_url")
                        ]
                        first_message["content"] = content
                        fallback_messages[0] = first_message
                        fallback_payload["messages"] = fallback_messages
                        response, payload_json = _post_image_generation(http_client, endpoint, api_key, fallback_payload)
                        if response.is_success:
                            payload = fallback_payload
                elif any(
                    token in error_message
                    for token in ("image", "unsupported", "invalid", "not supported", "unknown parameter")
                ):
                    fallback_payload = dict(payload)
                    fallback_payload.pop("image", None)
                    response, payload_json = _post_image_generation(http_client, endpoint, api_key, fallback_payload)
                    if response.is_success:
                        payload = fallback_payload

        if response.is_success:
            image_url = _extract_chat_image_url(payload_json) if use_chat_image_generation else _extract_image_url(payload_json)
            if image_url:
                result = {"success": True, "image_url": image_url}
                if use_chat_image_generation and primary_reference:
                    has_image_input = False
                    messages = payload.get("messages")
                    if isinstance(messages, list) and messages:
                        content = messages[0].get("content") if isinstance(messages[0], dict) else None
                        if isinstance(content, list):
                            has_image_input = any(
                                isinstance(item, dict) and str(item.get("type") or "").lower() == "image_url"
                                for item in content
                            )
                    if has_image_input:
                        result["reference_image_used"] = primary_reference
                        result["generation_mode"] = "image-to-image"
                    else:
                        result["generation_mode"] = "text-to-image"
                        result["reference_image_fallback"] = True
                elif primary_reference and "image" in payload:
                    result["reference_image_used"] = primary_reference
                    result["generation_mode"] = "image-to-image"
                else:
                    result["generation_mode"] = "text-to-image"
                    if primary_reference:
                        result["reference_image_fallback"] = True
                return result
            return {"success": False, "error": "No image URL returned", "raw_response": payload_json or response.text}

        error_message = _extract_error_message(response, payload_json)
        detail = f"openai image api error {response.status_code}"
        if error_message:
            detail = f"{detail} | {error_message}"
        result = {"success": False, "error": detail}
        if payload_json:
            result["raw_response"] = payload_json
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def _get_openai_client(api_key, base_url=None, timeout=60.0):
    normalized_base_url = _normalize_base_url(base_url)
    key = (str(api_key or "").strip(), normalized_base_url, float(timeout))
    if not key[0]:
        raise ValueError("api_key is required")

    http_client = _HTTP_CLIENTS.get(key)
    if http_client is None:
        http_client = httpx.Client(
            timeout=timeout,
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=40),
        )
        _HTTP_CLIENTS[key] = http_client

    openai_client = _OPENAI_CLIENTS.get(key)
    if openai_client is None:
        from openai import OpenAI

        client_kwargs = {"api_key": key[0], "http_client": http_client}
        if normalized_base_url:
            client_kwargs["base_url"] = normalized_base_url
        openai_client = OpenAI(**client_kwargs)
        _OPENAI_CLIENTS[key] = openai_client

    return openai_client


def test_connection(api_key, model, base_url=None):
    """
    Test OpenAI-compatible API connectivity.
    """
    try:
        openai_client = _get_openai_client(api_key, base_url=base_url, timeout=30.0)
        response = openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a test assistant."},
                {"role": "user", "content": "Reply OK only."},
            ],
            max_tokens=10,
        )

        if response and response.choices:
            return {
                "success": True,
                "message": f"Connection ok for model {model}",
                "response": response.choices[0].message.content,
            }

        return {"success": False, "message": "No valid response received"}

    except Exception as e:
        message = str(e)
        error_type = "unknown"
        lower = message.lower()
        if (
            "api key" in lower
            or "unauthorized" in lower
            or "401" in lower
            or "authentication" in lower
        ):
            error_type = "authentication"
            message = "API Key invalid or expired"
        elif (
            "timed out" in lower
            or "connection" in lower
            or "connect" in lower
            or "dns" in lower
        ):
            error_type = "connection"
            message = "Cannot connect to API service"
        elif "rate limit" in lower or "too many requests" in lower or "429" in lower:
            error_type = "rate_limit"
            message = "Rate limit exceeded"
        return {"success": False, "message": message, "error_type": error_type}


def chat_completion_byConfig(model_config, message, temperature=0.7, max_tokens=1000):
    return chat_completion(
        model_config.get("api_key"),
        model_config.get("model"),
        message,
        temperature,
        max_tokens,
        base_url=model_config.get("base_url"),
    )


def chat_completion(
    api_key,
    model,
    messages,
    temperature=0.7,
    max_tokens=1000,
    base_url=None,
    timeout_seconds=None,
):
    """
    Call OpenAI-compatible chat completion API.
    """
    effective_base_url = _normalize_base_url(base_url)
    if effective_base_url:
        print(f"Using Base URL: {effective_base_url}")

    primary_timeout = _normalize_timeout_seconds(timeout_seconds, default=60.0)
    retry_timeout = min(320.0, max(120.0, primary_timeout * 1.8))
    attempt_timeouts = [primary_timeout]
    if retry_timeout > primary_timeout + 1:
        attempt_timeouts.append(retry_timeout)

    for attempt_index, attempt_timeout in enumerate(attempt_timeouts, start=1):
        try:
            openai_client = _get_openai_client(
                api_key,
                base_url=effective_base_url,
                timeout=attempt_timeout,
            )

            started = time.perf_counter()
            json_mode_used = True
            try:
                response = openai_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    response_format={"type": "json_object"},
                )
            except Exception as e:
                # Retry once without strict JSON mode if provider/model does not support it.
                if (
                    "response_format" in str(e)
                    or "not supported" in str(e).lower()
                    or "invalidparameter" in str(e).lower()
                ):
                    print(f"JSON mode unsupported, retrying without response_format: {e}")
                    json_mode_used = False
                    response = openai_client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                else:
                    raise

            elapsed = time.perf_counter() - started
            print(
                f"ChatCompletion latency: {elapsed:.2f}s model={model} "
                f"max_tokens={max_tokens} timeout={attempt_timeout:.0f}s"
            )

            return {
                "success": True,
                "content": response.choices[0].message.content,
                "finish_reason": getattr(response.choices[0], "finish_reason", None),
                "json_mode_used": json_mode_used,
                "usage": (
                    response.usage.model_dump()
                    if hasattr(getattr(response, "usage", None), "model_dump")
                    else (dict(response.usage) if isinstance(getattr(response, "usage", None), dict) else None)
                ),
            }
        except Exception as e:
            is_timeout = _is_timeout_error(e)
            has_retry = attempt_index < len(attempt_timeouts)
            if is_timeout and has_retry:
                print(
                    f"ChatCompletion timeout (attempt {attempt_index}/{len(attempt_timeouts)}), "
                    f"retrying with timeout={attempt_timeouts[attempt_index]:.0f}s"
                )
                continue
            print(e)
            return {"success": False, "error": str(e)}

    return {"success": False, "error": "unknown chat completion failure"}


def general_chat_completion(messages, temperature=0.7, max_tokens=1000):
    """
    Call chat completion using the `general` process config.
    """
    try:
        chat_config = get_llm_config("general")
        print(f"Chat Completion general: {chat_config}")
        return chat_completion_byConfig(chat_config, messages, temperature, max_tokens)
    except Exception as e:
        return {
            "success": False,
            "content": "",
            "error": str(e),
        }
