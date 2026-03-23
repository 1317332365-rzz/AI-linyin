# -*- coding: utf-8 -*-
import json
import threading
import time
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, TypeVar

import mysql.connector
from modules.mysql_runtime import get_connection, init_mysql_schema

_LOCK = threading.Lock()
_T = TypeVar('_T')
_RETRYABLE_MYSQL_ERRNOS = {2006, 2013, 2055}
_RETRYABLE_MYSQL_MESSAGES = (
    'lost connection to mysql server',
    'server has gone away',
    'connection reset by peer',
    '10054',
)
_PROJECT_CORE_FIELDS = {
    'id',
    'owner',
    'name',
    'script_title',
    'episode_no',
    'video_provider',
    'createdAt',
    'updatedAt',
    'assets',
    'shots',
    'history',
    'generated_data',
    'episode_scripts',
    'episode_shots',
    'script',
    'created_at',
    'updated_at',
    'payload_json',
}


def _is_retryable_mysql_error(exc: Exception) -> bool:
    if not isinstance(exc, mysql.connector.Error):
        return False
    errno = getattr(exc, 'errno', None)
    if errno in _RETRYABLE_MYSQL_ERRNOS:
        return True
    message = str(exc or '').strip().lower()
    return any(fragment in message for fragment in _RETRYABLE_MYSQL_MESSAGES)


def _run_with_mysql_retry(
    operation: Callable[[Any], _T],
    *,
    operation_name: str,
    retries: int = 1,
) -> _T:
    attempt = 0
    while True:
        conn = None
        try:
            conn = get_connection()
            return operation(conn)
        except Exception as exc:
            if attempt >= retries or not _is_retryable_mysql_error(exc):
                raise
            attempt += 1
            errno = getattr(exc, 'errno', None)
            print(
                f"[mysql_project_store] transient mysql error op={operation_name} "
                f"attempt={attempt}/{retries} errno={errno} message={exc}; retrying"
            )
            time.sleep(0.2)
        finally:
            try:
                if conn is not None:
                    conn.close()
            except Exception:
                pass


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def _normalize_owner(owner: Any) -> str:
    text = str(owner or '').strip()
    return text or 'admin'


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


