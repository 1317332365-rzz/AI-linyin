import json
import os
import re
import time
import traceback
from typing import Any, Dict

from dotenv import load_dotenv

from modules.llm_config import get_llm_config
from modules.openai_client import chat_completion

load_dotenv()


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _mask_secret(value: Any) -> str:
    text = _safe_text(value)
    if not text:
        return ""
    if len(text) <= 8:
        return "*" * len(text)
    return f"{text[:4]}...{text[-4:]}"


def _preview_text(value: Any, max_len: int = 1200) -> str:
    text = _safe_text(value)
    if not text:
        return ""
    text = text.replace("\r", "\\r").replace("\n", "\\n")
    if len(text) <= max_len:
        return text
    return f"{text[:max_len]}...(truncated,total={len(text)})"


def _suggest_min_tokens(duration_text: str) -> int:
    text = _safe_text(duration_text).lower()
    if not text:
        return 2000

    if "30s" in text or "30秒" in text:
        return 1400
    if "3min" in text or "3分钟" in text:
        return 2400
    if "5min" in text or "5分钟" in text:
        return 3200

    minute_match = re.search(r"(\d+(\.\d+)?)\s*(min|分钟|m)\b", text)
    if minute_match:
        minutes = float(minute_match.group(1))
        return max(1800, min(5000, int(minutes * 700 + 1000)))

    second_match = re.search(r"(\d+(\.\d+)?)\s*(s|sec|秒)\b", text)
    if second_match:
        seconds = float(second_match.group(1))
        return max(1200, min(2800, int(seconds * 18 + 800)))

    return 2200


def _suggest_timeout_seconds(script_text: str, duration_text: str, max_tokens: int) -> float:
    script_len = len(_safe_text(script_text))
    timeout = 90.0
    if script_len > 2000:
        timeout += 30.0
    if script_len > 6000:
        timeout += 40.0

    timeout += max(0.0, min(90.0, (int(max_tokens) - 1500) * 0.03))

    if "min" in _safe_text(duration_text).lower() or "分钟" in _safe_text(duration_text):
        timeout += 20.0

    return max(60.0, min(320.0, timeout))


def _unwrap_json_fence(text: str) -> str:
    content = _safe_text(text)
    if not content.startswith("```"):
        return content

    lines = content.splitlines()
    if len(lines) >= 3 and lines[0].startswith("```") and lines[-1].startswith("```"):
        content = "\n".join(lines[1:-1]).strip()
        if content.lower().startswith("json"):
            content = content[4:].strip()
    return content


def _repair_json_commas(text: str) -> str:
    """
    Repair common LLM JSON issues:
    - trailing comma before '}' / ']'
    - duplicate commas such as ',,'
    Only touches commas outside JSON strings.
    """
    source = str(text or "")
    if not source:
        return source

    out = []
    in_string = False
    escaped = False
    i = 0
    length = len(source)

    while i < length:
        ch = source[i]
        if in_string:
            out.append(ch)
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            i += 1
            continue

        if ch == '"':
            in_string = True
            out.append(ch)
            i += 1
            continue

        if ch == ",":
            j = i + 1
            while j < length and source[j].isspace():
                j += 1
            if j >= length or source[j] in "}] ,":
                i += 1
                continue

        out.append(ch)
        i += 1

    return "".join(out)


def _extract_first_json_object(text: str) -> str:
    source = _safe_text(text)
    start = source.find("{")
    if start < 0:
        return ""

    in_string = False
    escaped = False
    depth = 0

    for idx in range(start, len(source)):
        ch = source[idx]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
            continue
        if ch == "{":
            depth += 1
            continue
        if ch == "}":
            depth -= 1
            if depth == 0:
                return source[start : idx + 1]

    return ""


