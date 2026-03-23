import json
import os
import re
import time

from dotenv import load_dotenv

from modules.doubao_client import generate_image as doubao_generate_image,generate_nonoImage
from modules.openai_client import general_chat_completion, generate_image as openai_generate_image

load_dotenv()

SENSITIVE_ERROR_HINTS = (
    "outputimagesensitivecontentdetected",
    "sensitive information",
    "sensitive content",
)
# ANIME_STYLE_LOCK_CN = (
#     "风格硬锁：高质量中国风动画电影风格，中国风水墨仙侠动画风，剑来同款画风，水墨写意，东方审美。，非写实非欧美，2D动画感，单幅画面。"
#     "清晰锐利线稿，线条干净无噪点，高对比光影，画面通透。"
#     "人物为中国风仙侠角色，比例修长，五官精致，衣袍随风流动。"
#     "场景具有中国山水意境，雾气、光影层次分明。"
#     "整体风格参考高质量中国国漫电影（白蛇缘起、雾山五行）。"
#     "色彩统一、干净，不发灰不发脏。"
#     "严格禁止：写实摄影、真实皮肤纹理、3D建模感、欧美风、低质量AI绘画风。"
# )
ANIME_STYLE_LOCK_CN = (
    "风格硬锁：严格中国动漫风 / 国漫风，高质感国风奇幻动画电影风格，东方审美，非水墨写意，非泼墨留白，非欧美写实。"
    "完整单幅电影感关键帧，主体重心明确，构图干净，前景、中景、远景层次清楚，空间纵深强。"
    "体积光、边缘光、环境雾气和场景光影分明，建筑、石阶、植被、服装纹理细节丰富且锐利。"
    "角色比例修长，动作克制有力量，画面像高端动画长片关键帧，不像普通分镜草图。"
    "色彩通透、高对比但不脏不灰。"
    "严格禁止：日式动漫脸、日漫校园风、热血少年漫套版、欧美卡通、韩漫、二次元萌系偶像风、水墨晕染、泼墨效果、低幼插画、Q版、廉价游戏立绘、写实摄影、3D塑料感、欧美风、标题字、水印。"
)
ANIME_STYLE_LOCK_EN = (
    "strict chinese anime style, guoman style, cinematic chinese fantasy animation, premium keyframe illustration, clear subject dominance, "
    "layered foreground midground background, strong depth and perspective, volumetric light, rim light, "
    "atmospheric perspective, clean detailed environment, crisp costume details, non-photorealistic, "
    "not japanese anime style, not western cartoon, not ink wash, not minimalist watercolor"
)
CHARACTER_STYLE_LOCK_CN = (
    "风格硬锁：严格中国动漫风 / 国漫风角色设定图，线稿干净锐利，色彩通透，服装与配饰细节完整，非写实摄影，非欧美卡通。"
)
CHARACTER_STYLE_LOCK_EN = (
    "strict chinese anime style, guoman character design sheet, clean lineart, crisp details, non-photorealistic, not western cartoon, not japanese school anime"
)
CHARACTER_THREE_VIEW_LOCK_CN = (
    "硬性输出：同一角色三视图（正面、左侧面、背面）完整全身，三视图等比例并排。"
    "背景必须纯白色（#FFFFFF），不添加场景、地面、道具、文字、水印、UI。"
)
CHARACTER_THREE_VIEW_LOCK_EN = (
    "must output one character turnaround sheet with full-body front view, left side view, and back view; "
    "same character identity and proportions; pure white background (#FFFFFF); no scene props text watermark or UI"
)


def _pick_model(config, default_model="gpt-4"):
    return str(config.get("model") or default_model)


def _pick_api_key(config):
    return str(config.get("api_key") or os.getenv("OPENAI_API_KEY", ""))


def _pick_temperature(config):
    try:
        value = float(config.get("temperature", 0.7))
    except (TypeError, ValueError):
        value = 0.7
    return max(0.0, min(2.0, value))


def _pick_sdk_type(config):
    return str(config.get("sdk_type") or "openai").lower()


