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


def init_db() -> None:
    create_database()
    conn = get_connection(use_database=True)
    try:
        cursor = conn.cursor()
        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS users (
                username VARCHAR(64) PRIMARY KEY,
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
                owner VARCHAR(64) NOT NULL,
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
        conn.commit()
    finally:
        conn.close()
