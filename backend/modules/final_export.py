import os
import re
import shutil
import tempfile
import time
import traceback
import uuid
from typing import Any, Dict, List, Tuple
from urllib.parse import urlparse

import requests
from moviepy.audio.fx.all import audio_fadein, audio_fadeout
from moviepy.editor import CompositeAudioClip, CompositeVideoClip, VideoFileClip


BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EXPORT_DIR = os.path.abspath(os.path.join(BACKEND_DIR, "data", "exports"))
TAIL_SECONDS = 0.5
MIN_CROSSFADE_SECONDS = 0.3
MAX_CROSSFADE_SECONDS = 0.7
DEFAULT_CROSSFADE_SECONDS = 0.5
EXPORT_FFMPEG_PRESET = str(os.getenv("EXPORT_FFMPEG_PRESET", "veryfast") or "veryfast").strip() or "veryfast"
try:
    EXPORT_FFMPEG_THREADS = max(
        1,
        int(str(os.getenv("EXPORT_FFMPEG_THREADS", str(os.cpu_count() or 4)) or "").strip() or str(os.cpu_count() or 4)),
    )
except (TypeError, ValueError):
    EXPORT_FFMPEG_THREADS = max(1, int(os.cpu_count() or 4))


def _safe_text(value: Any) -> str:
    return str(value or "").strip()


def _log(request_id: str, message: str) -> None:
    rid = _safe_text(request_id) or "export"
    print(f"[final_export][{rid}] {message}", flush=True)


def _short_url(value: str) -> str:
    text = _safe_text(value)
    if not text:
        return ""
    if text.lower().startswith(("http://", "https://")):
        parsed = urlparse(text)
        host = parsed.netloc or "unknown-host"
        path = parsed.path or ""
        if len(path) > 48:
            path = f"{path[:48]}..."
        return f"{host}{path}"
    return text if len(text) <= 96 else f"{text[:96]}..."


def _safe_episode_no(value: Any) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = 1
    return parsed if parsed > 0 else 1


def _guess_video_ext(url: str) -> str:
    match = re.search(r"\.([a-zA-Z0-9]{2,5})(?:\?|$)", url)
    if not match:
        return ".mp4"
    ext = f".{match.group(1).lower()}"
    if ext in {".mp4", ".mov", ".m4v", ".webm", ".mkv", ".avi"}:
        return ext
    return ".mp4"


def _collect_export_clips(shots: Any) -> List[Dict[str, Any]]:
    if not isinstance(shots, list):
        return []

    clips: List[Dict[str, Any]] = []
    for index, shot in enumerate(shots, start=1):
        if not isinstance(shot, dict):
            continue
        include_flag = shot.get("includeInFinal", True)
        if include_flag is False:
            continue
        video_url = _safe_text(shot.get("videoUrl") or shot.get("video_url"))
        if not video_url:
            continue
        clips.append(
            {
                "index": index,
                "title": _safe_text(shot.get("title")) or f"镜头 {index}",
                "video_url": video_url,
            }
        )
    return clips


def _download_video(url: str, path: str, request_id: str = "", clip_index: int = 0) -> None:
    url_text = _safe_text(url)
    if not url_text:
        raise ValueError("video url is empty")

    local_source = _resolve_local_source_path(url_text)
    if local_source:
        _log(request_id, f"clip#{clip_index} using local source: {_short_url(local_source)}")
        shutil.copyfile(local_source, path)
        return

    if not url_text.lower().startswith(("http://", "https://")):
        raise ValueError(f"unsupported video url format: {url_text}")

    _log(request_id, f"clip#{clip_index} downloading: {_short_url(url_text)}")
    try:
        _invoke_download_http_video(url_text, path, verify_tls=True, request_id=request_id, clip_index=clip_index)
    except requests.exceptions.SSLError:
        # Fallback for environments with incomplete TLS trust chain.
        _log(request_id, f"clip#{clip_index} tls verify failed, retrying with verify=False")
        _invoke_download_http_video(url_text, path, verify_tls=False, request_id=request_id, clip_index=clip_index)


def _invoke_download_http_video(url: str, path: str, verify_tls: bool, request_id: str = "", clip_index: int = 0) -> None:
    try:
        _download_http_video(url, path, verify_tls=verify_tls, request_id=request_id, clip_index=clip_index)
    except TypeError as exc:
        # Compatibility fallback for stale runtime where old signature may still be loaded.
        if "unexpected keyword argument 'request_id'" not in str(exc):
            raise
        _download_http_video(url, path, verify_tls=verify_tls)


def _download_http_video(url: str, path: str, verify_tls: bool, request_id: str = "", clip_index: int = 0) -> None:
    try:
        _download_http_video_once(
            url,
            path,
            verify_tls=verify_tls,
            use_env_proxy=True,
            request_id=request_id,
            clip_index=clip_index,
        )
        return
    except requests.exceptions.ProxyError:
        # Proxy tunnel failed; retry once by bypassing env proxies.
        _log(request_id, f"clip#{clip_index} proxy failed, retrying direct connection")
        _download_http_video_once(
            url,
            path,
            verify_tls=verify_tls,
            use_env_proxy=False,
            request_id=request_id,
            clip_index=clip_index,
        )


