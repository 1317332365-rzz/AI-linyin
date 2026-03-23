# -*- coding: utf-8 -*-
import argparse
import json
import os
import sqlite3
from typing import Dict, Iterable, List

from modules.mysql_project_store import _normalize_project, _serialize_payload
from modules.mysql_runtime import get_connection, init_mysql_schema


def load_projects(json_path: str) -> List[Dict]:
    if not json_path or not os.path.exists(json_path):
        return []
    with open(json_path, 'r', encoding='utf-8') as fp:
        payload = json.load(fp)
    projects = payload.get('projects', []) if isinstance(payload, dict) else []
    return projects if isinstance(projects, list) else []


def load_users(sqlite_path: str) -> List[Dict]:
    if not sqlite_path or not os.path.exists(sqlite_path):
        return []
    conn = sqlite3.connect(sqlite_path)
    try:
        rows = conn.execute(
            '''
            SELECT username, password_hash, created_at, updated_at, last_login_at
            FROM users
            '''
        ).fetchall()
    finally:
        conn.close()

    users = []
    for row in rows:
        users.append(
            {
                'username': str(row[0] or '').strip(),
                'password_hash': str(row[1] or '').strip(),
                'created_at': str(row[2] or ''),
                'updated_at': str(row[3] or ''),
                'last_login_at': str(row[4] or ''),
            }
        )
    return [item for item in users if item['username'] and item['password_hash']]


def migrate_projects(projects: Iterable[Dict]) -> int:
    migrated = 0
    conn = get_connection()
    try:
        cursor = conn.cursor()
        for project in projects:
            normalized = _normalize_project(project if isinstance(project, dict) else {})
            if not normalized.get('id'):
                continue
            cursor.execute(
                '''
                INSERT INTO projects (
                    id, owner, name, script_title, episode_no, video_provider, payload_json, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    owner = VALUES(owner),
                    name = VALUES(name),
                    script_title = VALUES(script_title),
                    episode_no = VALUES(episode_no),
                    video_provider = VALUES(video_provider),
                    payload_json = VALUES(payload_json),
                    created_at = VALUES(created_at),
                    updated_at = VALUES(updated_at)
                ''',
                (
                    normalized['id'],
                    normalized['owner'],
                    normalized['name'],
                    normalized['script_title'],
                    normalized['episode_no'],
                    normalized['video_provider'],
                    _serialize_payload(normalized),
                    normalized['createdAt'],
                    normalized['updatedAt'],
                ),
            )
            migrated += 1
        conn.commit()
    finally:
        conn.close()
    return migrated


def migrate_users(users: Iterable[Dict]) -> int:
    migrated = 0
    conn = get_connection()
    try:
        cursor = conn.cursor()
        for user in users:
            username = str(user.get('username', '') or '').strip()
            password_hash = str(user.get('password_hash', '') or '').strip()
            created_at = str(user.get('created_at', '') or '')
            updated_at = str(user.get('updated_at', '') or created_at)
            last_login_at = str(user.get('last_login_at', '') or '') or None
            if not username or not password_hash:
                continue
            cursor.execute(
                '''
                INSERT INTO users (username, password_hash, created_at, updated_at, last_login_at)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    password_hash = VALUES(password_hash),
                    created_at = VALUES(created_at),
                    updated_at = VALUES(updated_at),
                    last_login_at = VALUES(last_login_at)
                ''',
                (username, password_hash, created_at, updated_at, last_login_at),
            )
            migrated += 1
        conn.commit()
    finally:
        conn.close()
    return migrated


def main() -> int:
    parser = argparse.ArgumentParser(description='Migrate local project/user data into MySQL.')
    parser.add_argument(
        '--projects-json',
        default=os.path.join(os.path.dirname(__file__), 'data', 'projects_db.json'),
        help='Source projects_db.json path',
    )
    parser.add_argument(
        '--users-sqlite',
        default=os.path.join(os.path.dirname(__file__), 'data', 'users.sqlite3'),
        help='Source users.sqlite3 path',
    )
    args = parser.parse_args()

    init_mysql_schema()
    projects = load_projects(args.projects_json)
    users = load_users(args.users_sqlite)

    migrated_projects = migrate_projects(projects)
    migrated_users = migrate_users(users)

    print(
        json.dumps(
            {
                'projects_source': args.projects_json,
                'users_source': args.users_sqlite,
                'migrated_projects': migrated_projects,
                'migrated_users': migrated_users,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
