import json
import os
import threading
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

DB_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
DB_PATH = os.path.join(DB_DIR, 'projects_db.json')

_LOCK = threading.Lock()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_owner(owner: Any) -> str:
    """
    统一规范项目归属用户，避免空值导致数据泄漏。
    """
    text = str(owner or "").strip()
    return text or "admin"


def _default_store() -> Dict[str, Any]:
    return {'projects': []}


def _normalize_episode_scripts(raw_value: Any) -> Dict[str, Any]:
    if not isinstance(raw_value, dict):
        return {}

    normalized: Dict[str, Any] = {}
    for key, value in raw_value.items():
        if not isinstance(value, dict):
            continue
        script = value.get('script') if isinstance(value.get('script'), dict) else {}
        history = value.get('history') if isinstance(value.get('history'), list) else []
        normalized[str(key)] = {
            'script': {
                'input': str(script.get('input', '') or ''),
                'duration': str(script.get('duration', '3min') or '3min'),
                'result': script.get('result', None),
            },
            'history': history,
        }
    return normalized


def _normalize_episode_shots(raw_value: Any) -> Dict[str, List[Any]]:
    if not isinstance(raw_value, dict):
        return {}
    normalized: Dict[str, List[Any]] = {}
    for key, value in raw_value.items():
        normalized[str(key)] = value if isinstance(value, list) else []
    return normalized


def _read_store() -> Dict[str, Any]:
    os.makedirs(DB_DIR, exist_ok=True)
    if not os.path.exists(DB_PATH):
        return _default_store()

    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, dict) and isinstance(data.get('projects'), list):
            return data
        return _default_store()
    except (json.JSONDecodeError, OSError):
        return _default_store()


def _write_store(store: Dict[str, Any]) -> None:
    os.makedirs(DB_DIR, exist_ok=True)
    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(store, f, ensure_ascii=False, indent=2)


def _normalize_project(project: Dict[str, Any]) -> Dict[str, Any]:
    script = project.get('script') if isinstance(project.get('script'), dict) else {}
    episode_scripts = _normalize_episode_scripts(project.get('episode_scripts'))
    episode_shots = _normalize_episode_shots(project.get('episode_shots'))
    video_provider = str(project.get('video_provider', 'openai') or 'openai').strip().lower()
    if video_provider not in {'openai', 'jimeng', 'grsai'}:
        video_provider = 'openai'

    return {
        'id': str(project.get('id', '')),
        'owner': _normalize_owner(project.get('owner')),
        'name': str(project.get('name', '')).strip() or '未命名项目',
        'script_title': str(project.get('script_title', '')).strip(),
        'episode_no': max(1, int(project.get('episode_no', 1) or 1)),
        'video_provider': video_provider,
        'createdAt': str(project.get('createdAt', _utc_now())),
        'updatedAt': str(project.get('updatedAt', _utc_now())),
        'assets': project.get('assets') if isinstance(project.get('assets'), list) else [],
        'shots': project.get('shots') if isinstance(project.get('shots'), list) else [],
        'history': project.get('history') if isinstance(project.get('history'), list) else [],
        'generated_data': project.get('generated_data') if isinstance(project.get('generated_data'), list) else [],
        'episode_scripts': episode_scripts,
        'episode_shots': episode_shots,
        'script': {
            'input': str(script.get('input', '') or ''),
            'duration': str(script.get('duration', '3min') or '3min'),
            'result': script.get('result', None),
        },
    }


def init_db() -> None:
    with _LOCK:
        store = _read_store()
        _write_store(store)


def list_projects(owner: Optional[str] = None) -> List[Dict[str, Any]]:
    normalized_owner = _normalize_owner(owner) if owner is not None else None
    with _LOCK:
        projects = []
        for raw in _read_store().get('projects', []):
            project = _normalize_project(raw)
            if normalized_owner is not None and project.get('owner') != normalized_owner:
                continue
            projects.append(project)
    projects.sort(key=lambda p: p.get('updatedAt', ''), reverse=True)
    return projects


def get_project(project_id: str, owner: Optional[str] = None) -> Optional[Dict[str, Any]]:
    if not project_id:
        return None
    normalized_owner = _normalize_owner(owner) if owner is not None else None
    with _LOCK:
        for project in _read_store().get('projects', []):
            if str(project.get('id')) != str(project_id):
                continue
            normalized = _normalize_project(project)
            if normalized_owner is not None and normalized.get('owner') != normalized_owner:
                return None
            return normalized
    return None


def create_project(project_id: str, name: str, script_title: str, episode_no: int, owner: Optional[str] = None) -> Dict[str, Any]:
    now = _utc_now()
    new_project = _normalize_project(
        {
            'id': project_id,
            'owner': _normalize_owner(owner),
            'name': name,
            'script_title': script_title,
            'episode_no': episode_no,
            'createdAt': now,
            'updatedAt': now,
        }
    )

    with _LOCK:
        store = _read_store()
        store['projects'].append(new_project)
        _write_store(store)

    return new_project


def update_project(project_id: str, payload: Dict[str, Any], owner: Optional[str] = None) -> Optional[Dict[str, Any]]:
    if not project_id:
        return None
    if not isinstance(payload, dict):
        payload = {}
    normalized_owner = _normalize_owner(owner) if owner is not None else None

    with _LOCK:
        store = _read_store()
        projects = store.get('projects', [])

        for idx, project in enumerate(projects):
            if str(project.get('id')) != str(project_id):
                continue

            current = _normalize_project(project)
            if normalized_owner is not None and current.get('owner') != normalized_owner:
                continue
            merged = {
                **current,
                'owner': current.get('owner'),
                'name': payload.get('name', current['name']),
                'script_title': payload.get('script_title', current['script_title']),
                'episode_no': payload.get('episode_no', current['episode_no']),
                'video_provider': payload.get('video_provider', current.get('video_provider', 'openai')),
                'assets': payload.get('assets', current['assets']),
                'shots': payload.get('shots', current['shots']),
                'history': payload.get('history', current['history']),
                'generated_data': payload.get('generated_data', current['generated_data']),
                'episode_scripts': payload.get('episode_scripts', current.get('episode_scripts', {})),
                'episode_shots': payload.get('episode_shots', current.get('episode_shots', {})),
                'script': payload.get('script', current['script']),
                'updatedAt': _utc_now(),
            }
            normalized = _normalize_project(merged)
            normalized['createdAt'] = current['createdAt']

            projects[idx] = normalized
            store['projects'] = projects
            _write_store(store)
            return normalized

    return None