def _pick_base_url(config):
    return str(config.get("base_url") or "").strip()


def _pick_max_tokens(config, default_value=220):
    try:
        value = int(config.get("max_tokens", default_value))
    except (TypeError, ValueError):
        value = default_value
    return max(64, min(320, value))


def _normalize_context(context):
    return context if isinstance(context, dict) else {}


def _normalize_frame_key(frame_key):
    text = str(frame_key or "").strip().lower().replace("-", "_")
    if text in {"startframe", "start_frame", "first_frame", "opening_frame"}:
        return "startFrame"
    if text in {"endframe", "end_frame", "last_frame", "closing_frame"}:
        return "endFrame"
    return ""


def _is_single_frame_scene(kind, context=None):
    context = _normalize_context(context)
    frame_key = _normalize_frame_key(context.get("frame_key"))
    prompt_type = str(context.get("prompt_type") or "").strip().lower()
    return kind != "character" and (prompt_type == "frame" or bool(frame_key))


def _strip_storyboard_prompt_details(text):
    value = str(text or "").strip()
    if not value:
        return ""

    for marker in (
        "剧情细节参考：",
        "剧情细节参考:",
        "详细剧情：",
        "详细剧情:",
        "分镜调度：",
        "分镜调度:",
        "镜头部署：",
        "镜头部署:",
        "shot plan:",
        "shot plan：",
    ):
        idx = value.find(marker)
        if idx > 0:
            value = value[:idx]
            break

    value = re.sub(r"(?im)^\s*\d+\s*[\.、\)]\s*", "", value)
    value = re.sub(r"\|\s*台词:[^|，。\n]*", "", value)
    value = re.sub(r"\|\s*\d+(?:\.\d+)?s\b", "", value, flags=re.IGNORECASE)
    value = re.sub(r"(分镜调度|镜头部署|详细剧情|剧情细节参考)\s*[:：]?", "", value, flags=re.IGNORECASE)
    value = value.replace("\n", "，")
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"[,，]{2,}", "，", value)
    return value.strip("，,;； ")


def _normalize_hint_text(value):
    if isinstance(value, (list, tuple, set)):
        merged = "；".join(str(item or "").strip() for item in value if str(item or "").strip())
    else:
        merged = str(value or "").strip()
    return _strip_storyboard_prompt_details(merged)


def _normalize_name_list(raw_value):
    if isinstance(raw_value, (list, tuple, set)):
        candidates = raw_value
    else:
        text = str(raw_value or "").strip()
        if not text:
            return []
        candidates = re.split(r"[、,，;；/|]+", text)

    names = []
    for item in candidates:
        name = str(item or "").strip()
        if not name:
            continue
        if name in names:
            continue
        names.append(name)
    return names[:8]


def _collect_bound_character_names(context):
    names = []
    if not isinstance(context, dict):
        return names

    for key in ("bound_character_names", "character_names", "boundCharacterNames", "characterNames"):
        for name in _normalize_name_list(context.get(key)):
            if name not in names:
                names.append(name)

    bindings = context.get("character_binding") or context.get("characterBinding")
    if isinstance(bindings, (list, tuple)):
        for item in bindings:
            if not isinstance(item, dict):
                continue
            for field in ("character_name", "characterName", "name"):
                name = str(item.get(field) or "").strip()
                if name and name not in names:
                    names.append(name)
    return names[:8]


def _build_character_binding_hint(context):
    context = _normalize_context(context)
    if not context:
        return ""

    names = _collect_bound_character_names(context)
    character_hints = _normalize_hint_text(context.get("character_hints"))
    identity_rules = _normalize_hint_text(context.get("character_identity_rules"))

    parts = []
    if names:
        parts.append(
            f"角色绑定：{'、'.join(names)}。必须保持这些角色身份、脸型、发型、服饰、配色与站位逻辑一致，不得替换、合并或遗漏。"
        )
    if character_hints:
        parts.append(f"角色外观线索：{character_hints}")
    if identity_rules:
        parts.append(f"角色身份约束：{identity_rules}")
    return " ".join(parts).strip()


