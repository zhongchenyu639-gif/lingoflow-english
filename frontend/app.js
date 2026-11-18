const VIRTUAL_FAVORITES = "⭐ 我的收藏";
const VIRTUAL_MISTAKES = "📕 易错词本";

const state = {
  currentView: "dashboard",
  settings: {
    daily_goal: "15",
    tts_rate: "1.0",
    tts_accent: "en-US",
    theme: "light",
    auto_play: "0",
  },
  categories: [],
  favoritesCount: 0,
  mistakesCount: 0,
  flashcards: [],
  fcIndex: 0,
  fcFlipped: false,
  quizMode: "choice",
  quizQuestions: [],
  quizIndex: 0,
  quizScore: 0,
  quizAnswered: false,
  quizOutcomes: [],
  dialogues: [],
  activeDialogueIndex: 0,
  dialoguePlayState: "idle", // "idle" | "playing" | "paused"
  dialogueLineIndex: 0,
  grammarNotes: [],
  activeGrammarIndex: 0,
  // Audio control state
  speechToken: 0,
  isSpeakingSingle: false,
  isPausedSingle: false,
  activeAudioLabel: "",
  roleplayCancel: null,
};

const api = () => window.pywebview?.api || window.localLingoApi;

function showToast(msg) {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.classList.remove("hidden");
  clearTimeout(showToast._timer);
  showToast._timer = setTimeout(() => el.classList.add("hidden"), 2400);
}

function escapeHtml(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function updateAudioControllerUI() {
  const box = document.getElementById("audio-controller");
  const statusEl = document.getElementById("audio-status-text");
  const pauseBtn = document.getElementById("global-pause-btn");
  const stopBtn = document.getElementById("global-stop-btn");
  const quizStopBtn = document.getElementById("quiz-stop-btn");

  const isDlgActive = state.dialoguePlayState !== "idle";
  const isActive = isDlgActive || state.isSpeakingSingle;

  box.classList.toggle("active", isActive);
  pauseBtn.disabled = !isActive;
  stopBtn.disabled = !isActive;
  if (quizStopBtn) {
    quizStopBtn.classList.toggle("hidden", !state.isSpeakingSingle || state.currentView !== "quiz");
  }

  if (state.dialoguePlayState === "playing") {
    statusEl.textContent = state.activeAudioLabel || "🔊 正在播放对话...";
    pauseBtn.textContent = "⏸ 暂停";
  } else if (state.dialoguePlayState === "paused") {
    statusEl.textContent = `⏸ 已暂停 (${state.dialogueLineIndex + 1})`;
    pauseBtn.textContent = "▶ 继续";
  } else if (state.isSpeakingSingle) {
    if (state.isPausedSingle) {
      statusEl.textContent = "⏸ 发音已暂停";
      pauseBtn.textContent = "▶ 继续";
    } else {
      statusEl.textContent = state.activeAudioLabel || "🔊 正在朗读...";
      pauseBtn.textContent = "⏸ 暂停";
    }
  } else {
    statusEl.textContent = "🔇 语音空闲";
    pauseBtn.textContent = "⏸ 暂停";
  }

  updateDialogueControlUI();
}

function updateDialogueControlUI() {
  const playBtn = document.getElementById("dlg-play-all-btn");
  const stopBtn = document.getElementById("dlg-stop-btn");
  if (!playBtn || !stopBtn) return;

  if (state.dialoguePlayState === "playing") {
    playBtn.textContent = "⏸ 暂停对话";
    stopBtn.classList.remove("hidden");
  } else if (state.dialoguePlayState === "paused") {
    playBtn.textContent = "▶ 继续播放";
    stopBtn.classList.remove("hidden");
  } else {
    playBtn.textContent = "▶ 连续播放";
    stopBtn.classList.add("hidden");
  }
}

function speakSingleInternal(text, customRate = null, label = "🔊 正在朗读...") {
  const clean = (text || "").trim();
  if (!clean) return Promise.resolve(false);

  const myToken = ++state.speechToken;
  state.isSpeakingSingle = true;
  state.isPausedSingle = false;
  state.activeAudioLabel = label;
  updateAudioControllerUI();

  const rate = customRate ?? parseFloat(state.settings.tts_rate || "1.0");
  const accent = state.settings.tts_accent || "en-US";

  return new Promise((resolve) => {
    const finish = (completedNormally) => {
      if (myToken === state.speechToken) {
        state.isSpeakingSingle = false;
        state.isPausedSingle = false;
        updateAudioControllerUI();
      }
      resolve(completedNormally && myToken === state.speechToken);
    };

    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const voices = window.speechSynthesis.getVoices();
      const matched =
        voices.find((v) => v.lang === accent) ||
        voices.find((v) => v.lang.startsWith("en"));

      if (voices.length === 0 || matched) {
        const utter = new SpeechSynthesisUtterance(clean);
        window.__currentUtter = utter;
        utter.lang = accent;
        utter.rate = rate;
        if (matched) utter.voice = matched;
        utter.onend = () => finish(true);
        utter.onerror = () => {
          if (myToken !== state.speechToken) {
            finish(false);
            return;
          }
          api()
            .speak_fallback(clean, rate)
            .then((res) => finish(!res?.stopped))
            .catch(() => finish(false));
        };
        window.speechSynthesis.speak(utter);
        return;
      }
    }

    api()
      .speak_fallback(clean, rate)
      .then((res) => finish(!res?.stopped))
      .catch(() => finish(false));
  });
}

// Public single-utterance helper: stops any active continuous dialogue first
function speakText(text, customRate = null) {
  if (state.dialoguePlayState !== "idle") {
    state.dialoguePlayState = "idle";
    state.dialogueLineIndex = 0;
    if (state.roleplayCancel) state.roleplayCancel();
    document.querySelectorAll(".dlg-line").forEach((el) => el.classList.remove("speaking"));
  }
  return speakSingleInternal(text, customRate, `🔊 ${text.slice(0, 22)}`);
}

