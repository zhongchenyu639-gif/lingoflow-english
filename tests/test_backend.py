"""Unit tests for LingoFlow backend."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from backend.api import LingoFlowApi
from backend.database import Database, VIRTUAL_FAVORITES, VIRTUAL_MISTAKES
from backend.sm2 import calculate_sm2, preview_intervals
from backend.tts import stop_windows_sapi


class TestLingoFlowBackend(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp_dir.name) / "test.db"
        self.db = Database(self.db_path)
        self.api = LingoFlowApi(self.db)

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_sm2_progression_and_reset(self) -> None:
        r1 = calculate_sm2(2.5, 0, 0, "good")
        self.assertEqual(r1.repetitions, 1)
        self.assertEqual(r1.interval_days, 1)

        r2 = calculate_sm2(r1.ease_factor, r1.interval_days, r1.repetitions, "good")
        self.assertEqual(r2.repetitions, 2)
        self.assertEqual(r2.interval_days, 6)

        r_again = calculate_sm2(r2.ease_factor, r2.interval_days, r2.repetitions, "again")
        self.assertEqual(r_again.repetitions, 0)
        self.assertEqual(r_again.interval_days, 0)
        self.assertEqual(r_again.interval_label, "10分钟后")

        previews = preview_intervals(2.5, 0, 0)
        self.assertEqual(set(previews.keys()), {"again", "hard", "good", "easy"})

    def test_seed_data_and_dashboard(self) -> None:
        dash = self.api.get_dashboard()
        self.assertGreaterEqual(dash["total_words"], 60)
        self.assertEqual(dash["due_words"], dash["total_words"])
        self.assertGreaterEqual(len(self.api.get_dialogues()), 6)
        self.assertGreaterEqual(len(self.api.get_grammar_notes()), 8)

    def test_flashcard_review_flow(self) -> None:
        cards = self.api.get_due_flashcards(limit=5)
        self.assertEqual(len(cards), 5)
        first_id = cards[0]["id"]

        res = self.api.submit_flashcard_review(first_id, "good")
        self.assertEqual(res["interval_label"], "1天")

        dash = self.api.get_dashboard()
        self.assertEqual(dash["today_count"], 1)
        self.assertEqual(dash["due_words"], dash["total_words"] - 1)

    def test_wordbook_crud_and_import(self) -> None:
        created = self.api.add_word(
            {
                "word": "resilient",
                "phonetic": "/rɪˈzɪliənt/",
                "part_of_speech": "adj.",
                "meaning_zh": "有韧性的",
                "category": "自定义",
            }
        )
        self.assertEqual(created["word"], "resilient")

        imp = self.api.import_words_text(
            "serendipity | 意外惊喜 | /ˌserənˈdɪpəti/\nresilient | 重复词应跳过\nbadline\n",
            category="自定义",
        )
        self.assertEqual(imp["added"], 1)
        self.assertEqual(imp["skipped"], 2)

        self.assertTrue(self.api.delete_word(created["id"]))

    def test_quiz_generation_and_submission(self) -> None:
        qs = self.api.get_quiz_questions(mode="choice", count=5)
        self.assertEqual(len(qs), 5)
        for q in qs:
            self.assertEqual(len(q["options"]), 4)
            self.assertIn(q["id"], [o["id"] for o in q["options"]])

        res = self.api.submit_quiz_result(
            "quiz",
            4,
            5,
            [{"word_id": qs[0]["id"], "correct": True}],
        )
        self.assertTrue(res["ok"])

    def test_favorites_mistakes_notes_edit_export_cloze_and_stop(self) -> None:
        self.assertEqual(stop_windows_sapi(), {"ok": True})
        self.assertEqual(self.api.stop_speaking(), {"ok": True})

        words = self.api.get_words()
        target = words[0]
        wid = target["id"]

        # Toggle favorite on
        fav_res = self.api.toggle_favorite(wid)
        self.assertEqual(fav_res["is_favorite"], 1)
        fav_words = self.api.get_words(category=VIRTUAL_FAVORITES)
        self.assertEqual([w["id"] for w in fav_words], [wid])

        # Notes and edit word
        note_res = self.api.update_word_notes(wid, "词根记忆法")
        self.assertEqual(note_res["notes"], "词根记忆法")

        updated = self.api.update_word(
            wid,
            {
                "word": target["word"],
                "phonetic": target["phonetic"],
                "part_of_speech": target["part_of_speech"],
                "meaning_zh": target["meaning_zh"] + "（已修订）",
                "example_en": target["example_en"],
                "example_zh": target["example_zh"],
                "category": target["category"],
                "notes": "更新后的笔记",
            },
        )
        self.assertIn("已修订", updated["meaning_zh"])
        self.assertEqual(updated["notes"], "更新后的笔记")

        # Mark as mistake and verify virtual mistakes category
        self.api.submit_quiz_result("quiz", 0, 1, [{"word_id": wid, "correct": False}])
        mistake_words = self.api.get_words(category=VIRTUAL_MISTAKES)
        self.assertIn(wid, [w["id"] for w in mistake_words])

        # On-demand flashcards for favorites and mistakes even after review
        self.api.submit_flashcard_review(wid, "easy")
        fav_cards = self.api.get_due_flashcards(category=VIRTUAL_FAVORITES)
        self.assertTrue(any(c["id"] == wid for c in fav_cards))
        mistake_cards = self.api.get_due_flashcards(category=VIRTUAL_MISTAKES)
        self.assertTrue(any(c["id"] == wid for c in mistake_cards))

        # Cloze quiz generation & dashboard counts
        cloze_qs = self.api.get_quiz_questions(mode="cloze", category=VIRTUAL_FAVORITES, count=3)
        self.assertGreaterEqual(len(cloze_qs), 1)
        self.assertIn("______", cloze_qs[0]["cloze_en"])

        dash = self.api.get_dashboard()
        self.assertEqual(dash["favorites_count"], 1)
        self.assertEqual(dash["mistakes_count"], 1)

        # Export
        exported = self.api.export_words_text(category=VIRTUAL_FAVORITES)
        self.assertIn(target["word"], exported)

    def test_cloned_speech_cache_hit(self) -> None:
        import base64
        import hashlib
        from backend.tts import clone_voice_cloud

        sample = b"RIFFdemo_prompt_wav"
        text = "Hello cache test"
        ref = "你好。"
        prompt_hash = hashlib.sha1(sample).hexdigest()[:12]
        cache_key = hashlib.sha1(f"{text.lower()}|{prompt_hash}|{ref}".encode("utf-8")).hexdigest()
        cache_dir = Path(self.tmp_dir.name) / "voice_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        (cache_dir / f"{cache_key}.wav").write_bytes(b"RIFFcached_audio_payload_1234567890_1234567890_123456")

        res = clone_voice_cloud(text, sample, ref, cache_dir)
        self.assertTrue(res["ok"])
        self.assertTrue(res["cached"])
        self.assertEqual(base64.b64decode(res["audio_b64"]), b"RIFFcached_audio_payload_1234567890_1234567890_123456")


if __name__ == "__main__":
    unittest.main()
