# -*- coding: utf-8 -*-
import json
import os
import socket
import traceback
import uuid

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

try:
    import redis
except Exception:  # pragma: no cover - optional dependency fallback
    redis = None

from modules.asset_manager import generate_character, generate_scene
from modules.director_workbench import enhance_prompt, generate_voiceover
from modules.final_export import export_final_video
from modules.llm_config import get_llm_config, update_llm_config
from modules.openai_client import test_connection as test_openai_connection
from modules.storage_config import create_project, get_project, init_db, list_projects, update_project
from modules.script_parser import parse_script
from modules.auth_store import create_user, init_user_db, touch_last_login, verify_user_credentials
from modules.video_generator import generate_video, query_video_task

load_dotenv()

app = Flask(__name__)
CORS(app)
init_db()

app.config['JSON_AS_ASCII'] = False

ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', '@@Admin@321')
_AUTH_TOKENS = {}
TOKEN_REDIS_KEY = os.getenv('AUTH_TOKEN_REDIS_KEY', 'cinegen:auth:tokens')
TOKEN_REDIS_HOST = os.getenv('AUTH_REDIS_HOST', '127.0.0.1')
TOKEN_REDIS_PORT_RAW = os.getenv('AUTH_REDIS_PORT', '6379')
TOKEN_REDIS_DB_RAW = os.getenv('AUTH_REDIS_DB', '0')
TOKEN_REDIS_PASSWORD = os.getenv('AUTH_REDIS_PASSWORD', '')
TOKEN_REDIS_ENABLED = str(os.getenv('AUTH_TOKEN_USE_REDIS', '1')).strip().lower() not in {'0', 'false', 'no', 'off'}
DEFAULT_TOKEN_FILE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'auth_tokens.json')
TOKEN_FILE_PATH = str(os.getenv('AUTH_TOKEN_FILE', DEFAULT_TOKEN_FILE_PATH) or '').strip() or DEFAULT_TOKEN_FILE_PATH

AUTH_WHITELIST = {
    '/health',
    '/api/auth/login',
    '/api/auth/register',
    '/api/auth/logout',
    '/api/auth/status',
}


def _parse_int_env(raw_value: str, fallback: int) -> int:
    try:
        return int(str(raw_value or '').strip())
    except (TypeError, ValueError):
        return fallback


class _SocketRedisClient:
    """
    Minimal Redis client over RESP protocol (HSET/HGET/HDEL/PING/SELECT/AUTH).
    Used as fallback when redis-py is unavailable.
    """

    def __init__(self, host: str, port: int, db: int = 0, password: str = '', timeout: float = 2.0):
        self.host = host
        self.port = int(port)
        self.db = int(db)
        self.password = str(password or '').strip()
        self.timeout = float(timeout)

    @staticmethod
    def _to_bytes(value) -> bytes:
        if isinstance(value, bytes):
            return value
        return str(value).encode('utf-8')

    def _encode_command(self, *args) -> bytes:
        parts = [b'*' + str(len(args)).encode('ascii') + b'\r\n']
        for arg in args:
            item = self._to_bytes(arg)
            parts.append(b'$' + str(len(item)).encode('ascii') + b'\r\n')
            parts.append(item + b'\r\n')
        return b''.join(parts)

    def _read_response(self, fp):
        prefix = fp.read(1)
        if not prefix:
            raise RuntimeError('redis empty response')

        if prefix == b'+':
            return fp.readline().rstrip(b'\r\n').decode('utf-8', errors='replace')
        if prefix == b'-':
            err = fp.readline().rstrip(b'\r\n').decode('utf-8', errors='replace')
            raise RuntimeError(f'redis error: {err}')
        if prefix == b':':
            raw = fp.readline().rstrip(b'\r\n').decode('ascii', errors='ignore')
            return int(raw or '0')
        if prefix == b'$':
            raw_len = fp.readline().rstrip(b'\r\n').decode('ascii', errors='ignore')
            size = int(raw_len or '-1')
            if size == -1:
                return None
            payload = fp.read(size)
            fp.read(2)  # CRLF
            return payload.decode('utf-8', errors='replace')
        if prefix == b'*':
            raw_len = fp.readline().rstrip(b'\r\n').decode('ascii', errors='ignore')
            count = int(raw_len or '0')
            if count < 0:
                return None
            return [self._read_response(fp) for _ in range(count)]

        raise RuntimeError(f'redis unsupported response prefix: {prefix!r}')

    def _execute(self, *args):
        command = self._encode_command(*args)
        with socket.create_connection((self.host, self.port), timeout=self.timeout) as conn:
            conn.settimeout(self.timeout)
            fp = conn.makefile('rb')

            if self.password:
                conn.sendall(self._encode_command('AUTH', self.password))
                self._read_response(fp)
            if self.db > 0:
                conn.sendall(self._encode_command('SELECT', str(self.db)))
                self._read_response(fp)

            conn.sendall(command)
            return self._read_response(fp)

    def ping(self):
        return self._execute('PING')

    def hset(self, key, field, value):
        return self._execute('HSET', key, field, value)

    def hget(self, key, field):
        return self._execute('HGET', key, field)

    def hdel(self, key, field):
        return self._execute('HDEL', key, field)