def _extract_json_payload(content: str) -> Dict[str, Any]:
    text = _unwrap_json_fence(content)
    if not text:
        raise ValueError("empty model response")

    candidates = []
    seen = set()

    def add_candidate(label: str, candidate_text: str):
        candidate = _safe_text(candidate_text)
        if not candidate or candidate in seen:
            return
        seen.add(candidate)
        candidates.append((label, candidate))

    add_candidate("raw", text)
    add_candidate("comma_repair", _repair_json_commas(text))
    extracted = _extract_first_json_object(text)
    add_candidate("object_slice", extracted)
    add_candidate("object_slice_comma_repair", _repair_json_commas(extracted))

    last_exc = None
    last_text = text
    last_label = "raw"
    for label, candidate in candidates:
        try:
            obj = json.loads(candidate)
            if not isinstance(obj, dict):
                raise ValueError(
                    f"response is not a valid JSON object: top-level type is {type(obj).__name__}"
                )
            if label != "raw":
                print(
                    f"[parse_script][json_repair] strategy={label} "
                    f"raw_len={len(text)} parsed_len={len(candidate)}"
                )
            return obj
        except json.JSONDecodeError as exc:
            last_exc = exc
            last_text = candidate
            last_label = label
            continue

    if isinstance(last_exc, json.JSONDecodeError):
        exc = last_exc
        text_for_preview = last_text
        preview = _preview_text(text, 800)
        left = max(0, int(exc.pos) - 120)
        right = min(len(text_for_preview), int(exc.pos) + 120)
        near = _preview_text(text_for_preview[left:right], 400)
        raise ValueError(
            f"response is not a valid JSON object: {exc.msg} "
            f"(line={exc.lineno}, col={exc.colno}, pos={exc.pos}), "
            f"strategy={last_label}, near_pos_preview={near}, preview={preview}"
        ) from exc

    raise ValueError("response is not a valid JSON object")


def _safe_join_text(value: Any, delimiter: str = "；") -> str:
    if isinstance(value, (list, tuple, set)):
        parts = [_safe_text(item) for item in value if _safe_text(item)]
        return delimiter.join(parts)
    if isinstance(value, dict):
        return _safe_text(
            value.get("text")
            or value.get("action")
            or value.get("description")
            or value.get("content")
        )
    return _safe_text(value)


def _join_unique_text(parts: list[str], delimiter: str = "；") -> str:
    seen = set()
    merged = []
    for item in parts:
        text = _safe_text(item)
        if not text:
            continue
        if text in seen:
            continue
        seen.add(text)
        merged.append(text)
    return delimiter.join(merged)


def _normalize_motion_instruction_text(
    motion_instruction: Any,
    prev_state: Any = "",
    start_goal: Any = "",
) -> str:
    text = _safe_text(motion_instruction)
    prev_text = _safe_text(prev_state) or _safe_text(start_goal)

    if not text:
        if prev_text:
            return f"承接“{prev_text}”，重心前移并触发下一步动作。"
        return "主体动作持续推进并保持物理连续。"

    replacements = (
        ("已经走完", "重心前移，脚抬起并准备落步"),
        ("走完", "重心前移，脚抬起并准备落步"),
        ("已经完成", "动作持续推进中"),
        ("完成动作", "动作持续推进中"),
        ("已经结束", "动作进入收束阶段"),
    )
    for old, new in replacements:
        text = text.replace(old, new)

    if prev_text:
        anchor = prev_text[:24]
        if anchor and anchor not in text and "承接" not in text:
            text = f"承接“{anchor}”，{text}"

    return text.strip("，, ")


def _derive_target_state_from_motion(motion_instruction: Any, start_goal: Any = "") -> str:
    motion_text = _safe_text(motion_instruction)
    start_text = _safe_text(start_goal)
    if motion_text:
        return (
            f"承接“{motion_text}”，人物动作幅度逐渐减弱并趋于稳定，"
            "服装与空气反馈缓慢收束。"
        )
    if start_text:
        return f"承接起始状态“{start_text}”，人物与环境反馈逐步收束并稳定。"
    return "动作推进后，人物姿态与环境反馈逐步收束并稳定。"