function stopAllSpeech() {
  state.speechToken += 1;
  if (state.roleplayCancel) {
    state.roleplayCancel();
    state.roleplayCancel = null;
  }
  state.dialoguePlayState = "idle";
  state.dialogueLineIndex = 0;
  state.isSpeakingSingle = false;
  state.isPausedSingle = false;
  state.activeAudioLabel = "";

  if ("speechSynthesis" in window) {
    window.speechSynthesis.cancel();
  }
  if (window.pywebview?.api?.stop_speaking) {
    api().stop_speaking().catch(() => {});
  }
  document.querySelectorAll(".dlg-line").forEach((el) => el.classList.remove("speaking"));
  updateAudioControllerUI();
}

function togglePauseSpeech() {
  if (state.dialoguePlayState === "playing") {
    state.dialoguePlayState = "paused";
    state.speechToken += 1;
    if (state.roleplayCancel) {
      state.roleplayCancel();
      state.roleplayCancel = null;
    }
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
    if (window.pywebview?.api?.stop_speaking) {
      api().stop_speaking().catch(() => {});
    }
    state.isSpeakingSingle = false;
    updateAudioControllerUI();
    return;
  }

  if (state.dialoguePlayState === "paused") {
    runDialogueLoop(state.dialogueLineIndex);
    return;
  }

  if (state.isSpeakingSingle && "speechSynthesis" in window) {
    if (!state.isPausedSingle) {
      window.speechSynthesis.pause();
      state.isPausedSingle = true;
    } else {
      window.speechSynthesis.resume();
      state.isPausedSingle = false;
    }
    updateAudioControllerUI();
  }
}

// Navigation
function navigateTo(viewName) {
  if (state.currentView !== viewName) {
    stopAllSpeech();
  }
  state.currentView = viewName;
  document.querySelectorAll(".nav-item").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.view === viewName);
  });
  document.querySelectorAll(".view").forEach((sec) => {
    sec.classList.toggle("active", sec.id === `view-${viewName}`);
  });

  if (viewName === "dashboard") loadDashboard();
  if (viewName === "flashcards") loadFlashcards();
  if (viewName === "dialogues") loadDialogues();
  if (viewName === "grammar") loadGrammar();
  if (viewName === "wordbook") loadWordbook();
  updateAudioControllerUI();
}

function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  const btn = document.getElementById("theme-toggle");
  btn.textContent = theme === "dark" ? "☀️ 切换浅色模式" : "🌙 切换深色模式";
}

function populateCategorySelects(categories, favoritesCount = 0, mistakesCount = 0) {
  state.categories = categories;
  state.favoritesCount = favoritesCount;
  state.mistakesCount = mistakesCount;

  const optionsHtml =
    `<option value="全部">全部分类</option>` +
    `<option value="${VIRTUAL_FAVORITES}">${VIRTUAL_FAVORITES} (${favoritesCount})</option>` +
    `<option value="${VIRTUAL_MISTAKES}">${VIRTUAL_MISTAKES} (${mistakesCount})</option>` +
    categories
      .map(
        (c) =>
          `<option value="${escapeHtml(c.category)}">${escapeHtml(c.category)} (${c.count})</option>`
      )
      .join("");

  ["fc-category", "quiz-category", "wb-category"].forEach((id) => {
    const sel = document.getElementById(id);
    const prev = sel.value || "全部";
    sel.innerHTML = optionsHtml;
    if ([...sel.options].some((o) => o.value === prev)) {
      sel.value = prev;
    }
  });
}

// Dashboard
async function loadDashboard() {
  const data = await api().get_dashboard();
  state.settings = data.settings;
  applyTheme(data.settings.theme || "light");

  document.getElementById("tts-accent").value = data.settings.tts_accent || "en-US";
  document.getElementById("tts-rate").value = data.settings.tts_rate || "1.0";
  document.getElementById("tts-rate-val").textContent = `${data.settings.tts_rate || "1.0"}x`;
  document.getElementById("daily-goal-input").value = data.daily_goal;
  document.getElementById("fc-auto-play").checked = data.settings.auto_play === "1";

  document.getElementById("stat-due").textContent = data.due_words;
  document.getElementById("nav-due-badge").textContent = data.due_words;
  document.getElementById("stat-today").textContent = data.today_count;
  document.getElementById("stat-goal").textContent = data.daily_goal;
  document.getElementById("stat-mastered").textContent = data.mastered_words;
  document.getElementById("stat-total").textContent = data.total_words;
  document.getElementById("stat-streak").textContent = data.streak_days;
  document.getElementById("stat-accuracy").textContent = data.accuracy;

  const pct = Math.min(100, Math.round((data.today_count / data.daily_goal) * 100));
  document.getElementById("goal-progress").style.width = `${pct}%`;

  populateCategorySelects(
    data.categories,
    data.favorites_count ?? 0,
    data.mistakes_count ?? 0
  );

  const chart = document.getElementById("weekly-chart");
  const maxVal = Math.max(5, ...data.weekly_activity.map((d) => d.count));
  chart.innerHTML = data.weekly_activity
    .map((d) => {
      const h = Math.round((d.count / maxVal) * 125);
      return `
        <div class="chart-col">
          <div class="chart-val">${d.count}</div>
          <div class="chart-bar" style="height:${Math.max(6, h)}px"></div>
          <div class="chart-date">${d.date}</div>
        </div>
      `;
    })
    .join("");
}

// Flashcards
async function loadFlashcards() {
  const category = document.getElementById("fc-category").value;
  state.flashcards = await api().get_due_flashcards(category, 25);
  state.fcIndex = 0;
  renderFlashcard();
}

