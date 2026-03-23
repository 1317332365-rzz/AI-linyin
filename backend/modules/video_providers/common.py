# -*- coding: utf-8 -*-
"""
瑙嗛 Provider 鐨勫叕鍏卞父閲忎笌宸ュ叿鍑芥暟銆?"""

import json
import os
import re
from typing import Any, Dict, Optional
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse


DEFAULT_PROVIDER = "openai"
DEFAULT_VIDEO_MODEL = "doubao-seedance-1-5-pro-251215"
DEFAULT_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
DEFAULT_JIMENG_BASE_URL = "https://visual.volcengineapi.com"
DEFAULT_JIMENG_SUBMIT_ACTION = "CVSync2AsyncSubmitTask"
DEFAULT_JIMENG_QUERY_ACTION = "CVSync2AsyncGetResult"
DEFAULT_JIMENG_VERSION = "2022-08-31"
PLACEHOLDER_IMAGE_DOMAIN = "via.placeholder.com"


def safe_text(value: Any) -> str:
    return str(value or "").strip()


def _coerce_mapping(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                return item
    return {}


def parse_duration_seconds(raw_duration: Any, fallback: int = 5) -> int:
    if isinstance(raw_duration, (int, float)):
        return max(1, min(60, int(raw_duration)))

    text = safe_text(raw_duration).lower()
    if not text:
        return fallback

    match = re.search(r"(\d+)", text)
    if not match:
        return fallback
    return max(1, min(60, int(match.group(1))))


def normalize_duration_for_model(model: str, mode: str, duration_seconds: int, has_end_frame: bool) -> int:
    # 先做统一安全范围裁剪，模型兼容降级由重试逻辑处理。
    return max(1, min(60, int(duration_seconds)))


def build_duration_candidates(model: str, mode: str, requested_duration: int, has_end_frame: bool) -> list[int]:
    requested = normalize_duration_for_model(model, mode, requested_duration, has_end_frame)
    model_text = safe_text(model).lower()

    candidates: list[int] = [requested]
    if "seedance-1-5-pro" in model_text:
        # Seedance i2v/kf 通常只支持部分时长，优先保留用户时长，再逐级降档。
        fallback_values = [value for value in (20, 15, 10, 8, 6, 5) if value < requested]
        if requested < 5:
            fallback_values.append(5)
        for value in fallback_values:
            normalized = max(1, min(60, int(value)))
            if normalized not in candidates:
                candidates.append(normalized)
    return candidates


def is_invalid_duration_response(response_payload: Dict[str, Any]) -> bool:
    text = str(response_payload).lower()
    return ("duration" in text) and ("not valid" in text or "invalidparameter" in text)


def is_invalid_parameter_response(response_payload: Dict[str, Any]) -> bool:
    text = str(response_payload).lower()
    return ("invalidparameter" in text) or ("not valid" in text) or ("invalid parameter" in text)


def normalize_ark_base_url(base_url: Optional[str]) -> str:
    if not base_url:
        return DEFAULT_BASE_URL

    normalized = str(base_url).strip().rstrip("/").lower()
    normalized = normalized.replace("/contents/generations/tasks", "")
    normalized = normalized.replace("/images/generations", "")
    normalized = normalized.replace("/chat/completions", "")

    if "volces.com" not in normalized:
        return DEFAULT_BASE_URL
    if "/api/v3" in normalized:
        return normalized.split("/api/v3")[0] + "/api/v3"
    return normalized + "/api/v3"


def normalize_jimeng_base_url(base_url: Optional[str]) -> str:
    candidate = safe_text(base_url) or safe_text(os.getenv("JIMENG_BASE_URL")) or DEFAULT_JIMENG_BASE_URL
    if "://" not in candidate:
        candidate = f"https://{candidate.lstrip('/')}"

    parsed = urlparse(candidate)
    cleaned = urlunparse((parsed.scheme or "https", parsed.netloc, parsed.path.rstrip("/"), "", "", ""))
    if not cleaned or "ark.cn-beijing.volces.com" in cleaned.lower():
        return DEFAULT_JIMENG_BASE_URL
    return cleaned


def build_action_endpoint(base_url: str, action: str, version: str) -> str:
    parsed = urlparse(base_url)
    query_pairs = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if key.lower() not in {"action", "version"}
    ]
    query_pairs.append(("Action", action))
    query_pairs.append(("Version", version))
    query_text = urlencode(query_pairs)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path or "/", "", query_text, ""))


