(function (globalScope) {
  "use strict";

  const STORAGE_KEY = "lingoflow_ios_state_v1";
  const VIRTUAL_FAVORITES = "⭐ 我的收藏";
  const VIRTUAL_MISTAKES = "📕 易错词本";

  const DEFAULT_SETTINGS = {
    daily_goal: "15",
    tts_rate: "1.0",
    tts_accent: "en-US",
    theme: "light",
    auto_play: "0",
  };

  const RATING_QUALITY_MAP = {
    again: 1,
    hard: 3,
    good: 4,
    easy: 5,
  };

  function formatIntervalLabel(intervalDays, isRelearn = false) {
    if (isRelearn) return "10分钟后";
    if (intervalDays <= 0) return "今天";
    if (intervalDays === 1) return "1天";
    if (intervalDays < 30) return `${intervalDays}天`;
    return `${Math.round(intervalDays / 30)}个月`;
  }

  function calculateSM2(easeFactor, intervalDays, repetitions, rating, now = new Date()) {
    if (!(rating in RATING_QUALITY_MAP)) {
      throw new Error(`Unsupported rating: ${rating}`);
    }
    const quality = RATING_QUALITY_MAP[rating];
    let newEase = easeFactor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02));
    newEase = Math.max(1.3, Math.round(newEase * 100) / 100);

    let newRepetitions = 0;
    let newInterval = 0;
    let nextReview;
    let label;

    if (quality < 3) {
      newRepetitions = 0;
      newInterval = 0;
      nextReview = new Date(now.getTime() + 10 * 60 * 1000);
      label = formatIntervalLabel(0, true);
    } else {
      newRepetitions = repetitions + 1;
      if (newRepetitions === 1) {
        newInterval = rating !== "easy" ? 1 : 4;
      } else if (newRepetitions === 2) {
        newInterval = rating !== "easy" ? 6 : 8;
      } else {
        const base = Math.max(1, intervalDays);
        let multiplier = newEase;
        if (rating === "hard") multiplier = Math.max(1.2, newEase * 0.8);
        else if (rating === "easy") multiplier = newEase * 1.3;
        newInterval = Math.max(1, Math.round(base * multiplier));
      }
      nextReview = new Date(now.getTime() + newInterval * 24 * 60 * 60 * 1000);
      label = formatIntervalLabel(newInterval, false);
    }

    return {
      ease_factor: newEase,
      interval_days: newInterval,
      repetitions: newRepetitions,
      next_review_at: nextReview.toISOString(),
      interval_label: label,
    };
  }

  function previewIntervals(easeFactor, intervalDays, repetitions) {
    const out = {};
    for (const rating of Object.keys(RATING_QUALITY_MAP)) {
      out[rating] = calculateSM2(easeFactor, intervalDays, repetitions, rating).interval_label;
    }
    return out;
  }

  function localDateString(d) {
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
  }

  function escapeRegExp(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  function shuffleArray(arr) {
    const copy = [...arr];
    for (let i = copy.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [copy[i], copy[j]] = [copy[j], copy[i]];
    }
    return copy;
  }

  function createLocalLingoApi(seedInput, customStorage) {
    const seed = seedInput || globalScope.LINGOFLOW_SEED || { words: [], dialogues: [], grammar_notes: [] };
    const memStore = new Map();
    const storage =
      customStorage ||
      (typeof globalScope.window !== "undefined" && globalScope.window.localStorage
        ? globalScope.window.localStorage
        : {
            getItem: (k) => (memStore.has(k) ? memStore.get(k) : null),
            setItem: (k, v) => memStore.set(k, String(v)),
          });

    function buildInitialState() {
      const nowIso = new Date().toISOString();
      const words = (seed.words || []).map((w, idx) => ({
        id: idx + 1,
        word: w.word,
        phonetic: w.phonetic || "",
        part_of_speech: w.part_of_speech || "",
        meaning_zh: w.meaning_zh,
        example_en: w.example_en || "",
        example_zh: w.example_zh || "",
        category: w.category || "自定义",
        difficulty: w.difficulty || 1,
        ease_factor: 2.5,
        interval_days: 0,
        repetitions: 0,
        next_review_at: nowIso,
        last_reviewed_at: null,
        correct_count: 0,
        wrong_count: 0,
        is_favorite: 0,
        notes: "",
        created_at: nowIso,
      }));
      return {
        nextWordId: words.length + 1,
        words,
        study_logs: [],
        settings: { ...DEFAULT_SETTINGS },
      };
    }

    function loadState() {
      try {
        const raw = storage.getItem(STORAGE_KEY);
        if (raw) {
          const parsed = JSON.parse(raw);
          if (parsed && Array.isArray(parsed.words)) {
            parsed.settings = { ...DEFAULT_SETTINGS, ...(parsed.settings || {}) };
            parsed.study_logs = Array.isArray(parsed.study_logs) ? parsed.study_logs : [];
            parsed.nextWordId = parsed.nextWordId || (parsed.words.reduce((m, w) => Math.max(m, w.id || 0), 0) + 1);
            return parsed;
          }
        }
      } catch {
        // Re-seed if stored JSON is corrupted
      }
      const fresh = buildInitialState();
      saveState(fresh);
      return fresh;
    }

    function saveState(st) {
      storage.setItem(STORAGE_KEY, JSON.stringify(st));
    }

    return {
      async get_dashboard() {
        const st = loadState();
        const nowIso = new Date().toISOString();
        const today = new Date();
        const todayStr = localDateString(today);
        const dailyGoal = Math.max(1, parseInt(st.settings.daily_goal || "15", 10) || 15);

        const totalWords = st.words.length;
        const dueWords = st.words.filter((w) => w.next_review_at <= nowIso).length;
        const masteredWords = st.words.filter((w) => w.repetitions >= 2 && w.interval_days >= 6).length;
        const favoritesCount = st.words.filter((w) => Boolean(w.is_favorite)).length;
        const mistakesCount = st.words.filter((w) => (w.wrong_count || 0) > 0).length;

        const catCounts = new Map();
        for (const w of st.words) {
          const c = w.category || "自定义";
          catCounts.set(c, (catCounts.get(c) || 0) + 1);
        }
        const categories = [...catCounts.entries()]
          .map(([category, count]) => ({ category, count }))
          .sort((a, b) => b.count - a.count);

        const dailyCounts = new Map();
        for (let i = 6; i >= 0; i--) {
          const d = new Date(today.getFullYear(), today.getMonth(), today.getDate() - i);
          dailyCounts.set(localDateString(d), 0);
        }

        let todayCount = 0;
        let totalCorrect = 0;
        let totalAnswered = 0;
        const activeDays = new Set();

        for (const log of st.study_logs) {
          const dt = new Date(log.created_at);
          const dayStr = localDateString(dt);
          activeDays.add(dayStr);
          const items = Math.max(1, log.total || 1);
          if (dayStr === todayStr) todayCount += items;
          if (dailyCounts.has(dayStr)) dailyCounts.set(dayStr, dailyCounts.get(dayStr) + items);
          if ((log.total || 0) > 0) {
            totalCorrect += log.score || 0;
            totalAnswered += log.total;
          }
        }

        let streak = 0;
        for (let offset = 0; ; offset++) {
          const d = new Date(today.getFullYear(), today.getMonth(), today.getDate() - offset);
          if (activeDays.has(localDateString(d))) streak += 1;
          else break;
        }

        const accuracy = totalAnswered > 0 ? Math.round((totalCorrect / totalAnswered) * 100) : 0;

        return {
          total_words: totalWords,
          due_words: dueWords,
          mastered_words: masteredWords,
          favorites_count: favoritesCount,
          mistakes_count: mistakesCount,
          today_count: todayCount,
          daily_goal: dailyGoal,
          streak_days: streak,
          accuracy,
          categories,
          weekly_activity: [...dailyCounts.entries()].map(([date, count]) => ({
            date: date.slice(5),
            count,
          })),
          settings: { ...st.settings },
        };
      },

      async get_due_flashcards(category = "全部", limit = 20) {
        const st = loadState();
        const nowIso = new Date().toISOString();
        let rows;

        if (category === VIRTUAL_FAVORITES || category === VIRTUAL_MISTAKES) {
          const pred =
            category === VIRTUAL_FAVORITES
              ? (w) => Boolean(w.is_favorite)
              : (w) => (w.wrong_count || 0) > 0;
          const matching = st.words.filter(pred);
          const due = matching.filter((w) => w.next_review_at <= nowIso);
          rows = (due.length ? due : matching).sort(
            (a, b) =>
              a.next_review_at.localeCompare(b.next_review_at) ||
              (b.wrong_count || 0) - (a.wrong_count || 0) ||
              a.id - b.id
          );
        } else if (category && category !== "全部") {
          rows = st.words
            .filter((w) => w.next_review_at <= nowIso && w.category === category)
            .sort((a, b) => a.next_review_at.localeCompare(b.next_review_at) || a.id - b.id);
        } else {
          rows = st.words
            .filter((w) => w.next_review_at <= nowIso)
            .sort((a, b) => a.next_review_at.localeCompare(b.next_review_at) || a.id - b.id);
        }

        return rows.slice(0, Number(limit) || 20).map((item) => ({
          ...item,
          interval_previews: previewIntervals(item.ease_factor, item.interval_days, item.repetitions),
        }));
      },

      async submit_flashcard_review(word_id, rating) {
        const st = loadState();
        const item = st.words.find((w) => w.id === Number(word_id));
        if (!item) throw new Error(`Word not found: ${word_id}`);

        const result = calculateSM2(item.ease_factor, item.interval_days, item.repetitions, rating);
        const nowIso = new Date().toISOString();
        const isCorrect = rating !== "again" ? 1 : 0;

        item.ease_factor = result.ease_factor;
        item.interval_days = result.interval_days;
        item.repetitions = result.repetitions;
        item.next_review_at = result.next_review_at;
        item.last_reviewed_at = nowIso;
        item.correct_count = (item.correct_count || 0) + isCorrect;
        item.wrong_count = (item.wrong_count || 0) + (rating === "again" ? 1 : 0);

        st.study_logs.unshift({
          activity_type: "flashcard",
          score: isCorrect,
          total: 1,
          duration_sec: 0,
          created_at: nowIso,
        });
        st.study_logs = st.study_logs.slice(0, 500);
        saveState(st);

        return {
          word_id: item.id,
          interval_label: result.interval_label,
          next_review_at: result.next_review_at,
        };
      },

      async get_words(search = "", category = "全部") {
        const st = loadState();
        const q = (search || "").trim().toLowerCase();
        return st.words
          .filter((w) => {
            if (category === VIRTUAL_FAVORITES && !w.is_favorite) return false;
            if (category === VIRTUAL_MISTAKES && !(w.wrong_count > 0)) return false;
            if (category && category !== "全部" && category !== VIRTUAL_FAVORITES && category !== VIRTUAL_MISTAKES) {
              if (w.category !== category) return false;
            }
            if (q) {
              const hay = `${w.word} ${w.meaning_zh} ${w.example_en} ${w.notes || ""}`.toLowerCase();
              if (!hay.includes(q)) return false;
            }
            return true;
          })
          .sort((a, b) => b.id - a.id)
          .map((w) => ({ ...w }));
      },

      async add_word(payload) {
        const st = loadState();
        const word = (payload?.word || "").trim();
        const meaningZh = (payload?.meaning_zh || "").trim();
        if (!word || !meaningZh) throw new Error("英文单词和中文释义不能为空");
        if (st.words.some((w) => w.word.toLowerCase() === word.toLowerCase())) {
          throw new Error(`单词 ${word} 已存在`);
        }

        const nowIso = new Date().toISOString();
        const item = {
          id: st.nextWordId++,
          word,
          phonetic: (payload.phonetic || "").trim(),
          part_of_speech: (payload.part_of_speech || "").trim(),
          meaning_zh: meaningZh,
          example_en: (payload.example_en || "").trim(),
          example_zh: (payload.example_zh || "").trim(),
          category: (payload.category || "自定义").trim() || "自定义",
          difficulty: Number(payload.difficulty || 1),
          ease_factor: 2.5,
          interval_days: 0,
          repetitions: 0,
          next_review_at: nowIso,
          last_reviewed_at: null,
          correct_count: 0,
          wrong_count: 0,
          is_favorite: 0,
          notes: (payload.notes || "").trim(),
          created_at: nowIso,
        };
        st.words.push(item);
        saveState(st);
        return { ...item };
      },

      async update_word(word_id, payload) {
        const st = loadState();
        const item = st.words.find((w) => w.id === Number(word_id));
        if (!item) throw new Error(`Word not found: ${word_id}`);
        const word = (payload?.word || "").trim();
        const meaningZh = (payload?.meaning_zh || "").trim();
        if (!word || !meaningZh) throw new Error("英文单词和中文释义不能为空");

        item.word = word;
        item.phonetic = (payload.phonetic || "").trim();
        item.part_of_speech = (payload.part_of_speech || "").trim();
        item.meaning_zh = meaningZh;
        item.example_en = (payload.example_en || "").trim();
        item.example_zh = (payload.example_zh || "").trim();
        item.category = (payload.category || "自定义").trim() || "自定义";
        item.notes = (payload.notes || "").trim();
        saveState(st);
        return { ...item };
      },

      async toggle_favorite(word_id) {
        const st = loadState();
        const item = st.words.find((w) => w.id === Number(word_id));
        if (!item) throw new Error(`Word not found: ${word_id}`);
        item.is_favorite = item.is_favorite ? 0 : 1;
        saveState(st);
        return { id: item.id, is_favorite: item.is_favorite };
      },

      async update_word_notes(word_id, notes) {
        const st = loadState();
        const item = st.words.find((w) => w.id === Number(word_id));
        if (!item) throw new Error(`Word not found: ${word_id}`);
        item.notes = (notes || "").trim();
        saveState(st);
        return { id: item.id, notes: item.notes };
      },

      async delete_word(word_id) {
        const st = loadState();
        const before = st.words.length;
        st.words = st.words.filter((w) => w.id !== Number(word_id));
        if (st.words.length !== before) {
          saveState(st);
          return true;
        }
        return false;
      },

      async reset_word_progress(word_id) {
        const st = loadState();
        const item = st.words.find((w) => w.id === Number(word_id));
        if (!item) return false;
        item.ease_factor = 2.5;
        item.interval_days = 0;
        item.repetitions = 0;
        item.next_review_at = new Date().toISOString();
        item.last_reviewed_at = null;
        item.correct_count = 0;
        item.wrong_count = 0;
        saveState(st);
        return true;
      },

      async import_words_text(raw_text, category = "自定义") {
        const st = loadState();
        const nowIso = new Date().toISOString();
        const existing = new Set(st.words.map((w) => w.word.toLowerCase()));
        let added = 0;
        let skipped = 0;

        for (const rawLine of String(raw_text || "").split(/\r?\n/)) {
          const line = rawLine.trim();
          if (!line || line.startsWith("#")) continue;
          const sep = line.includes("|") ? "|" : line.includes("\t") ? "\t" : ",";
          const parts = line.split(sep).map((p) => p.trim());
          if (parts.length < 2 || !parts[0] || !parts[1]) {
            skipped += 1;
            continue;
          }
          if (existing.has(parts[0].toLowerCase())) {
            skipped += 1;
            continue;
          }
          existing.add(parts[0].toLowerCase());
          st.words.push({
            id: st.nextWordId++,
            word: parts[0],
            meaning_zh: parts[1],
            phonetic: parts[2] || "",
            part_of_speech: "",
            example_en: parts[3] || "",
            example_zh: parts[4] || "",
            category: category || "自定义",
            difficulty: 1,
            ease_factor: 2.5,
            interval_days: 0,
            repetitions: 0,
            next_review_at: nowIso,
            last_reviewed_at: null,
            correct_count: 0,
            wrong_count: 0,
            is_favorite: 0,
            notes: "",
            created_at: nowIso,
          });
          added += 1;
        }
        saveState(st);
        return { added, skipped };
      },

      async export_words_text(category = "全部") {
        const words = await this.get_words("", category);
        return words
          .slice()
          .reverse()
          .map((w) =>
            [
              w.word || "",
              w.meaning_zh || "",
              w.phonetic || "",
              w.example_en || "",
              w.example_zh || "",
              w.category || "自定义",
            ].join(" | ")
          )
          .join("\n");
      },

      async get_quiz_questions(mode = "choice", category = "全部", count = 8) {
        const st = loadState();
        const allWords = st.words;
        if (allWords.length < 4) return [];

        let pool;
        if (category === VIRTUAL_FAVORITES) {
          pool = allWords.filter((w) => Boolean(w.is_favorite));
        } else if (category === VIRTUAL_MISTAKES) {
          pool = allWords.filter((w) => (w.wrong_count || 0) > 0);
        } else if (category && category !== "全部") {
          pool = allWords.filter((w) => w.category === category);
        } else {
          pool = [...allWords];
        }
        if (!pool.length) pool = [...allWords];

        const selected = shuffleArray(pool).slice(0, Math.min(Number(count) || 8, pool.length));
        return selected.map((item) => {
          const distractors = shuffleArray(allWords.filter((w) => w.id !== item.id)).slice(0, 3);
          const options = shuffleArray([item, ...distractors]);
          const exampleEn = item.example_en || "";
          const escapedWord = escapeRegExp(item.word);
          let clozeEn = exampleEn.replace(new RegExp(`\\b${escapedWord}\\b`, "gi"), "______");
          if (clozeEn === exampleEn && exampleEn) {
            clozeEn = exampleEn.replace(new RegExp(escapedWord, "gi"), "______");
          }
          if (!clozeEn || clozeEn === exampleEn) {
            clozeEn = `______ (${item.part_of_speech || "vocab"})`;
          }
          return {
            id: item.id,
            mode,
            word: item.word,
            phonetic: item.phonetic,
            part_of_speech: item.part_of_speech,
            meaning_zh: item.meaning_zh,
            example_en: item.example_en,
            example_zh: item.example_zh,
            cloze_en: clozeEn,
            is_favorite: item.is_favorite || 0,
            options: options.map((o) => ({ id: o.id, word: o.word, meaning_zh: o.meaning_zh })),
          };
        });
      },

      async submit_quiz_result(activity_type, score, total, word_outcomes = null) {
        const st = loadState();
        const nowIso = new Date().toISOString();
        st.study_logs.unshift({
          activity_type,
          score: Number(score) || 0,
          total: Number(total) || 0,
          duration_sec: 0,
          created_at: nowIso,
        });
        st.study_logs = st.study_logs.slice(0, 500);

        if (Array.isArray(word_outcomes)) {
          for (const outcome of word_outcomes) {
            const item = st.words.find((w) => w.id === Number(outcome.word_id));
            if (!item) continue;
            item.last_reviewed_at = nowIso;
            if (outcome.correct) item.correct_count = (item.correct_count || 0) + 1;
            else item.wrong_count = (item.wrong_count || 0) + 1;
          }
        }
        saveState(st);
        return { ok: true };
      },

      async get_dialogues() {
        return (seed.dialogues || []).map((d, idx) => ({ id: idx + 1, ...d }));
      },

      async get_grammar_notes() {
        return (seed.grammar_notes || []).map((g, idx) => ({ id: idx + 1, ...g }));
      },

      async update_settings(updates) {
        const st = loadState();
        for (const [key, val] of Object.entries(updates || {})) {
          if (key in DEFAULT_SETTINGS) st.settings[key] = String(val);
        }
        saveState(st);
        return { ...st.settings };
      },

      async speak_fallback() {
        return { ok: true, stopped: false };
      },

      async stop_speaking() {
        return { ok: true };
      },
    };
  }

  globalScope.createLocalLingoApi = createLocalLingoApi;
  if (typeof globalScope.window !== "undefined") {
    globalScope.localLingoApi = createLocalLingoApi();
  }
  if (typeof module !== "undefined" && module.exports) {
    module.exports = { createLocalLingoApi, calculateSM2, previewIntervals };
  }
})(typeof globalThis !== "undefined" ? globalThis : window);