function updateFlashcardFavoriteButton(card) {
  const btn = document.getElementById("fc-fav-btn");
  if (!card) return;
  const fav = Boolean(card.is_favorite);
  btn.textContent = fav ? "⭐ 已收藏" : "☆ 收藏";
  btn.classList.toggle("fav-btn-active", fav);
}

function renderFlashcard() {
  const total = state.flashcards.length;
  const emptyEl = document.getElementById("fc-empty");
  const stageEl = document.getElementById("fc-stage");
  const progressEl = document.getElementById("fc-progress-text");
  const prevBtn = document.getElementById("fc-prev-btn");
  const favBtn = document.getElementById("fc-fav-btn");

  prevBtn.disabled = state.fcIndex <= 0;

  if (state.fcIndex >= total) {
    progressEl.textContent = "本轮待复习卡片已全部完成";
    favBtn.disabled = true;
    emptyEl.classList.remove("hidden");
    stageEl.classList.add("hidden");
    return;
  }

  favBtn.disabled = false;
  emptyEl.classList.add("hidden");
  stageEl.classList.remove("hidden");
  const card = state.flashcards[state.fcIndex];
  progressEl.textContent = `进度：${state.fcIndex + 1} / ${total} 张待复习`;
  updateFlashcardFavoriteButton(card);

  state.fcFlipped = false;
  document.getElementById("flashcard").classList.remove("flipped");
  document.getElementById("fc-flip-btn").classList.remove("hidden");
  document.getElementById("fc-ratings").classList.add("hidden");

  document.getElementById("fc-cat-tag").textContent = card.category;
  document.getElementById("fc-word").textContent = card.word;
  document.getElementById("fc-word-back").textContent = card.word;
  document.getElementById("fc-phonetic").textContent = card.phonetic || "";
  document.getElementById("fc-phonetic-back").textContent = card.phonetic || "";
  document.getElementById("fc-pos").textContent = card.part_of_speech || "vocab";
  document.getElementById("fc-meaning").textContent = card.meaning_zh;
  document.getElementById("fc-example-en").textContent = card.example_en || "暂无例句";
  document.getElementById("fc-example-zh").textContent = card.example_zh || "";
  document.getElementById("fc-notes-input").value = card.notes || "";

  const prev = card.interval_previews || {};
  document.getElementById("prev-again").textContent = prev.again || "10分钟后";
  document.getElementById("prev-hard").textContent = prev.hard || "1天";
  document.getElementById("prev-good").textContent = prev.good || "1天";
  document.getElementById("prev-easy").textContent = prev.easy || "4天";

  if (document.getElementById("fc-auto-play").checked) {
    speakText(card.word);
  }
}

function flipFlashcard() {
  if (state.fcIndex >= state.flashcards.length) return;
  state.fcFlipped = !state.fcFlipped;
  document.getElementById("flashcard").classList.toggle("flipped", state.fcFlipped);
  document.getElementById("fc-flip-btn").classList.toggle("hidden", state.fcFlipped);
  document.getElementById("fc-ratings").classList.toggle("hidden", !state.fcFlipped);
}

async function rateFlashcard(rating) {
  const card = state.flashcards[state.fcIndex];
  if (!card) return;
  const res = await api().submit_flashcard_review(card.id, rating);
  if (rating === "again") {
    state.flashcards.push(card);
    showToast("已加入本轮末尾再次巩固");
  } else {
    showToast(`下次复习：${res.interval_label}`);
  }
  state.fcIndex += 1;
  renderFlashcard();
  const dash = await api().get_dashboard();
  document.getElementById("nav-due-badge").textContent = dash.due_words;
}

// Quiz & Listening & Cloze
const QUIZ_MODE_INFO = {
  choice: { title: "选择题测验", desc: "根据英文单词选出正确的中文释义，检验词汇反应速度。" },
  spelling: { title: "拼写填空", desc: "根据中文释义与发音提示，拼写出完整的英文单词。" },
  listening: { title: "听力练习", desc: "纯听英语发音并选出正确的词义，强化语音识别能力。" },
  cloze: { title: "语境例句填空", desc: "结合真实英文例句上下文，选出最恰当的填入单词。" },
};

function setQuizMode(mode) {
  stopAllSpeech();
  state.quizMode = mode;
  document.querySelectorAll(".mode-tab").forEach((b) => b.classList.toggle("active", b.dataset.mode === mode));
  document.getElementById("quiz-mode-title").textContent = QUIZ_MODE_INFO[mode].title;
  document.getElementById("quiz-mode-desc").textContent = QUIZ_MODE_INFO[mode].desc;
  document.getElementById("quiz-start-screen").classList.remove("hidden");
  document.getElementById("quiz-active-screen").classList.add("hidden");
  document.getElementById("quiz-result-screen").classList.add("hidden");
}

function startQuickQuiz(mode) {
  navigateTo("quiz");
  setQuizMode(mode);
  startQuiz();
}

async function startQuiz() {
  const category = document.getElementById("quiz-category").value;
  const count = parseInt(document.getElementById("quiz-count").value, 10);
  const questions = await api().get_quiz_questions(state.quizMode, category, count);
  if (!questions.length) {
    showToast("词库词汇不足 4 个，请先添加词汇");
    return;
  }
  state.quizQuestions = questions;
  state.quizIndex = 0;
  state.quizScore = 0;
  state.quizOutcomes = [];

  document.getElementById("quiz-start-screen").classList.add("hidden");
  document.getElementById("quiz-result-screen").classList.add("hidden");
  document.getElementById("quiz-active-screen").classList.remove("hidden");
  renderQuizQuestion();
}

