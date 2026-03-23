import json
import re

from modules.llm_config import get_llm_config
from modules.openai_client import chat_completion


def _safe_text(value):
    return str(value or '').strip()


def _first_non_empty(*values):
    for value in values:
        text = _safe_text(value)
        if text:
            return text
    return ''


def _normalize_voiceover_text(text):
    value = _safe_text(text)
    if not value:
        return ''

    value = value.replace('\r', '\n')
    value = re.sub(r'^\s*(旁白|解说)\s*[：:]\s*', '', value)
    value = re.sub(r'^\s*["“”\'`]+|["“”\'`]+\s*$', '', value)
    value = re.sub(r'\n{3,}', '\n\n', value)
    value = re.sub(r'[ \t]+', ' ', value).strip()
    value = value.strip('，,;；')

    if len(value) > 120:
        value = value[:120].rstrip('，,;；、') + '。'
    if value and value[-1] not in '。！？!?':
        value += '。'
    return value


def _build_fallback_voiceover_text(prompt_text, context=None):
    context = context or {}
    subject = _first_non_empty(
        context.get('subject_name'),
        context.get('shot_title'),
        context.get('name'),
    ) or '主角'
    story_context = _first_non_empty(
        context.get('story_context'),
        context.get('scene_script'),
        context.get('detailed_plot'),
        context.get('shot_summary'),
        prompt_text,
    )
    summary = _first_non_empty(
        context.get('detailed_plot'),
        context.get('scene_script'),
        context.get('shot_summary'),
        context.get('action_details'),
        context.get('dialogue_details'),
        prompt_text,
    )
    prev_state = _first_non_empty(
        context.get('prev_state'),
        context.get('previous_state'),
        context.get('start_frame_goal'),
    )
    target_state = _first_non_empty(
        context.get('target_state'),
        context.get('end_frame_goal'),
        context.get('end_frame_description'),
    )
    continuity_hint = _first_non_empty(
        context.get('continuity_hint'),
        context.get('next_shot_summary'),
    )
    emotion_arc = _first_non_empty(
        context.get('mood'),
        context.get('emotion_arc'),
        context.get('emotionArc'),
    )
    summary = re.sub(r'[\r\n]+', '，', summary)
    summary = re.sub(r'[，,]{2,}', '，', summary).strip('，,;； ')
    story_context = re.sub(r'[\r\n]+', '，', story_context)
    story_context = re.sub(r'[，,]{2,}', '，', story_context).strip('，,;； ')

    if not summary and not story_context:
        return '风云将起，命运在这一刻悄然改写。'

    lead = story_context or summary
    if len(summary) > 44:
        summary = summary[:44].rstrip('，,;；、') + '…'
    if len(lead) > 48:
        lead = lead[:48].rstrip('，,;；、') + '…'

    sentence_parts = []
    if subject and subject not in lead:
        sentence_parts.append(f'{subject}正被卷入一场关键变化')
    else:
        sentence_parts.append(lead)
    if prev_state and target_state:
        sentence_parts.append(f'从{prev_state[:16]}走向{target_state[:16]}')
    elif summary:
        sentence_parts.append(summary)

    if continuity_hint:
        sentence_parts.append(f'下一步会{continuity_hint[:20]}')
    elif emotion_arc:
        sentence_parts.append(f'情绪正在{emotion_arc[:18]}')
    else:
        sentence_parts.append('局势正在悄然转向')

    base = '，'.join(sentence_parts)
    return _normalize_voiceover_text(base)