def _build_token_redis_client():
    if not TOKEN_REDIS_ENABLED:
        return None

    port = _parse_int_env(TOKEN_REDIS_PORT_RAW, 灵映台)
    db = _parse_int_env(TOKEN_REDIS_DB_RAW, 0)
    password = str(TOKEN_REDIS_PASSWORD or '').strip() or None

    if redis is None:
        try:
            client = _SocketRedisClient(
                host=TOKEN_REDIS_HOST,
                port=port,
                db=db,
                password=password or '',
                timeout=2,
            )
            pong = str(client.ping() or '').strip().upper()
            if pong != 'PONG':
                raise RuntimeError(f'invalid PING response: {pong!r}')
            print(f'[auth] token store = redis-socket://{TOKEN_REDIS_HOST}:{port}/{db}')
            return client
        except Exception as e:
            print(f'[auth] redis socket fallback unavailable ({e}), fallback to in-memory token store')
            return None

    try:
        client = redis.Redis(
            host=TOKEN_REDIS_HOST,
            port=port,
            db=db,
            password=password,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        client.ping()
        print(f'[auth] token store = redis://{TOKEN_REDIS_HOST}:{port}/{db}')
        return client
    except Exception as e:
        print(f'[auth] redis unavailable ({e}), fallback to in-memory token store')
        return None


_TOKEN_REDIS = _build_token_redis_client()


def _load_auth_tokens_snapshot_from_file() -> dict:
    path = str(TOKEN_FILE_PATH or '').strip()
    if not path or not os.path.exists(path):
        return {}

    try:
        with open(path, 'r', encoding='utf-8') as fp:
            payload = json.load(fp)
    except Exception as e:
        print(f'[auth] token file load failed ({e})')
        return {}

    if not isinstance(payload, dict):
        return {}

    normalized = {}
    for token, username in payload.items():
        token_text = str(token or '').strip()
        user_text = str(username or '').strip()
        if not token_text or not user_text:
            continue
        normalized[token_text] = user_text
    return normalized


def _load_auth_tokens_from_file() -> None:
    path = str(TOKEN_FILE_PATH or '').strip()
    snapshot = _load_auth_tokens_snapshot_from_file()
    if not snapshot:
        return

    loaded = 0
    for token_text, user_text in snapshot.items():
        if token_text not in _AUTH_TOKENS:
            loaded += 1
        _AUTH_TOKENS[token_text] = user_text

    if loaded:
        print(f'[auth] loaded {loaded} persisted token(s) from {path or "<memory>"}')


def _persist_auth_tokens_to_file() -> None:
    path = str(TOKEN_FILE_PATH or '').strip()
    if not path:
        return

    directory = os.path.dirname(path) or '.'
    tmp_path = f'{path}.tmp'
    snapshot = {str(token): str(username) for token, username in _AUTH_TOKENS.items() if str(token).strip() and str(username).strip()}

    try:
        os.makedirs(directory, exist_ok=True)
        with open(tmp_path, 'w', encoding='utf-8') as fp:
            json.dump(snapshot, fp, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)
    except Exception as e:
        print(f'[auth] token file save failed ({e})')
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass


_load_auth_tokens_from_file()


def _save_auth_token(token: str, username: str) -> None:
    token_text = str(token or '').strip()
    user_text = str(username or '').strip()
    if not token_text or not user_text:
        return

    _AUTH_TOKENS[token_text] = user_text
    _persist_auth_tokens_to_file()
    if _TOKEN_REDIS is None:
        return
    try:
        _TOKEN_REDIS.hset(TOKEN_REDIS_KEY, token_text, user_text)
    except Exception:
        # Redis 异常不影响当前请求，保留内存兜底。
        pass


def _delete_auth_token(token: str) -> None:
    token_text = str(token or '').strip()
    if not token_text:
        return

    _AUTH_TOKENS.pop(token_text, None)
    _persist_auth_tokens_to_file()
    if _TOKEN_REDIS is None:
        return
    try:
        _TOKEN_REDIS.hdel(TOKEN_REDIS_KEY, token_text)
    except Exception:
        pass


def _lookup_auth_user_from_file(token: str):
    token_text = str(token or '').strip()
    if not token_text:
        return None

    snapshot = _load_auth_tokens_snapshot_from_file()
    if not snapshot:
        return None

    user = str(snapshot.get(token_text) or '').strip()
    if not user:
        return None

    _AUTH_TOKENS[token_text] = user
    return user


def _get_auth_user_from_store(token: str):
    token_text = str(token or '').strip()
    if not token_text:
        return None

    if _TOKEN_REDIS is not None:
        try:
            user = _TOKEN_REDIS.hget(TOKEN_REDIS_KEY, token_text)
            if user:
                _AUTH_TOKENS[token_text] = user
                return user
        except Exception:
            # Redis 暂时不可用时退回内存。
            pass

    if _TOKEN_REDIS is None:
        # Redis 不可用时，必须允许当前进程内存 token 生效，
        # 否则在 AUTH_TOKEN_FILE 为空或落盘失败时会出现“登录成功后立即 401”。
        memory_user = _AUTH_TOKENS.get(token_text)
        if memory_user:
            return memory_user
        file_user = _lookup_auth_user_from_file(token_text)
        if file_user:
            return file_user
        _AUTH_TOKENS.pop(token_text, None)
        return None

    memory_user = _AUTH_TOKENS.get(token_text)
    if memory_user:
        return memory_user
    return _lookup_auth_user_from_file(token_text)


def _parse_auth_users_from_env() -> dict:
    """
    从环境变量加载可登录账号:
    1) AUTH_USERS_JSON='{"admin":"***","user1":"***"}'
    2) AUTH_USERS='admin:***,user1:***'
    """
    users = {}

    raw_json = str(os.getenv('AUTH_USERS_JSON', '') or '').strip()
    if raw_json:
        try:
            parsed = json.loads(raw_json)
            if isinstance(parsed, dict):
                for username, password in parsed.items():
                    name = str(username or '').strip()
                    pwd = str(password or '')
                    if name and pwd:
                        users[name] = pwd
        except Exception:
            # JSON 配置错误时忽略，继续尝试 AUTH_USERS。
            pass

    raw_pairs = str(os.getenv('AUTH_USERS', '') or '').strip()
    if raw_pairs:
        for pair in raw_pairs.split(','):
            if ':' not in pair:
                continue
            username, password = pair.split(':', 1)
            name = str(username or '').strip()
            pwd = str(password or '')
            if name and pwd:
                users[name] = pwd

    # 保留兼容：若未配置多账号，则使用现有管理员账号。
    if ADMIN_USERNAME and ADMIN_PASSWORD and ADMIN_USERNAME not in users:
        users[ADMIN_USERNAME] = ADMIN_PASSWORD
    return users


_AUTH_USERS = _parse_auth_users_from_env()
init_user_db(_AUTH_USERS)


def _extract_bearer_token():
    header = str(request.headers.get('Authorization', '')).strip()
    if header.lower().startswith('bearer '):
        return header[7:].strip()
    return ''


def _current_auth_user():
    token = _extract_bearer_token()
    if not token:
        return None
    return _get_auth_user_from_store(token)


def _is_auth_required():
    path = str(request.path or '')
    if request.method == 'OPTIONS':
        return False
    if path in AUTH_WHITELIST:
        return False
    return path.startswith('/api/')


@app.before_request
def require_auth():
    if not _is_auth_required():
        return None
    user = _current_auth_user()
    if user:
        request.current_user = user
        return None
    return jsonify({'error': 'Unauthorized', 'code': 'AUTH_REQUIRED'}), 401


@app.route('/api/auth/login', methods=['POST'])
def api_auth_login():
    data = request.json or {}
    username = str(data.get('email') or data.get('username') or '').strip()
    password = str(data.get('password', ''))

    user = verify_user_credentials(username, password)
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401

    token = uuid.uuid4().hex
    account = str(user.get('username', username)).strip()
    touch_last_login(account)
    _save_auth_token(token, account)
    return jsonify({'token': token, 'username': account, 'email': account})


@app.route('/api/auth/register', methods=['POST'])
def api_auth_register():
    data = request.json or {}
    username = str(data.get('email') or data.get('username') or '').strip()
    password = str(data.get('password', ''))

    try:
        created_user = create_user(username, password)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    token = uuid.uuid4().hex
    created_username = str(created_user.get('username', username)).strip()
    touch_last_login(created_username)
    _save_auth_token(token, created_username)
    return jsonify({'token': token, 'username': created_username, 'email': created_username}), 201


@app.route('/api/auth/logout', methods=['POST'])
def api_auth_logout():
    token = _extract_bearer_token()
    if token:
        _delete_auth_token(token)
    return jsonify({'success': True})


@app.route('/api/auth/status', methods=['GET'])
def api_auth_status():
    user = _current_auth_user()
    if not user:
        return jsonify({'authenticated': False}), 401
    return jsonify({'authenticated': True, 'username': user, 'email': user})


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})