def _build_direct_single_frame_prompt(description, context=None):
    context = _normalize_context(context)
    frame_key = _normalize_frame_key(context.get("frame_key"))
    cleaned = _strip_storyboard_prompt_details(description)
    parts = [cleaned] if cleaned else []
    scene_description = _strip_storyboard_prompt_details(context.get("scene_description"))
    shot_summary = _strip_storyboard_prompt_details(context.get("shot_summary"))
    detailed_shot_description = _strip_storyboard_prompt_details(context.get("detailed_shot_description"))
    previous_summary = _strip_storyboard_prompt_details(context.get("previous_shot_summary"))
    next_summary = _strip_storyboard_prompt_details(context.get("next_shot_summary"))
    scene_hints = _normalize_hint_text(context.get("scene_hints"))
    continuity_rules = _normalize_hint_text(context.get("continuity_rules"))
    character_binding_hint = _build_character_binding_hint(context)
    narration_text = _normalize_hint_text(
        context.get("narration_text")
        or context.get("voiceover_text")
        or context.get("voiceoverText")
    )

    if scene_description and scene_description not in parts:
        parts.append(f"场次剧情：{scene_description}")
    if shot_summary and shot_summary not in parts:
        parts.append(f"镜头概述：{shot_summary}")
    if detailed_shot_description and detailed_shot_description not in parts:
        parts.append(f"详细分镜：{detailed_shot_description}")
    if previous_summary:
        parts.append(f"承接上一镜头：{previous_summary}")
    if next_summary:
        parts.append(f"衔接下一镜头：{next_summary}")
    if scene_hints:
        parts.append(f"场景绑定线索：{scene_hints}")
    if character_binding_hint:
        parts.append(character_binding_hint)
    if narration_text:
        parts.append(f"旁白语义：{narration_text}")
    if continuity_rules:
        parts.append(f"连续性规则：{continuity_rules}")

    if frame_key == "startFrame":
        parts.append("只表现当前镜头开场这一瞬间，不要同时画出后续动作阶段。")
    elif frame_key == "endFrame":
        parts.append("只表现当前镜头收束这一瞬间，不要把起始状态和结束状态并列展示。")
    else:
        parts.append("只表现当前镜头的一个时刻，不要做连续分镜排版。")
    parts.append("优先采用高质感电影关键帧构图：主体重心明确，空间纵深强，光线从场景深处打入，环境叙事信息完整。")
    parts.append(ANIME_STYLE_LOCK_CN)
    parts.append(ANIME_STYLE_LOCK_EN)

    return "，".join(part for part in parts if part).strip("，")