function renderQuizQuestion() {
  const q = state.quizQuestions[state.quizIndex];
  state.quizAnswered = false;
  document.getElementById("quiz-progress").textContent = `第 ${state.quizIndex + 1} / ${state.quizQuestions.length} 题`;
  document.getElementById("quiz-score-live").textContent = `得分: ${state.quizScore}`;
  document.getElementById("quiz-feedback").classList.add("hidden");
  document.getElementById("quiz-next-btn").classList.add("hidden");

  const hintEl = document.getElementById("quiz-hint-text");
  hintEl.classList.add("hidden");
  hintEl.textContent = "";

  const mainEl = document.getElementById("quiz-prompt-main");
  const subEl = document.getElementById("quiz-prompt-sub");
  const optsEl = document.getElementById("quiz-options");
  const spellEl = document.getElementById("quiz-spelling-box");

  if (state.quizMode === "choice") {
    mainEl.textContent = q.word;
    subEl.textContent = `${q.phonetic || ""} ${q.part_of_speech || ""}`;
    optsEl.classList.remove("hidden");
    spellEl.classList.add("hidden");
    renderQuizOptions(q, "meaning");
  } else if (state.quizMode === "cloze") {
    mainEl.textContent = q.cloze_en;
    subEl.textContent = q.example_zh || `词义提示：${q.meaning_zh}`;
    optsEl.classList.remove("hidden");
    spellEl.classList.add("hidden");
    renderQuizOptions(q, "word");
  } else if (state.quizMode === "listening") {
    mainEl.textContent = "🎧 请点击播放按钮听音辨词";
    subEl.textContent = q.part_of_speech ? `词性提示：${q.part_of_speech}` : "选出你听到的单词释义";
    optsEl.classList.remove("hidden");
    spellEl.classList.add("hidden");
    renderQuizOptions(q, "meaning");
    speakText(q.word);
  } else {
    mainEl.textContent = q.meaning_zh;
    subEl.textContent = `${q.phonetic || ""} ${q.part_of_speech || ""}`;
    optsEl.classList.add("hidden");
    spellEl.classList.remove("hidden");
    const input = document.getElementById("quiz-spelling-input");
    input.value = "";
    input.disabled = false;
    input.focus();
    speakText(q.word);
  }
}

function renderQuizOptions(q, displayField = "meaning") {
  const optsEl = document.getElementById("quiz-options");
  optsEl.innerHTML = q.options
    .map((opt) => {
      const text = displayField === "word" ? opt.word : opt.meaning_zh;
      return `<button class="quiz-opt" data-opt-id="${opt.id}">${escapeHtml(text)}</button>`;
    })
    .join("");
  optsEl.querySelectorAll(".quiz-opt").forEach((btn) => {
    btn.addEventListener("click", () => handleChoiceAnswer(parseInt(btn.dataset.optId, 10), btn));
  });
}

function handleChoiceAnswer(selectedId, btnEl) {
  if (state.quizAnswered) return;
  state.quizAnswered = true;
  const q = state.quizQuestions[state.quizIndex];
  const isCorrect = selectedId === q.id;
  if (isCorrect) state.quizScore += 1;
  state.quizOutcomes.push({
    word_id: q.id,
    word: q.word,
    meaning_zh: q.meaning_zh,
    is_favorite: q.is_favorite || 0,
    correct: isCorrect,
  });

  document.querySelectorAll(".quiz-opt").forEach((b) => {
    b.disabled = true;
    const oid = parseInt(b.dataset.optId, 10);
    if (oid === q.id) b.classList.add("correct");
    else if (b === btnEl && !isCorrect) b.classList.add("wrong");
  });

  showQuizFeedback(isCorrect, q);
}

function handleSpellingSubmit() {
  if (state.quizAnswered) return;
  const input = document.getElementById("quiz-spelling-input");
  const userText = input.value.trim().toLowerCase();
  if (!userText) return;

  state.quizAnswered = true;
  input.disabled = true;
  const q = state.quizQuestions[state.quizIndex];
  const isCorrect = userText === q.word.trim().toLowerCase();
  if (isCorrect) state.quizScore += 1;
  state.quizOutcomes.push({
    word_id: q.id,
    word: q.word,
    meaning_zh: q.meaning_zh,
    is_favorite: q.is_favorite || 0,
    correct: isCorrect,
  });
  showQuizFeedback(isCorrect, q);
}

function showSpellingHint() {
  const q = state.quizQuestions[state.quizIndex];
  if (!q) return;
  const w = q.word.trim();
  const masked =
    w.length <= 2
      ? w[0] + "_".repeat(Math.max(0, w.length - 1))
      : `${w[0]} ${"_ ".repeat(w.length - 2)}${w[w.length - 1]}`;
  const hintEl = document.getElementById("quiz-hint-text");
  hintEl.textContent = `提示：${masked} (${w.length} 个字母)`;
  hintEl.classList.remove("hidden");
}

function showQuizFeedback(isCorrect, q) {
  const fb = document.getElementById("quiz-feedback");
  fb.className = `quiz-feedback ${isCorrect ? "ok" : "err"}`;
  fb.innerHTML = isCorrect
    ? `✅ 回答正确！<strong>${escapeHtml(q.word)}</strong> — ${escapeHtml(q.meaning_zh)}`
    : `❌ 正确答案是 <strong>${escapeHtml(q.word)}</strong>（${escapeHtml(q.meaning_zh)}）`;
  fb.classList.remove("hidden");
  document.getElementById("quiz-score-live").textContent = `得分: ${state.quizScore}`;
  document.getElementById("quiz-next-btn").classList.remove("hidden");
}

async function nextQuizQuestion() {
  state.quizIndex += 1;
  if (state.quizIndex < state.quizQuestions.length) {
    renderQuizQuestion();
    return;
  }

  const total = state.quizQuestions.length;
  const actType = state.quizMode === "listening" ? "listening" : "quiz";
  await api().submit_quiz_result(actType, state.quizScore, total, state.quizOutcomes);

  document.getElementById("quiz-active-screen").classList.add("hidden");
  document.getElementById("quiz-result-screen").classList.remove("hidden");
  const pct = Math.round((state.quizScore / total) * 100);
  document.getElementById("quiz-final-score").textContent = `本组得分：${state.quizScore} / ${total}`;
  document.getElementById("quiz-final-msg").textContent = `正确率 ${pct}%${pct >= 80 ? "，表现非常出色！" : "，错题已记录到「易错词本」，多复习巩固吧！"}`;
  renderQuizReviewList();
}

