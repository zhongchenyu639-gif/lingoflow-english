(function (globalScope) {
  "use strict";

  const STORAGE_KEY = "lingoflow_state_v2";
  const VIRTUAL_FAVORITES = "⭐ 我的收藏";
  const VIRTUAL_MISTAKES = "📕 易错词本";

  const DEFAULT_SETTINGS = {
    daily_goal: "15",
    tts_rate: "1.0",
    tts_accent: "us-neural",
    theme: "light",
    auto_play: "0",
    mic_calibration: "",
    listen_sort: "shuffle",
  };

  const _PAK_LRU_LIMIT = 24;
  const _pakCache = new Map();

  function fnv1aBucket(text) {
    const bytes = new TextEncoder().encode(text);
    let h = 0x811c9dc5;
    for (let i = 0; i < bytes.length; i++) {
      h ^= bytes[i];
      h = Math.imul(h, 0x01000193) >>> 0;
    }
    return (h & 0xff).toString(16).padStart(2, "0");
  }

  function parsePakBuffer(buf) {
    const view = new DataView(buf);
    const hdrLen = view.getUint32(0, true);
    const hdrJson = new TextDecoder().decode(new Uint8Array(buf, 4, hdrLen));
    return {
      index: JSON.parse(hdrJson),
      dataOffset: 4 + hdrLen,
      buffer: buf,
    };
  }

  function uint8ToBase64(bytes) {
    let binary = "";
    const chunk = 0x8000;
    for (let i = 0; i < bytes.length; i += chunk) {
      binary += String.fromCharCode.apply(null, bytes.subarray(i, i + chunk));
    }
    return btoa(binary);
  }

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
    const seed = seedInput || globalScope.LINGOFLOW_SEED || { words: [], compact_words: [], dialogues: [], grammar_notes: [] };
    const memStore = new Map();
    const storage =
      customStorage ||
      (typeof globalScope.window !== "undefined" && globalScope.window.localStorage
        ? globalScope.window.localStorage
        : {
            getItem: (k) => (memStore.has(k) ? memStore.get(k) : null),
            setItem: (k, v) => memStore.set(k, String(v)),
          });

    // Build immutable base dictionary in memory (keeps localStorage tiny even with 15k+ words)
    const baseEntries = [];
    let nextBaseId = 1;
    for (const w of seed.words || []) {
      baseEntries.push({
        id: nextBaseId++,
        word: w.word,
        phonetic: w.phonetic || "",
        part_of_speech: w.part_of_speech || "",
        meaning_zh: w.meaning_zh,
        example_en: w.example_en || "",
        example_zh: w.example_zh || "",
        category: w.category || "日常高频",
        difficulty: w.difficulty || 1,
      });
    }
    for (const row of seed.compact_words || []) {
      baseEntries.push({
        id: nextBaseId++,
        word: row[0],
        phonetic: row[1] || "",
        part_of_speech: row[2] || "",
        meaning_zh: row[3] || "",
        example_en: "",
        example_zh: "",
        category: row[4] || "高频拓展",
        difficulty: row[5] || 2,
      });
    }

    function loadUserStore() {
      try {
        const raw = storage.getItem(STORAGE_KEY);
        if (raw) {
          const p = JSON.parse(raw);
          if (p && typeof p === "object") {
            return {
              nextCustomId: p.nextCustomId || 1000000,
              progress: p.progress || {},
              edited: p.edited || {},
              deleted: Array.isArray(p.deleted) ? p.deleted : [],
              custom_words: Array.isArray(p.custom_words) ? p.custom_words : [],
              study_logs: Array.isArray(p.study_logs) ? p.study_logs : [],
              settings: { ...DEFAULT_SETTINGS, ...(p.settings || {}) },
            };
          }
        }
      } catch {}
      return {
        nextCustomId: 1000000,
        progress: {},
        edited: {},
        deleted: [],
        custom_words: [],
        study_logs: [],
        settings: { ...DEFAULT_SETTINGS },
      };
    }

    function saveUserStore(us) {
      storage.setItem(STORAGE_KEY, JSON.stringify(us));
    }

    const epochIso = "2020-01-01T00:00:00.000Z";

    function hydrateWord(base, us) {
      const ed = us.edited[base.id];
      const pr = us.progress[base.id];
      const w = ed ? { ...base, ...ed } : { ...base };
      return {
        ...w,
        ease_factor: pr?.ef ?? 2.5,
        interval_days: pr?.iv ?? 0,
        repetitions: pr?.rep ?? 0,
        next_review_at: pr?.next ?? epochIso,
        last_reviewed_at: pr?.last ?? null,
        correct_count: pr?.ok ?? 0,
        wrong_count: pr?.err ?? 0,
        is_favorite: pr?.fav ?? 0,
        notes: pr?.notes ?? "",
      };
    }

    function getAllWords(us) {
      const deletedSet = new Set(us.deleted);
      const out = [];
      for (const b of baseEntries) {
        if (!deletedSet.has(b.id)) out.push(hydrateWord(b, us));
      }
      for (const c of us.custom_words) {
        if (!deletedSet.has(c.id)) out.push(hydrateWord(c, us));
      }
      return out;
    }

    function findWordById(id, us) {
      const wid = Number(id);
      if (us.deleted.includes(wid)) return null;
      const b = baseEntries.find((x) => x.id === wid) || us.custom_words.find((x) => x.id === wid);
      return b ? hydrateWord(b, us) : null;
    }

    function filterWords(allWords, search = "", category = "全部") {
      const q = (search || "").trim().toLowerCase();
      return allWords.filter((w) => {
        if (category === VIRTUAL_FAVORITES && !w.is_favorite) return false;
        if (category === VIRTUAL_MISTAKES && !(w.wrong_count > 0)) return false;
        if (
          category &&
          category !== "全部" &&
          category !== VIRTUAL_FAVORITES &&
          category !== VIRTUAL_MISTAKES &&
          w.category !== category
        ) {
          return false;
        }
        if (q) {
          const hay = `${w.word} ${w.meaning_zh} ${w.example_en || ""} ${w.notes || ""}`.toLowerCase();
          if (!hay.includes(q)) return false;
        }
        return true;
      });
    }

    return {
      async get_dashboard() {
        const us = loadUserStore();
        const nowIso = new Date().toISOString();
        const today = new Date();
        const todayStr = localDateString(today);
        const dailyGoal = Math.max(1, parseInt(us.settings.daily_goal || "15", 10) || 15);

        const allWords = getAllWords(us);
        const totalWords = allWords.length;
        let learnedWords = 0;
        let reviewDue = 0;
        let masteredWords = 0;
        let favoritesCount = 0;
        let mistakesCount = 0;
        const catCounts = new Map();

        for (const w of allWords) {
          if (w.last_reviewed_at) {
            learnedWords += 1;
            if (w.next_review_at <= nowIso) reviewDue += 1;
          }
          if (w.repetitions >= 2 && w.interval_days >= 6) masteredWords += 1;
          if (w.is_favorite) favoritesCount += 1;
          if (w.wrong_count > 0) mistakesCount += 1;
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

        for (const log of us.study_logs) {
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
        const unlearned = Math.max(0, totalWords - learnedWords);
        const remainingNewQuota = Math.min(unlearned, Math.max(0, dailyGoal - todayCount));
        const dueWords = reviewDue + remainingNewQuota;

        const xp = totalCorrect * 10 + streak * 25 + masteredWords * 15;
        const level = Math.max(1, Math.floor(xp / 150) + 1);
        const titles = ["初学萌新", "词汇新星", "专注行者", "进阶学者", "口语达人", "词海领航", "语言大师"];
        const levelTitle = titles[Math.min(titles.length - 1, level - 1)];
        const badges = [
          { id: "first_step", name: "初次启航", desc: "完成首次学习记录", unlocked: us.study_logs.length > 0 },
          { id: "streak_3", name: "连签 3 天", desc: "连续学习打卡 3 天", unlocked: streak >= 3 },
          { id: "learned_50", name: "五十词斩", desc: "累计学习 50 个词汇", unlocked: learnedWords >= 50 },
          { id: "mastered_100", name: "百词熟练", desc: "熟练掌握 100 个词汇", unlocked: masteredWords >= 100 },
          { id: "fav_10", name: "精挑细选", desc: "收藏 10 个核心生词", unlocked: favoritesCount >= 10 },
          { id: "acc_90", name: "精准学霸", desc: "累计正确率达到 90%", unlocked: accuracy >= 90 && totalAnswered >= 10 },
        ];

        return {
          total_words: totalWords,
          learned_words: learnedWords,
          due_words: dueWords,
          review_due: reviewDue,
          mastered_words: masteredWords,
          favorites_count: favoritesCount,
          mistakes_count: mistakesCount,
          today_count: todayCount,
          daily_goal: dailyGoal,
          streak_days: streak,
          accuracy,
          xp,
          level,
          level_title: levelTitle,
          badges,
          categories,
          weekly_activity: [...dailyCounts.entries()].map(([date, count]) => ({
            date: date.slice(5),
            count,
          })),
          settings: { ...us.settings },
        };
      },

      async get_due_flashcards(category = "全部", limit = 20) {
        const us = loadUserStore();
        const nowIso = new Date().toISOString();
        const allWords = getAllWords(us);
        const lim = Number(limit) || 20;
        let selected;

        if (category === VIRTUAL_FAVORITES || category === VIRTUAL_MISTAKES) {
          const pred = category === VIRTUAL_FAVORITES ? (w) => Boolean(w.is_favorite) : (w) => w.wrong_count > 0;
          const matching = allWords.filter(pred);
          const due = matching.filter((w) => w.next_review_at <= nowIso);
          selected = (due.length ? due : matching)
            .sort((a, b) => a.next_review_at.localeCompare(b.next_review_at) || b.wrong_count - a.wrong_count || a.id - b.id)
            .slice(0, lim);
        } else {
          const pool = category && category !== "全部" ? allWords.filter((w) => w.category === category) : allWords;
          const due = pool
            .filter((w) => w.last_reviewed_at && w.next_review_at <= nowIso)
            .sort((a, b) => a.next_review_at.localeCompare(b.next_review_at) || a.id - b.id);
          const remaining = Math.max(0, lim - due.length);
          const fresh = remaining > 0 ? pool.filter((w) => !w.last_reviewed_at).slice(0, remaining) : [];
          selected = [...due.slice(0, lim), ...fresh];
        }

        return selected.map((item) => ({
          ...item,
          interval_previews: previewIntervals(item.ease_factor, item.interval_days, item.repetitions),
        }));
      },

      async submit_flashcard_review(word_id, rating) {
        const us = loadUserStore();
        const item = findWordById(word_id, us);
        if (!item) throw new Error(`Word not found: ${word_id}`);

        const result = calculateSM2(item.ease_factor, item.interval_days, item.repetitions, rating);
        const nowIso = new Date().toISOString();
        const isCorrect = rating !== "again" ? 1 : 0;

        const prev = us.progress[item.id] || {};
        us.progress[item.id] = {
          ...prev,
          ef: result.ease_factor,
          iv: result.interval_days,
          rep: result.repetitions,
          next: result.next_review_at,
          last: nowIso,
          ok: (prev.ok || 0) + isCorrect,
          err: (prev.err || 0) + (rating === "again" ? 1 : 0),
        };
        us.study_logs.unshift({
          activity_type: "flashcard",
          score: isCorrect,
          total: 1,
          duration_sec: 0,
          created_at: nowIso,
        });
        us.study_logs = us.study_logs.slice(0, 500);
        saveUserStore(us);

        return {
          word_id: item.id,
          interval_label: result.interval_label,
          next_review_at: result.next_review_at,
        };
      },

      async get_words(search = "", category = "全部") {
        const us = loadUserStore();
        return filterWords(getAllWords(us), search, category);
      },

      async get_words_paged(search = "", category = "全部", page = 1, page_size = 50) {
        const us = loadUserStore();
        const filtered = filterWords(getAllWords(us), search, category);
        const size = Math.max(10, Math.min(200, Number(page_size) || 50));
        const total = filtered.length;
        const total_pages = Math.max(1, Math.ceil(total / size));
        const curPage = Math.max(1, Math.min(total_pages, Number(page) || 1));
        const start = (curPage - 1) * size;
        return {
          items: filtered.slice(start, start + size),
          total,
          page: curPage,
          page_size: size,
          total_pages,
        };
      },

      async get_listen_words(category = "全部", limit = 40, sortMode = "shuffle") {
        const us = loadUserStore();
        let pool = filterWords(getAllWords(us), "", category);
        if (sortMode === "alpha_asc") {
          pool.sort((a, b) => a.word.toLowerCase().localeCompare(b.word.toLowerCase()));
        } else if (sortMode === "alpha_desc") {
          pool.sort((a, b) => b.word.toLowerCase().localeCompare(a.word.toLowerCase()));
        } else if (sortMode === "freq_asc") {
          pool = shuffleArray(pool);
          pool.sort((a, b) => (a.difficulty || 1) - (b.difficulty || 1));
        } else if (sortMode === "freq_desc") {
          pool = shuffleArray(pool);
          pool.sort((a, b) => (b.difficulty || 1) - (a.difficulty || 1));
        } else if (sortMode === "due") {
          pool = shuffleArray(pool);
          pool.sort((a, b) => {
            const wa = a.wrong_count > 0 ? 1 : 0;
            const wb = b.wrong_count > 0 ? 1 : 0;
            if (wa !== wb) return wb - wa;
            if (a.wrong_count !== b.wrong_count) return b.wrong_count - a.wrong_count;
            return String(a.next_review_at || "").localeCompare(String(b.next_review_at || ""));
          });
        } else if (sortMode === "newest") {
          pool.sort((a, b) => b.id - a.id);
        } else if (sortMode === "custom") {
          pool.sort((a, b) => (b.wrong_count - a.wrong_count) || (b.id - a.id));
        } else {
          pool = shuffleArray(pool);
        }
        return pool.slice(0, Number(limit) || 40);
      },

      async add_word(payload) {
        const us = loadUserStore();
        const word = (payload?.word || "").trim();
        const meaningZh = (payload?.meaning_zh || "").trim();
        if (!word || !meaningZh) throw new Error("英文单词和中文释义不能为空");
        const all = getAllWords(us);
        if (all.some((w) => w.word.toLowerCase() === word.toLowerCase())) {
          throw new Error(`单词 ${word} 已存在`);
        }

        const item = {
          id: us.nextCustomId++,
          word,
          phonetic: (payload.phonetic || "").trim(),
          part_of_speech: (payload.part_of_speech || "").trim(),
          meaning_zh: meaningZh,
          example_en: (payload.example_en || "").trim(),
          example_zh: (payload.example_zh || "").trim(),
          category: (payload.category || "自定义").trim() || "自定义",
          difficulty: Number(payload.difficulty || 1),
        };
        us.custom_words.push(item);
        if (payload.notes) {
          us.progress[item.id] = { notes: String(payload.notes).trim() };
        }
        saveUserStore(us);
        return findWordById(item.id, us);
      },

      async update_word(word_id, payload) {
        const us = loadUserStore();
        const item = findWordById(word_id, us);
        if (!item) throw new Error(`Word not found: ${word_id}`);
        const word = (payload?.word || "").trim();
        const meaningZh = (payload?.meaning_zh || "").trim();
        if (!word || !meaningZh) throw new Error("英文单词和中文释义不能为空");

        us.edited[item.id] = {
          word,
          phonetic: (payload.phonetic || "").trim(),
          part_of_speech: (payload.part_of_speech || "").trim(),
          meaning_zh: meaningZh,
          example_en: (payload.example_en || "").trim(),
          example_zh: (payload.example_zh || "").trim(),
          category: (payload.category || "自定义").trim() || "自定义",
        };
        us.progress[item.id] = {
          ...(us.progress[item.id] || {}),
          notes: (payload.notes || "").trim(),
        };
        saveUserStore(us);
        return findWordById(item.id, us);
      },

      async toggle_favorite(word_id) {
        const us = loadUserStore();
        const item = findWordById(word_id, us);
        if (!item) throw new Error(`Word not found: ${word_id}`);
        const nextFav = item.is_favorite ? 0 : 1;
        us.progress[item.id] = { ...(us.progress[item.id] || {}), fav: nextFav };
        saveUserStore(us);
        return { id: item.id, is_favorite: nextFav };
      },

      async update_word_notes(word_id, notes) {
        const us = loadUserStore();
        const item = findWordById(word_id, us);
        if (!item) throw new Error(`Word not found: ${word_id}`);
        const clean = (notes || "").trim();
        us.progress[item.id] = { ...(us.progress[item.id] || {}), notes: clean };
        saveUserStore(us);
        return { id: item.id, notes: clean };
      },

      async delete_word(word_id) {
        const us = loadUserStore();
        const wid = Number(word_id);
        if (!us.deleted.includes(wid)) {
          us.deleted.push(wid);
          saveUserStore(us);
          return true;
        }
        return false;
      },

      async reset_word_progress(word_id) {
        const us = loadUserStore();
        const item = findWordById(word_id, us);
        if (!item) return false;
        const prev = us.progress[item.id] || {};
        us.progress[item.id] = { fav: prev.fav || 0, notes: prev.notes || "" };
        saveUserStore(us);
        return true;
      },

      async import_words_text(raw_text, category = "自定义") {
        const us = loadUserStore();
        const existing = new Set(getAllWords(us).map((w) => w.word.toLowerCase()));
        let added = 0;
        let skipped = 0;

        for (const rawLine of String(raw_text || "").split(/\r?\n/)) {
          const line = rawLine.trim();
          if (!line || line.startsWith("#")) continue;
          const sep = line.includes("|") ? "|" : line.includes("\t") ? "\t" : ",";
          const parts = line.split(sep).map((p) => p.trim());
          if (parts.length < 2 || !parts[0] || !parts[1] || existing.has(parts[0].toLowerCase())) {
            skipped += 1;
            continue;
          }
          existing.add(parts[0].toLowerCase());
          us.custom_words.push({
            id: us.nextCustomId++,
            word: parts[0],
            meaning_zh: parts[1],
            phonetic: parts[2] || "",
            part_of_speech: "",
            example_en: parts[3] || "",
            example_zh: parts[4] || "",
            category: category || "自定义",
            difficulty: 1,
          });
          added += 1;
        }
        saveUserStore(us);
        return { added, skipped };
      },

      async export_words_text(category = "全部") {
        const words = await this.get_words("", category);
        return words
          .slice(0, 2000)
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
        const us = loadUserStore();
        const allWords = getAllWords(us);
        if (allWords.length < 4) return [];

        const pool = filterWords(allWords, "", category);
        const activePool = pool.length ? pool : allWords;
        const selected = shuffleArray(activePool).slice(0, Math.min(Number(count) || 8, activePool.length));

        return selected.map((item) => {
          const distractors = [];
          while (distractors.length < 3) {
            const pick = allWords[Math.floor(Math.random() * allWords.length)];
            if (pick.id !== item.id && !distractors.some((d) => d.id === pick.id)) {
              distractors.push(pick);
            }
          }
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
        const us = loadUserStore();
        const nowIso = new Date().toISOString();
        us.study_logs.unshift({
          activity_type,
          score: Number(score) || 0,
          total: Number(total) || 0,
          duration_sec: 0,
          created_at: nowIso,
        });
        us.study_logs = us.study_logs.slice(0, 500);

        if (Array.isArray(word_outcomes)) {
          for (const outcome of word_outcomes) {
            const wid = Number(outcome.word_id);
            const prev = us.progress[wid] || {};
            us.progress[wid] = {
              ...prev,
              last: nowIso,
              ok: (prev.ok || 0) + (outcome.correct ? 1 : 0),
              err: (prev.err || 0) + (outcome.correct ? 0 : 1),
            };
          }
        }
        saveUserStore(us);
        return { ok: true };
      },

      async get_dialogues() {
        return (seed.dialogues || []).map((d, idx) => ({ id: idx + 1, ...d }));
      },

      async get_grammar_notes() {
        return (seed.grammar_notes || []).map((g, idx) => ({ id: idx + 1, ...g }));
      },

      async update_settings(updates) {
        const us = loadUserStore();
        for (const [key, val] of Object.entries(updates || {})) {
          if (key in DEFAULT_SETTINGS) us.settings[key] = String(val);
        }
        saveUserStore(us);
        return { ...us.settings };
      },

      async speak_fallback() {
        return { ok: true, stopped: false };
      },

      async get_offline_audio(text, accent = "us-neural") {
        const key = String(text || "").trim().toLowerCase();
        if (!key) return { ok: false, error: "Empty text" };
        const code = accent === "gb-neural" || accent === "en-GB" ? "gb" : "us";
        const bucket = fnv1aBucket(key);
        const cacheKey = `${code}/${bucket}`;

        let entry = _pakCache.get(cacheKey);
        if (entry) {
          _pakCache.delete(cacheKey);
          _pakCache.set(cacheKey, entry);
        } else {
          try {
            const resp = await fetch(`voice_pak/${cacheKey}.pak`);
            if (!resp.ok) return { ok: false, error: `Pack HTTP ${resp.status}` };
            const buf = await resp.arrayBuffer();
            entry = parsePakBuffer(buf);
            _pakCache.set(cacheKey, entry);
            if (_pakCache.size > _PAK_LRU_LIMIT) {
              const oldest = _pakCache.keys().next().value;
              _pakCache.delete(oldest);
            }
          } catch (err) {
            return { ok: false, error: String(err) };
          }
        }

        const span = entry.index[key];
        if (!span) return { ok: false, error: "Not in voice pack" };
        const [off, len] = span;
        const slice = new Uint8Array(entry.buffer, entry.dataOffset + off, len);
        return { ok: true, audio_b64: uint8ToBase64(slice), mime: "audio/mpeg" };
      },

      async stop_speaking() {
        return { ok: true };
      },

      async synthesize_cloned_speech(text, customSampleB64 = "", refText = "") {
        const clean = String(text || "").trim();
        if (!clean) return { ok: false, error: "Empty text" };
        const sampleB64 = customSampleB64 || globalScope.USER_VOICE_SAMPLE_B64 || "";
        const ref = refText || globalScope.USER_VOICE_REF_TEXT || "Hi there! What can I get started for you today?";
        if (!sampleB64) return { ok: false, error: "Missing voice sample" };

        const cacheKey = `${clean.toLowerCase()}|${sampleB64.slice(0, 32)}|${ref}`;
        if (!createLocalLingoApi._audioCache) createLocalLingoApi._audioCache = new Map();
        const audioCache = createLocalLingoApi._audioCache;

        if (audioCache.has(cacheKey)) {
          return { ok: true, audio_b64: audioCache.get(cacheKey), cached: true };
        }
        return { ok: false, error: "Offline mode: cloud TTS disabled" };
      },
    };
  }

  globalScope.createLocalLingoApi = createLocalLingoApi;
  if (typeof globalScope.window !== "undefined") {
    globalScope.localLingoApi = createLocalLingoApi();
  }
  if (typeof module !== "undefined" && module.exports) {
    module.exports = { createLocalLingoApi, calculateSM2, previewIntervals, fnv1aBucket, parsePakBuffer };
  }
})(typeof globalThis !== "undefined" ? globalThis : window);
