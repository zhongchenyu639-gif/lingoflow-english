"""pywebview JavaScript bridge API."""

from __future__ import annotations

import base64
import sys
from pathlib import Path
from typing import Any

from backend.database import Database
from backend.tts import clone_voice_cloud, get_pack_audio, speak_windows_sapi, stop_windows_sapi


def _default_prompt_wav_path() -> Path:
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    else:
        base = Path(__file__).resolve().parent.parent
    return base / "frontend" / "assets" / "user_voice_prompt.wav"


class LingoFlowApi:
    """Exposed to frontend via window.pywebview.api."""

    def __init__(self, db: Database) -> None:
        self.db = db

    def get_dashboard(self) -> dict[str, Any]:
        return self.db.get_dashboard()

    def get_due_flashcards(self, category: str = "全部", limit: int = 20) -> list[dict[str, Any]]:
        return self.db.get_due_flashcards(category=category, limit=int(limit))

    def submit_flashcard_review(self, word_id: int, rating: str) -> dict[str, Any]:
        return self.db.submit_flashcard_review(word_id=int(word_id), rating=rating)

    def get_words(self, search: str = "", category: str = "全部") -> list[dict[str, Any]]:
        return self.db.get_words(search=search, category=category)

    def get_words_paged(
        self, search: str = "", category: str = "全部", page: int = 1, page_size: int = 50
    ) -> dict[str, Any]:
        return self.db.get_words_paged(
            search=search, category=category, page=int(page), page_size=int(page_size)
        )

    def get_listen_words(
        self, category: str = "全部", limit: int = 40, sort_mode: str = "shuffle"
    ) -> list[dict[str, Any]]:
        return self.db.get_listen_words(category=category, limit=int(limit), sort_mode=sort_mode)

    def add_word(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self.db.add_word(payload)

    def update_word(self, word_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        return self.db.update_word(int(word_id), payload)

    def toggle_favorite(self, word_id: int) -> dict[str, Any]:
        return self.db.toggle_favorite(int(word_id))

    def update_word_notes(self, word_id: int, notes: str) -> dict[str, Any]:
        return self.db.update_word_notes(int(word_id), notes)

    def delete_word(self, word_id: int) -> bool:
        return self.db.delete_word(int(word_id))

    def reset_word_progress(self, word_id: int) -> bool:
        return self.db.reset_word_progress(int(word_id))

    def import_words_text(self, raw_text: str, category: str = "自定义") -> dict[str, int]:
        return self.db.import_words_text(raw_text=raw_text, category=category)

    def export_words_text(self, category: str = "全部") -> str:
        return self.db.export_words_text(category=category)

    def get_quiz_questions(
        self, mode: str = "choice", category: str = "全部", count: int = 8
    ) -> list[dict[str, Any]]:
        return self.db.get_quiz_questions(mode=mode, category=category, count=int(count))

    def submit_quiz_result(
        self,
        activity_type: str,
        score: int,
        total: int,
        word_outcomes: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        return self.db.submit_quiz_result(
            activity_type=activity_type,
            score=int(score),
            total=int(total),
            word_outcomes=word_outcomes,
        )

    def get_dialogues(self) -> list[dict[str, Any]]:
        return self.db.get_dialogues()

    def get_grammar_notes(self) -> list[dict[str, Any]]:
        return self.db.get_grammar_notes()

    def update_settings(self, updates: dict[str, Any]) -> dict[str, str]:
        return self.db.update_settings(updates)

    def speak_fallback(self, text: str, rate: float = 1.0) -> dict[str, Any]:
        return speak_windows_sapi(text=text, rate=float(rate))

    def stop_speaking(self) -> dict[str, bool]:
        return stop_windows_sapi()

    def get_offline_audio(self, text: str, accent: str = "us-neural") -> dict[str, Any]:
        return get_pack_audio(text=text, accent=accent)

    def synthesize_cloned_speech(
        self, text: str, custom_sample_b64: str = "", ref_text: str = "你好。"
    ) -> dict[str, Any]:
        if custom_sample_b64:
            prompt_bytes = base64.b64decode(custom_sample_b64)
        else:
            wav_path = _default_prompt_wav_path()
            if not wav_path.is_file():
                return {"ok": False, "error": f"Missing voice sample: {wav_path}"}
            prompt_bytes = wav_path.read_bytes()

        cache_dir = self.db.db_path.parent / "voice_cache"
        return clone_voice_cloud(
            text=text,
            prompt_wav_bytes=prompt_bytes,
            ref_text=ref_text or "你好。",
            cache_dir=cache_dir,
        )
