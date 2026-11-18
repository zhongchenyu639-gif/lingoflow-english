"""Offline Windows SAPI TTS and local cached voice playback (100% offline)."""

from __future__ import annotations

import base64
import hashlib
import sqlite3
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any


_PROC_LOCK = threading.Lock()
_ACTIVE_PROC: subprocess.Popen[bytes] | None = None
_SPEAK_SEQ = 0


def get_voice_pack_dir() -> Path:
    """Directory holding voice_us.db / voice_gb.db (kept next to the exe, not inside it)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / "voice_packs"
    return Path(__file__).resolve().parent.parent / "voice_packs"


def get_pack_audio(text: str, accent: str = "us-neural", pack_dir: Path | None = None) -> dict[str, Any]:
    """Look up pre-generated broadcast MP3 for a word/sentence in the offline voice pack."""
    key = (text or "").strip().lower()
    if not key:
        return {"ok": False, "error": "Empty text"}
    code = "gb" if accent in ("gb-neural", "en-GB") else "us"
    pack_file = (pack_dir or get_voice_pack_dir()) / f"voice_{code}.db"
    if not pack_file.is_file():
        return {"ok": False, "error": f"Missing voice pack: {pack_file.name}"}
    conn = sqlite3.connect(f"file:{pack_file.as_posix()}?mode=ro", uri=True)
    try:
        row = conn.execute("SELECT mp3 FROM audio WHERE key = ?", (key,)).fetchone()
    finally:
        conn.close()
    if not row:
        return {"ok": False, "error": "Not in voice pack"}
    return {"ok": True, "audio_b64": base64.b64encode(row[0]).decode("ascii"), "mime": "audio/mpeg"}


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


def speak_windows_sapi(text: str, rate: float = 1.0, lang: str = "en-US") -> dict[str, Any]:
    """Speak English or Chinese text clearly at full volume using Windows System.Speech."""
    global _ACTIVE_PROC
    clean_text = (text or "").strip()
    if not clean_text:
        return {"ok": False, "stopped": False}

    stop_windows_sapi()

    sapi_rate = max(-6, min(6, round((rate - 1.0) * 6)))
    escaped = clean_text.replace("\r", " ").replace("\n", " ").replace("'", "''")
    culture = "zh-CN" if (lang or "").lower().startswith("zh") else "en-US"
    ps_script = (
        "Add-Type -AssemblyName System.Speech; "
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        "$s.Volume = 100; "
        f"$s.Rate = {sapi_rate}; "
        "try { $s.SelectVoiceByHints([System.Speech.Synthesis.VoiceGender]::Female, "
        f"[System.Speech.Synthesis.VoiceAge]::Adult, 0, [System.Globalization.CultureInfo]'{culture}') }} catch {{}}; "
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


def clone_voice_cloud(
    text: str,
    prompt_wav_bytes: bytes,
    ref_text: str,
    cache_dir: Path,
) -> dict[str, Any]:
    """Return locally cached WAV audio if present; never makes network requests."""
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

    return {"ok": False, "error": "Offline mode: cloud TTS disabled"}