function renderQuizReviewList() {
  const container = document.getElementById("quiz-review-list");
  container.innerHTML = state.quizOutcomes
    .map(
      (o, idx) => `
      <div class="review-row">
        <span><strong>${escapeHtml(o.word)}</strong> · ${escapeHtml(o.meaning_zh)}</span>
        <div style="display:flex;align-items:center;gap:8px;">
          <button class="btn-icon sm ${o.is_favorite ? "fav-btn-active" : ""}" data-review-fav="${idx}" title="收藏单词">
            ${o.is_favorite ? "⭐" : "☆"}
          </button>
          <span>${o.correct ? "✅" : "❌"}</span>
        </div>
      </div>`
    )
    .join("");

  container.querySelectorAll("[data-review-fav]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const idx = parseInt(btn.dataset.reviewFav, 10);
      const item = state.quizOutcomes[idx];
      const res = await api().toggle_favorite(item.word_id);
      item.is_favorite = res.is_favorite;
      renderQuizReviewList();
      showToast(res.is_favorite ? "已加入我的收藏" : "已取消收藏");
    });
  });
}

// Dialogues
async function loadDialogues() {
  if (!state.dialogues.length) {
    state.dialogues = await api().get_dialogues();
  }
  const listEl = document.getElementById("dialogue-list");
  listEl.innerHTML = state.dialogues
    .map(
      (d, idx) => `
      <button class="list-item ${idx === state.activeDialogueIndex ? "active" : ""}" data-idx="${idx}">
        <div class="list-item-title">${escapeHtml(d.title)}</div>
        <div class="list-item-meta">${escapeHtml(d.scene)} · ${escapeHtml(d.level)}</div>
      </button>`
    )
    .join("");
  listEl.querySelectorAll(".list-item").forEach((btn) => {
    btn.addEventListener("click", () => {
      stopAllSpeech();
      state.activeDialogueIndex = parseInt(btn.dataset.idx, 10);
      loadDialogues();
    });
  });
  renderDialogueDetail();
}

function renderDialogueDetail() {
  const dlg = state.dialogues[state.activeDialogueIndex];
  if (!dlg) return;
  const showZh = document.getElementById("dlg-show-zh").checked;
  document.getElementById("dlg-title").textContent = dlg.title;
  document.getElementById("dlg-level").textContent = dlg.level;
  document.getElementById("dlg-scene").textContent = dlg.scene;

  const linesEl = document.getElementById("dlg-lines");
  linesEl.innerHTML = dlg.lines
    .map(
      (line, idx) => `
      <div class="dlg-line" id="dlg-line-${idx}">
        <div>
          <div class="dlg-speaker">${escapeHtml(line.speaker)}</div>
          <div class="dlg-en">${escapeHtml(line.en)}</div>
          <div class="dlg-zh ${showZh ? "" : "hidden"}">${escapeHtml(line.zh)}</div>
        </div>
        <button class="btn-icon sm" data-speak-line="${idx}" title="朗读此句">🔊</button>
      </div>`
    )
    .join("");

  linesEl.querySelectorAll("[data-speak-line]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const i = parseInt(btn.dataset.speakLine, 10);
      speakText(dlg.lines[i].en);
    });
  });

  document.getElementById("dlg-phrases").innerHTML = dlg.key_phrases
    .map(
      (p, idx) => `
      <div class="phrase-chip" data-phrase="${escapeHtml(p.en)}">
        <div>
          <div style="font-weight:600;font-size:13.5px;">🔊 ${escapeHtml(p.en)}</div>
          <div style="font-size:12px;color:var(--text-muted);margin-top:3px;">${escapeHtml(p.zh)}</div>
        </div>
        <button class="phrase-add-btn" data-add-phrase="${idx}" title="加入生词本">＋收</button>
      </div>`
    )
    .join("");

  document.querySelectorAll(".phrase-chip").forEach((chip) => {
    chip.addEventListener("click", (e) => {
      if (e.target.closest("[data-add-phrase]")) return;
      speakText(chip.dataset.phrase);
    });
  });

  document.querySelectorAll("[data-add-phrase]").forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      e.stopPropagation();
      const p = dlg.key_phrases[parseInt(btn.dataset.addPhrase, 10)];
      try {
        await api().add_word({
          word: p.en,
          meaning_zh: p.zh,
          category: dlg.scene || "情景表达",
          example_en: "",
          example_zh: "",
        });
        showToast(`已收藏表达「${p.en}」到词库`);
        loadDashboard();
      } catch (err) {
        showToast(`该表达已在词库中或添加失败`);
      }
    });
  });
}

function cancellableSleep(ms) {
  return new Promise((resolve) => {
    const timer = setTimeout(() => {
      state.roleplayCancel = null;
      resolve(true);
    }, ms);
    state.roleplayCancel = () => {
      clearTimeout(timer);
      state.roleplayCancel = null;
      resolve(false);
    };
  });
}

