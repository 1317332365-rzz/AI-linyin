# -*- coding: utf-8 -*-
"""
MySQL数据存储模块
提供与project_store.py兼容的API，但使用MySQL作为后端
"""
import json
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import threading

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'ai_gender_db'
}

_LOCK = threading.Lock()


def get_connection():
    """获取数据库连接"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"数据库连接错误: {e}")
        raise


def _utc_now() -> str:
    """获取当前UTC时间"""
    return datetime.now(timezone.utc).isoformat()


def _normalize_owner(owner: Any) -> str:
    """规范化项目所有者"""
    text = str(owner or "").strip()
    return text or "admin"


def _normalize_episode_scripts(raw_value: Any) -> Dict[str, Any]:
    """规范化剧集脚本"""
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
    """规范化剧集镜头"""
    if not isinstance(raw_value, dict):
        return {}
    normalized: Dict[str, List[Any]] = {}
    for key, value in raw_value.items():
        normalized[str(key)] = value if isinstance(value, list) else []
    return normalized


def _normalize_project(project: Dict[str, Any]) -> Dict[str, Any]:
    """规范化项目数据"""
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
    """初始化数据库连接"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        print("✓ MySQL数据库连接成功")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")


def list_projects(owner: Optional[str] = None) -> List[Dict[str, Any]]:
    """获取项目列表"""
    normalized_owner = _normalize_owner(owner) if owner is not None else None
    
    with _LOCK:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            if normalized_owner:
                query = "SELECT * FROM projects WHERE owner = %s ORDER BY updated_at DESC"
                cursor.execute(query, (normalized_owner,))
            else:
                query = "SELECT * FROM projects ORDER BY updated_at DESC"
                cursor.execute(query)
            
            rows = cursor.fetchall()
            projects = []
            
            for row in rows:
                project = {
                    'id': row[0],
                    'owner': row[1],
                    'name': row[2],
                    'script_title': row[3],
                    'episode_no': row[4],
                    'video_provider': row[5],
                    'createdAt': str(row[6]),
                    'updatedAt': str(row[7]),
                    'assets': _get_project_assets(row[0]),
                    'shots': _get_project_shots(row[0]),
                    'history': _get_project_history(row[0]),
                    'generated_data': _get_project_generated_data(row[0]),
                    'episode_scripts': _get_episode_scripts(row[0]),
                    'episode_shots': {},
                    'script': _get_project_script(row[0]),
                }
                projects.append(_normalize_project(project))
            
            cursor.close()
            conn.close()
            return projects
            
        except Error as e:
            print(f"Error listing projects: {e}")
            return []


