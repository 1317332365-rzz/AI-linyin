import copy
import json
import os

from dotenv import load_dotenv

load_dotenv()

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "llm_config.json")

_BASE_DEFAULT = {
    "model": "gpt-4",
    "api_key": os.getenv("OPENAI_API_KEY", ""),
    "access_key": "",
    "secret_key": "",
    "base_url": "",
    "temperature": 0.7,
    "max_tokens": 1000,
    "sdk_type": "openai",
}

DEFAULT_CONFIG = {
    "general": copy.deepcopy(_BASE_DEFAULT),
    "script": {**copy.deepcopy(_BASE_DEFAULT), "max_tokens": 2000},
    "character": copy.deepcopy(_BASE_DEFAULT),
    "scene": copy.deepcopy(_BASE_DEFAULT),
    "video": {
        **copy.deepcopy(_BASE_DEFAULT),
        "model": "doubao-seedance-1-5-pro-251215",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "sdk_type": "doubao",
    },
    "dialogue": copy.deepcopy(_BASE_DEFAULT),
}

ALLOWED_FIELDS = {
    "model",
    "api_key",
    "access_key",
    "secret_key",
    "base_url",
    "temperature",
    "max_tokens",
    "sdk_type",
}
ALLOWED_SDK_TYPES = {"openai", "dashscope", "doubao", "grsai"}


def _safe_load_config():
    if not os.path.exists(CONFIG_FILE):
        return copy.deepcopy(DEFAULT_CONFIG), False
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            raw = f.read()
        data = json.loads(raw)
        return (data if isinstance(data, dict) else copy.deepcopy(DEFAULT_CONFIG), True)
    except (json.JSONDecodeError, OSError):
        # Allow simple comment lines that start with // (jsonc-like format).
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                raw = f.read()
            cleaned = "\n".join(
                line for line in raw.splitlines() if not line.lstrip().startswith("//")
            )
            data = json.loads(cleaned)
            return (data if isinstance(data, dict) else copy.deepcopy(DEFAULT_CONFIG), True)
        except (json.JSONDecodeError, OSError):
            return copy.deepcopy(DEFAULT_CONFIG), False


def _save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def _normalize_process_name(process):
    if not process:
        return "general"
    return str(process).strip().lower()


def _sanitize_patch(patch):
    if not isinstance(patch, dict):
        return {}

    result = {}
    for key, value in patch.items():
        if key not in ALLOWED_FIELDS:
            continue
        if key == "temperature":
            try:
                value = float(value)
            except (TypeError, ValueError):
                continue
            value = max(0.0, min(2.0, value))
        elif key == "max_tokens":
            try:
                value = int(value)
            except (TypeError, ValueError):
                continue
            value = max(1, value)
        elif key == "sdk_type":
            value = str(value).strip().lower()
            if value not in ALLOWED_SDK_TYPES:
                continue
        else:
            value = "" if value is None else str(value)
        result[key] = value
    return result


def ensure_config_file():
    config, loaded_ok = _safe_load_config()
    changed = not loaded_ok

    for process, defaults in DEFAULT_CONFIG.items():
        if process not in config or not isinstance(config[process], dict):
            config[process] = copy.deepcopy(defaults)
            changed = True
            continue
        for field, field_default in defaults.items():
            if field not in config[process]:
                config[process][field] = field_default
                changed = True

    if changed or not os.path.exists(CONFIG_FILE):
        _save_config(config)


def get_llm_config(process="general"):
    ensure_config_file()
    config, _ = _safe_load_config()
    process_name = _normalize_process_name(process)

    base = copy.deepcopy(DEFAULT_CONFIG["general"])
    base.update(_sanitize_patch(config.get("general", {})))

    process_cfg = config.get(process_name, {})
    base.update(_sanitize_patch(process_cfg))
    return base


def update_llm_config(new_config):
    ensure_config_file()
    if not isinstance(new_config, dict):
        raise ValueError("new_config must be a dict")

    process_name = _normalize_process_name(new_config.get("process", "general"))

    patch = dict(new_config)
    patch.pop("process", None)
    patch = _sanitize_patch(patch)
    if not patch:
        return get_llm_config(process_name)

    config, _ = _safe_load_config()
    current = config.get(process_name, {})
    if not isinstance(current, dict):
        current = {}
    current.update(patch)
    config[process_name] = current
    _save_config(config)

    return get_llm_config(process_name)