def _build_prompt(description, kind, context=None):
    context = _normalize_context(context)
    frame_key = _normalize_frame_key(context.get("frame_key"))
    is_single_frame_scene = _is_single_frame_scene(kind, context)
    scene_hints = _normalize_hint_text(context.get("scene_hints"))
    character_binding_hint = _build_character_binding_hint(context)
    continuity_rules = _normalize_hint_text(context.get("continuity_rules"))
    narration_text = _normalize_hint_text(
        context.get("narration_text")
        or context.get("voiceover_text")
        or context.get("voiceoverText")
    )

    if kind == "character":
        subject = "角色三视图设定图"
    elif frame_key == "startFrame":
        subject = "起始帧单帧关键画面"
    elif frame_key == "endFrame":
        subject = "结束帧单帧关键画面"
    elif is_single_frame_scene:
        subject = "单帧关键画面"
    else:
        subject = "场景关键帧"

    if kind == "character":
        style_hint = "保留人物外貌、服饰、表情、发型和时代质感，统一严格中国动漫风 / 国漫风角色设定风格。"
        extra_rules = (
            "输出同一角色三视图设定图提示词：正面、左侧面、背面，完整全身，三视图等比例并排。"
            "背景必须纯白色（white background, #FFFFFF），只保留人物，不要场景、地面、道具。"
            "禁止文字标注、水印、logo、UI。"
            "允许仅用于三视图排布，不要漫画分镜板、多故事格拼贴、contact sheet。"
        )
    else:
        style_hint = "保留环境布局、空间关系、镜头构图、光影氛围和动作方向，统一严格中国动漫风 / 国漫风美术风格。"
        extra_rules = (
            "只输出当前镜头的单幅关键帧提示词，只允许一个时刻、一张完整画面、一个主要构图。"
            "严禁多宫格、分镜板、上下拼接、左右拼接、三联画、四宫格、九宫格、拼贴、contact sheet、漫画页、字幕文字、水印和UI元素。"
            "不要把起始帧和结束帧同时放进同一张图，不要做前后对比排版。"
            if is_single_frame_scene
            else "输出场景关键帧的单幅画面提示词，只允许一张完整画面。禁止分屏、多格漫画、拼贴、字幕文字、水印、漫画页排版和UI元素。"
        )
        if scene_hints:
            extra_rules += f" 场景绑定线索：{scene_hints}。"
        if character_binding_hint:
            extra_rules += f" {character_binding_hint}"
        if narration_text:
            extra_rules += f" 旁白语义：{narration_text}。"
        if continuity_rules:
            extra_rules += f" 连续性规则：{continuity_rules}。"
    return (
        "你是中国动漫风 / 国漫风概念设计提示词工程师。"
        "请把输入描述改写为可直接用于文生图的高质量中文提示词。"
        f"目标主体：{subject}。"
        f"输入描述：{description}。"
        f"要求：{style_hint}{extra_rules}"
        "必须严格锁定中国动漫风，禁止改写成日漫、欧美动画、写实摄影或水墨写意风。"
        "只返回严格 JSON，对象仅包含一个字段：prompt。"
    )


def _parse_prompt_json(content):
    try:
        payload = json.loads(content)
        prompt = payload.get("prompt") if isinstance(payload, dict) else None
        if isinstance(prompt, str) and prompt.strip():
            return prompt.strip()
    except Exception:
        pass
    return str(content).strip()


def _normalize_reference_images(reference_images):
    if not isinstance(reference_images, (list, tuple)):
        return []
    normalized = []
    for item in reference_images:
        text = str(item or "").strip()
        if not text:
            continue
        if not (text.startswith("http://") or text.startswith("https://")):
            continue
        if text not in normalized:
            normalized.append(text)
    return normalized[:6]


def _build_reference_locked_prompt(prompt, kind, reference_count, context=None):
    base = str(prompt or "").strip()
    if not base:
        base = "严格中国动漫风 / 国漫风单幅画面"
    context = _normalize_context(context)
    frame_key = _normalize_frame_key(context.get("frame_key"))
    single_frame_scene = _is_single_frame_scene(kind, context)
    character_binding_hint = _build_character_binding_hint(context)
    narration_text = _normalize_hint_text(
        context.get("narration_text")
        or context.get("voiceover_text")
        or context.get("voiceoverText")
    )

    if kind == "character":
        instruction = (
            "把输入图片作为角色身份参考，保留角色五官、发型、服饰、配色和整体气质。"
            "必须输出同一角色三视图（正面、左侧面、背面）完整全身，三视图比例一致。"
            "背景必须纯白色（#FFFFFF），不添加场景、地面、道具、文字、水印。"
            "不要改人设，不要增加其他角色。"
        )
    elif single_frame_scene:
        instruction = (
            "把输入图片作为同一镜头连续性参考，保留同一角色身份、同一场景背景、同一构图重心和同一机位方向。"
            "只允许微动作变化（幅度不超过30%），保持主体位置稳定，禁止更换景别、重构空间或跳变背景。"
            "输出单幅高质感国风动画电影关键帧，主体明确，空间纵深强，体积光和环境细节清楚。"
            "禁止分屏、多格漫画、拼贴、字幕文字和水印。"
        )
        if frame_key == "endFrame":
            instruction += " 该图是结束帧，必须与参考起始帧保持same scene、same background、consistent composition、smooth transition。"
        elif frame_key == "startFrame":
            instruction += " 该图是起始帧，需保持与连续镜头的角色外观和空间关系一致。"
    else:
        instruction = (
            "把输入图片作为角色与场景风格参考，保留人物身份、服饰体系、时代氛围、建筑材质、色调和光线方向。"
            "必须按照当前镜头描述重新组织动作、景别和构图，不要照抄同一机位、同一姿态和同一画面布局。"
            "输出单幅严格中国动漫风 / 国漫风关键帧，保持同一场景与同一角色连续性，不要分屏、多格漫画、拼贴、字幕文字和水印。"
        )
    if character_binding_hint:
        instruction += f" {character_binding_hint}"
    if narration_text:
        instruction += f" 旁白语义：{narration_text}"

    if reference_count > 1:
        if single_frame_scene:
            instruction += " 以第一张参考图作为构图主锚点，其余参考图用于补充角色外观一致性。"
        else:
            instruction += " 以第一张参考图作为主参考，其余参考图用于补充角色造型一致性。"

    return f"{instruction}\n{base}".strip()