def get_project(project_id: str, owner: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """获取单个项目"""
    if not project_id:
        return None
    
    normalized_owner = _normalize_owner(owner) if owner is not None else None
    
    with _LOCK:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = "SELECT * FROM projects WHERE id = %s"
            cursor.execute(query, (project_id,))
            row = cursor.fetchone()
            
            if not row:
                cursor.close()
                conn.close()
                return None
            
            project = {
                'id': row[0],
                'owner': row[1],
                'name': row[2],
                'script_title': row[3],
                'episode_no': row[4],
                'video_provider': row[5],
                'createdAt': str(row[6]),
                'updatedAt': str(row[7]),
                'assets': _get_project_assets(row[0]),
                'shots': _get_project_shots(row[0]),
                'history': _get_project_history(row[0]),
                'generated_data': _get_project_generated_data(row[0]),
                'episode_scripts': _get_episode_scripts(row[0]),
                'episode_shots': {},
                'script': _get_project_script(row[0]),
            }
            
            if normalized_owner and project.get('owner') != normalized_owner:
                cursor.close()
                conn.close()
                return None
            
            normalized = _normalize_project(project)
            cursor.close()
            conn.close()
            return normalized
            
        except Error as e:
            print(f"Error getting project: {e}")
            return None


def create_project(project_id: str, name: str, script_title: str, episode_no: int, owner: Optional[str] = None) -> Dict[str, Any]:
    """创建新项目"""
    now = _utc_now()
    normalized_owner = _normalize_owner(owner)
    
    with _LOCK:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = """
                INSERT INTO projects (id, owner, name, script_title, episode_no, video_provider, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (project_id, normalized_owner, name or '未命名项目', script_title, episode_no, 'openai', now, now))
            conn.commit()
            cursor.close()
            conn.close()
            
        except Error as e:
            print(f"Error creating project: {e}")
    
    return get_project(project_id, normalized_owner) or {}


def update_project(project_id: str, **kwargs) -> Dict[str, Any]:
    """更新项目"""
    if not project_id:
        return {}
    
    with _LOCK:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # 获取现有项目
            current_project = get_project(project_id)
            if not current_project:
                return {}
            
            now = _utc_now()
            
            # 更新基本字段
            updateable_fields = {'name', 'script_title', 'episode_no', 'video_provider'}
            updates = {k: v for k, v in kwargs.items() if k in updateable_fields}
            
            if updates:
                updates['updated_at'] = now
                set_clause = ', '.join([f"{k.replace('_', '')} = %s" if k == 'updated_at' else f"{k} = %s" for k in updates.keys()])
                # 修正字段名
                set_clause = ', '.join([
                    'updated_at = %s' if k == 'updated_at' else 
                    f"episode_no = %s" if k == 'episode_no' else 
                    f"{k} = %s" for k in updates.keys()
                ])
                values = list(updates.values())
                query = f"UPDATE projects SET {set_clause} WHERE id = %s"
                cursor.execute(query, values + [project_id])
            
            # 处理assets
            if 'assets' in kwargs and isinstance(kwargs['assets'], list):
                _update_assets(cursor, project_id, kwargs['assets'])
            
            # 处理shots
            if 'shots' in kwargs and isinstance(kwargs['shots'], list):
                _update_shots(cursor, project_id, kwargs['shots'])
            
            # 处理history
            if 'history' in kwargs and isinstance(kwargs['history'], list):
                _update_history(cursor, project_id, kwargs['history'])
            
            # 处理script
            if 'script' in kwargs:
                _update_script(cursor, project_id, kwargs['script'])
            
            # 处理generated_data
            if 'generated_data' in kwargs:
                _update_generated_data(cursor, project_id, kwargs['generated_data'])
            
            # 处理episode_scripts
            if 'episode_scripts' in kwargs:
                _update_episode_scripts(cursor, project_id, kwargs['episode_scripts'])
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Error as e:
            print(f"Error updating project: {e}")
    
    return get_project(project_id) or {}


def _get_project_assets(project_id: str) -> List[Dict[str, Any]]:
    """获取项目资源"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT id, image_url, name, prompt, type FROM assets WHERE project_id = %s"
        cursor.execute(query, (project_id,))
        rows = cursor.fetchall()
        assets = [{'id': row[0], 'image_url': row[1], 'name': row[2], 'prompt': row[3], 'type': row[4]} for row in rows]
        cursor.close()
        conn.close()
        return assets
    except Error as e:
        print(f"Error getting assets: {e}")
        return []


def _get_project_shots(project_id: str) -> List[Dict[str, Any]]:
    """获取项目镜头"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            SELECT id, scene_no, title, duration, dialogue_details, bound_character_asset_ids,
                   bound_character_names, start_frame_description, start_frame_enhanced_prompt,
                   start_frame_image_url, end_frame_description, end_frame_enhanced_prompt,
                   end_frame_image_url, video_url, video_task_id, video_task_status,
                   video_task_message, video_task_progress, video_task_provider
            FROM shots WHERE project_id = %s
        """
        cursor.execute(query, (project_id,))
        rows = cursor.fetchall()
        shots = []
        for row in rows:
            shot = {
                'sceneNo': row[1],
                'title': row[2],
                'duration': row[3],
                'dialogueDetails': row[4],
                'boundCharacterAssetIds': json.loads(row[5]) if row[5] else [],
                'boundCharacterNames': json.loads(row[6]) if row[6] else [],
                'startFrame': {
                    'description': row[7],
                    'enhanced_prompt': row[8],
                    'image_url': row[9]
                },
                'endFrame': {
                    'description': row[10],
                    'enhanced_prompt': row[11],
                    'image_url': row[12]
                },
                'videoUrl': row[13],
                'videoTask': {
                    'taskId': row[14],
                    'status': row[15],
                    'message': row[16],
                    'progress': row[17],
                    'provider': row[18],
                    'reqKey': ''
                }
            }
            shots.append(shot)
        cursor.close()
        conn.close()
        return shots
    except Error as e:
        print(f"Error getting shots: {e}")
        return []


def _get_project_history(project_id: str) -> List[Any]:
    """获取项目历史"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT history_data FROM project_history WHERE project_id = %s"
        cursor.execute(query, (project_id,))
        rows = cursor.fetchall()
        history = []
        for row in rows:
            if row[0]:
                history.append(json.loads(row[0]))
        cursor.close()
        conn.close()
        return history
    except Error as e:
        print(f"Error getting history: {e}")
        return []


def _get_project_generated_data(project_id: str) -> List[Any]:
    """获取项目生成的数据"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT generated_data FROM project_generated_data WHERE project_id = %s"
        cursor.execute(query, (project_id,))
        rows = cursor.fetchall()
        data = []
        for row in rows:
            if row[0]:
                data.append(json.loads(row[0]))
        cursor.close()
        conn.close()
        return data
    except Error as e:
        print(f"Error getting generated data: {e}")
        return []


def _get_episode_scripts(project_id: str) -> Dict[str, Any]:
    """获取剧集脚本"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            SELECT episode_key, script_input, script_duration, script_result, history
            FROM episode_scripts WHERE project_id = %s
        """
        cursor.execute(query, (project_id,))
        rows = cursor.fetchall()
        scripts = {}
        for row in rows:
            scripts[row[0]] = {
                'script': {
                    'input': row[1],
                    'duration': row[2],
                    'result': json.loads(row[3]) if row[3] else None
                },
                'history': json.loads(row[4]) if row[4] else []
            }
        cursor.close()
        conn.close()
        return scripts
    except Error as e:
        print(f"Error getting episode scripts: {e}")
        return {}


def _get_project_script(project_id: str) -> Dict[str, Any]:
    """获取项目脚本"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = "SELECT script_input, script_duration, script_result FROM project_script WHERE project_id = %s"
        cursor.execute(query, (project_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if row:
            return {
                'input': row[0] or '',
                'duration': row[1] or '3min',
                'result': json.loads(row[2]) if row[2] else None
            }
        return {'input': '', 'duration': '3min', 'result': None}
    except Error as e:
        print(f"Error getting script: {e}")
        return {'input': '', 'duration': '3min', 'result': None}


def _update_assets(cursor, project_id: str, assets: List[Dict[str, Any]]):
    """更新资源"""
    cursor.execute("DELETE FROM assets WHERE project_id = %s", (project_id,))
    for asset in assets:
        query = """
            INSERT INTO assets (id, project_id, image_url, name, prompt, type)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            asset.get('id'),
            project_id,
            asset.get('image_url'),
            asset.get('name'),
            asset.get('prompt'),
            asset.get('type')
        ))