def _collect_urls(node: Any, urls: list[str], depth: int = 0) -> None:
    if depth > 8 or node is None:
        return

    if isinstance(node, str):
        text = node.strip()
        if text.startswith("http://") or text.startswith("https://"):
            urls.append(text)
        return

    if isinstance(node, dict):
        for key, value in node.items():
            key_text = str(key).lower()
            if key_text in {"url", "video_url", "output_url", "download_url", "file_url"}:
                _collect_urls(value, urls, depth + 1)
                continue
            _collect_urls(value, urls, depth + 1)
        return

    if isinstance(node, list):
        for item in node:
            _collect_urls(item, urls, depth + 1)


def extract_video_url(payload: Dict[str, Any]) -> str:
    urls: list[str] = []
    _collect_urls(payload, urls, 0)
    if not urls:
        return ""
    preferred = [u for u in urls if any(flag in u.lower() for flag in (".mp4", ".m3u8", ".mov", "video"))]
    return preferred[0] if preferred else urls[0]


def _to_percent(value: Any) -> Optional[int]:
    if value is None:
        return None

    text = safe_text(value)
    if not text:
        return None

    match = re.search(r"(\d+(\.\d+)?)", text)
    if not match:
        return None

    number = float(match.group(1))
    if number <= 1:
        number *= 100
    return max(0, min(100, int(round(number))))


def extract_progress(payload: Dict[str, Any]) -> Optional[int]:
    payload = _coerce_mapping(payload)
    keys = ("progress", "progress_percent", "percent", "percentage", "completed_percent")
    for key in keys:
        progress = _to_percent(payload.get(key))
        if progress is not None:
            return progress

    data = payload.get("data")
    if isinstance(data, dict):
        for key in keys:
            progress = _to_percent(data.get(key))
            if progress is not None:
                return progress
    return None


def extract_task_id(payload: Dict[str, Any]) -> str:
    payload = _coerce_mapping(payload)
    direct = safe_text(payload.get("id") or payload.get("task_id"))
    if direct:
        return direct
    data = payload.get("data")
    if isinstance(data, dict):
        return safe_text(data.get("id") or data.get("task_id"))
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                task_id = safe_text(item.get("id") or item.get("task_id"))
                if task_id:
                    return task_id
    return ""


def normalize_task_status(payload: Dict[str, Any]) -> str:
    payload = _coerce_mapping(payload)
    data = payload.get("data")

    data_status = ""
    if isinstance(data, dict):
        data_status = safe_text(data.get("status") or data.get("state") or data.get("task_status"))
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict):
                data_status = safe_text(item.get("status") or item.get("state") or item.get("task_status"))
                if data_status:
                    break

    root_status = safe_text(
        payload.get("task_status")
        or payload.get("status")
        or payload.get("state")
    )
    root_normalized = root_status.lower()

    # 某些平台根级 status 是业务码（例如 10000），真实任务状态在 data.status。
    prefer_data_status = (
        not root_status
        or bool(re.fullmatch(r"\d+", root_normalized))
        or root_normalized in {"ok", "success", "true"}
    )
    raw = data_status if (prefer_data_status and data_status) else (root_status or data_status)

    status = raw.lower()
    if not status:
        if extract_video_url(payload):
            return "succeeded"
        if extract_task_id(payload):
            return "processing"
        return "unknown"
    if any(word in status for word in ("success", "succeed", "complete", "finished", "done")):
        # 仅有任务 ID 且无视频地址时，按处理中对待，避免误判完成。
        if extract_task_id(payload) and not extract_video_url(payload):
            return "processing"
        return "succeeded"
    if any(word in status for word in ("fail", "error", "cancel", "timeout", "reject")):
        return "failed"
    if status in {"submitted", "submitting", "accepted", "created"}:
        return "submitted" if status != "submitting" else "submitting"
    if any(word in status for word in ("queue", "pending", "submit", "running", "process", "creating", "generating", "in_progress")):
        return "processing"

    # 纯数字状态通常是业务码，不是任务生命周期状态。
    if re.fullmatch(r"\d+", status):
        if extract_video_url(payload):
            return "succeeded"
        if extract_task_id(payload):
            return "processing"
        return "unknown"

    return status


def normalize_provider(value: Any) -> str:
    text = safe_text(value).lower()
    if text in {"jimeng", "jimeng_api", "jimeng-api", "jimeng_video", "jimeng-video", "即梦", "即梦视频"}:
        return "jimeng"
    if text in {"grsai", "grs", "grs-ai", "grs_ai", "grs video", "grs-video"}:
        return "grsai"
    return "openai"


