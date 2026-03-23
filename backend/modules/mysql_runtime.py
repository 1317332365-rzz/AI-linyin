# -*- coding: utf-8 -*-
import os

import mysql.connector
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = str(os.getenv('MYSQL_HOST', '127.0.0.1') or '127.0.0.1').strip()
MYSQL_PORT = int(str(os.getenv('MYSQL_PORT', '3306') or '3306').strip())
MYSQL_USER = str(os.getenv('MYSQL_USER', 'root') or 'root').strip()
MYSQL_PASSWORD = str(os.getenv('MYSQL_PASSWORD', '') or '')
MYSQL_DATABASE = str(os.getenv('MYSQL_DATABASE', 'ai_gender_db') or 'ai_gender_db').strip()


def get_connection(use_database: bool = True):
    config = {
        'host': MYSQL_HOST,
        'port': MYSQL_PORT,
        'user': MYSQL_USER,
        'password': MYSQL_PASSWORD,
        'charset': 'utf8mb4',
        'use_unicode': True,
    }
    if use_database:
        config['database'] = MYSQL_DATABASE
    return mysql.connector.connect(**config)


def create_database() -> None:
    conn = get_connection(use_database=False)
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DATABASE}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        conn.commit()
    finally:
        conn.close()


def _column_exists(cursor, table_name: str, column_name: str) -> bool:
    cursor.execute(f"SHOW COLUMNS FROM `{table_name}` LIKE %s", (column_name,))
    return cursor.fetchone() is not None


def _index_exists(cursor, table_name: str, index_name: str) -> bool:
    cursor.execute(f"SHOW INDEX FROM `{table_name}` WHERE Key_name = %s", (index_name,))
    return len(cursor.fetchall()) > 0


def _add_column_if_missing(cursor, table_name: str, column_name: str, definition_sql: str) -> None:
    if _column_exists(cursor, table_name, column_name):
        return
    cursor.execute(f"ALTER TABLE `{table_name}` ADD COLUMN `{column_name}` {definition_sql}")


def init_mysql_schema() -> None:
    create_database()
    conn = get_connection(use_database=True)
    try:
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS users (
                username VARCHAR(255) PRIMARY KEY,
                password_hash VARCHAR(255) NOT NULL,
                created_at VARCHAR(64) NOT NULL,
                updated_at VARCHAR(64) NOT NULL,
                last_login_at VARCHAR(64) NULL,
                INDEX idx_users_updated_at (updated_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            '''
        )
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS projects (
                id VARCHAR(64) PRIMARY KEY,
                owner VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                script_title VARCHAR(255) NOT NULL,
                episode_no INT NOT NULL DEFAULT 1,
                video_provider VARCHAR(32) NOT NULL DEFAULT 'openai',
                payload_json LONGTEXT NOT NULL,
                created_at VARCHAR(64) NOT NULL,
                updated_at VARCHAR(64) NOT NULL,
                INDEX idx_projects_owner_updated (owner, updated_at),
                INDEX idx_projects_updated_at (updated_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            '''
        )

        # users 表增量迁移
        _add_column_if_missing(cursor, 'users', 'last_login_at', 'VARCHAR(64) NULL AFTER updated_at')
        cursor.execute('ALTER TABLE users MODIFY username VARCHAR(255) NOT NULL')
        if not _index_exists(cursor, 'users', 'idx_users_updated_at'):
            cursor.execute('CREATE INDEX idx_users_updated_at ON users(updated_at)')

        # projects 表增量迁移，确保线上旧库自动补齐结构
        _add_column_if_missing(cursor, 'projects', 'owner', "VARCHAR(255) NULL AFTER `id`")
        _add_column_if_missing(cursor, 'projects', 'name', "VARCHAR(255) NULL AFTER `owner`")
        _add_column_if_missing(cursor, 'projects', 'script_title', "VARCHAR(255) NULL AFTER `name`")
        _add_column_if_missing(cursor, 'projects', 'episode_no', "INT NULL DEFAULT 1 AFTER `script_title`")
        _add_column_if_missing(cursor, 'projects', 'video_provider', "VARCHAR(32) NULL DEFAULT 'openai' AFTER `episode_no`")
        _add_column_if_missing(cursor, 'projects', 'payload_json', 'LONGTEXT NULL AFTER `video_provider`')
        _add_column_if_missing(cursor, 'projects', 'created_at', 'VARCHAR(64) NULL AFTER `payload_json`')
        _add_column_if_missing(cursor, 'projects', 'updated_at', 'VARCHAR(64) NULL AFTER `created_at`')

        # 历史数据回填默认值，避免后续 NOT NULL 迁移失败。
        cursor.execute("UPDATE projects SET owner = 'admin' WHERE owner IS NULL OR owner = ''")
        cursor.execute("UPDATE projects SET name = '未命名项目' WHERE name IS NULL OR name = ''")
        cursor.execute("UPDATE projects SET script_title = '' WHERE script_title IS NULL")
        cursor.execute('UPDATE projects SET episode_no = 1 WHERE episode_no IS NULL OR episode_no <= 0')
        cursor.execute("UPDATE projects SET video_provider = 'openai' WHERE video_provider IS NULL OR video_provider = ''")
        cursor.execute("UPDATE projects SET payload_json = '{}' WHERE payload_json IS NULL OR payload_json = ''")
        cursor.execute(
            "UPDATE projects SET created_at = DATE_FORMAT(UTC_TIMESTAMP(), '%Y-%m-%d %H:%i:%s') "
            "WHERE created_at IS NULL OR NULLIF(TRIM(CAST(created_at AS CHAR)), '') IS NULL"
        )
        cursor.execute(
            "UPDATE projects SET updated_at = DATE_FORMAT(UTC_TIMESTAMP(), '%Y-%m-%d %H:%i:%s') "
            "WHERE updated_at IS NULL OR NULLIF(TRIM(CAST(updated_at AS CHAR)), '') IS NULL"
        )

        cursor.execute('ALTER TABLE projects MODIFY owner VARCHAR(255) NOT NULL')
        cursor.execute('ALTER TABLE projects MODIFY name VARCHAR(255) NOT NULL')
        cursor.execute('ALTER TABLE projects MODIFY script_title VARCHAR(255) NOT NULL')
        cursor.execute('ALTER TABLE projects MODIFY episode_no INT NOT NULL DEFAULT 1')
        cursor.execute("ALTER TABLE projects MODIFY video_provider VARCHAR(32) NOT NULL DEFAULT 'openai'")
        cursor.execute('ALTER TABLE projects MODIFY payload_json LONGTEXT NOT NULL')
        cursor.execute('ALTER TABLE projects MODIFY created_at VARCHAR(64) NOT NULL')
        cursor.execute('ALTER TABLE projects MODIFY updated_at VARCHAR(64) NOT NULL')

        if not _index_exists(cursor, 'projects', 'idx_projects_owner_updated'):
            cursor.execute('CREATE INDEX idx_projects_owner_updated ON projects(owner, updated_at)')
        if not _index_exists(cursor, 'projects', 'idx_projects_updated_at'):
            cursor.execute('CREATE INDEX idx_projects_updated_at ON projects(updated_at)')

        conn.commit()
    finally:
        conn.close()