async function runDialogueLoop(startIndex = 0) {
  const dlg = state.dialogues[state.activeDialogueIndex];
  if (!dlg) return;

  state.dialoguePlayState = "playing";
  state.dialogueLineIndex = startIndex;
  updateAudioControllerUI();

  while (state.dialogueLineIndex < dlg.lines.length) {
    if (state.dialoguePlayState !== "playing") break;
    const i = state.dialogueLineIndex;
    const line = dlg.lines[i];
    const roleplay = document.getElementById("dlg-roleplay-toggle").checked;

    document.querySelectorAll(".dlg-line").forEach((el, idx) => {
      el.classList.toggle("speaking", idx === i);
    });
    const activeLineEl = document.getElementById(`dlg-line-${i}`);
    activeLineEl?.scrollIntoView({ block: "nearest", behavior: "smooth" });

    let completed = false;
    if (roleplay && line.speaker.toLowerCase() === "you") {
      state.activeAudioLabel = `🎭 轮到你跟读 (${i + 1}/${dlg.lines.length})`;
      updateAudioControllerUI();
      completed = await cancellableSleep(2500);
    } else {
      completed = await speakSingleInternal(
        line.en,
        null,
        `🔊 对话 (${i + 1}/${dlg.lines.length})`
      );
    }

    if (!completed || state.dialoguePlayState !== "playing") {
      break;
    }
    state.dialogueLineIndex += 1;
  }

  if (state.dialoguePlayState === "playing") {
    state.dialoguePlayState = "idle";
    state.dialogueLineIndex = 0;
    document.querySelectorAll(".dlg-line").forEach((el) => el.classList.remove("speaking"));
    updateAudioControllerUI();
  }
}

function handleDialoguePlayPause() {
  if (state.dialoguePlayState === "idle") {
    runDialogueLoop(0);
  } else {
    togglePauseSpeech();
  }
}

// Grammar & Mini-Check
function buildGrammarMiniCheck(g) {
  for (const m of g.common_mistakes || []) {
    const match = m.match(/错误：(.+?)\s*→\s*正确：(.+?)(?:（|$)/);
    if (match) {
      return {
        prompt: "请选择符合本节语法规则的正确表达：",
        options: [
          { text: match[2].trim(), correct: true },
          { text: match[1].trim(), correct: false },
        ],
        explanation: m,
      };
    }
  }
  const ex = g.examples?.[0]?.en || "If I were you, I would take that opportunity.";
  const wrong = ex.includes("If I were")
    ? ex.replace("If I were", "If I was")
    : `${ex} (incorrect tense)`;
  return {
    prompt: "请选择更符合标准书面/口语规范的句子：",
    options: [
      { text: ex, correct: true },
      { text: wrong, correct: false },
    ],
    explanation: (g.common_mistakes && g.common_mistakes[0]) || g.summary,
  };
}

function renderGrammarMiniCheck(g) {
  const check = buildGrammarMiniCheck(g);
  const shuffled = [...check.options].sort(() => Math.random() - 0.5);
  document.getElementById("gram-check-question").textContent = check.prompt;
  const optsEl = document.getElementById("gram-check-options");
  const fbEl = document.getElementById("gram-check-feedback");
  fbEl.classList.add("hidden");

  optsEl.innerHTML = shuffled
    .map(
      (opt, idx) =>
        `<button class="gram-check-opt" data-gopt="${idx}">${escapeHtml(opt.text)}</button>`
    )
    .join("");

  optsEl.querySelectorAll(".gram-check-opt").forEach((btn) => {
    btn.addEventListener("click", () => {
      const picked = shuffled[parseInt(btn.dataset.gopt, 10)];
      optsEl.querySelectorAll(".gram-check-opt").forEach((b, i) => {
        b.disabled = true;
        if (shuffled[i].correct) b.classList.add("correct");
        else if (b === btn && !picked.correct) b.classList.add("wrong");
      });
      fbEl.className = `quiz-feedback ${picked.correct ? "ok" : "err"}`;
      fbEl.textContent = (picked.correct ? "✅ 正确！" : "❌ 再看看规则：") + check.explanation;
      fbEl.classList.remove("hidden");
    });
  });
}

async function loadGrammar() {
  if (!state.grammarNotes.length) {
    state.grammarNotes = await api().get_grammar_notes();
  }
  const listEl = document.getElementById("grammar-list");
  listEl.innerHTML = state.grammarNotes
    .map(
      (g, idx) => `
      <button class="list-item ${idx === state.activeGrammarIndex ? "active" : ""}" data-idx="${idx}">
        <div class="list-item-title">${escapeHtml(g.title)}</div>
        <div class="list-item-meta">${escapeHtml(g.category)} · ${escapeHtml(g.level)}</div>
      </button>`
    )
    .join("");
  listEl.querySelectorAll(".list-item").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.activeGrammarIndex = parseInt(btn.dataset.idx, 10);
      loadGrammar();
    });
  });

  const g = state.grammarNotes[state.activeGrammarIndex];
  if (!g) return;
  document.getElementById("gram-level").textContent = g.level;
  document.getElementById("gram-category").textContent = g.category;
  document.getElementById("gram-title").textContent = g.title;
  document.getElementById("gram-summary").textContent = g.summary;
  document.getElementById("gram-explanation").textContent = g.explanation;

  const exEl = document.getElementById("gram-examples");
  exEl.innerHTML = g.examples
    .map(
      (ex, i) => `
      <div class="gram-ex-row">
        <div>
          <div style="font-weight:600;font-size:14.5px;">${escapeHtml(ex.en)}</div>
          <div style="font-size:13px;color:var(--text-muted);margin-top:2px;">${escapeHtml(ex.zh)}</div>
        </div>
        <button class="btn-icon sm" data-gram-ex="${i}">🔊</button>
      </div>`
    )
    .join("");
  exEl.querySelectorAll("[data-gram-ex]").forEach((btn) => {
    btn.addEventListener("click", () => speakText(g.examples[parseInt(btn.dataset.gramEx, 10)].en));
  });

  document.getElementById("gram-mistakes").innerHTML = g.common_mistakes
    .map((m) => `<li>${escapeHtml(m)}</li>`)
    .join("");

  renderGrammarMiniCheck(g);
}

// Wordbook
let wordbookCache = [];

