# -*- coding: utf-8 -*-
import base64
import hashlib
import hmac
import os
import re
import threading
from datetime import datetime, timezone
from typing import Dict, Optional

from modules.mysql_runtime import get_connection, init_mysql_schema

_LOCK = threading.Lock()
_EMAIL_RE = re.compile(r'^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$')
_HASH_PREFIX = 'pbkdf2_sha256'
_ITERATIONS = 120_000


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_username(username) -> str:
    return str(username or '').strip().lower()


def _normalize_password(password) -> str:
    return str(password or '')


def validate_username(username) -> Optional[str]:
    name = _normalize_username(username)
    if not name:
        return 'Email is required'
    if len(name) > 254 or not _EMAIL_RE.match(name):
        return 'Please enter a valid email address'
    return None


def validate_password(password) -> Optional[str]:
    text = _normalize_password(password)
    if not text:
        return 'Password is required'
    if len(text) < 6:
        return 'Password must be at least 6 characters'
    if len(text) > 128:
        return 'Password must be 128 characters or fewer'
    return None


def _hash_password(password: str, salt: Optional[bytes] = None) -> str:
    return _normalize_password(password)


def _verify_password(password: str, stored_hash: str) -> bool:
    text = str(stored_hash or '').strip()
    if not text:
        return False
    # 兼容历史哈希数据（老账号），新账号按明文校验。
    if text.startswith(f'{_HASH_PREFIX}$'):
        try:
            prefix, iterations_text, salt_text, digest_text = text.split('$', 3)
            if prefix != _HASH_PREFIX:
                return False
            iterations = int(iterations_text)
            salt = base64.b64decode(salt_text.encode('ascii'))
            expected_digest = base64.b64decode(digest_text.encode('ascii'))
            actual_digest = hashlib.pbkdf2_hmac(
                'sha256',
                _normalize_password(password).encode('utf-8'),
                salt,
                iterations,
            )
            return hmac.compare_digest(actual_digest, expected_digest)
        except Exception:
            return False
    return hmac.compare_digest(_normalize_password(password), text)


def _row_to_user(row) -> Optional[Dict[str, str]]:
    if not row:
        return None
    return {
        'username': str(row[0] or ''),
        'created_at': str(row[2] or ''),
        'updated_at': str(row[3] or ''),
        'last_login_at': str(row[4] or ''),
    }


def init_user_db(seed_users: Optional[Dict[str, str]] = None) -> None:
    init_mysql_schema()
    if not isinstance(seed_users, dict):
        return
    for username, password in seed_users.items():
        name = _normalize_username(username)
        pwd = _normalize_password(password)
        if validate_username(name) or validate_password(pwd):
            continue
        if get_user(name):
            continue
        _insert_user(name, pwd)


def _insert_user(username: str, password: str) -> Dict[str, str]:
    now = _utc_now()
    password_hash = _hash_password(password)
    with _LOCK:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                '''
                INSERT INTO users (username, password_hash, created_at, updated_at, last_login_at)
                VALUES (%s, %s, %s, %s, %s)
                ''',
                (username, password_hash, now, now, None),
            )
            conn.commit()
        finally:
            conn.close()
    return get_user(username) or {'username': username}


def get_user(username: str) -> Optional[Dict[str, str]]:
    name = _normalize_username(username)
    if not name:
        return None
    with _LOCK:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT username, password_hash, created_at, updated_at, last_login_at
                FROM users
                WHERE username = %s
                ''',
                (name,),
            )
            return _row_to_user(cursor.fetchone())
        finally:
            conn.close()


def create_user(username: str, password: str) -> Dict[str, str]:
    name = _normalize_username(username)
    pwd = _normalize_password(password)

    username_error = validate_username(name)
    if username_error:
        raise ValueError(username_error)

    password_error = validate_password(pwd)
    if password_error:
        raise ValueError(password_error)

    if get_user(name):
        raise ValueError('Email already exists')

    return _insert_user(name, pwd)


def verify_user_credentials(username: str, password: str) -> Optional[Dict[str, str]]:
    name = _normalize_username(username)
    pwd = _normalize_password(password)
    if not name or not pwd:
        return None

    with _LOCK:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT username, password_hash, created_at, updated_at, last_login_at
                FROM users
                WHERE username = %s
                ''',
                (name,),
            )
            row = cursor.fetchone()
        finally:
            conn.close()

    if not row:
        return None
    if not _verify_password(pwd, str(row[1] or '')):
        return None
    return _row_to_user(row)


def touch_last_login(username: str) -> None:
    name = _normalize_username(username)
    if not name:
        return
    now = _utc_now()
    with _LOCK:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                '''
                UPDATE users
                SET last_login_at = %s, updated_at = %s
                WHERE username = %s
                ''',
                (now, now, name),
            )
            conn.commit()
        finally:
            conn.close()