def _normalize_target_state_text(target_state: Any, motion_instruction: Any, start_goal: Any = "") -> str:
    text = _safe_text(target_state)
    motion_text = _safe_text(motion_instruction)
    if not text:
        text = _derive_target_state_from_motion(motion_text, start_goal)

    replacements = (
        ("突然静止", "动作幅度逐渐减弱并趋于稳定"),
        ("瞬间静止", "动作幅度逐渐减弱并趋于稳定"),
        ("突然爆炸", "能量持续抬升后向外扩散"),
        ("瞬间爆炸", "能量持续抬升后向外扩散"),
        ("突然", "逐渐"),
        ("瞬间", "逐步"),
        ("立刻", "随动作推进"),
        ("马上", "随动作推进"),
    )
    for old, new in replacements:
        text = text.replace(old, new)

    gradual_tokens = ("逐渐", "逐步", "缓慢", "持续", "收束", "趋于", "回落")
    if not any(token in text for token in gradual_tokens):
        text = f"{text}，并逐渐收束到稳定状态"

    if motion_text:
        motion_anchor = motion_text[:24]
        if motion_anchor and motion_anchor not in text:
            text = f"承接“{motion_anchor}”，{text}"

    return text.strip("，, ")


def _normalize_visual_anchor_text(
    visual_anchor: Any,
    prev_state: Any,
    target_state: Any,
    scene_description: Any = "",
) -> str:
    prev_text = _safe_text(prev_state)
    target_text = _safe_text(target_state)
    scene_text = _safe_text(scene_description)
    explicit = _safe_text(visual_anchor)

    parts = []
    if explicit:
        parts.append(explicit)
    if scene_text:
        parts.append(f"同一空间锚点：{scene_text[:36]}")
    if prev_text:
        parts.append(f"承接上一镜头目标状态：{prev_text[:42]}")
    if target_text:
        parts.append(f"当前镜头状态收束：{target_text[:42]}")

    return _join_unique_text(parts)


def _normalize_continuity_hint_text(
    continuity_hint: Any,
    target_state: Any,
    prev_state: Any,
    scene_description: Any = "",
) -> str:
    text = _safe_text(continuity_hint)
    target_text = _safe_text(target_state)
    prev_text = _safe_text(prev_state)
    scene_text = _safe_text(scene_description)

    if not text:
        direction = target_text[:34] or "动作能量持续推进后收束"
        text = f"下一镜头变化方向：继承当前状态并沿“{direction}”继续演化。"

    extra_parts = []
    if "下一镜头" not in text:
        direction = target_text[:34] or "动作能量持续推进后收束"
        extra_parts.append(f"下一镜头变化方向：沿“{direction}”继续演化")
    if "空间" not in text:
        space_anchor = scene_text[:24] if scene_text else "当前场景"
        extra_parts.append(f"空间连续：保持同一地点（{space_anchor}），仅允许机位/景别平滑变化")
    if "物理" not in text and "过渡" not in text:
        extra_parts.append("物理连续：风场、能量、姿态变化必须有过渡，禁止突变")
    if prev_text and "继承" not in text:
        extra_parts.append(f"状态继承基线：{prev_text[:30]}")

    merged = _join_unique_text([text, *extra_parts], delimiter="。")
    return merged.strip("。") + "。"


