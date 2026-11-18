"""Offline Windows SAPI TTS fallback with interrupt/stop support."""

from __future__ import annotations

import subprocess
import threading
from typing import Any


_PROC_LOCK = threading.Lock()
_ACTIVE_PROC: subprocess.Popen[bytes] | None = None
_SPEAK_SEQ = 0


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
