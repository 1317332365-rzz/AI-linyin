# -*- coding: utf-8 -*-
import os

from dotenv import load_dotenv

load_dotenv()

USE_MYSQL = str(os.getenv('USE_MYSQL', 'true') or 'true').strip().lower() in {'true', '1', 'yes', 'on'}

if USE_MYSQL:
    from modules.mysql_user_store import create_user, get_user, init_user_db, touch_last_login, verify_user_credentials
else:
    from modules.user_store import create_user, get_user, init_user_db, touch_last_login, verify_user_credentials

__all__ = [
    'create_user',
    'get_user',
    'init_user_db',
    'touch_last_login',
    'verify_user_credentials',
    'USE_MYSQL',
]