def _normalize_shot_plan_fields(
    shot_plan: Any,
    *,
    scene_motion_instruction: str = "",
    scene_target_state: str = "",
    scene_start_goal: str = "",
    scene_prev_state: str = "",
    scene_description: str = "",
) -> Any:
    if not isinstance(shot_plan, list):
        return shot_plan

    normalized_plan = []
    previous_target_state = _safe_text(scene_prev_state) or _safe_text(scene_start_goal)
    for item in shot_plan:
        if not isinstance(item, dict):
            normalized_plan.append(item)
            continue

        normalized_item = dict(item)
        prev_state = _safe_text(
            normalized_item.get("prev_state")
            or normalized_item.get("previous_state")
            or previous_target_state
            or scene_start_goal
        )
        if not prev_state:
            prev_state = "承接上一镜头同场景基础状态"
        motion_instruction = _normalize_motion_instruction_text(
            normalized_item.get("motion_instruction")
            or normalized_item.get("action")
            or normalized_item.get("blocking")
            or scene_motion_instruction,
            prev_state,
            scene_start_goal,
        )
        target_state = _normalize_target_state_text(
            normalized_item.get("target_state")
            or normalized_item.get("end_frame_goal")
            or normalized_item.get("EndFrame")
            or normalized_item.get("end_frame_description")
            or scene_target_state,
            motion_instruction,
            prev_state or scene_start_goal,
        )
        visual_anchor = _normalize_visual_anchor_text(
            normalized_item.get("visual_anchor"),
            prev_state,
            target_state,
            scene_description,
        )
        continuity_hint = _normalize_continuity_hint_text(
            normalized_item.get("continuity_hint"),
            target_state,
            prev_state,
            scene_description,
        )

        if prev_state:
            normalized_item["prev_state"] = prev_state
        if motion_instruction:
            normalized_item["motion_instruction"] = motion_instruction
        if target_state:
            normalized_item["target_state"] = target_state
        if visual_anchor:
            normalized_item["visual_anchor"] = visual_anchor
        if continuity_hint:
            normalized_item["continuity_hint"] = continuity_hint

        normalized_item.pop("EndFrame", None)
        normalized_item.pop("end_frame_goal", None)
        normalized_plan.append(normalized_item)
        previous_target_state = _safe_text(target_state) or _safe_text(prev_state) or previous_target_state

    return normalized_plan