def _update_shots(cursor, project_id: str, shots: List[Dict[str, Any]]):
    """更新镜头"""
    cursor.execute("DELETE FROM shots WHERE project_id = %s", (project_id,))
    for shot in shots:
        query = """
            INSERT INTO shots (project_id, scene_no, title, duration, dialogue_details,
                              bound_character_asset_ids, bound_character_names,
                              start_frame_description, start_frame_enhanced_prompt,
                              start_frame_image_url, end_frame_description,
                              end_frame_enhanced_prompt, end_frame_image_url,
                              video_url, video_task_id, video_task_status,
                              video_task_message, video_task_progress, video_task_provider)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            project_id,
            shot.get('sceneNo'),
            shot.get('title'),
            shot.get('duration'),
            shot.get('dialogueDetails'),
            json.dumps(shot.get('boundCharacterAssetIds', [])),
            json.dumps(shot.get('boundCharacterNames', [])),
            shot.get('startFrame', {}).get('description'),
            shot.get('startFrame', {}).get('enhanced_prompt'),
            shot.get('startFrame', {}).get('image_url'),
            shot.get('endFrame', {}).get('description'),
            shot.get('endFrame', {}).get('enhanced_prompt'),
            shot.get('endFrame', {}).get('image_url'),
            shot.get('videoUrl'),
            shot.get('videoTask', {}).get('taskId'),
            shot.get('videoTask', {}).get('status'),
            shot.get('videoTask', {}).get('message'),
            shot.get('videoTask', {}).get('progress'),
            shot.get('videoTask', {}).get('provider')
        ))


def _update_history(cursor, project_id: str, history: List[Any]):
    """更新历史"""
    cursor.execute("DELETE FROM project_history WHERE project_id = %s", (project_id,))
    for item in history:
        query = "INSERT INTO project_history (project_id, history_data) VALUES (%s, %s)"
        cursor.execute(query, (project_id, json.dumps(item)))


def _update_script(cursor, project_id: str, script: Dict[str, Any]):
    """更新脚本"""
    query = """
        INSERT INTO project_script (project_id, script_input, script_duration, script_result)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE script_input = %s, script_duration = %s, script_result = %s, updated_at = NOW()
    """
    cursor.execute(query, (
        project_id,
        script.get('input'),
        script.get('duration'),
        json.dumps(script.get('result')),
        script.get('input'),
        script.get('duration'),
        json.dumps(script.get('result'))
    ))


def _update_generated_data(cursor, project_id: str, data: List[Any]):
    """更新生成的数据"""
    cursor.execute("DELETE FROM project_generated_data WHERE project_id = %s", (project_id,))
    for item in data:
        query = "INSERT INTO project_generated_data (project_id, generated_data) VALUES (%s, %s)"
        cursor.execute(query, (project_id, json.dumps(item)))


def _update_episode_scripts(cursor, project_id: str, scripts: Dict[str, Any]):
    """更新剧集脚本"""
    cursor.execute("DELETE FROM episode_scripts WHERE project_id = %s", (project_id,))
    for key, value in scripts.items():
        script = value.get('script', {})
        query = """
            INSERT INTO episode_scripts (project_id, episode_key, script_input, script_duration, script_result, history)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            project_id,
            key,
            script.get('input'),
            script.get('duration'),
            json.dumps(script.get('result')),
            json.dumps(value.get('history', []))
        ))