def _enforce_single_frame_prompt(prompt, kind, context=None):
    base = str(prompt or "").strip()
    context = _normalize_context(context)
    frame_key = _normalize_frame_key(context.get("frame_key"))
    is_single_frame_scene = _is_single_frame_scene(kind, context)

    if kind == "character":
        hard_rules = (
            "硬性要求：只生成同一角色三视图设定图（正面、左侧面、背面），完整全身，三视图等比例并排。"
            "背景必须纯白色（white background, #FFFFFF），不得出现阴影地台、渐变背景、场景元素。"
            "除三视图排布外，禁止漫画分镜、多故事格、拼贴、字幕、水印、UI和设定表文字。"
        )
    elif is_single_frame_scene:
        frame_label = "起始帧" if frame_key == "startFrame" else ("结束帧" if frame_key == "endFrame" else "当前帧")
        hard_rules = (
            f"硬性要求：只生成{frame_label}这一张完整画面，只表现当前镜头的一个时刻。"
            "不能做多宫格、连环画、分镜板、拼图、上下分栏、左右分栏、三联画、四宫格、九宫格、角色表、设定表、contact sheet、漫画页。"
            "不要把起始状态和结束状态同时放在同一张图里，不要出现前后对比布局。"
            "整幅画面不能出现分隔线、边框、黑边缩略图、上下拼接预览条、左右对比栏。"
            "画面中禁止字幕、台词文字、水印、UI元素。"
        )
    else:
        hard_rules = (
            "硬性要求：只生成一张完整电影感画面，只表现一个时刻。"
            "禁止多宫格、拼贴、分镜板、三联画、四宫格、九宫格、漫画页、字幕、文字、水印和UI元素。"
        )

    return f"{base}\n{hard_rules}".strip() if base else hard_rules


def _enforce_character_three_view_prompt(prompt):
    base = str(prompt or "").strip()
    if not base:
        return f"{CHARACTER_THREE_VIEW_LOCK_CN}\n{CHARACTER_THREE_VIEW_LOCK_EN}"

    normalized = base.lower()
    extra_lines = []
    if not any(token in base for token in ("三视图", "正面", "侧面", "背面")):
        extra_lines.append(CHARACTER_THREE_VIEW_LOCK_CN)
    if not any(token in normalized for token in ("three view", "front view", "side view", "back view", "white background")):
        extra_lines.append(CHARACTER_THREE_VIEW_LOCK_EN)
    if not extra_lines:
        return base
    return f"{base}\n" + "\n".join(extra_lines)