def resolve_provider(explicit_provider: Any, context: Optional[Dict[str, Any]], llm_config: Optional[Dict[str, Any]]) -> str:
    context = context or {}
    config = llm_config or {}

    candidates = [
        explicit_provider,
        context.get("video_provider"),
        context.get("provider"),
        config.get("video_provider"),
        config.get("provider"),
    ]

    sdk_type = safe_text(config.get("sdk_type")).lower()
    if sdk_type == "jimeng":
        candidates.append("jimeng")
    if sdk_type == "grsai":
        candidates.append("grsai")

    for item in candidates:
        text = safe_text(item)
        if not text:
            continue
        return normalize_provider(text)
    return DEFAULT_PROVIDER


def pick_ark_api_key(config: Dict[str, Any]) -> str:
    return (
        safe_text(config.get("api_key"))
        or safe_text(os.getenv("ARK_API_KEY"))
        or safe_text(os.getenv("VOLCENGINE_API_KEY"))
    )


def pick_video_model(config: Dict[str, Any]) -> str:
    model = safe_text(config.get("model"))
    if (not model) or model.lower().startswith(("gpt-", "claude", "gemini")):
        return DEFAULT_VIDEO_MODEL
    return model


def pick_jimeng_req_key(config: Dict[str, Any], context: Dict[str, Any]) -> str:
    return (
        safe_text(context.get("jimeng_req_key"))
        or safe_text(config.get("model"))
        or safe_text(os.getenv("JIMENG_REQ_KEY"))
    )


def pick_jimeng_submit_action(context: Dict[str, Any]) -> str:
    return safe_text(context.get("jimeng_submit_action")) or safe_text(os.getenv("JIMENG_SUBMIT_ACTION")) or DEFAULT_JIMENG_SUBMIT_ACTION


def pick_jimeng_query_action(context: Dict[str, Any]) -> str:
    return safe_text(context.get("jimeng_query_action")) or safe_text(os.getenv("JIMENG_QUERY_ACTION")) or DEFAULT_JIMENG_QUERY_ACTION


def pick_jimeng_version(context: Dict[str, Any]) -> str:
    return safe_text(context.get("jimeng_version")) or safe_text(os.getenv("JIMENG_VERSION")) or DEFAULT_JIMENG_VERSION


def _is_veo_prompt_target(context: Dict[str, Any]) -> bool:
    context = _coerce_mapping(context)
    model = safe_text(context.get("model")).lower()
    provider = safe_text(context.get("video_provider") or context.get("provider")).lower()
    endpoint = safe_text(context.get("video_submit_endpoint")).lower()
    if "veo" in model:
        return True
    if "vectorengine.ai" in endpoint and "video/create" in endpoint:
        return True
    return provider == "openai"


def _compact_prompt_text(text: Any, max_chars: int = 220) -> str:
    value = safe_text(text)
    if not value:
        return ""
    value = re.sub(r"\s+", " ", value).strip("，,。；; ")
    if len(value) <= max_chars:
        return value
    return f"{value[:max_chars].rstrip('，,。；; ')}…"


def _join_bound_character_names(raw_value: Any, limit: int = 8) -> str:
    names: list[str] = []
    if isinstance(raw_value, (list, tuple, set)):
        candidates = list(raw_value)
    else:
        text = safe_text(raw_value)
        if not text:
            return ""
        candidates = re.split(r"[、,，;；/|]+", text)

    for item in candidates:
        name = safe_text(item)
        if not name or name in names:
            continue
        names.append(name)
        if len(names) >= limit:
            break
    return "、".join(names)


