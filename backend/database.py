"""SQLite database management for LingoFlow."""

from __future__ import annotations

import json
import random
import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from backend.seed_data import SEED_DIALOGUES, SEED_GRAMMAR, SEED_WORDS
from backend.sm2 import calculate_sm2, preview_intervals


VIRTUAL_FAVORITES = "⭐ 我的收藏"
VIRTUAL_MISTAKES = "📕 易错词本"

DEFAULT_SETTINGS = {
    "daily_goal": "15",
    "tts_rate": "1.0",
    "tts_accent": "us-neural",
    "theme": "light",
    "auto_play": "0",
    "mic_calibration": "",
    "listen_sort": "shuffle",
}


class Database:
    """Encapsulates all SQLite persistence and learning queries."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()
        self._seed_if_empty()

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS words (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT NOT NULL UNIQUE,
                    phonetic TEXT DEFAULT '',
                    part_of_speech TEXT DEFAULT '',
                    meaning_zh TEXT NOT NULL,
                    example_en TEXT DEFAULT '',
                    example_zh TEXT DEFAULT '',
                    category TEXT DEFAULT '自定义',
                    difficulty INTEGER DEFAULT 1,
                    ease_factor REAL DEFAULT 2.5,
                    interval_days INTEGER DEFAULT 0,
                    repetitions INTEGER DEFAULT 0,
                    next_review_at TEXT NOT NULL,
                    last_reviewed_at TEXT,
                    correct_count INTEGER DEFAULT 0,
                    wrong_count INTEGER DEFAULT 0,
                    is_favorite INTEGER DEFAULT 0,
                    notes TEXT DEFAULT '',
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS dialogues (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    scene TEXT NOT NULL,
                    level TEXT NOT NULL,
                    lines_json TEXT NOT NULL,
                    key_phrases_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS grammar_notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    level TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    explanation TEXT NOT NULL,
                    examples_json TEXT NOT NULL,
                    common_mistakes_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS study_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    activity_type TEXT NOT NULL,
                    score INTEGER DEFAULT 0,
                    total INTEGER DEFAULT 0,
                    duration_sec INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """
            )
            for ddl in (
                "ALTER TABLE words ADD COLUMN is_favorite INTEGER DEFAULT 0",
                "ALTER TABLE words ADD COLUMN notes TEXT DEFAULT ''",
                "CREATE INDEX IF NOT EXISTS idx_words_cat ON words(category)",
                "CREATE INDEX IF NOT EXISTS idx_words_due ON words(next_review_at)",
            ):
                try:
                    conn.execute(ddl)
                except sqlite3.OperationalError:
                    pass

    def _seed_if_empty(self) -> None:
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT OR IGNORE INTO words (
                    word, phonetic, part_of_speech, meaning_zh,
                    example_en, example_zh, category, difficulty,
                    next_review_at, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [(*item, now_iso, now_iso) for item in SEED_WORDS],
            )

            existing_dlgs = {r[0] for r in conn.execute("SELECT title FROM dialogues").fetchall()}
            new_dlgs = [d for d in SEED_DIALOGUES if d["title"] not in existing_dlgs]
            if new_dlgs:
                conn.executemany(
                    """
                    INSERT INTO dialogues (title, scene, level, lines_json, key_phrases_json)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    [
                        (
                            d["title"],
                            d["scene"],
                            d["level"],
                            json.dumps(d["lines"], ensure_ascii=False),
                            json.dumps(d["key_phrases"], ensure_ascii=False),
                        )
                        for d in new_dlgs
                    ],
                )

            existing_grams = {r[0] for r in conn.execute("SELECT title FROM grammar_notes").fetchall()}
            new_grams = [g for g in SEED_GRAMMAR if g["title"] not in existing_grams]
            if new_grams:
                conn.executemany(
                    """
                    INSERT INTO grammar_notes (
                        title, category, level, summary, explanation,
                        examples_json, common_mistakes_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    [
                        (
                            g["title"],
                            g["category"],
                            g["level"],
                            g["summary"],
                            g["explanation"],
                            json.dumps(g["examples"], ensure_ascii=False),
                            json.dumps(g["common_mistakes"], ensure_ascii=False),
                        )
                        for g in new_grams
                    ],
                )

            for key, value in DEFAULT_SETTINGS.items():
                conn.execute(
                    "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
                    (key, value),
                )

    def get_settings(self) -> dict[str, str]:
        with self._connect() as conn:
            rows = conn.execute("SELECT key, value FROM settings").fetchall()
            result = dict(DEFAULT_SETTINGS)
            for row in rows:
                result[row["key"]] = row["value"]
            return result

    def update_settings(self, updates: dict[str, Any]) -> dict[str, str]:
        with self._connect() as conn:
            for key, value in updates.items():
                if key in DEFAULT_SETTINGS:
                    conn.execute(
                        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                        (key, str(value)),
                    )
        return self.get_settings()

    def get_dashboard(self) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        today_local = datetime.now().date()
        settings = self.get_settings()
        daily_goal = max(1, int(settings.get("daily_goal", "15")))

        with self._connect() as conn:
            total_words = conn.execute("SELECT COUNT(*) FROM words").fetchone()[0]
            learned_words = conn.execute(
                "SELECT COUNT(*) FROM words WHERE last_reviewed_at IS NOT NULL"
            ).fetchone()[0]
            review_due = conn.execute(
                "SELECT COUNT(*) FROM words WHERE last_reviewed_at IS NOT NULL AND next_review_at <= ?",
                (now_iso,),
            ).fetchone()[0]
            mastered_words = conn.execute(
                "SELECT COUNT(*) FROM words WHERE repetitions >= 2 AND interval_days >= 6"
            ).fetchone()[0]
            favorites_count = conn.execute(
                "SELECT COUNT(*) FROM words WHERE is_favorite = 1"
            ).fetchone()[0]
            mistakes_count = conn.execute(
                "SELECT COUNT(*) FROM words WHERE wrong_count > 0"
            ).fetchone()[0]
            categories = [
                {"category": r["category"], "count": r["cnt"]}
                for r in conn.execute(
                    "SELECT category, COUNT(*) AS cnt FROM words GROUP BY category ORDER BY cnt DESC"
                ).fetchall()
            ]
            logs = conn.execute(
                "SELECT activity_type, score, total, created_at FROM study_logs ORDER BY created_at DESC LIMIT 500"
            ).fetchall()

        today_count = 0
        total_correct = 0
        total_answered = 0
        active_days = set()
        daily_counts: dict[str, int] = {}

        for i in range(6, -1, -1):
            day_str = (today_local - timedelta(days=i)).isoformat()
            daily_counts[day_str] = 0

        for log in logs:
            dt = datetime.fromisoformat(log["created_at"]).astimezone()
            day_str = dt.date().isoformat()
            active_days.add(day_str)
            items = max(1, log["total"] or 1)
            if dt.date() == today_local:
                today_count += items
            if day_str in daily_counts:
                daily_counts[day_str] += items
            if log["total"] > 0:
                total_correct += log["score"]
                total_answered += log["total"]

        streak = 0
        cursor = today_local
        while cursor.isoformat() in active_days:
            streak += 1
            cursor -= timedelta(days=1)

        accuracy = round((total_correct / total_answered) * 100) if total_answered > 0 else 0
        unlearned = max(0, total_words - learned_words)
        remaining_new_quota = min(unlearned, max(0, daily_goal - today_count))
        due_words = review_due + remaining_new_quota

        xp = total_correct * 10 + streak * 25 + mastered_words * 15
        level = max(1, xp // 150 + 1)
        titles = ["初学萌新", "词汇新星", "专注行者", "进阶学者", "口语达人", "词海领航", "语言大师"]
        level_title = titles[min(len(titles) - 1, level - 1)]
        badges = [
            {"id": "first_step", "name": "初次启航", "desc": "完成首次学习记录", "unlocked": len(logs) > 0},
            {"id": "streak_3", "name": "连签 3 天", "desc": "连续学习打卡 3 天", "unlocked": streak >= 3},
            {"id": "learned_50", "name": "五十词斩", "desc": "累计学习 50 个词汇", "unlocked": learned_words >= 50},
            {"id": "mastered_100", "name": "百词熟练", "desc": "熟练掌握 100 个词汇", "unlocked": mastered_words >= 100},
            {"id": "fav_10", "name": "精挑细选", "desc": "收藏 10 个核心生词", "unlocked": favorites_count >= 10},
            {"id": "acc_90", "name": "精准学霸", "desc": "累计正确率达到 90%", "unlocked": accuracy >= 90 and total_answered >= 10},
        ]

        return {
            "total_words": total_words,
            "learned_words": learned_words,
            "due_words": due_words,
            "review_due": review_due,
            "mastered_words": mastered_words,
            "favorites_count": favorites_count,
            "mistakes_count": mistakes_count,
            "today_count": today_count,
            "daily_goal": daily_goal,
            "streak_days": streak,
            "accuracy": accuracy,
            "xp": xp,
            "level": level,
            "level_title": level_title,
            "badges": badges,
            "categories": categories,
            "weekly_activity": [
                {"date": k[5:], "count": v} for k, v in daily_counts.items()
            ],
            "settings": settings,
        }

    def get_due_flashcards(self, category: str = "全部", limit: int = 20) -> list[dict[str, Any]]:
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            if category in (VIRTUAL_FAVORITES, VIRTUAL_MISTAKES):
                cond = "is_favorite = 1" if category == VIRTUAL_FAVORITES else "wrong_count > 0"
                rows = conn.execute(
                    f"""
                    SELECT * FROM words
                    WHERE next_review_at <= ? AND {cond}
                    ORDER BY next_review_at ASC, wrong_count DESC, id ASC
                    LIMIT ?
                    """,
                    (now_iso, limit),
                ).fetchall()
                if not rows:
                    rows = conn.execute(
                        f"""
                        SELECT * FROM words
                        WHERE {cond}
                        ORDER BY next_review_at ASC, wrong_count DESC, id ASC
                        LIMIT ?
                        """,
                        (limit,),
                    ).fetchall()
            else:
                cat_clause = "AND category = ?" if (category and category != "全部") else ""
                cat_params = (category,) if cat_clause else ()
                due_rows = conn.execute(
                    f"""
                    SELECT * FROM words
                    WHERE last_reviewed_at IS NOT NULL AND next_review_at <= ? {cat_clause}
                    ORDER BY next_review_at ASC, id ASC
                    LIMIT ?
                    """,
                    (now_iso, *cat_params, limit),
                ).fetchall()
                remaining = max(0, limit - len(due_rows))
                new_rows = []
                if remaining > 0:
                    new_rows = conn.execute(
                        f"""
                        SELECT * FROM words
                        WHERE last_reviewed_at IS NULL {cat_clause}
                        ORDER BY id ASC
                        LIMIT ?
                        """,
                        (*cat_params, remaining),
                    ).fetchall()
                rows = list(due_rows) + list(new_rows)

        cards = []
        for row in rows:
            item = dict(row)
            item["interval_previews"] = preview_intervals(
                item["ease_factor"],
                item["interval_days"],
                item["repetitions"],
            )
            cards.append(item)
        return cards

    def submit_flashcard_review(self, word_id: int, rating: str) -> dict[str, Any]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM words WHERE id = ?", (word_id,)).fetchone()
            if not row:
                raise ValueError(f"Word not found: {word_id}")

            result = calculate_sm2(
                ease_factor=row["ease_factor"],
                interval_days=row["interval_days"],
                repetitions=row["repetitions"],
                rating=rating,
            )
            now_iso = datetime.now(timezone.utc).isoformat()
            is_correct = 1 if rating != "again" else 0
            is_wrong = 1 if rating == "again" else 0

            conn.execute(
                """
                UPDATE words
                SET ease_factor = ?,
                    interval_days = ?,
                    repetitions = ?,
                    next_review_at = ?,
                    last_reviewed_at = ?,
                    correct_count = correct_count + ?,
                    wrong_count = wrong_count + ?
                WHERE id = ?
                """,
                (
                    result.ease_factor,
                    result.interval_days,
                    result.repetitions,
                    result.next_review_at,
                    now_iso,
                    is_correct,
                    is_wrong,
                    word_id,
                ),
            )
            conn.execute(
                """
                INSERT INTO study_logs (activity_type, score, total, duration_sec, created_at)
                VALUES ('flashcard', ?, 1, 0, ?)
                """,
                (is_correct, now_iso),
            )

        return {
            "word_id": word_id,
            "interval_label": result.interval_label,
            "next_review_at": result.next_review_at,
        }

    def _build_word_filter(self, search: str = "", category: str = "全部") -> tuple[str, list[Any]]:
        where = "WHERE 1=1"
        params: list[Any] = []
        if category == VIRTUAL_FAVORITES:
            where += " AND is_favorite = 1"
        elif category == VIRTUAL_MISTAKES:
            where += " AND wrong_count > 0"
        elif category and category != "全部":
            where += " AND category = ?"
            params.append(category)
        if search.strip():
            like = f"%{search.strip()}%"
            where += " AND (word LIKE ? OR meaning_zh LIKE ? OR example_en LIKE ? OR notes LIKE ?)"
            params.extend([like, like, like, like])
        return where, params

    def get_words(self, search: str = "", category: str = "全部") -> list[dict[str, Any]]:
        where, params = self._build_word_filter(search, category)
        query = f"SELECT * FROM words {where} ORDER BY id ASC"
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def get_words_paged(
        self,
        search: str = "",
        category: str = "全部",
        page: int = 1,
        page_size: int = 50,
    ) -> dict[str, Any]:
        page = max(1, int(page))
        page_size = max(10, min(200, int(page_size)))
        where, params = self._build_word_filter(search, category)
        with self._connect() as conn:
            total = conn.execute(f"SELECT COUNT(*) FROM words {where}", params).fetchone()[0]
            total_pages = max(1, (total + page_size - 1) // page_size)
            page = min(page, total_pages)
            offset = (page - 1) * page_size
            rows = conn.execute(
                f"SELECT * FROM words {where} ORDER BY id ASC LIMIT ? OFFSET ?",
                (*params, page_size, offset),
            ).fetchall()
        return {
            "items": [dict(r) for r in rows],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }

    def get_listen_words(
        self, category: str = "全部", limit: int = 40, sort_mode: str = "shuffle"
    ) -> list[dict[str, Any]]:
        order_map = {
            "shuffle": "RANDOM()",
            "due": "(wrong_count > 0) DESC, wrong_count DESC, next_review_at ASC, RANDOM()",
            "freq_asc": "difficulty ASC, RANDOM()",
            "freq_desc": "difficulty DESC, RANDOM()",
            "alpha_asc": "LOWER(word) ASC",
            "alpha_desc": "LOWER(word) DESC",
            "newest": "id DESC",
            "custom": "wrong_count DESC, id DESC",
        }
        order_sql = order_map.get(sort_mode, "RANDOM()")
        where, params = self._build_word_filter("", category)
        with self._connect() as conn:
            rows = conn.execute(
                f"SELECT * FROM words {where} ORDER BY {order_sql} LIMIT ?",
                (*params, int(limit)),
            ).fetchall()
        return [dict(r) for r in rows]

    def add_word(self, payload: dict[str, Any]) -> dict[str, Any]:
        word = (payload.get("word") or "").strip()
        meaning_zh = (payload.get("meaning_zh") or "").strip()
        if not word or not meaning_zh:
            raise ValueError("英文单词和中文释义不能为空")

        now_iso = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO words (
                    word, phonetic, part_of_speech, meaning_zh,
                    example_en, example_zh, category, difficulty,
                    next_review_at, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    word,
                    (payload.get("phonetic") or "").strip(),
                    (payload.get("part_of_speech") or "").strip(),
                    meaning_zh,
                    (payload.get("example_en") or "").strip(),
                    (payload.get("example_zh") or "").strip(),
                    (payload.get("category") or "自定义").strip() or "自定义",
                    int(payload.get("difficulty") or 1),
                    now_iso,
                    now_iso,
                ),
            )
            new_id = cursor.lastrowid
            row = conn.execute("SELECT * FROM words WHERE id = ?", (new_id,)).fetchone()
        return dict(row)

    def delete_word(self, word_id: int) -> bool:
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM words WHERE id = ?", (word_id,))
            return cur.rowcount > 0

    def toggle_favorite(self, word_id: int) -> dict[str, Any]:
        with self._connect() as conn:
            row = conn.execute("SELECT is_favorite FROM words WHERE id = ?", (word_id,)).fetchone()
            if not row:
                raise ValueError(f"Word not found: {word_id}")
            new_val = 0 if row["is_favorite"] else 1
            conn.execute("UPDATE words SET is_favorite = ? WHERE id = ?", (new_val, word_id))
        return {"id": word_id, "is_favorite": new_val}

    def update_word_notes(self, word_id: int, notes: str) -> dict[str, Any]:
        clean_notes = (notes or "").strip()
        with self._connect() as conn:
            cur = conn.execute("UPDATE words SET notes = ? WHERE id = ?", (clean_notes, word_id))
            if cur.rowcount == 0:
                raise ValueError(f"Word not found: {word_id}")
        return {"id": word_id, "notes": clean_notes}

    def update_word(self, word_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        word = (payload.get("word") or "").strip()
        meaning_zh = (payload.get("meaning_zh") or "").strip()
        if not word or not meaning_zh:
            raise ValueError("英文单词和中文释义不能为空")
        with self._connect() as conn:
            cur = conn.execute(
                """
                UPDATE words
                SET word = ?, phonetic = ?, part_of_speech = ?, meaning_zh = ?,
                    example_en = ?, example_zh = ?, category = ?, notes = ?
                WHERE id = ?
                """,
                (
                    word,
                    (payload.get("phonetic") or "").strip(),
                    (payload.get("part_of_speech") or "").strip(),
                    meaning_zh,
                    (payload.get("example_en") or "").strip(),
                    (payload.get("example_zh") or "").strip(),
                    (payload.get("category") or "自定义").strip() or "自定义",
                    (payload.get("notes") or "").strip(),
                    word_id,
                ),
            )
            if cur.rowcount == 0:
                raise ValueError(f"Word not found: {word_id}")
            row = conn.execute("SELECT * FROM words WHERE id = ?", (word_id,)).fetchone()
        return dict(row)

    def export_words_text(self, category: str = "全部") -> str:
        words = self.get_words(search="", category=category)
        lines = []
        for w in reversed(words):
            lines.append(
                " | ".join(
                    [
                        w.get("word", ""),
                        w.get("meaning_zh", ""),
                        w.get("phonetic", ""),
                        w.get("example_en", ""),
                        w.get("example_zh", ""),
                        w.get("category", "自定义"),
                    ]
                )
            )
        return "\n".join(lines)

    def reset_word_progress(self, word_id: int) -> bool:
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            cur = conn.execute(
                """
                UPDATE words
                SET ease_factor = 2.5, interval_days = 0, repetitions = 0,
                    next_review_at = ?, last_reviewed_at = NULL,
                    correct_count = 0, wrong_count = 0
                WHERE id = ?
                """,
                (now_iso, word_id),
            )
            return cur.rowcount > 0

    def import_words_text(self, raw_text: str, category: str = "自定义") -> dict[str, int]:
        """Import lines formatted as: word | meaning | [phonetic] | [example_en] | [example_zh]."""
        now_iso = datetime.now(timezone.utc).isoformat()
        added = 0
        skipped = 0
        with self._connect() as conn:
            for line in raw_text.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                sep = "|" if "|" in line else ("\t" if "\t" in line else ",")
                parts = [p.strip() for p in line.split(sep)]
                if len(parts) < 2 or not parts[0] or not parts[1]:
                    skipped += 1
                    continue
                word = parts[0]
                meaning = parts[1]
                phonetic = parts[2] if len(parts) > 2 else ""
                example_en = parts[3] if len(parts) > 3 else ""
                example_zh = parts[4] if len(parts) > 4 else ""
                try:
                    conn.execute(
                        """
                        INSERT INTO words (
                            word, phonetic, part_of_speech, meaning_zh,
                            example_en, example_zh, category, difficulty,
                            next_review_at, created_at
                        ) VALUES (?, ?, '', ?, ?, ?, ?, 1, ?, ?)
                        """,
                        (word, phonetic, meaning, example_en, example_zh, category, now_iso, now_iso),
                    )
                    added += 1
                except sqlite3.IntegrityError:
                    skipped += 1
        return {"added": added, "skipped": skipped}

    def get_quiz_questions(
        self,
        mode: str = "choice",
        category: str = "全部",
        count: int = 8,
    ) -> list[dict[str, Any]]:
        with self._connect() as conn:
            all_words = [dict(r) for r in conn.execute("SELECT * FROM words").fetchall()]

        if len(all_words) < 4:
            return []

        if category == VIRTUAL_FAVORITES:
            pool = [w for w in all_words if w.get("is_favorite")]
        elif category == VIRTUAL_MISTAKES:
            pool = [w for w in all_words if (w.get("wrong_count") or 0) > 0]
        elif category and category != "全部":
            pool = [w for w in all_words if w["category"] == category]
        else:
            pool = list(all_words)

        if not pool:
            pool = list(all_words)

        random.shuffle(pool)
        selected = pool[: min(count, len(pool))]
        questions = []

        for item in selected:
            distractors = [w for w in all_words if w["id"] != item["id"]]
            random.shuffle(distractors)
            options = [item] + distractors[:3]
            random.shuffle(options)

            example_en = item.get("example_en") or ""
            word = item["word"]
            cloze_en = re.sub(rf"\b{re.escape(word)}\b", "______", example_en, flags=re.IGNORECASE)
            if cloze_en == example_en and example_en:
                cloze_en = re.sub(re.escape(word), "______", example_en, flags=re.IGNORECASE)
            if not cloze_en or cloze_en == example_en:
                pos = item.get("part_of_speech") or "vocab"
                cloze_en = f"______ ({pos})"

            questions.append(
                {
                    "id": item["id"],
                    "mode": mode,
                    "word": item["word"],
                    "phonetic": item["phonetic"],
                    "part_of_speech": item["part_of_speech"],
                    "meaning_zh": item["meaning_zh"],
                    "example_en": item["example_en"],
                    "example_zh": item["example_zh"],
                    "cloze_en": cloze_en,
                    "is_favorite": item.get("is_favorite", 0),
                    "options": [
                        {"id": opt["id"], "word": opt["word"], "meaning_zh": opt["meaning_zh"]}
                        for opt in options
                    ],
                }
            )
        return questions

    def submit_quiz_result(
        self,
        activity_type: str,
        score: int,
        total: int,
        word_outcomes: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        now_iso = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO study_logs (activity_type, score, total, duration_sec, created_at)
                VALUES (?, ?, ?, 0, ?)
                """,
                (activity_type, score, total, now_iso),
            )
            if word_outcomes:
                for outcome in word_outcomes:
                    wid = outcome.get("word_id")
                    correct = bool(outcome.get("correct"))
                    if wid is None:
                        continue
                    if correct:
                        conn.execute(
                            "UPDATE words SET correct_count = correct_count + 1, last_reviewed_at = ? WHERE id = ?",
                            (now_iso, wid),
                        )
                    else:
                        conn.execute(
                            "UPDATE words SET wrong_count = wrong_count + 1, last_reviewed_at = ? WHERE id = ?",
                            (now_iso, wid),
                        )
        return {"ok": True}

    def get_dialogues(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM dialogues ORDER BY id ASC").fetchall()
        result = []
        for row in rows:
            result.append(
                {
                    "id": row["id"],
                    "title": row["title"],
                    "scene": row["scene"],
                    "level": row["level"],
                    "lines": json.loads(row["lines_json"]),
                    "key_phrases": json.loads(row["key_phrases_json"]),
                }
            )
        return result

    def get_grammar_notes(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM grammar_notes ORDER BY id ASC").fetchall()
        result = []
        for row in rows:
            result.append(
                {
                    "id": row["id"],
                    "title": row["title"],
                    "category": row["category"],
                    "level": row["level"],
                    "summary": row["summary"],
                    "explanation": row["explanation"],
                    "examples": json.loads(row["examples_json"]),
                    "common_mistakes": json.loads(row["common_mistakes_json"]),
                }
            )
        return result
