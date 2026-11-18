"""Offline Windows SAPI TTS fallback and Cloud Zero-Shot Voice Cloning."""

from __future__ import annotations

import base64
import hashlib
import json
import subprocess
import threading
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any


_PROC_LOCK = threading.Lock()
_ACTIVE_PROC: subprocess.Popen[bytes] | None = None
_SPEAK_SEQ = 0

_F5_BASE_URL = "https://mrfakename-e2-f5-tts.hf.space"
_UPLOAD_CACHE_LOCK = threading.Lock()
_UPLOADED_PROMPT_CACHE: dict[str, str] = {}


def stop_windows_sapi() -> dict[str, bool]:
    """Immediately stop any active Windows SAPI speech synthesis process."""
    global _ACTIVE_PROC, _SPEAK_SEQ
    with _PROC_LOCK:
        _SPEAK_SEQ += 1
        proc = _ACTIVE_PROC
        _ACTIVE_PROC = None
        if proc is not None and proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=0.5)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
    return {"ok": True}


def speak_windows_sapi(text: str, rate: float = 1.0) -> dict[str, Any]:
    """Speak English text using built-in Windows System.Speech synthesizer."""
    global _ACTIVE_PROC
    clean_text = (text or "").strip()
    if not clean_text:
        return {"ok": False, "stopped": False}

    # Stop any prior speech so clicks or dialogue playback never pile up
    stop_windows_sapi()

    sapi_rate = max(-6, min(6, round((rate - 1.0) * 6)))
    escaped = clean_text.replace("'", "''")
    ps_script = (
        "Add-Type -AssemblyName System.Speech; "
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        f"$s.Rate = {sapi_rate}; "
        "try { $s.SelectVoiceByHints([System.Speech.Synthesis.VoiceGender]::Female, "
        "[System.Speech.Synthesis.VoiceAge]::Adult, 0, [System.Globalization.CultureInfo]'en-US') } catch {}; "
        f"$s.Speak('{escaped}')"
    )

    with _PROC_LOCK:
        my_seq = _SPEAK_SEQ
        proc = subprocess.Popen(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        _ACTIVE_PROC = proc

    try:
        proc.wait()
    finally:
        with _PROC_LOCK:
            if _ACTIVE_PROC is proc:
                _ACTIVE_PROC = None

    return {"ok": True, "stopped": my_seq != _SPEAK_SEQ}


def _upload_prompt_to_f5(prompt_wav_bytes: bytes, prompt_hash: str) -> str:
    with _UPLOAD_CACHE_LOCK:
        cached = _UPLOADED_PROMPT_CACHE.get(prompt_hash)
    if cached:
        return cached

    boundary = f"----LingoFlow{uuid.uuid4().hex}"
    body = (
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="files"; filename="prompt.wav"\r\n'
        "Content-Type: audio/wav\r\n\r\n"
    ).encode("utf-8") + prompt_wav_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")

    req = urllib.request.Request(
        f"{_F5_BASE_URL}/gradio_api/upload",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=25) as resp:
        uploaded = json.loads(resp.read().decode("utf-8"))
    if not isinstance(uploaded, list) or not uploaded:
        raise RuntimeError(f"Unexpected upload response: {uploaded}")
    remote_path = str(uploaded[0])
    with _UPLOAD_CACHE_LOCK:
        _UPLOADED_PROMPT_CACHE[prompt_hash] = remote_path
    return remote_path


def _call_f5_predict(remote_path: str, ref_text: str, text: str) -> bytes:
    payload = json.dumps(
        {
            "data": [
                {"path": remote_path, "meta": {"_type": "gradio.FileData"}},
                ref_text,
                text,
                False,
            ]
        }
    ).encode("utf-8")
    call_req = urllib.request.Request(
        f"{_F5_BASE_URL}/gradio_api/call/predict",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(call_req, timeout=25) as resp:
        call_data = json.loads(resp.read().decode("utf-8"))
    event_id = call_data.get("event_id")
    if not event_id:
        raise RuntimeError(f"Missing event_id: {call_data}")

    sse_req = urllib.request.Request(f"{_F5_BASE_URL}/gradio_api/call/predict/{event_id}")
    with urllib.request.urlopen(sse_req, timeout=75) as resp:
        sse_text = resp.read().decode("utf-8", errors="replace")

    current_event = ""
    audio_url = ""
    for raw_line in sse_text.splitlines():
        line = raw_line.strip()
        if line.startswith("event:"):
            current_event = line[6:].strip()
        elif line.startswith("data:") and current_event == "complete":
            parsed = json.loads(line[5:].strip())
            if isinstance(parsed, list) and parsed and isinstance(parsed[0], dict):
                audio_url = parsed[0].get("url") or ""
                if not audio_url and parsed[0].get("path"):
                    audio_url = f"{_F5_BASE_URL}/gradio_api/file={parsed[0]['path']}"
            break
        elif line.startswith("data:") and current_event == "error":
            raise RuntimeError(f"Cloud TTS error: {line}")

    if not audio_url:
        raise RuntimeError(f"Cloud TTS returned no audio URL: {sse_text[:300]}")

    with urllib.request.urlopen(audio_url, timeout=30) as audio_resp:
        return audio_resp.read()


def clone_voice_cloud(
    text: str,
    prompt_wav_bytes: bytes,
    ref_text: str,
    cache_dir: Path,
) -> dict[str, Any]:
    """Synthesize cloned English speech via E2-F5-TTS Cloud API with local WAV cache."""
    clean_text = (text or "").strip()
    if not clean_text:
        return {"ok": False, "error": "Empty text"}
    if not prompt_wav_bytes:
        return {"ok": False, "error": "Empty prompt audio"}

    prompt_hash = hashlib.sha1(prompt_wav_bytes).hexdigest()[:12]
    key_src = f"{clean_text.lower()}|{prompt_hash}|{ref_text.strip()}".encode("utf-8")
    cache_key = hashlib.sha1(key_src).hexdigest()

    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / f"{cache_key}.wav"
    if cache_file.is_file() and cache_file.stat().st_size > 44:
        wav_bytes = cache_file.read_bytes()
        return {
            "ok": True,
            "audio_b64": base64.b64encode(wav_bytes).decode("ascii"),
            "cached": True,
        }

    try:
        remote_path = _upload_prompt_to_f5(prompt_wav_bytes, prompt_hash)
        try:
            wav_bytes = _call_f5_predict(remote_path, ref_text, clean_text)
        except Exception:
            # Retry once with fresh upload in case remote /tmp expired
            with _UPLOAD_CACHE_LOCK:
                _UPLOADED_PROMPT_CACHE.pop(prompt_hash, None)
            remote_path = _upload_prompt_to_f5(prompt_wav_bytes, prompt_hash)
            wav_bytes = _call_f5_predict(remote_path, ref_text, clean_text)

        cache_file.write_bytes(wav_bytes)
        return {
            "ok": True,
            "audio_b64": base64.b64encode(wav_bytes).decode("ascii"),
            "cached": False,
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