def _build_fallback_enhanced_prompt(prompt_text, context=None):
    context = context or {}
    prompt_type = _safe_text(context.get('prompt_type') or context.get('type')).lower()
    asset_type = _safe_text(context.get('asset_type')).lower()
    visual_style = _safe_text(context.get('visual_style')) or '严格中国动漫风 / 国漫风，高质感国风奇幻动画电影感，主体明确，空间纵深强，体积光明显，美术风格统一'
    detailed_plot = _safe_text(context.get('detailed_plot'))
    shot_deployment = _safe_text(context.get('shot_deployment'))
    action_details = _safe_text(context.get('action_details'))
    dialogue_details = _safe_text(context.get('dialogue_details'))
    continuity_rules = _safe_text(context.get('continuity_rules'))
    wardrobe = _safe_text(context.get('wardrobe'))
    subject_name = _safe_text(context.get('subject_name') or context.get('name'))
    narration_text = _safe_text(
        context.get('narration_text')
        or context.get('voiceover_text')
        or context.get('voiceoverText')
    )
    character_identity_rules = _safe_text(context.get('character_identity_rules'))
    raw_bound_names = context.get('bound_character_names') or context.get('boundCharacterNames')
    if isinstance(raw_bound_names, (list, tuple, set)):
        bound_character_names = '、'.join(
            _safe_text(item) for item in raw_bound_names if _safe_text(item)
        )
    else:
        bound_character_names = _safe_text(raw_bound_names)

    parts = [visual_style]
    if subject_name:
        parts.append(f'主体：{subject_name}')
    parts.append(prompt_text)
    if bound_character_names:
        parts.append(f'绑定角色：{bound_character_names}')
    if character_identity_rules:
        parts.append(f'角色身份约束：{character_identity_rules}')
    if narration_text:
        parts.append(f'旁白语义：{narration_text}')

    if prompt_type == 'character_asset' or asset_type == 'character':
        parts.append('角色设定图，单幅完整构图，人物五官、发型、服饰和气质清晰稳定')
        if wardrobe:
            parts.append(f'造型要求：{wardrobe}')
        parts.append('禁止分屏、拼贴、文字、水印、漫画页排版')
    elif prompt_type in {'shot_plan', 'shot', 'director_shot'}:
        parts.append('单镜头分镜提示词，明确景别、机位、主体动作、空间关系、情绪推进和起止帧衔接')
        parts.append('只描述当前镜头片段，不写成整场戏，不做分屏、多镜头拼贴、字幕、水印或UI元素')
    elif prompt_type in {'scene_asset', 'frame', 'keyframe'} or asset_type == 'scene':
        parts.append('单幅关键帧画面，构图完整，场景空间明确')
        parts.append('禁止分屏、多格漫画、拼贴、字幕、水印、UI元素')
    else:
        parts.append('画面构图明确，主体清晰，动作与情绪可执行')

    if detailed_plot:
        parts.append(f'详细剧情：{detailed_plot}')
    elif shot_deployment:
        parts.append(f'镜头部署：{shot_deployment}')
    if action_details and action_details != detailed_plot:
        parts.append(f'动作细节：{action_details}')
    if dialogue_details and dialogue_details != detailed_plot:
        parts.append(f'对白细节：{dialogue_details}')
    if continuity_rules:
        parts.append(f'连续性约束：{continuity_rules}')

    return '，'.join(part for part in parts if part).replace('，，', '，').strip('，')