def _download_http_video_once(
    url: str,
    path: str,
    verify_tls: bool,
    use_env_proxy: bool,
    request_id: str = "",
    clip_index: int = 0,
) -> None:
    request_kwargs = {
        "stream": True,
        "timeout": 180,
        "verify": verify_tls,
    }

    try:
        if use_env_proxy:
            with requests.get(url, **request_kwargs) as resp:
                resp.raise_for_status()
                with open(path, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=1024 * 256):
                        if chunk:
                            f.write(chunk)
            return

        with requests.Session() as session:
            session.trust_env = False
            with session.get(url, proxies={"http": None, "https": None}, **request_kwargs) as resp:
                resp.raise_for_status()
                with open(path, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=1024 * 256):
                        if chunk:
                            f.write(chunk)
    except Exception as exc:
        channel = "proxy" if use_env_proxy else "direct"
        _log(request_id, f"clip#{clip_index} {channel} download error: {type(exc).__name__}: {exc}")
        raise


def _resolve_local_source_path(url: str) -> str:
    text = _safe_text(url)
    if not text:
        return ""
    if text.lower().startswith(("http://", "https://")):
        return ""

    if text.lower().startswith("file://"):
        candidate = text[7:]
        if os.name == "nt":
            candidate = candidate.lstrip("/")
        candidate_path = os.path.abspath(os.path.expanduser(candidate))
        return candidate_path if os.path.isfile(candidate_path) else ""

    candidates = []
    if os.path.isabs(text):
        candidates.append(text)
    else:
        candidates.append(os.path.join(BACKEND_DIR, text.lstrip("/\\")))
        candidates.append(os.path.abspath(text))

    for candidate in candidates:
        candidate_path = os.path.abspath(os.path.expanduser(candidate))
        if os.path.isfile(candidate_path):
            return candidate_path
    return ""


def _resolve_overlap_seconds(left_duration: float, right_duration: float) -> float:
    left = max(0.0, float(left_duration or 0.0))
    right = max(0.0, float(right_duration or 0.0))
    max_feasible = min(
        MAX_CROSSFADE_SECONDS,
        left * 0.45,
        right * 0.45,
    )
    if max_feasible <= 0:
        return 0.0
    if max_feasible < MIN_CROSSFADE_SECONDS:
        return round(max_feasible, 3)
    return round(max(MIN_CROSSFADE_SECONDS, min(DEFAULT_CROSSFADE_SECONDS, max_feasible)), 3)


def _compose_with_crossfade(video_clips: List[VideoFileClip]) -> Tuple[CompositeVideoClip, List[float], List[Dict[str, Any]]]:
    if len(video_clips) < 2:
        canvas_w = int(video_clips[0].w or 1920)
        canvas_h = int(video_clips[0].h or 1080)
        return CompositeVideoClip([video_clips[0]], size=(canvas_w, canvas_h)), [], []

    canvas_w = max(int(getattr(clip, "w", 0) or 0) for clip in video_clips) or 1920
    canvas_h = max(int(getattr(clip, "h", 0) or 0) for clip in video_clips) or 1080
    timeline_layers = []
    audio_layers = []
    overlaps: List[float] = []
    tail_segments: List[Dict[str, Any]] = []
    starts: List[float] = []

    cursor = 0.0
    for idx, clip in enumerate(video_clips):
        duration = float(getattr(clip, "duration", 0.0) or 0.0)
        if duration <= 0:
            duration = 0.01

        tail_start = max(0.0, duration - TAIL_SECONDS)
        tail_segments.append(
            {
                "index": idx + 1,
                "tail_start": round(tail_start, 3),
                "tail_duration": round(duration - tail_start, 3),
            }
        )

        overlap = 0.0
        if idx > 0:
            prev_duration = float(getattr(video_clips[idx - 1], "duration", 0.0) or 0.0)
            overlap = _resolve_overlap_seconds(prev_duration, duration)
            overlaps.append(overlap)
            cursor = max(0.0, cursor - overlap)
        starts.append(cursor)

        layer = clip.set_start(cursor).set_position(("center", "center"))
        if idx > 0 and overlap > 0:
            layer = layer.crossfadein(overlap)
        timeline_layers.append(layer)

        audio = clip.audio
        if audio is not None:
            if idx > 0 and overlap > 0:
                audio = audio.fx(audio_fadein, overlap)
            if idx < len(video_clips) - 1:
                next_duration = float(getattr(video_clips[idx + 1], "duration", 0.0) or 0.0)
                out_overlap = _resolve_overlap_seconds(duration, next_duration)
                if out_overlap > 0:
                    audio = audio.fx(audio_fadeout, out_overlap)
            audio_layers.append(audio.set_start(cursor))

        cursor += duration

    final_clip = CompositeVideoClip(timeline_layers, size=(canvas_w, canvas_h))
    if audio_layers:
        final_clip = final_clip.set_audio(CompositeAudioClip(audio_layers))
    return final_clip, overlaps, tail_segments