@app.route('/api/projects', methods=['GET'])
def api_list_projects():
    owner = getattr(request, 'current_user', None)
    return jsonify(list_projects(owner=owner))


@app.route('/api/projects', methods=['POST'])
def api_create_project():
    data = request.json or {}
    name = str(data.get('name', '')).strip() or 'New Project'
    script_title = str(data.get('script_title', '')).strip()

    try:
        episode_no = int(data.get('episode_no', 1))
    except (TypeError, ValueError):
        episode_no = 1
    if episode_no <= 0:
        episode_no = 1

    project_id = f"p_{uuid.uuid4().hex[:12]}"
    owner = getattr(request, 'current_user', None)
    project = create_project(project_id, name, script_title, episode_no, owner=owner)
    return jsonify(project), 201


@app.route('/api/projects/<project_id>', methods=['GET'])
def api_get_project(project_id):
    owner = getattr(request, 'current_user', None)
    project = get_project(project_id, owner=owner)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    return jsonify(project)


@app.route('/api/projects/<project_id>', methods=['PUT'])
def api_update_project(project_id):
    data = request.json or {}
    owner = getattr(request, 'current_user', None)
    request_id = f"api-project-update-{uuid.uuid4().hex[:8]}"
    data_keys = sorted(list(data.keys())) if isinstance(data, dict) else []
    episode_scripts_count = len(data.get('episode_scripts') or {}) if isinstance(data.get('episode_scripts'), dict) else 0
    episode_shots_count = len(data.get('episode_shots') or {}) if isinstance(data.get('episode_shots'), dict) else 0
    script_input_len = 0
    if isinstance(data.get('script'), dict):
        script_input_len = len(str(data.get('script', {}).get('input', '') or ''))
    print(
        f"[api_update_project][{request_id}] incoming "
        f"project_id={project_id} owner={owner} keys={data_keys} "
        f"episode_scripts={episode_scripts_count} episode_shots={episode_shots_count} "
        f"script_input_len={script_input_len}"
    )
    try:
        project = update_project(project_id, data, owner=owner)
        if not project:
            print(f"[api_update_project][{request_id}] not_found_or_forbidden project_id={project_id} owner={owner}")
            return jsonify({'error': 'Project not found'}), 404
        saved_episode_scripts = len(project.get('episode_scripts') or {}) if isinstance(project.get('episode_scripts'), dict) else 0
        saved_episode_shots = len(project.get('episode_shots') or {}) if isinstance(project.get('episode_shots'), dict) else 0
        saved_script_input_len = 0
        if isinstance(project.get('script'), dict):
            saved_script_input_len = len(str(project.get('script', {}).get('input', '') or ''))
        print(
            f"[api_update_project][{request_id}] success "
            f"project_id={project_id} saved_episode_scripts={saved_episode_scripts} "
            f"saved_episode_shots={saved_episode_shots} saved_script_input_len={saved_script_input_len}"
        )
        return jsonify(project)
    except Exception as e:
        print(f"[api_update_project][{request_id}] error type={type(e).__name__} message={e}")
        print(f"[api_update_project][{request_id}] traceback:\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/parse-script', methods=['POST'])
def api_parse_script():
    data = request.json or {}
    script = data.get('script', '')
    duration = data.get('duration', '3min')
    request_id = f"api-parse-{uuid.uuid4().hex[:8]}"
    script_len = len(str(script or ''))
    print(f"[api_parse_script][{request_id}] incoming duration={duration} script_len={script_len}")

    if not script:
        print(f"[api_parse_script][{request_id}] bad_request missing script")
        return jsonify({'error': 'Script is required'}), 400

    try:
        llm_config = get_llm_config('script')
        print(
            f"[api_parse_script][{request_id}] llm_config "
            f"model={llm_config.get('model')} sdk_type={llm_config.get('sdk_type')} "
            f"base_url={llm_config.get('base_url')} max_tokens={llm_config.get('max_tokens')}"
        )
        result = parse_script(script, duration, llm_config)
        scenes_count = len(result.get('scenes') or []) if isinstance(result, dict) else 0
        print(f"[api_parse_script][{request_id}] success scenes={scenes_count}")
        return jsonify(result)
    except Exception as e:
        message = str(e)
        lower = message.lower()
        print(f"[api_parse_script][{request_id}] error type={type(e).__name__} message={message}")
        print(f"[api_parse_script][{request_id}] traceback:\n{traceback.format_exc()}")
        if 'timed out' in lower or 'timeout' in lower:
            return jsonify({'error': message}), 504
        if 'response is not a valid json object' in lower or 'invalid response' in lower:
            return jsonify({'error': message}), 422
        if 'api_key' in lower or 'authentication' in lower or 'unauthorized' in lower:
            return jsonify({'error': message}), 401
        return jsonify({'error': message}), 500


@app.route('/api/generate-character', methods=['POST'])
def api_generate_character():
    data = request.json or {}
    character_desc = data.get('description', '')

    if not character_desc:
        return jsonify({'error': 'Character description is required'}), 400

    try:
        llm_config = get_llm_config('character')
        result = generate_character(character_desc, llm_config)
        if not result.get('success'):
            return jsonify(result), 400
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-scene', methods=['POST'])
def api_generate_scene():
    data = request.json or {}
    scene_desc = data.get('description', '')
    reference_images = data.get('reference_images', [])
    prefer_img2img = bool(data.get('prefer_img2img'))
    context = data.get('context', {})

    if not scene_desc:
        return jsonify({'error': 'Scene description is required'}), 400

    try:
        llm_config = get_llm_config('scene')
        result = generate_scene(
            scene_desc,
            llm_config,
            reference_images=reference_images,
            prefer_img2img=prefer_img2img,
            context=context,
        )
        if not result.get('success'):
            return jsonify(result), 400
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-video', methods=['POST'])
def api_generate_video():
    data = request.json or {}
    start_frame = data.get('start_frame')
    end_frame = data.get('end_frame')
    mode = data.get('mode', 'keyframe-interpolation')
    context = data.get('context', {})
    provider = data.get('provider') or (context or {}).get('video_provider')

    if not start_frame:
        return jsonify({'error': 'Start frame is required'}), 400

    try:
        llm_config = get_llm_config('video')
        result = generate_video(start_frame, end_frame, mode, context, llm_config, provider=provider)
        if result.get('status') == 'error':
            return jsonify(result), 400
        return jsonify(result)
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-video/tasks/<task_id>', methods=['GET'])
def api_generate_video_task_status(task_id):
    try:
        llm_config = get_llm_config('video')
        provider = request.args.get('provider', '')
        req_key = request.args.get('req_key', '')
        query_url = request.args.get('query_url', '')
        query_method = request.args.get('query_method', '')
        provider_options = {}
        if str(req_key or '').strip():
            provider_options['req_key'] = req_key
        if str(query_url or '').strip():
            provider_options['query_url'] = query_url
        if str(query_method or '').strip():
            provider_options['query_method'] = query_method
        if not provider_options:
            provider_options = None
        result = query_video_task(task_id, llm_config, provider=provider, provider_options=provider_options)
        # 查询接口统一返回 200，业务状态由 body.status 表达，避免前端轮询被 HTTP 错误中断。
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export-video', methods=['POST'])
def api_export_video():
    export_request_id = f"exp-{uuid.uuid4().hex[:8]}"
    try:
        data = request.get_json(silent=True) or {}
        shots = data.get('shots', [])
        episode_no = data.get('episode_no', 1)
        print(f"[api_export_video][{export_request_id}] incoming episode={episode_no} shots={len(shots) if isinstance(shots, list) else 'n/a'}")

        if not isinstance(shots, list):
            print(f"[api_export_video][{export_request_id}] bad_request shots is not list")
            return jsonify({'error': 'shots must be a list'}), 400

        result = export_final_video(shots, episode_no, request_id=export_request_id)
        if not result.get('success'):
            print(f"[api_export_video][{export_request_id}] export_failed error={result.get('error')}")
            return jsonify({'error': result.get('error', '导出失败')}), 400

        file_path = os.path.abspath(str(result.get('file_path') or '').strip())
        if not file_path or not os.path.isfile(file_path):
            print(f"[api_export_video][{export_request_id}] file_missing path={file_path}")
            return jsonify({'error': '导出文件不存在，请重试'}), 500

        print(f"[api_export_video][{export_request_id}] success path={file_path}")
        return send_file(
            file_path,
            mimetype='video/mp4',
            as_attachment=True,
            download_name=result.get('filename') or 'final-export.mp4',
        )
    except Exception as e:
        print(f"[api_export_video][{export_request_id}] unexpected_error={type(e).__name__}: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/enhance-prompt', methods=['POST'])
def api_enhance_prompt():
    data = request.json or {}
    raw_prompt = data.get('prompt', '')
    context = data.get('context', {})

    if not str(raw_prompt).strip():
        return jsonify({'error': 'prompt is required'}), 400

    try:
        result = enhance_prompt(raw_prompt, context)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-voiceover', methods=['POST'])
def api_generate_voiceover():
    data = request.json or {}
    raw_prompt = data.get('prompt', '')
    context = data.get('context', {})

    if not str(raw_prompt).strip() and not isinstance(context, dict):
        return jsonify({'error': 'prompt or context is required'}), 400

    try:
        result = generate_voiceover(raw_prompt, context if isinstance(context, dict) else {})
        if not result.get('success'):
            return jsonify(result), 400
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/llm-config', methods=['GET', 'POST'])
def api_llm_config():
    if request.method == 'GET':
        process = request.args.get('process', 'general')
        return jsonify(get_llm_config(process))

    data = request.json or {}
    try:
        updated_config = update_llm_config(data)
        return jsonify(updated_config)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/test-llm', methods=['POST'])
def api_test_llm():
    data = request.json or {}
    data.pop('process', None)

    api_key = data.get('api_key')
    model = data.get('model', '')
    base_url = data.get('base_url', None)
    sdk_type = data.get('sdk_type', 'openai')

    if not api_key:
        return jsonify({'error': 'API Key is required'}), 400
    if not model:
        return jsonify({'status': 'error', 'message': 'Model is required'})

    if sdk_type == 'dashscope':
        try:
            import requests

            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            }
            resp = requests.get('https://dashscope.aliyuncs.com/api/v1/tasks/dummy_id', headers=headers)
            if resp.status_code in [401, 403]:
                result = {
                    'success': False,
                    'message': f'Authentication failed ({resp.status_code})',
                    'error_type': 'authentication',
                }
            else:
                result = {'success': True, 'message': 'Connection verified', 'response': 'ok'}
        except Exception as e:
            result = {'success': False, 'message': str(e), 'error_type': 'connection'}
    elif sdk_type == 'doubao':
        try:
            import requests

            headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {api_key}'}
            resp = requests.post(
                'https://ark.cn-beijing.volces.com/api/v3/images/generations',
                headers=headers,
                json={},
            )
            if resp.status_code == 401:
                result = {'success': False, 'message': 'Authentication failed', 'error_type': 'authentication'}
            else:
                result = {'success': True, 'message': 'Connection verified', 'response': 'ok'}
        except Exception as e:
            result = {'success': False, 'message': str(e), 'error_type': 'connection'}
    else:
        result = test_openai_connection(api_key, model, base_url)

    if result.get('success'):
        return jsonify({'status': 'success', 'message': result.get('message', ''), 'response': result.get('response')})

    return jsonify(
        {
            'status': 'error',
            'message': result.get('message', 'Unknown error'),
            'error_type': result.get('error_type', 'unknown'),
        }
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