def _build_veo_prompt_booster(start_frame: Dict[str, Any], context: Dict[str, Any]) -> str:
    shot_title = safe_text(context.get("shot_title")) or "当前镜头"
    shot_duration = safe_text(context.get("shot_duration")) or "5s"
    story_focus = (
        _compact_prompt_text(context.get("scene_script"), max_chars=260)
        or _compact_prompt_text(context.get("scene_narrative"), max_chars=260)
        or _compact_prompt_text(context.get("detailed_shot_description"), max_chars=240)
        or _compact_prompt_text(context.get("shot_summary"), max_chars=220)
        or _compact_prompt_text(context.get("scene_description"), max_chars=220)
        or _compact_prompt_text((start_frame or {}).get("description"), max_chars=220)
    )
    start_state = _compact_prompt_text(
        context.get("start_frame_description") or context.get("StartFrame") or (start_frame or {}).get("description"),
        max_chars=180,
    )
    prev_state = _compact_prompt_text(
        context.get("prev_state")
        or context.get("previous_state")
        or context.get("previous_end_frame_description"),
        max_chars=180,
    )
    end_state = _compact_prompt_text(
        context.get("target_state")
        or context.get("end_frame_description")
        or context.get("end_frame_goal")
        or context.get("EndFrame"),
        max_chars=180,
    )
    motion_instruction = _compact_prompt_text(
        context.get("motion_instruction")
        or context.get("Action")
        or context.get("action_details"),
        max_chars=200,
    )
    action_detail = _compact_prompt_text(context.get("action_details") or context.get("detailed_plot"), max_chars=200)
    action_arc = _compact_prompt_text(context.get("action_arc") or context.get("Action"), max_chars=180)
    emotion_arc = _compact_prompt_text(context.get("emotion_arc") or context.get("Mood"), max_chars=170)
    rhythm_plan = _compact_prompt_text(context.get("rhythm_plan"), max_chars=160)
    visual_anchor = _compact_prompt_text(context.get("visual_anchor"), max_chars=180)
    continuity_hint = _compact_prompt_text(context.get("continuity_hint"), max_chars=180)
    dialogue_detail = _compact_prompt_text(context.get("dialogue_details"), max_chars=150)
    narration_text = _compact_prompt_text(
        context.get("narration_text") or context.get("voiceover_text") or context.get("voiceoverText"),
        max_chars=150,
    )
    bound_character_names = _join_bound_character_names(
        context.get("bound_character_names") or context.get("boundCharacterNames")
    )

    scene_block = [
        f"- 镜头：{shot_title}",
        f"- 时长：{shot_duration}",
        "- 边界：仅覆盖当前镜头，不跨到前后镜头。",
        "- 叙事目标：这一镜头必须推动故事前进，不要只是复述上一镜头。",
    ]
    if story_focus:
        scene_block.append(f"- 核心画面：{story_focus}")

    character_block = [
        "- 角色连续性：保持同一脸型、发型、服装、体型、道具归属和空间方位。",
        "- 镜头一致性：同一角色的服装颜色、道具位置、站位和镜头轴线必须稳定。",
    ]
    if bound_character_names:
        character_block.append(f"- 绑定角色：{bound_character_names}（不得替换或遗漏）")

    action_block = []
    if action_arc:
        action_block.append(f"- 动作节拍：{action_arc}")
    if motion_instruction:
        action_block.append(f"- 动作指令：{motion_instruction}")
    if prev_state:
        action_block.append(f"- 继承状态：{prev_state}")
    if action_detail:
        action_block.append(f"- 动作细节推进：{action_detail}")
    if start_state:
        action_block.append(f"- 起始状态：{start_state}")
    if end_state:
        action_block.append(f"- 状态收敛方向：{end_state}")
    if continuity_hint:
        action_block.append(f"- 下一镜头变化方向：{continuity_hint}")
    if rhythm_plan:
        action_block.append(f"- 节奏计划：{rhythm_plan}")
    if dialogue_detail:
        action_block.append(f"- 表演与对白：{dialogue_detail}")
    if narration_text:
        action_block.append(f"- 旁白语义：{narration_text}")

    camera_block = [
        "- 运镜：镜头运动平滑，开场建立空间，中段推进冲突，结尾明确收势。",
        "- 画质：电影感构图，主体清晰，动作有物理反馈。",
        "- 空间几何：起始帧与结束帧应处于同一场景结构中，只允许自然位移，不允许场景重建。",
    ]
    if visual_anchor:
        camera_block.append(f"- 视觉锚点：{visual_anchor}")

    mood_block = []
    if emotion_arc:
        mood_block.append(f"- 情绪节拍：{emotion_arc}")
    else:
        mood_block.append("- 情绪：起点/转折/落点必须可拍。")

    constraints_block = [
        "- 必须单画幅连续视频，禁止分屏、多宫格漫画、拼贴、字幕、logo、水印、英文文本。",
        "- 每个镜头只允许单人物、单动作、单空间，禁止同镜头内人物切换、景别跳变、空间跳变。",
        "- 状态继承：当前镜头必须承接 prev_state，并在 target_state 中平滑收束，起始状态和结束状态必须可连续过渡。",
        "- 空间连续：地点必须连续，禁止无因果空间跳跃。",
        "- 物理连续：风场/能量/姿态变化必须有过渡，禁止突变。",
        "- 若存在“对话→行动”“角色A→角色B”“静态→环境巨变”，必须拆为相邻镜头分别生成。",
        "- Audio language lock: mandarin speech, chinese dialogue, no english voice.",
        "- 音频要求：全程使用中文普通话对白与旁白，禁止英语旁白、英语对白、英语歌词和英文口播。",
        "- 禁止人物变脸、肢体畸形、道具漂移和无因果跳切。",
    ]

    blocks = [
        ("Scene", scene_block),
        ("Character", character_block),
        ("Action", action_block),
        ("Camera", camera_block),
        ("Mood", mood_block),
        ("Constraints", constraints_block),
    ]
    return "\n\n".join(
        f"{title}:\n" + "\n".join([line for line in lines if safe_text(line)])
        for title, lines in blocks
        if any(safe_text(line) for line in lines)
    )