def generate_voiceover(raw_prompt, context=None):
    """
    Generate short Chinese narration text for one shot.
    """
    context = context or {}
    prompt_text = _safe_text(raw_prompt)
    context_seed = _first_non_empty(
        context.get('story_context'),
        context.get('scene_script'),
        context.get('detailed_plot'),
        context.get('shot_summary'),
        context.get('action_details'),
        context.get('dialogue_details'),
        context.get('prev_state'),
        context.get('target_state'),
        context.get('continuity_hint'),
    )
    if not prompt_text and not context_seed:
        return {
            'success': False,
            'error': 'prompt or context is required',
            'voiceover_text': '',
        }

    cfg = get_llm_config('general')
    api_key = cfg.get('api_key', '')
    model = cfg.get('model', 'gpt-4')
    base_url = cfg.get('base_url')
    try:
        configured_temperature = float(cfg.get('temperature', 0.5))
    except (TypeError, ValueError):
        configured_temperature = 0.5
    temperature = max(0.2, min(configured_temperature, 0.8))
    try:
        configured_max_tokens = int(cfg.get('max_tokens', 800) or 800)
    except (TypeError, ValueError):
        configured_max_tokens = 800
    max_tokens = max(180, min(600, configured_max_tokens))

    if not api_key:
        fallback_text = _build_fallback_voiceover_text(prompt_text, context)
        return {
            'success': True,
            'voiceover_text': fallback_text,
            'used_fallback': True,
            'message': 'general api_key is empty, fallback to deterministic narration text',
        }

    system_message = (
        '你是影视导演旁白编剧。'
        '任务是为单个镜头生成中文普通话旁白文案。'
        '旁白必须有故事推进感，体现起承转合、人物处境变化、情绪张力和下一步悬念。'
        '不要只复述画面，不要写成镜头说明书。'
        '只输出严格 JSON，字段必须是 voiceover_text。'
        '要求：18-70字，1-2句，可口播，有画面感，有情绪推进；优先写冲突、变化、结果或悬念，不要镜头术语，不要英文，不要解释。'
    )

    user_payload = {
        'shot_prompt': prompt_text,
        'context': context,
        'constraints': [
            '必须是中文普通话旁白',
            '紧扣当前镜头，但要让故事往前走，不展开整场戏',
            '优先写人物处境、情绪变化、冲突推进、结果或悬念',
            '避免“镜头切换/推拉摇移”等拍摄术语',
            '不输出角色A/角色B占位符',
            '只返回 JSON',
        ],
    }

    result = chat_completion(
        api_key=api_key,
        model=model,
        base_url=base_url,
        messages=[
            {'role': 'system', 'content': system_message},
            {'role': 'user', 'content': json.dumps(user_payload, ensure_ascii=False)},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )

    if not result.get('success'):
        fallback_text = _build_fallback_voiceover_text(prompt_text, context)
        return {
            'success': True,
            'voiceover_text': fallback_text,
            'used_fallback': True,
            'message': result.get('error', 'voiceover generation failed, fallback to deterministic narration text'),
        }

    content = _safe_text(result.get('content'))
    voiceover_text = ''
    try:
        parsed = json.loads(content)
        voiceover_text = _normalize_voiceover_text(parsed.get('voiceover_text'))
    except json.JSONDecodeError:
        voiceover_text = _normalize_voiceover_text(content)

    if voiceover_text:
        return {'success': True, 'voiceover_text': voiceover_text, 'used_fallback': False}

    fallback_text = _build_fallback_voiceover_text(prompt_text, context)
    return {
        'success': True,
        'voiceover_text': fallback_text,
        'used_fallback': True,
        'message': 'voiceover text empty, fallback to deterministic narration text',
    }


def enhance_prompt(raw_prompt, context=None):
    """
    Enhance a raw director prompt using DEFAULT_CONFIG['general'] / general llm config.
    """
    context = context or {}
    prompt_text = _safe_text(raw_prompt)
    if not prompt_text:
        return {
            'success': False,
            'error': 'prompt is required',
            'enhanced_prompt': '',
        }

    cfg = get_llm_config('general')
    api_key = cfg.get('api_key', '')
    model = cfg.get('model', 'gpt-4')
    base_url = cfg.get('base_url')
    temperature = cfg.get('temperature', 0.4)
    max_tokens = min(int(cfg.get('max_tokens', 1000) or 1000), 1200)

    if not api_key:
        fallback_prompt = _build_fallback_enhanced_prompt(prompt_text, context)
        return {
            'success': True,
            'enhanced_prompt': fallback_prompt,
            'used_fallback': True,
            'message': 'general api_key is empty, fallback to deterministic enhanced prompt',
        }

    system_message = (
        'You are a strict Chinese anime style (guoman) prompt engineer. '
        'Rewrite user input into a concise, visual, production-ready prompt. '
        'Preserve subject identity, scene intent, and action continuity. '
        'Keep the result strictly in Chinese anime / guoman style, not Japanese anime, not western cartoon, not photoreal. '
        'If context says character_asset, prioritize stable character design. '
        'If context says shot_plan or shot, prioritize one-shot scope, lensing, blocking, action progression, '
        'emotional beat, and continuity between start and end frames. '
        'If context says frame/keyframe, enforce single-frame composition, no split panels, no collage, no text overlay. '
        'Output strict JSON with one field: enhanced_prompt.'
    )

    user_payload = {
        'raw_prompt': prompt_text,
        'context': context,
        'constraints': [
            'language: same as raw prompt',
            'default style: strict chinese anime style / guoman, cinematic composition, coherent action, clear subject',
            'forbidden drift: japanese anime, western cartoon, photoreal, ink wash minimalism',
            'if prompt_type=shot_plan: keep it as a single-shot prompt, not a full-scene synopsis',
            'include camera/composition/lighting/style details',
            'no markdown, no explanation',
        ],
    }

    result = chat_completion(
        api_key=api_key,
        model=model,
        base_url=base_url,
        messages=[
            {'role': 'system', 'content': system_message},
            {'role': 'user', 'content': json.dumps(user_payload, ensure_ascii=False)},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )

    if not result.get('success'):
        fallback_prompt = _build_fallback_enhanced_prompt(prompt_text, context)
        return {
            'success': True,
            'enhanced_prompt': fallback_prompt,
            'used_fallback': True,
            'message': result.get('error', 'enhance failed, fallback to deterministic enhanced prompt'),
        }

    content = _safe_text(result.get('content'))
    try:
        parsed = json.loads(content)
        enhanced = _safe_text(parsed.get('enhanced_prompt'))
        if enhanced:
            return {'success': True, 'enhanced_prompt': enhanced, 'used_fallback': False}
    except json.JSONDecodeError:
        pass

    return {
        'success': True,
        'enhanced_prompt': content or _build_fallback_enhanced_prompt(prompt_text, context),
        'used_fallback': not bool(content),
    }