def _enforce_anime_style_prompt(prompt, kind="scene"):
    base = str(prompt or "").strip()
    if str(kind or "").strip().lower() == "character":
        cn_lock = CHARACTER_STYLE_LOCK_CN
        en_lock = CHARACTER_STYLE_LOCK_EN
        cn_tokens = ("严格中国动漫风", "国漫风", "角色设定")
        en_tokens = ("strict chinese anime style", "guoman", "character design sheet")
    else:
        cn_lock = ANIME_STYLE_LOCK_CN
        en_lock = ANIME_STYLE_LOCK_EN
        cn_tokens = ("严格中国动漫风", "中国动漫风", "国漫风")
        en_tokens = ("strict chinese anime style", "guoman style")

    if not base:
        return f"{cn_lock}\n{en_lock}"

    normalized = base.lower()
    extra_lines = []
    if not any(token in base for token in cn_tokens):
        extra_lines.append(cn_lock)
    if not any(token in normalized for token in en_tokens):
        extra_lines.append(en_lock)
    if not extra_lines:
        return base
    return f"{base}\n" + "\n".join(extra_lines)


def _generate_image(api_key, model, image_prompt, sdk_type, base_url="", reference_images=None):
    references = _normalize_reference_images(reference_images)
    if str(sdk_type or "").lower() == "openai":
        return openai_generate_image(
            api_key,
            model,
            image_prompt,
            size="2k",
            base_url=base_url,
            reference_images=references,
        )
    if str(sdk_type or "").lower() == "nono":
        return generate_nonoImage(
            api_key,
            model,
            image_prompt,
        )
    return doubao_generate_image(
        api_key,
        model,
        image_prompt,
        size="2k",
        base_url=base_url,
        reference_images=references,
    )


def _is_sensitive_content_error(error_message):
    text = str(error_message or "").lower()
    if not text:
        return False
    return any(flag in text for flag in SENSITIVE_ERROR_HINTS)


def _build_safe_prompt(prompt, kind):
    base = str(prompt or "").strip()
    if not base:
        base = "严格中国动漫风 / 国漫风单幅场景"

    safety_suffix = (
        "仅使用克制、安全的画面表达。"
        "不要裸露、性暗示、未成年人敏感内容、自残、血腥、断肢或露骨暴力。"
        "保留氛围、表情、构图、光影和环境细节。"
    )
    if kind == "character":
        safety_suffix += (
            " 角色需完整着装，姿态自然，不做挑逗化呈现。"
            " 保持同一角色三视图（正面、左侧面、背面）完整全身，背景纯白色（#FFFFFF）。"
        )
    else:
        safety_suffix += " 保持单幅画面，不要分屏、多格漫画、拼贴和文字叠加。"

    return f"{base}\n{safety_suffix}"


def _humanize_sensitive_error(original_error):
    return (
        "触发平台内容安全拦截（OutputImageSensitiveContentDetected）。"
        "请弱化暴力、血腥、裸露或未成年人敏感元素，改写为更克制的镜头表达。"
        f" 原始错误: {str(original_error or '').strip()}"
    )