async function loadWordbook() {
  const search = document.getElementById("wb-search").value;
  const category = document.getElementById("wb-category").value;
  const words = await api().get_words(search, category);
  wordbookCache = words;
  document.getElementById("wb-count").textContent = `共 ${words.length} 个词汇`;

  const tbody = document.getElementById("wb-tbody");
  tbody.innerHTML = words
    .map((w) => {
      const status =
        w.repetitions >= 2 && w.interval_days >= 6
          ? "已掌握"
          : w.repetitions > 0
          ? `复习中 (${w.interval_days}天)`
          : "新词";
      const favClass = w.is_favorite ? "fav-btn-active" : "";
      const noteLine = w.notes ? `<div class="word-cell-sub">📝 ${escapeHtml(w.notes)}</div>` : "";
      return `
        <tr>
          <td>
            <div class="word-cell-main">${escapeHtml(w.word)}</div>
            <div class="word-cell-sub">${escapeHtml(w.phonetic)}</div>
          </td>
          <td>
            <div>${escapeHtml(w.part_of_speech)} ${escapeHtml(w.meaning_zh)}</div>
            <div class="word-cell-sub">${escapeHtml(w.example_en)}</div>
            ${noteLine}
          </td>
          <td><span class="badge badge-outline">${escapeHtml(w.category)}</span></td>
          <td>${status}</td>
          <td style="white-space:nowrap;">
            <button class="btn-icon sm" onclick="speakText(${JSON.stringify(w.word)})" title="发音">🔊</button>
            <button class="btn-icon sm ${favClass}" onclick="toggleWordFavorite(${w.id})" title="收藏">${w.is_favorite ? "⭐" : "☆"}</button>
            <button class="btn-icon sm" onclick="openEditWordModal(${w.id})" title="编辑">✏️</button>
            <button class="btn-icon sm" onclick="resetWord(${w.id})" title="重置进度">↺</button>
            <button class="btn-icon sm" onclick="deleteWord(${w.id})" title="删除">🗑️</button>
          </td>
        </tr>`;
    })
    .join("");
}

async function toggleWordFavorite(id) {
  const res = await api().toggle_favorite(id);
  showToast(res.is_favorite ? "已加入我的收藏" : "已取消收藏");
  await loadWordbook();
  await loadDashboard();
}

function openEditWordModal(id) {
  const w = wordbookCache.find((item) => item.id === id);
  if (!w) return;
  const form = document.getElementById("edit-word-form");
  form.elements.id.value = w.id;
  form.elements.word.value = w.word || "";
  form.elements.phonetic.value = w.phonetic || "";
  form.elements.part_of_speech.value = w.part_of_speech || "";
  form.elements.category.value = w.category || "自定义";
  form.elements.meaning_zh.value = w.meaning_zh || "";
  form.elements.example_en.value = w.example_en || "";
  form.elements.example_zh.value = w.example_zh || "";
  form.elements.notes.value = w.notes || "";
  openModal("edit-word-modal");
}

async function resetWord(id) {
  await api().reset_word_progress(id);
  showToast("已重置该单词复习进度");
  loadWordbook();
}

async function deleteWord(id) {
  await api().delete_word(id);
  showToast("单词已删除");
  loadWordbook();
  loadDashboard();
}

function openModal(id) {
  document.getElementById(id).classList.remove("hidden");
}

function closeModal(id) {
  document.getElementById(id).classList.add("hidden");
}