def _dedupe_prompt_lines(prompt_text: str) -> str:
    lines = [safe_text(line) for line in safe_text(prompt_text).splitlines()]
    if not lines:
        return ""
    result: list[str] = []
    seen: set[str] = set()
    for line in lines:
        if not line:
            continue
        marker = re.sub(r"\s+", "", line).lower()
        if marker in seen:
            continue
        seen.add(marker)
        result.append(line)
    return "\n".join(result)


def build_text_prompt(start_frame: Dict[str, Any], context: Dict[str, Any]) -> str:
    start_frame = _coerce_mapping(start_frame)
    context = _coerce_mapping(context)
    base_prompt = (
        safe_text(context.get("prompt"))
        or safe_text((start_frame or {}).get("enhanced_prompt"))
        or safe_text((start_frame or {}).get("description"))
        or "东方动漫风电影镜头，主体清晰，动作自然，运镜流畅，保持当前片段内动作连续与人物关系稳定。"
    )

    extra_parts = []
    for key in (
        "scene_script",
        "scene_narrative",
        "ShotSize",
        "Camera",
        "StartFrame",
        "Action",
        "Mood",
        "scene_description",
        "shot_summary",
        "detailed_shot_description",
        "story_context",
        "previous_shot_summary",
        "next_shot_summary",
        "start_frame_description",
        "end_frame_description",
        "prev_state",
        "visual_anchor",
        "continuity_hint",
        "character_identity_rules",
        "character_hints",
        "scene_hints",
        "continuity_rules",
        "prompt_scaffold",
        "detailed_plot",
        "action_details",
        "action_arc",
        "emotion_arc",
        "rhythm_plan",
        "start_frame_goal",
        "dialogue_details",
        "dialogue_beat_details",
        "narration_text",
        "voiceover_text",
        "voiceoverText",
        "motion_instruction",
        "target_state",
        "audio_requirements",
    ):
        text = safe_text(context.get(key))
        if text and text not in base_prompt:
            extra_parts.append(text)

    bound_character_names = _join_bound_character_names(
        context.get("bound_character_names") or context.get("boundCharacterNames")
    )
    if bound_character_names:
        line = f"绑定角色：{bound_character_names}"
        if line not in base_prompt and line not in extra_parts:
            extra_parts.append(line)

    force_mandarin_audio = _is_veo_prompt_target(context) or bool(context.get("generate_audio", False))
    if force_mandarin_audio:
        audio_lock_line = "Audio language lock: mandarin speech, chinese dialogue, no english voice."
        chinese_audio_rule = "音频要求：全程使用中文普通话对白与旁白，禁止英语旁白、英语对白、英语歌词和英文口播。"
        if audio_lock_line not in base_prompt and audio_lock_line not in extra_parts:
            extra_parts.append(audio_lock_line)
        if chinese_audio_rule not in base_prompt and chinese_audio_rule not in extra_parts:
            extra_parts.append(chinese_audio_rule)

    # 低信息镜头兜底：当镜头描述过短或结构化字段缺失时，补齐最小可用镜头语言模板。
    signal_keys = (
        "scene_description",
        "shot_summary",
        "detailed_shot_description",
        "story_context",
        "detailed_plot",
        "action_details",
        "dialogue_details",
        "start_frame_description",
        "target_state",
        "prev_state",
        "continuity_hint",
        "visual_anchor",
    )
    signal_count = sum(1 for key in signal_keys if safe_text(context.get(key)))
    composed_preview = "\n".join([base_prompt, *extra_parts]).strip()
    if signal_count <= 2 or (signal_count <= 4 and len(composed_preview) < 140):
        shot_title = safe_text(context.get("shot_title")) or "当前镜头"
        shot_duration = safe_text(context.get("shot_duration")) or "5s"
        fallback_lines = [
            f"镜头任务：仅生成「{shot_title}」这一段，时长约 {shot_duration}，不要跨到上一镜头尾声或下一镜头开场。",
            "视觉风格：东方动漫风电影感，完整构图，主体清晰，光影层次自然，空间关系稳定。",
            "调度结构：开场建立空间与站位，中段推进动作与情绪反应，结尾给出清晰收束并留可衔接动作。",
            "叙事要求：这一镜头要承接上一镜头的状态变化，并把故事推进到下一步。",
            "连续性约束：单人物+单动作+单空间，禁止人物切换、景别跳变、空间跳变；触发对话转行动时拆镜头。",
            "质量约束：禁止分屏、多格漫画、拼贴、字幕、水印与英文文本，动作反馈要自然连贯；同角色、同服装、同道具、同机位轴线必须稳定。",
        ]
        start_desc = safe_text(context.get("start_frame_description") or (start_frame or {}).get("description"))
        end_desc = safe_text(
            context.get("target_state")
            or context.get("end_frame_description")
            or context.get("end_frame_goal")
            or context.get("EndFrame")
        )
        if start_desc:
            fallback_lines.append(f"起始状态：{start_desc}")
        if end_desc:
            fallback_lines.append(f"状态收敛方向：{end_desc}")
        prev_desc = safe_text(context.get("prev_state") or context.get("previous_state"))
        if prev_desc:
            fallback_lines.append(f"继承状态：{prev_desc}")
        visual_anchor = safe_text(context.get("visual_anchor"))
        if visual_anchor:
            fallback_lines.append(f"视觉锚点：{visual_anchor}")
        continuity_hint = safe_text(context.get("continuity_hint"))
        if continuity_hint:
            fallback_lines.append(f"下一镜头方向：{continuity_hint}")

        low_info_block = "\n".join(fallback_lines)
        if low_info_block not in base_prompt and low_info_block not in extra_parts:
            extra_parts.append(low_info_block)

    composed_prompt = base_prompt if not extra_parts else "\n".join([base_prompt, *extra_parts])

    if _is_veo_prompt_target(context):
        booster = _build_veo_prompt_booster(start_frame, context)
        if booster and booster not in composed_prompt:
            composed_prompt = "\n".join([composed_prompt, booster]).strip()

    return _dedupe_prompt_lines(composed_prompt)