def _generate_visual(description, llm_config, kind, reference_images=None, prefer_img2img=False, context=None):
    config = llm_config or {}
    context = _normalize_context(context)
    model = _pick_model(config)
    api_key = _pick_api_key(config)
    temperature = _pick_temperature(config)
    sdk_type = _pick_sdk_type(config)
    base_url = _pick_base_url(config)
    prompt_max_tokens = _pick_max_tokens(config, default_value=220)
    normalized_references = _normalize_reference_images(reference_images)
    use_reference_generation = bool(prefer_img2img and normalized_references)
    effective_generation_references = normalized_references if use_reference_generation else []

    if normalized_references and not use_reference_generation:
        print("[asset_manager] reference images received but prefer_img2img=false; force text-to-image mode")

    if not description or not str(description).strip():
        return {"success": False, "error": "description is required", "prompt": "", "image_url": ""}
    description = str(description).strip()

    if _is_single_frame_scene(kind, context):
        image_prompt = _build_direct_single_frame_prompt(description, context)
        print("[asset_manager] skip prompt rewrite for single-frame scene")
    else:
        llm_started = time.perf_counter()
        completion = general_chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": "你是中国动漫风 / 国漫风影视项目的提示词工程师，擅长把镜头描述改写成稳定、统一、可执行的单幅关键帧提示词。",
                },
                {"role": "user", "content": _build_prompt(description, kind, context)},
            ],
            temperature=temperature,
            max_tokens=prompt_max_tokens,
        )
        llm_elapsed = time.perf_counter() - llm_started
        print(f"[asset_manager] prompt rewrite latency: {llm_elapsed:.2f}s kind={kind} max_tokens={prompt_max_tokens}")

        if completion.get("success"):
            image_prompt = _parse_prompt_json(completion.get("content", ""))
        else:
            image_prompt = description
    if use_reference_generation:
        image_prompt = _build_reference_locked_prompt(
            image_prompt,
            kind,
            len(effective_generation_references),
            context=context,
        )
    if kind == "character":
        image_prompt = _enforce_character_three_view_prompt(image_prompt)
    image_prompt = _enforce_single_frame_prompt(image_prompt, kind, context)
    image_prompt = _enforce_anime_style_prompt(image_prompt, kind=kind)

    image_started = time.perf_counter()
    image_result = _generate_image(
        api_key,
        model,
        image_prompt,
        sdk_type,
        base_url=base_url,
        reference_images=effective_generation_references,
    )
    image_elapsed = time.perf_counter() - image_started
    print(f"[asset_manager] image generation latency: {image_elapsed:.2f}s kind={kind}")
    print(f"LLM completion image_result: {image_result}")
    if image_result.get("success") and image_result.get("image_url"):
        result = {"success": True, "prompt": image_prompt, "image_url": image_result["image_url"]}
        if effective_generation_references:
            result["reference_images"] = effective_generation_references
        if image_result.get("reference_image_used"):
            result["reference_image_used"] = image_result["reference_image_used"]
        if image_result.get("generation_mode"):
            result["generation_mode"] = image_result["generation_mode"]
        return result

    original_error = str(image_result.get("error") or "image generation failed")

    if _is_sensitive_content_error(original_error):
        safe_prompt = _build_safe_prompt(image_prompt, kind)
        print("[asset_manager] sensitive content detected, retrying with safe prompt")
        retry_started = time.perf_counter()
        if use_reference_generation:
            safe_prompt = _build_reference_locked_prompt(
                safe_prompt,
                kind,
                len(effective_generation_references),
                context=context,
            )
        if kind == "character":
            safe_prompt = _enforce_character_three_view_prompt(safe_prompt)
        safe_prompt = _enforce_single_frame_prompt(safe_prompt, kind, context)
        safe_prompt = _enforce_anime_style_prompt(safe_prompt, kind=kind)
        retry_result = _generate_image(
            api_key,
            model,
            safe_prompt,
            sdk_type,
            base_url=base_url,
            reference_images=effective_generation_references,
        )
        retry_elapsed = time.perf_counter() - retry_started
        print(f"[asset_manager] safety retry latency: {retry_elapsed:.2f}s kind={kind}")
        print(f"[asset_manager] safety retry result: {retry_result}")
        if retry_result.get("success") and retry_result.get("image_url"):
            result = {
                "success": True,
                "prompt": safe_prompt,
                "image_url": retry_result["image_url"],
                "safety_retry": True,
            }
            if effective_generation_references:
                result["reference_images"] = effective_generation_references
            if retry_result.get("reference_image_used"):
                result["reference_image_used"] = retry_result["reference_image_used"]
            if retry_result.get("generation_mode"):
                result["generation_mode"] = retry_result["generation_mode"]
            return result

        return {
            "success": False,
            "error": _humanize_sensitive_error(original_error),
            "prompt": safe_prompt,
            "image_url": "",
        }

    result = {
        "success": False,
        "error": original_error,
        "prompt": image_prompt,
        "image_url": "",
    }
    if effective_generation_references:
        result["reference_images"] = effective_generation_references
    if image_result.get("raw_response"):
        result["raw_response"] = image_result["raw_response"]
    return result


def generate_character(description, llm_config=None):
    return _generate_visual(description, llm_config, kind="character")


def generate_scene(description, llm_config=None, reference_images=None, prefer_img2img=False, context=None):
    return _generate_visual(
        description,
        llm_config,
        kind="scene",
        reference_images=reference_images,
        prefer_img2img=prefer_img2img,
        context=context,
    )