def _normalize_scene_frame_fields(scene: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(scene, dict):
        raise ValueError("invalid scene: each scene must be an object")

    normalized = dict(scene)
    scene_description = _safe_text(normalized.get("description"))

    start_goal = _safe_text(
        normalized.get("start_frame_goal")
        or normalized.get("StartFrame")
        or normalized.get("start_frame_description")
    )
    prev_state = _safe_text(
        normalized.get("prev_state")
        or normalized.get("previous_state")
        or start_goal
    )
    if not prev_state:
        prev_state = "承接上一镜头同场景基础状态"
    motion_instruction = _normalize_motion_instruction_text(
        normalized.get("motion_instruction")
        or normalized.get("Action")
        or normalized.get("action_instruction")
        or normalized.get("action"),
        prev_state,
        start_goal,
    )
    if not motion_instruction:
        motion_instruction = _normalize_motion_instruction_text(
            _safe_join_text(normalized.get("action_arc")),
            prev_state,
            start_goal,
        )
    if not motion_instruction:
        motion_instruction = _normalize_motion_instruction_text(
            _safe_join_text(normalized.get("character_actions")),
            prev_state,
            start_goal,
        )

    target_state = _normalize_target_state_text(
        normalized.get("target_state")
        or normalized.get("end_frame_goal")
        or normalized.get("EndFrame")
        or normalized.get("end_frame_description"),
        motion_instruction,
        prev_state or start_goal,
    )
    visual_anchor = _normalize_visual_anchor_text(
        normalized.get("visual_anchor"),
        prev_state,
        target_state,
        scene_description,
    )
    continuity_hint = _normalize_continuity_hint_text(
        normalized.get("continuity_hint"),
        target_state,
        prev_state,
        scene_description,
    )

    if start_goal:
        normalized["start_frame_goal"] = start_goal
        normalized["StartFrame"] = start_goal
        normalized["start_frame_description"] = start_goal

    if prev_state:
        normalized["prev_state"] = prev_state
    if motion_instruction:
        normalized["motion_instruction"] = motion_instruction
    if target_state:
        normalized["target_state"] = target_state
    if visual_anchor:
        normalized["visual_anchor"] = visual_anchor
    if continuity_hint:
        normalized["continuity_hint"] = continuity_hint

    normalized.pop("EndFrame", None)
    normalized.pop("end_frame_goal", None)

    normalized_shot_plan = _normalize_shot_plan_fields(
        normalized.get("shot_plan"),
        scene_motion_instruction=motion_instruction,
        scene_target_state=target_state,
        scene_start_goal=start_goal,
        scene_prev_state=prev_state,
        scene_description=scene_description,
    )
    if isinstance(normalized_shot_plan, list):
        normalized["shot_plan"] = normalized_shot_plan
        if normalized_shot_plan:
            first_shot = normalized_shot_plan[0] if isinstance(normalized_shot_plan[0], dict) else {}
            last_shot = normalized_shot_plan[-1] if isinstance(normalized_shot_plan[-1], dict) else {}
            normalized["prev_state"] = _safe_text(first_shot.get("prev_state") or normalized.get("prev_state"))
            normalized["target_state"] = _safe_text(last_shot.get("target_state") or normalized.get("target_state"))
            normalized["visual_anchor"] = _safe_text(first_shot.get("visual_anchor") or normalized.get("visual_anchor"))
            normalized["continuity_hint"] = _safe_text(last_shot.get("continuity_hint") or normalized.get("continuity_hint"))

    return normalized


def _extract_story_package_from_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        return {}

    story_package = payload.get("story_package")
    if isinstance(story_package, dict):
        merged = dict(story_package)
    else:
        merged = {}

    # 兼容部分模型把角色字段放在顶层。
    if "character_bible" not in merged and isinstance(payload.get("character_bible"), list):
        merged["character_bible"] = payload.get("character_bible")
    if "scene_bible" not in merged and isinstance(payload.get("scene_bible"), list):
        merged["scene_bible"] = payload.get("scene_bible")
    return merged


def _normalize_character_bible(value: Any) -> list:
    if not isinstance(value, list):
        return []

    normalized = []
    seen = set()
    for item in value:
        if isinstance(item, dict):
            name = _safe_text(item.get("name") or item.get("character_name") or item.get("id"))
            role = _safe_text(item.get("role") or item.get("identity") or item.get("position"))
            goal = _safe_text(item.get("goal") or item.get("motivation"))
            tension = _safe_text(item.get("tension") or item.get("conflict"))
            voice = _safe_text(item.get("voice") or item.get("tone") or item.get("speech_style"))
            visual_anchor = _safe_text(item.get("visual_anchor") or item.get("visualAnchor") or item.get("appearance"))
        else:
            name = _safe_text(item)
            role = ""
            goal = ""
            tension = ""
            voice = ""
            visual_anchor = ""

        if not name:
            continue
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        normalized.append(
            {
                "name": name,
                "role": role,
                "goal": goal,
                "tension": tension,
                "voice": voice,
                "visual_anchor": visual_anchor,
            }
        )

    return normalized


def _normalize_story_package(value: Any) -> Dict[str, Any]:
    source = dict(value) if isinstance(value, dict) else {}
    normalized = dict(source)
    normalized["character_bible"] = _normalize_character_bible(source.get("character_bible"))
    return normalized


def _infer_character_bible_from_scenes(scenes: Any) -> list:
    if not isinstance(scenes, list):
        return []

    ignored = {"旁白", "解说", "镜头", "环境音"}
    names = []
    seen = set()

    def collect(name_text: Any):
        name = _safe_text(name_text)
        if not name or name in ignored:
            return
        if len(name) > 16:
            return
        key = name.lower()
        if key in seen:
            return
        seen.add(key)
        names.append(
            {
                "name": name,
                "role": "待补充",
                "goal": "",
                "tension": "",
                "voice": "",
                "visual_anchor": "",
            }
        )

    for scene in scenes:
        if not isinstance(scene, dict):
            continue
        for key in ("dialogue_details", "dialogue_beats"):
            beats = scene.get(key)
            if isinstance(beats, list):
                for beat in beats:
                    if isinstance(beat, dict):
                        collect(beat.get("speaker") or beat.get("role") or beat.get("character"))
        dialogue_text = _safe_text(scene.get("dialogue"))
        if dialogue_text:
            for line in dialogue_text.splitlines():
                match = re.match(r"^\s*([^:：\s]{1,12})\s*[:：]", line)
                if match:
                    collect(match.group(1))

    return names


def _extract_story_package_by_llm(
    script_text: str,
    duration_text: str,
    *,
    api_key: str,
    model_name: str,
    temperature: float,
    base_url: Any,
    timeout_seconds: float,
    request_id: str,
) -> Dict[str, Any]:
    user_prompt = (
        "请从剧情中提取角色与场景推荐信息，只输出 JSON，不要解释。\n"
        "顶层字段必须是 story_package（对象）。\n"
        "story_package.character_bible 必须是数组；每项字段：name, role, goal, tension, voice, visual_anchor。\n"
        "story_package.scene_bible 可选数组；每项字段：name, description, mood, time。\n"
        "角色名必须来自剧情，禁止使用“角色A/角色B”这类占位符。\n"
        f"目标时长：{duration_text}\n"
        f"剧情输入：{script_text}"
    )

    response = chat_completion(
        api_key=api_key,
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": "你是影视编剧分析助手。你必须输出严格 JSON。禁止输出 Markdown。",
            },
            {"role": "user", "content": user_prompt},
        ],
        temperature=max(0.1, min(temperature, 0.6)),
        max_tokens=1800,
        base_url=base_url,
        timeout_seconds=max(60.0, min(240.0, timeout_seconds)),
    )
    if not response.get("success"):
        raise ValueError(_safe_text(response.get("error") or "character extraction failed"))

    payload = _extract_json_payload(_safe_text(response.get("content")))
    story_package = _normalize_story_package(_extract_story_package_from_payload(payload))
    print(
        f"[parse_script][{request_id}] enrich_story_package "
        f"character_count={len(story_package.get('character_bible') or [])}"
    )
    return story_package