def validate_start_image_url(start_frame: Optional[Dict[str, Any]]) -> tuple[bool, str, str]:
    start_frame = _coerce_mapping(start_frame)
    start_image_url = safe_text((start_frame or {}).get("image_url"))
    if not start_image_url:
        return False, "start_frame.image_url is required", ""
    if PLACEHOLDER_IMAGE_DOMAIN in start_image_url.lower():
        return False, "start_frame.image_url is placeholder; generate a real start frame first", ""
    return True, "", start_image_url


def build_jimeng_payload_candidates(base_payload: Dict[str, Any], requested_duration: int, ratio: str) -> list[Dict[str, Any]]:
    """
    鍗虫ⅵ鍙傛暟鍦ㄤ笉鍚岀増鏈?妯″瀷涓婂彲鑳藉瓨鍦ㄥ樊寮傦紝鎸夊€欓€?payload 閫愪釜灏濊瘯浠ユ彁鍗囧吋瀹圭巼銆?    """
    has_images = isinstance(base_payload.get("image_urls"), list) and bool(base_payload.get("image_urls"))
    include_ratio = bool(safe_text(ratio) and safe_text(ratio).lower() != "adaptive")

    image_variants = [True, False] if has_images else [False]
    duration_variants = [True, False]
    ratio_variants = [True, False] if include_ratio else [False]

    candidates: list[Dict[str, Any]] = []
    seen: set[str] = set()

    for use_images in image_variants:
        for use_duration in duration_variants:
            for use_ratio in ratio_variants:
                payload = dict(base_payload)
                if not use_images:
                    payload.pop("image_urls", None)
                if use_duration:
                    payload["duration"] = requested_duration
                else:
                    payload.pop("duration", None)
                if use_ratio:
                    payload["ratio"] = safe_text(ratio)
                else:
                    payload.pop("ratio", None)

                marker = json.dumps(payload, ensure_ascii=False, sort_keys=True)
                if marker in seen:
                    continue
                seen.add(marker)
                candidates.append(payload)

    return candidates
