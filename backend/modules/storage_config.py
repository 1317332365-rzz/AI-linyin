# -*- coding: utf-8 -*-
import os

from dotenv import load_dotenv

load_dotenv()

USE_MYSQL = str(os.getenv('USE_MYSQL', 'true') or 'true').strip().lower() in {'true', '1', 'yes', 'on'}
MYSQL_HOST = str(os.getenv('MYSQL_HOST', 'localhost') or 'localhost').strip()
MYSQL_USER = str(os.getenv('MYSQL_USER', 'root') or 'root').strip()
MYSQL_PASSWORD = str(os.getenv('MYSQL_PASSWORD', 'root') or 'root')
MYSQL_DATABASE = str(os.getenv('MYSQL_DATABASE', 'ai_gender_db') or 'ai_gender_db').strip()

if USE_MYSQL:
    from modules.mysql_project_store import create_project, get_project, init_db, list_projects, update_project
else:
    from modules.project_store import create_project, get_project, init_db, list_projects, update_project

__all__ = [
    'init_db',
    'list_projects',
    'get_project',
    'create_project',
    'update_project',
    'USE_MYSQL',
    'MYSQL_HOST',
    'MYSQL_USER',
    'MYSQL_PASSWORD',
    'MYSQL_DATABASE',
]