def parse_script(script: str, duration: str = "3min", llm_config=None) -> Dict[str, Any]:
    request_id = f"ps-{int(time.time() * 1000)}"
    started = time.perf_counter()
    try:
        script_text = _safe_text(script)
        duration_text = _safe_text(duration) or "3min"
        if not script_text:
            raise ValueError("script is empty")

        config = llm_config if isinstance(llm_config, dict) and llm_config else get_llm_config("script")

        model_name = _safe_text(config.get("model")) or "gpt-4"
        try:
            temperature = float(config.get("temperature", 0.7))
        except (TypeError, ValueError):
            temperature = 0.7
        try:
            configured_max_tokens = int(config.get("max_tokens", 2000) or 2000)
        except (TypeError, ValueError):
            configured_max_tokens = 2000

        suggested_tokens = _suggest_min_tokens(duration_text)
        max_tokens = max(configured_max_tokens, suggested_tokens)
        max_tokens = max(1200, min(12000, max_tokens))
        request_timeout = _suggest_timeout_seconds(script_text, duration_text, max_tokens)
        api_key = _safe_text(config.get("api_key") or os.getenv("OPENAI_API_KEY", ""))
        if not api_key:
            raise ValueError("script api_key is empty")
        base_url = config.get("base_url")
        sdk_type = _safe_text(config.get("sdk_type") or "openai")

        print(
            f"[parse_script][{request_id}] start "
            f"script_len={len(script_text)} duration={duration_text} "
            f"model={model_name} sdk_type={sdk_type} max_tokens={max_tokens} "
            f"timeout={request_timeout:.1f}s base_url={_safe_text(base_url)} api_key={_mask_secret(api_key)}"
        )

        user_prompt = (
            "把输入剧情改写为分镜 JSON（只输出 JSON，不要解释）。\n"
            "顶层字段必须有 scenes（数组）和 story_package（对象）。\n"
            "story_package 必须包含 character_bible（数组），每项字段：name, role, goal, tension, voice, visual_anchor。\n"
            "角色名必须来自剧情，不要输出“角色A/角色B”占位名。\n"
            "scene 字段必须包含：scene_id, description, time, mood, shot_description, detailed_shot_description, staging_notes, "
            "shot_plan, character_actions, action_arc, emotion_arc, rhythm_plan, prev_state, motion_instruction, target_state, "
            "visual_anchor, continuity_hint, start_frame_goal, start_frame_description, scene_script, dialogue, dialogue_details, dialogue_beats, duration, "
            "ShotSize, Camera, StartFrame, Action, Mood, prompt。\n"
            "shot_plan 每项包含：beat_id, shot_type, camera_angle, camera_movement, blocking, action, "
            "prev_state, motion_instruction, target_state, visual_anchor, continuity_hint, dialogue, duration, transition。\n"
            "规则：\n"
            "- StartFrame 及 start_frame_goal/start_frame_description 必须是中文可视化描述，禁止纯数字帧号。\n"
            "- prev_state 必须描述上一镜头结束状态；首镜头可用 start_frame_goal 作为 prev_state。\n"
            "- motion_instruction 必须可拍摄；target_state 必须描述动作推进后的渐变收束结果，禁止“突然/瞬间/立刻”式跳跃结果。\n"
            "- motion_instruction 必须从 prev_state 推导，禁止直接写完成态（如“已经走完”）。\n"
            "- target_state 必须作为下一镜头输入基础，下一镜头需继承该状态（可弱化但不可消失）。\n"
            "- visual_anchor 必须包含上一镜头 target_state 的衔接信息；并锁定同一空间锚点。\n"
            "- continuity_hint 必须明确下一镜头变化方向（如“空气完全静止”“能量爆发”）。\n"
            "- 禁止空间跳跃；禁止物理状态突变（例如风到静止必须有过渡）。\n"
            "- 字段一致：StartFrame==start_frame_goal==start_frame_description。\n"
            "- 风格锁：东方动漫风；scene.prompt 必须含 eastern anime style, 2d animation, cel shading。\n"
            "- 中文配音锁：scene.prompt 必须含 mandarin speech, chinese dialogue, no english voice。\n"
            "- 连续性锁：每个 shot 必须单人物+单动作+单空间；禁止人物切换、景别跳变、空间跳变。\n"
            "- 遇到“对话→行动 / 角色A→角色B / 静态→环境巨变”必须拆成相邻 shot。\n"
            "- 每个 scene 的 shot_plan 建议 3-6 个 shot，不要只给 1 个。\n"
            "- 输出紧凑：description/detailed_shot_description/staging_notes/scene_script 每项尽量控制在 80 字内。\n"
            "- 输出去重：不要在 Action、action_arc、character_actions、scene_script 间重复同一句。\n"
            "- 输出预算：尽量控制整体输出体积，优先保留可执行镜头信息。\n"
            f"目标时长：{duration_text}\n"
            f"剧情输入：{script_text}"
        )

        llm_started = time.perf_counter()
        response = chat_completion(
            api_key=api_key,
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是专业分镜编剧。"
                        "你必须输出严格 JSON。"
                        "顶层必须包含 scenes 与 story_package.character_bible。"
                        "帧描述字段必须是中文可视化句子，不能是纯数字。"
                        "每个 shot 都必须有 prev_state、motion_instruction、target_state、visual_anchor、continuity_hint。"
                        "motion_instruction 必须从 prev_state 推导；target_state 必须是可继承的渐变收束结果。"
                        "每镜头必须单人物、单动作、单空间；遇到对话转行动/角色切换/静态转环境巨变必须拆镜头。"
                        "scene.prompt 必须包含 eastern anime style, 2d animation, cel shading, mandarin speech, chinese dialogue, no english voice。"
                    ),
                },
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            base_url=base_url,
            timeout_seconds=request_timeout,
        )
        llm_elapsed = time.perf_counter() - llm_started
        content_text = _safe_text(response.get("content"))
        finish_reason = _safe_text(response.get("finish_reason"))
        json_mode_used = response.get("json_mode_used")
        usage = response.get("usage")
        print(
            f"[parse_script][{request_id}] llm_done success={bool(response.get('success'))} "
            f"elapsed={llm_elapsed:.2f}s content_len={len(content_text)} "
            f"finish_reason={finish_reason or 'unknown'} json_mode_used={json_mode_used} usage={usage}"
        )
        if content_text:
            print(f"[parse_script][{request_id}] llm_preview={_preview_text(content_text, 1200)}")
        if finish_reason.lower() == "length":
            print(
                f"[parse_script][{request_id}] warning finish_reason=length, "
                "model output may be truncated by max_tokens"
            )
            raise ValueError(
                "invalid response: model output truncated (finish_reason=length), "
                f"please reduce output length or increase max_tokens (current={max_tokens})"
            )
        if not response.get("success"):
            err = _safe_text(response.get("error") or "chat_completion failed")
            print(f"[parse_script][{request_id}] llm_error={err}")
            raise ValueError(err)

        payload = _extract_json_payload(content_text)
        scenes = payload.get("scenes")
        if not isinstance(scenes, list):
            raise ValueError(f"invalid response: scenes must be a list, got {type(scenes).__name__}")

        normalized_scenes = []
        for index, item in enumerate(scenes):
            if not isinstance(item, dict):
                raise ValueError(f"invalid response: scene[{index}] must be an object, got {type(item).__name__}")
            normalized_scenes.append(_normalize_scene_frame_fields(item))

        llm_call_count = 1
        used_fallback = False

        story_package = _normalize_story_package(_extract_story_package_from_payload(payload))
        character_bible = story_package.get("character_bible") or []

        if not character_bible:
            llm_call_count += 1
            print(f"[parse_script][{request_id}] story_package.character_bible empty, trying enrichment")
            try:
                enriched_story_package = _extract_story_package_by_llm(
                    script_text,
                    duration_text,
                    api_key=api_key,
                    model_name=model_name,
                    temperature=temperature,
                    base_url=base_url,
                    timeout_seconds=request_timeout,
                    request_id=request_id,
                )
                enriched_characters = _normalize_character_bible(enriched_story_package.get("character_bible"))
                if enriched_characters:
                    story_package.update(enriched_story_package)
                    story_package["character_bible"] = enriched_characters
                    character_bible = enriched_characters
                    used_fallback = True
            except Exception as enrich_exc:
                print(
                    f"[parse_script][{request_id}] enrich_story_package_failed "
                    f"type={type(enrich_exc).__name__} message={_safe_text(enrich_exc)}"
                )

        if not character_bible:
            inferred_characters = _infer_character_bible_from_scenes(normalized_scenes)
            if inferred_characters:
                story_package["character_bible"] = inferred_characters
                character_bible = inferred_characters
                used_fallback = True
                print(
                    f"[parse_script][{request_id}] infer_character_bible_from_scenes "
                    f"character_count={len(inferred_characters)}"
                )

        elapsed = time.perf_counter() - started
        print(
            f"[parse_script][{request_id}] success scenes={len(normalized_scenes)} "
            f"characters={len(character_bible)} elapsed={elapsed:.2f}s"
        )
        return {
            "scenes": normalized_scenes,
            "story_package": story_package,
            "generation_scheme": payload.get("generation_scheme", {}),
            "_meta": {
                "used_fallback": used_fallback,
                "llm_call_count": llm_call_count,
            },
        }
    except Exception as exc:
        elapsed = time.perf_counter() - started
        print(
            f"[parse_script][{request_id}] error type={type(exc).__name__} "
            f"elapsed={elapsed:.2f}s message={_safe_text(exc)}"
        )
        print(f"[parse_script][{request_id}] traceback:\n{traceback.format_exc()}")
        raise