def _normalize_project(project: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(project, dict):
        project = {}
    script = project.get('script') if isinstance(project.get('script'), dict) else {}
    episode_scripts = _normalize_episode_scripts(project.get('episode_scripts'))
    episode_shots = _normalize_episode_shots(project.get('episode_shots'))
    video_provider = str(project.get('video_provider', 'openai') or 'openai').strip().lower()
    if video_provider not in {'openai', 'jimeng', 'grsai'}:
        video_provider = 'openai'

    try:
        episode_no = max(1, int(project.get('episode_no', 1) or 1))
    except (TypeError, ValueError):
        episode_no = 1

    normalized = {
        'id': str(project.get('id', '') or ''),
        'owner': _normalize_owner(project.get('owner')),
        'name': str(project.get('name', '')).strip() or '未命名项目',
        'script_title': str(project.get('script_title', '')).strip(),
        'episode_no': episode_no,
        'video_provider': video_provider,
        'createdAt': str(project.get('createdAt', _utc_now()) or _utc_now()),
        'updatedAt': str(project.get('updatedAt', _utc_now()) or _utc_now()),
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
    # 保留扩展字段，避免业务新增键在持久化时丢失。
    for key, value in project.items():
        key_text = str(key or '').strip()
        if not key_text or key_text in _PROJECT_CORE_FIELDS:
            continue
        normalized[key_text] = value
    return normalized


def _serialize_payload(project: Dict[str, Any]) -> str:
    return json.dumps(project, ensure_ascii=False, separators=(',', ':'), default=str)


def _deserialize_payload(raw_value: Any) -> Dict[str, Any]:
    text = str(raw_value or '').strip()
    if not text:
        return {}
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


def _row_to_project(row) -> Optional[Dict[str, Any]]:
    if not row:
        return None

    payload = _deserialize_payload(row[6])
    merged = {
        **payload,
        'id': row[0],
        'owner': row[1],
        'name': row[2],
        'script_title': row[3],
        'episode_no': row[4],
        'video_provider': row[5],
        'createdAt': row[7],
        'updatedAt': row[8],
    }
    return _normalize_project(merged)


def _default_project(
    project_id: str,
    name: str,
    script_title: str,
    episode_no: int,
    owner: Optional[str] = None,
) -> Dict[str, Any]:
    now = _utc_now()
    return _normalize_project(
        {
            'id': project_id,
            'owner': _normalize_owner(owner),
            'name': name,
            'script_title': script_title,
            'episode_no': episode_no,
            'video_provider': 'openai',
            'createdAt': now,
            'updatedAt': now,
            'assets': [],
            'shots': [],
            'history': [],
            'generated_data': [],
            'episode_scripts': {},
            'episode_shots': {},
            'script': {
                'input': '',
                'duration': '3min',
                'result': None,
            },
        }
    )


def init_db() -> None:
    init_mysql_schema()


def list_projects(owner: Optional[str] = None) -> List[Dict[str, Any]]:
    normalized_owner = _normalize_owner(owner) if owner is not None else None

    def _operation(conn) -> List[Dict[str, Any]]:
        cursor = None
        try:
            cursor = conn.cursor()
            if normalized_owner is not None:
                cursor.execute(
                    '''
                    SELECT id, owner, name, script_title, episode_no, video_provider, payload_json, created_at, updated_at
                    FROM projects
                    WHERE owner = %s
                    ORDER BY updated_at DESC
                    ''',
                    (normalized_owner,),
                )
            else:
                cursor.execute(
                    '''
                    SELECT id, owner, name, script_title, episode_no, video_provider, payload_json, created_at, updated_at
                    FROM projects
                    ORDER BY updated_at DESC
                    '''
                )
            rows = cursor.fetchall()
            return [project for project in (_row_to_project(row) for row in rows) if project]
        finally:
            if cursor is not None:
                cursor.close()

    with _LOCK:
        return _run_with_mysql_retry(_operation, operation_name='list_projects')


def get_project(project_id: str, owner: Optional[str] = None) -> Optional[Dict[str, Any]]:
    if not project_id:
        return None

    normalized_owner = _normalize_owner(owner) if owner is not None else None

    def _operation(conn) -> Optional[Dict[str, Any]]:
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT id, owner, name, script_title, episode_no, video_provider, payload_json, created_at, updated_at
                FROM projects
                WHERE id = %s
                ''',
                (project_id,),
            )
            project = _row_to_project(cursor.fetchone())
            if not project:
                return None
            if normalized_owner is not None and project.get('owner') != normalized_owner:
                return None
            return project
        finally:
            if cursor is not None:
                cursor.close()

    with _LOCK:
        return _run_with_mysql_retry(_operation, operation_name='get_project')


def create_project(
    project_id: str,
    name: str,
    script_title: str,
    episode_no: int,
    owner: Optional[str] = None,
) -> Dict[str, Any]:
    project = _default_project(project_id, name, script_title, episode_no, owner)

    def _operation(conn) -> None:
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute(
                '''
                INSERT INTO projects (
                    id, owner, name, script_title, episode_no, video_provider, payload_json, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''',
                (
                    project['id'],
                    project['owner'],
                    project['name'],
                    project['script_title'],
                    project['episode_no'],
                    project['video_provider'],
                    _serialize_payload(project),
                    project['createdAt'],
                    project['updatedAt'],
                ),
            )
            conn.commit()
        finally:
            if cursor is not None:
                cursor.close()

    with _LOCK:
        _run_with_mysql_retry(_operation, operation_name='create_project')
    return project


def update_project(project_id: str, payload: Dict[str, Any], owner: Optional[str] = None) -> Optional[Dict[str, Any]]:
    if not project_id:
        return None
    if not isinstance(payload, dict):
        payload = {}

    current = get_project(project_id, owner=owner)
    if not current:
        return None

    merged = {
        **current,
        **payload,
        'id': current.get('id', project_id),
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

    def _operation(conn) -> None:
        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute(
                '''
                UPDATE projects
                SET name = %s,
                    script_title = %s,
                    episode_no = %s,
                    video_provider = %s,
                    payload_json = %s,
                    updated_at = %s
                WHERE id = %s
                ''',
                (
                    normalized['name'],
                    normalized['script_title'],
                    normalized['episode_no'],
                    normalized['video_provider'],
                    _serialize_payload(normalized),
                    normalized['updatedAt'],
                    project_id,
                ),
            )
            conn.commit()
        finally:
            if cursor is not None:
                cursor.close()

    with _LOCK:
        _run_with_mysql_retry(
            _operation,
            operation_name=f'update_project project_id={project_id}',
        )
    return normalized