def export_final_video(shots: Any, episode_no: Any = 1, request_id: str = "") -> Dict[str, Any]:
    rid = _safe_text(request_id) or uuid.uuid4().hex[:8]
    clips_meta = _collect_export_clips(shots)
    _log(
        rid,
        f"start export episode={_safe_episode_no(episode_no)} raw_shots={len(shots) if isinstance(shots, list) else 'n/a'} active_clips={len(clips_meta)}",
    )
    if not clips_meta:
        _log(rid, "no clips to export")
        return {"success": False, "error": "没有可导出的入片视频镜头"}

    episode = _safe_episode_no(episode_no)

    video_clips: List[VideoFileClip] = []
    final_clip = None
    output_path = ""
    export_result: Dict[str, Any] = {}

    try:
        os.makedirs(EXPORT_DIR, exist_ok=True)
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                local_paths: List[str] = []
                for idx, item in enumerate(clips_meta, start=1):
                    ext = _guess_video_ext(item["video_url"])
                    local_path = os.path.join(temp_dir, f"clip_{idx:03d}{ext}")
                    _download_video(item["video_url"], local_path, request_id=rid, clip_index=idx)
                    if (not os.path.exists(local_path)) or os.path.getsize(local_path) <= 0:
                        raise ValueError(f"clip {idx} download is empty: {item['video_url']}")
                    _log(rid, f"clip#{idx} downloaded size={os.path.getsize(local_path)}B")
                    local_paths.append(local_path)

                for idx, path in enumerate(local_paths, start=1):
                    clip = VideoFileClip(path)
                    video_clips.append(clip)
                    duration = float(getattr(clip, "duration", 0.0) or 0.0)
                    _log(rid, f"clip#{idx} opened duration={duration:.3f}s")

                if len(video_clips) == 1:
                    final_clip = video_clips[0]
                    overlap_seconds: List[float] = []
                    single_duration = float(getattr(video_clips[0], "duration", 0.0) or 0.0)
                    tail_segments = [
                        {
                            "index": 1,
                            "tail_start": round(max(0.0, single_duration - TAIL_SECONDS), 3),
                            "tail_duration": round(min(TAIL_SECONDS, single_duration), 3),
                        }
                    ]
                else:
                    final_clip, overlap_seconds, tail_segments = _compose_with_crossfade(video_clips)
                    _log(rid, f"crossfade overlaps={overlap_seconds}")

                filename = f"episode-{episode}-final-{uuid.uuid4().hex[:8]}.mp4"
                output_path = os.path.join(EXPORT_DIR, filename)
                temp_audio = os.path.join(temp_dir, "temp-audio.m4a")
                fps = getattr(final_clip, "fps", None) or getattr(video_clips[0], "fps", 24)
                duration = float(getattr(final_clip, "duration", 0.0) or 0.0)
                _log(
                    rid,
                    f"write start output={output_path} fps={fps} duration={duration:.3f}s preset={EXPORT_FFMPEG_PRESET} threads={EXPORT_FFMPEG_THREADS}",
                )
                write_started = time.perf_counter()
                final_clip.write_videofile(
                    output_path,
                    codec="libx264",
                    audio_codec="aac",
                    temp_audiofile=temp_audio,
                    remove_temp=True,
                    fps=fps,
                    preset=EXPORT_FFMPEG_PRESET,
                    threads=EXPORT_FFMPEG_THREADS,
                    ffmpeg_params=["-movflags", "+faststart"],
                    logger="bar",
                )
                write_elapsed = time.perf_counter() - write_started
                output_size = os.path.getsize(output_path) if os.path.isfile(output_path) else 0
                _log(rid, f"write done elapsed={write_elapsed:.2f}s size={output_size}B")

                export_result = {
                    "success": True,
                    "file_path": output_path,
                    "filename": filename,
                    "clips_count": len(video_clips),
                    "transition": "crossfade" if len(video_clips) > 1 else "single",
                    "overlap_seconds": overlap_seconds,
                    "tail_seconds": TAIL_SECONDS,
                    "tail_segments": tail_segments,
                }
            finally:
                # Close media handles before leaving TemporaryDirectory on Windows.
                try:
                    if final_clip is not None and final_clip not in video_clips:
                        final_clip.close()
                except Exception:
                    pass
                for clip in video_clips:
                    try:
                        clip.close()
                    except Exception:
                        pass
                final_clip = None
                video_clips = []
                _log(rid, "media handles closed")

        if export_result:
            _log(rid, f"export success file={export_result.get('filename')}")
            return export_result
        _log(rid, "export finished without result")
        return {"success": False, "error": "export failed"}

    except Exception as e:
        _log(rid, f"export error: {type(e).__name__}: {e}")
        _log(rid, traceback.format_exc())
        # Remove incomplete output file if write failed halfway.
        if output_path and os.path.exists(output_path):
            try:
                os.remove(output_path)
            except OSError:
                pass
        return {"success": False, "error": str(e)}