// Event Bindings
function bindEvents() {
  document.querySelectorAll(".nav-item").forEach((btn) => {
    btn.addEventListener("click", () => navigateTo(btn.dataset.view));
  });

  // Global audio controller
  document.getElementById("global-pause-btn").addEventListener("click", togglePauseSpeech);
  document.getElementById("global-stop-btn").addEventListener("click", stopAllSpeech);
  document.getElementById("quiz-stop-btn").addEventListener("click", stopAllSpeech);

  document.getElementById("theme-toggle").addEventListener("click", async () => {
    const next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
    applyTheme(next);
    state.settings = await api().update_settings({ theme: next });
  });

  document.getElementById("tts-accent").addEventListener("change", async (e) => {
    state.settings = await api().update_settings({ tts_accent: e.target.value });
  });

  document.getElementById("tts-rate").addEventListener("input", (e) => {
    document.getElementById("tts-rate-val").textContent = `${e.target.value}x`;
  });
  document.getElementById("tts-rate").addEventListener("change", async (e) => {
    state.settings = await api().update_settings({ tts_rate: e.target.value });
  });

  document.getElementById("save-goal-btn").addEventListener("click", async () => {
    const val = Math.max(5, Math.min(200, parseInt(document.getElementById("daily-goal-input").value || "15", 10)));
    await api().update_settings({ daily_goal: String(val) });
    showToast("每日目标已更新");
    loadDashboard();
  });

  // Flashcards
  document.getElementById("fc-auto-play").addEventListener("change", async (e) => {
    state.settings = await api().update_settings({ auto_play: e.target.checked ? "1" : "0" });
  });
  document.getElementById("fc-category").addEventListener("change", loadFlashcards);
  document.getElementById("fc-reload-btn").addEventListener("click", loadFlashcards);
  document.getElementById("fc-prev-btn").addEventListener("click", () => {
    if (state.fcIndex > 0) {
      state.fcIndex -= 1;
      renderFlashcard();
    }
  });
  document.getElementById("fc-fav-btn").addEventListener("click", async () => {
    const card = state.flashcards[state.fcIndex];
    if (!card) return;
    const res = await api().toggle_favorite(card.id);
    card.is_favorite = res.is_favorite;
    updateFlashcardFavoriteButton(card);
    showToast(res.is_favorite ? "已加入我的收藏" : "已取消收藏");
  });
  document.getElementById("fc-notes-save").addEventListener("click", async () => {
    const card = state.flashcards[state.fcIndex];
    if (!card) return;
    const notes = document.getElementById("fc-notes-input").value;
    const res = await api().update_word_notes(card.id, notes);
    card.notes = res.notes;
    showToast("助记笔记已保存");
  });
  document.getElementById("flashcard").addEventListener("click", (e) => {
    if (e.target.closest("button") || e.target.closest("input")) return;
    flipFlashcard();
  });
  document.getElementById("fc-flip-btn").addEventListener("click", flipFlashcard);
  document.getElementById("fc-speak-btn").addEventListener("click", () => {
    const c = state.flashcards[state.fcIndex];
    if (c) speakText(c.word);
  });
  document.getElementById("fc-speak-back-btn").addEventListener("click", () => {
    const c = state.flashcards[state.fcIndex];
    if (c) speakText(c.word);
  });
  document.getElementById("fc-speak-ex-btn").addEventListener("click", () => {
    const c = state.flashcards[state.fcIndex];
    if (c?.example_en) speakText(c.example_en);
  });
  document.querySelectorAll(".rate-btn").forEach((btn) => {
    btn.addEventListener("click", () => rateFlashcard(btn.dataset.rating));
  });

  // Quiz
  document.querySelectorAll(".mode-tab").forEach((btn) => {
    btn.addEventListener("click", () => setQuizMode(btn.dataset.mode));
  });
  document.getElementById("quiz-start-btn").addEventListener("click", startQuiz);
  document.getElementById("quiz-restart-btn").addEventListener("click", startQuiz);
  document.getElementById("quiz-next-btn").addEventListener("click", nextQuizQuestion);
  document.getElementById("quiz-hint-btn").addEventListener("click", showSpellingHint);
  document.getElementById("quiz-spelling-submit").addEventListener("click", handleSpellingSubmit);
  document.getElementById("quiz-spelling-input").addEventListener("keydown", (e) => {
    if (e.key === "Enter") handleSpellingSubmit();
  });
  document.getElementById("quiz-play-btn").addEventListener("click", () => {
    const q = state.quizQuestions[state.quizIndex];
    if (q) speakText(state.quizMode === "cloze" && q.example_en ? q.example_en : q.word);
  });
  document.getElementById("quiz-slow-btn").addEventListener("click", () => {
    const q = state.quizQuestions[state.quizIndex];
    if (q) speakText(state.quizMode === "cloze" && q.example_en ? q.example_en : q.word, 0.75);
  });

  // Dialogues
  document.getElementById("dlg-show-zh").addEventListener("change", renderDialogueDetail);
  document.getElementById("dlg-play-all-btn").addEventListener("click", handleDialoguePlayPause);
  document.getElementById("dlg-stop-btn").addEventListener("click", stopAllSpeech);

  // Wordbook
  document.getElementById("wb-search").addEventListener("input", loadWordbook);
  document.getElementById("wb-category").addEventListener("change", loadWordbook);
  document.getElementById("open-add-modal").addEventListener("click", () => openModal("add-word-modal"));
  document.getElementById("open-import-modal").addEventListener("click", () => openModal("import-modal"));
  document.getElementById("open-export-modal").addEventListener("click", async () => {
    const category = document.getElementById("wb-category").value;
    const txt = await api().export_words_text(category);
    document.getElementById("export-textarea").value = txt;
    openModal("export-modal");
  });
  document.getElementById("copy-export-btn").addEventListener("click", async () => {
    const ta = document.getElementById("export-textarea");
    try {
      await navigator.clipboard.writeText(ta.value);
    } catch {
      ta.select();
      document.execCommand("copy");
    }
    showToast("已复制到剪贴板");
  });

  document.getElementById("add-word-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const payload = Object.fromEntries(fd.entries());
    try {
      await api().add_word(payload);
      e.target.reset();
      closeModal("add-word-modal");
      showToast("单词添加成功");
      loadWordbook();
      loadDashboard();
    } catch (err) {
      showToast(`添加失败: ${err}`);
    }
  });

  document.getElementById("edit-word-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const payload = Object.fromEntries(fd.entries());
    const id = parseInt(payload.id, 10);
    delete payload.id;
    try {
      await api().update_word(id, payload);
      closeModal("edit-word-modal");
      showToast("单词修改已保存");
      loadWordbook();
      loadDashboard();
    } catch (err) {
      showToast(`保存失败: ${err}`);
    }
  });

  document.getElementById("import-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const res = await api().import_words_text(fd.get("raw_text") || "", fd.get("category") || "自定义");
    closeModal("import-modal");
    e.target.reset();
    showToast(`导入完成：新增 ${res.added} 个，跳过 ${res.skipped} 个`);
    loadWordbook();
    loadDashboard();
  });

  // Global keyboard shortcuts (Escape stops playback everywhere; flashcard shortcuts in flashcards view)
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      stopAllSpeech();
      return;
    }
    if (state.currentView !== "flashcards") return;
    if (["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName)) return;
    if (e.code === "Space") {
      e.preventDefault();
      flipFlashcard();
    } else if (e.key.toLowerCase() === "r") {
      const c = state.flashcards[state.fcIndex];
      if (c) speakText(c.word);
    } else if (state.fcFlipped && ["1", "2", "3", "4"].includes(e.key)) {
      const map = { "1": "again", "2": "hard", "3": "good", "4": "easy" };
      rateFlashcard(map[e.key]);
    }
  });
}

let appBooted = false;

function bootApp() {
  if (appBooted) return;
  appBooted = true;
  bindEvents();
  loadDashboard();
  updateAudioControllerUI();
}

window.addEventListener("pywebviewready", bootApp);
window.addEventListener("DOMContentLoaded", () => {
  if (window.pywebview?.api) {
    bootApp();
    return;
  }
  if (window.Capacitor || window.location.protocol !== "file:") {
    bootApp();
    return;
  }
  // In desktop pywebview, wait briefly for pywebviewready before falling back
  setTimeout(() => {
    if (!appBooted && window.localLingoApi) {
      bootApp();
    }
  }, 1200);
});
