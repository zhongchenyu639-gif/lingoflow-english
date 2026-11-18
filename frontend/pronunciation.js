/**
 * LingoFlow Duolingo-style Pronunciation Calibration & Grading Engine
 * Works 100% offline on Desktop (WebView2 / Windows) and Android (Capacitor WebView),
 * optionally fused with OS SpeechRecognition when available.
 */
(function (globalScope) {
  "use strict";

  const TARGET_SR = 16000;
  const FFT_SIZE = 512;
  const HOP_SIZE = 240; // 15 ms at 16 kHz
  const NUM_BANDS = 12;
  const CAL_STORAGE_KEY = "lingoflow_mic_cal_v1";

  const _refCache = new Map();
  let _melFilters = null;
  let _hannWin = null;

  function defaultCalibration() {
    return {
      noiseFloorRms: 0.008,
      speechThreshRms: 0.022,
      noiseDb: -42,
      envLabel: "未校准（将自动自适应底噪）",
      calibratedAt: null,
    };
  }

  function loadCalibration() {
    try {
      const raw = globalScope.localStorage?.getItem(CAL_STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (parsed && typeof parsed.noiseFloorRms === "number") {
          return { ...defaultCalibration(), ...parsed };
        }
      }
    } catch {}
    return defaultCalibration();
  }

  function saveCalibration(cal) {
    try {
      globalScope.localStorage?.setItem(CAL_STORAGE_KEY, JSON.stringify(cal));
    } catch {}
  }

  function hzToMel(hz) {
    return 2595 * Math.log10(1 + hz / 700);
  }

  function melToHz(mel) {
    return 700 * (Math.pow(10, mel / 2595) - 1);
  }

  function getHannWindow() {
    if (_hannWin) return _hannWin;
    _hannWin = new Float32Array(FFT_SIZE);
    for (let i = 0; i < FFT_SIZE; i++) {
      _hannWin[i] = 0.5 * (1 - Math.cos((2 * Math.PI * i) / (FFT_SIZE - 1)));
    }
    return _hannWin;
  }

  function getMelFilterbank() {
    if (_melFilters) return _melFilters;
    const bins = FFT_SIZE / 2 + 1;
    const melLow = hzToMel(200);
    const melHigh = hzToMel(6800);
    const points = new Float32Array(NUM_BANDS + 2);
    for (let i = 0; i < NUM_BANDS + 2; i++) {
      const mel = melLow + ((melHigh - melLow) * i) / (NUM_BANDS + 1);
      points[i] = Math.floor(((FFT_SIZE + 1) * melToHz(mel)) / TARGET_SR);
    }
    _melFilters = [];
    for (let b = 0; b < NUM_BANDS; b++) {
      const f = new Float32Array(bins);
      const left = points[b];
      const center = points[b + 1];
      const right = points[b + 2];
      for (let k = Math.max(1, left); k < Math.min(bins, center); k++) {
        f[k] = (k - left) / Math.max(1, center - left);
      }
      for (let k = Math.max(1, center); k < Math.min(bins, right); k++) {
        f[k] = (right - k) / Math.max(1, right - center);
      }
      _melFilters.push(f);
    }
    return _melFilters;
  }

  function fftPowerSpectrum(frame) {
    const n = FFT_SIZE;
    const re = new Float32Array(n);
    const im = new Float32Array(n);
    for (let i = 0; i < n; i++) re[i] = frame[i];

    // Bit-reversal permutation
    for (let i = 1, j = 0; i < n; i++) {
      let bit = n >> 1;
      for (; j & bit; bit >>= 1) j ^= bit;
      j ^= bit;
      if (i < j) {
        const tmp = re[i];
        re[i] = re[j];
        re[j] = tmp;
      }
    }

    // Cooley-Tukey iterative radix-2 FFT
    for (let len = 2; len <= n; len <<= 1) {
      const ang = (-2 * Math.PI) / len;
      const wlenRe = Math.cos(ang);
      const wlenIm = Math.sin(ang);
      for (let i = 0; i < n; i += len) {
        let wRe = 1;
        let wIm = 0;
        const half = len >> 1;
        for (let j = 0; j < half; j++) {
          const uRe = re[i + j];
          const uIm = im[i + j];
          const vRe = re[i + j + half] * wRe - im[i + j + half] * wIm;
          const vIm = re[i + j + half] * wIm + im[i + j + half] * wRe;
          re[i + j] = uRe + vRe;
          im[i + j] = uIm + vIm;
          re[i + j + half] = uRe - vRe;
          im[i + j + half] = uIm - vIm;
          const nextRe = wRe * wlenRe - wIm * wlenIm;
          wIm = wRe * wlenIm + wIm * wlenRe;
          wRe = nextRe;
        }
      }
    }

    const bins = n / 2 + 1;
    const pow = new Float32Array(bins);
    for (let k = 0; k < bins; k++) {
      pow[k] = re[k] * re[k] + im[k] * im[k];
    }
    return pow;
  }

  function resampleMono(samples, fromSr, toSr = TARGET_SR) {
    if (!samples || !samples.length) return new Float32Array(0);
    if (fromSr === toSr) return Float32Array.from(samples);
    const ratio = fromSr / toSr;
    const outLen = Math.max(1, Math.round(samples.length / ratio));
    const out = new Float32Array(outLen);
    for (let i = 0; i < outLen; i++) {
      const pos = i * ratio;
      const idx = Math.floor(pos);
      const frac = pos - idx;
      const s0 = samples[Math.min(idx, samples.length - 1)];
      const s1 = samples[Math.min(idx + 1, samples.length - 1)];
      out[i] = s0 + (s1 - s0) * frac;
    }
    return out;
  }

  function computeSignalStats(samples) {
    let sumSq = 0;
    let peak = 0;
    let clipped = 0;
    for (let i = 0; i < samples.length; i++) {
      const v = Math.abs(samples[i]);
      sumSq += v * v;
      if (v > peak) peak = v;
      if (v >= 0.98) clipped++;
    }
    const rms = samples.length ? Math.sqrt(sumSq / samples.length) : 0;
    return {
      rms,
      peak,
      clipRatio: samples.length ? clipped / samples.length : 0,
    };
  }

  function extractAcousticFeatures(samples, floorThresh = 0.012) {
    const win = getHannWindow();
    const filters = getMelFilterbank();
    const numFrames = Math.max(0, Math.floor((samples.length - FFT_SIZE) / HOP_SIZE) + 1);
    if (numFrames < 3) {
      return { frames: [], rmsEnv: [], activeSec: 0, syllables: 0, highBandRatio: 0, snrDb: 0 };
    }

    const rawBands = [];
    const frameRms = new Float32Array(numFrames);
    let maxRms = 0;

    for (let t = 0; t < numFrames; t++) {
      const start = t * HOP_SIZE;
      const windowed = new Float32Array(FFT_SIZE);
      let sq = 0;
      for (let i = 0; i < FFT_SIZE; i++) {
        const s = samples[start + i];
        sq += s * s;
        windowed[i] = s * win[i];
      }
      const r = Math.sqrt(sq / FFT_SIZE);
      frameRms[t] = r;
      if (r > maxRms) maxRms = r;

      const pow = fftPowerSpectrum(windowed);
      const vec = new Float32Array(NUM_BANDS);
      for (let b = 0; b < NUM_BANDS; b++) {
        const filt = filters[b];
        let e = 1e-8;
        for (let k = 1; k < filt.length; k++) {
          if (filt[k] > 0) e += pow[k] * filt[k];
        }
        vec[b] = Math.log(e);
      }
      rawBands.push(vec);
    }

    // Active speech trimming calibrated by noise floor + utterance peak
    const sortedRms = Array.from(frameRms).sort((a, b) => a - b);
    const estNoise = Math.max(1e-5, sortedRms[Math.floor(sortedRms.length * 0.15)] || floorThresh * 0.5);
    const gate = Math.max(floorThresh, estNoise * 2.2, maxRms * 0.12);

    let firstActive = -1;
    let lastActive = -1;
    const activeIndices = [];
    let speechSqSum = 0;
    for (let t = 0; t < numFrames; t++) {
      if (frameRms[t] >= gate) {
        if (firstActive < 0) firstActive = t;
        lastActive = t;
        activeIndices.push(t);
        speechSqSum += frameRms[t] * frameRms[t];
      }
    }

    if (firstActive < 0 || activeIndices.length < 4) {
      return { frames: [], rmsEnv: [], activeSec: 0, syllables: 0, highBandRatio: 0, snrDb: 0 };
    }

    // Keep padding of 1 frame around boundaries
    firstActive = Math.max(0, firstActive - 1);
    lastActive = Math.min(numFrames - 1, lastActive + 1);

    const trimmedBands = rawBands.slice(firstActive, lastActive + 1);
    const trimmedRms = Array.from(frameRms.slice(firstActive, lastActive + 1));
    const M = trimmedBands.length;

    // CMVN across active utterance so speaker pitch & mic EQ don't dominate
    const mean = new Float32Array(NUM_BANDS);
    const std = new Float32Array(NUM_BANDS);
    for (let t = 0; t < M; t++) {
      for (let b = 0; b < NUM_BANDS; b++) mean[b] += trimmedBands[t][b];
    }
    for (let b = 0; b < NUM_BANDS; b++) mean[b] /= M;
    for (let t = 0; t < M; t++) {
      for (let b = 0; b < NUM_BANDS; b++) {
        const d = trimmedBands[t][b] - mean[b];
        std[b] += d * d;
      }
    }
    for (let b = 0; b < NUM_BANDS; b++) {
      std[b] = Math.max(0.25, Math.sqrt(std[b] / M));
    }

    // Add 1st-order delta (dynamic consonant/vowel movement) -> 24-dim normalized vector per frame
    const normBands = trimmedBands.map((vec) => {
      const out = new Float32Array(NUM_BANDS);
      for (let b = 0; b < NUM_BANDS; b++) out[b] = (vec[b] - mean[b]) / std[b];
      return out;
    });

    const frames = [];
    for (let t = 0; t < M; t++) {
      const feat = new Float32Array(NUM_BANDS * 2);
      const prev = normBands[Math.max(0, t - 2)];
      const next = normBands[Math.min(M - 1, t + 2)];
      for (let b = 0; b < NUM_BANDS; b++) {
        feat[b] = normBands[t][b];
        feat[NUM_BANDS + b] = (next[b] - prev[b]) * 0.65;
      }
      frames.push(feat);
    }

    // Syllable nucleus peak counter from smoothed active RMS
    const smoothRms = trimmedRms.map((_, idx) => {
      const a = trimmedRms[Math.max(0, idx - 1)];
      const c = trimmedRms[idx];
      const d = trimmedRms[Math.min(M - 1, idx + 1)];
      return (a + 2 * c + d) / 4;
    });
    const activePeak = Math.max(...smoothRms, 1e-5);
    const sylThresh = activePeak * 0.28;
    let syllables = 0;
    let lastPeakIdx = -10;
    for (let t = 1; t < M - 1; t++) {
      if (
        smoothRms[t] >= sylThresh &&
        smoothRms[t] >= smoothRms[t - 1] &&
        smoothRms[t] >= smoothRms[t + 1] &&
        t - lastPeakIdx >= 4
      ) {
        syllables++;
        lastPeakIdx = t;
      }
    }
    syllables = Math.max(1, syllables);

    // High-band articulation check (consonant presence: bands 7..11 vs bands 0..3)
    let lowE = 0;
    let highE = 0;
    for (const t of activeIndices) {
      for (let b = 0; b < 4; b++) lowE += Math.exp(rawBands[t][b]);
      for (let b = 7; b < NUM_BANDS; b++) highE += Math.exp(rawBands[t][b]);
    }
    const highBandRatio = highE / Math.max(1e-9, lowE + highE);

    const speechRms = Math.sqrt(speechSqSum / activeIndices.length);
    const snrDb = 20 * Math.log10(speechRms / Math.max(1e-5, estNoise));
    const activeSec = (activeIndices.length * HOP_SIZE) / TARGET_SR;

    return { frames, rmsEnv: smoothRms, activeSec, syllables, highBandRatio, snrDb };
  }

  function cosineSim(a, b) {
    let dot = 0;
    let na = 0;
    let nb = 0;
    for (let i = 0; i < a.length; i++) {
      dot += a[i] * b[i];
      na += a[i] * a[i];
      nb += b[i] * b[i];
    }
    if (na <= 1e-9 || nb <= 1e-9) return 0;
    return dot / Math.sqrt(na * nb);
  }

  /**
   * Banded DTW aligning user frames (N) against reference frames (M).
   * Returns mean path cosine similarity and per-ref-frame best similarity.
   */
  function alignAcousticDTW(userFrames, refFrames) {
    const N = userFrames.length;
    const M = refFrames.length;
    if (!N || !M) return { avgSim: 0, refSims: [], pathCoverage: 0 };

    const INF = 1e9;
    const band = Math.max(12, Math.round(Math.max(N, M) * 0.42));
    const dp = new Float32Array((N + 1) * (M + 1)).fill(INF);
    const back = new Uint8Array((N + 1) * (M + 1)); // 1=diag, 2=up(i-1), 3=left(j-1)
    dp[0] = 0;

    for (let i = 1; i <= N; i++) {
      const expectedJ = Math.round((i * M) / N);
      const jMin = Math.max(1, expectedJ - band);
      const jMax = Math.min(M, expectedJ + band);
      const u = userFrames[i - 1];
      for (let j = jMin; j <= jMax; j++) {
        const sim = cosineSim(u, refFrames[j - 1]);
        const cost = 1 - Math.max(-0.5, Math.min(1, sim));
        const idx = i * (M + 1) + j;
        const cDiag = dp[(i - 1) * (M + 1) + (j - 1)];
        const cUp = dp[(i - 1) * (M + 1) + j] + 0.06; // mild step penalty favors balanced alignment
        const cLeft = dp[i * (M + 1) + (j - 1)] + 0.06;

        let best = cDiag;
        let dir = 1;
        if (cUp < best) {
          best = cUp;
          dir = 2;
        }
        if (cLeft < best) {
          best = cLeft;
          dir = 3;
        }
        dp[idx] = best + cost;
        back[idx] = dir;
      }
    }

    // Backtrack path
    const refSums = new Float32Array(M);
    const refCounts = new Uint16Array(M);
    let i = N;
    let j = M;
    let steps = 0;
    let simTotal = 0;
    const coveredRef = new Set();

    while (i > 0 && j > 0 && steps < N + M + 5) {
      const sim = Math.max(0, cosineSim(userFrames[i - 1], refFrames[j - 1]));
      refSums[j - 1] += sim;
      refCounts[j - 1]++;
      coveredRef.add(j - 1);
      simTotal += sim;
      steps++;

      const dir = back[i * (M + 1) + j];
      if (dir === 1) {
        i--;
        j--;
      } else if (dir === 2) {
        i--;
      } else if (dir === 3) {
        j--;
      } else {
        i--;
        j--;
      }
    }

    const refSims = new Float32Array(M);
    for (let k = 0; k < M; k++) {
      refSims[k] = refCounts[k] ? refSums[k] / refCounts[k] : 0.25;
    }

    return {
      avgSim: steps ? simTotal / steps : 0,
      refSims,
      pathCoverage: coveredRef.size / M,
    };
  }

  function tokenizeWords(text) {
    return String(text || "")
      .toLowerCase()
      .replace(/['’]/g, "'")
      .replace(/[^a-z0-9'\s]/g, " ")
      .trim()
      .split(/\s+/)
      .filter(Boolean);
  }

  function displayWords(text) {
    return String(text || "")
      .trim()
      .split(/\s+/)
      .filter(Boolean);
  }

  function levenshteinRatio(a, b) {
    if (a === b) return 1;
    const m = a.length;
    const n = b.length;
    if (!m || !n) return 0;
    const dp = Array.from({ length: m + 1 }, () => new Uint16Array(n + 1));
    for (let i = 0; i <= m; i++) dp[i][0] = i;
    for (let j = 0; j <= n; j++) dp[0][j] = j;
    for (let i = 1; i <= m; i++) {
      for (let j = 1; j <= n; j++) {
        const cost = a[i - 1] === b[j - 1] ? 0 : 1;
        dp[i][j] = Math.min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost);
      }
    }
    return 1 - dp[m][n] / Math.max(m, n);
  }

  function alignWordsLexical(targetTokens, spokenTranscripts) {
    if (!targetTokens.length || !spokenTranscripts?.length) return null;
    let bestResult = null;

    for (const rawSpoken of spokenTranscripts) {
      const spokenTokens = tokenizeWords(rawSpoken);
      if (!spokenTokens.length) continue;

      const T = targetTokens.length;
      const S = spokenTokens.length;
      const dp = Array.from({ length: T + 1 }, () => new Float32Array(S + 1));

      for (let i = 1; i <= T; i++) {
        for (let j = 1; j <= S; j++) {
          const sim = levenshteinRatio(targetTokens[i - 1], spokenTokens[j - 1]);
          dp[i][j] = Math.max(
            dp[i - 1][j - 1] + (sim >= 0.55 ? sim : -0.2),
            dp[i - 1][j],
            dp[i][j - 1]
          );
        }
      }

      // Trace back matched status per target token
      const perTokenSim = new Float32Array(T);
      let i = T;
      let j = S;
      while (i > 0 && j > 0) {
        const sim = levenshteinRatio(targetTokens[i - 1], spokenTokens[j - 1]);
        const diag = dp[i - 1][j - 1] + (sim >= 0.55 ? sim : -0.2);
        if (Math.abs(dp[i][j] - diag) < 1e-4 && sim >= 0.55) {
          perTokenSim[i - 1] = sim;
          i--;
          j--;
        } else if (dp[i - 1][j] >= dp[i][j - 1]) {
          i--;
        } else {
          j--;
        }
      }

      const avg = Array.from(perTokenSim).reduce((s, v) => s + v, 0) / T;
      if (!bestResult || avg > bestResult.avgWordSim) {
        bestResult = { transcript: rawSpoken, perTokenSim: Array.from(perTokenSim), avgWordSim: avg };
      }
    }
    return bestResult;
  }

  function decodeBase64ToArrayBuffer(b64) {
    const bin = atob(b64);
    const bytes = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    return bytes.buffer;
  }

  async function loadReferenceAudioBuffer(text, accent, apiProvider) {
    const clean = String(text || "").trim();
    if (!clean) return null;
    const isGB = accent === "gb-neural" || accent === "en-GB";
    const cacheKey = `${isGB ? "gb" : "us"}|${clean.toLowerCase()}`;
    if (_refCache.has(cacheKey)) return _refCache.get(cacheKey);

    let arrayBuf = null;
    const voiceMap = isGB ? globalScope.OFFLINE_VOICE_MAP_GB : globalScope.OFFLINE_VOICE_MAP;
    const rel = voiceMap?.[clean.toLowerCase()];
    if (rel) {
      try {
        const resp = await fetch(rel);
        if (resp.ok) arrayBuf = await resp.arrayBuffer();
      } catch {}
    }

    if (!arrayBuf && typeof apiProvider?.get_offline_audio === "function") {
      try {
        const res = await apiProvider.get_offline_audio(clean, accent);
        if (res?.ok && res.audio_b64) {
          arrayBuf = decodeBase64ToArrayBuffer(res.audio_b64);
        }
      } catch {}
    }

    if (!arrayBuf) return null;

    const Ctx = globalScope.AudioContext || globalScope.webkitAudioContext;
    if (!Ctx) return null;
    const ctx = new Ctx();
    try {
      const decoded = await ctx.decodeAudioData(arrayBuf.slice(0));
      const ch0 = decoded.getChannelData(0);
      const mono = resampleMono(ch0, decoded.sampleRate, TARGET_SR);
      const feats = extractAcousticFeatures(mono, 0.008);
      if (feats.frames.length >= 3) {
        _refCache.set(cacheKey, feats);
        if (_refCache.size > 40) {
          const oldest = _refCache.keys().next().value;
          _refCache.delete(oldest);
        }
        return feats;
      }
    } catch {} finally {
      try {
        await ctx.close();
      } catch {}
    }
    return null;
  }

  function classifyGrade(score, tooQuietReason = "") {
    if (tooQuietReason) {
      return {
        grade: "D",
        gradeTitle: "D 级 · 未捕捉有效人声",
        gradeClass: "grade-d",
        stars: "★☆☆☆☆",
        tip: tooQuietReason,
      };
    }
    if (score >= 90) {
      return {
        grade: "S",
        gradeTitle: "S 级 · 地道播音级",
        gradeClass: "grade-s",
        stars: "★★★★★",
        tip: "音准、重音节奏与饱满度极佳，非常接近母语播音标准！",
      };
    }
    if (score >= 78) {
      return {
        grade: "A",
        gradeTitle: "A 级 · 优秀清晰",
        gradeClass: "grade-a",
        stars: "★★★★☆",
        tip: "整体清晰自然、流畅达标，微调黄色提示音节可冲击 S 级。",
      };
    }
    if (score >= 60) {
      return {
        grade: "B",
        gradeTitle: "B 级 · 良好达标",
        gradeClass: "grade-b",
        stars: "★★★☆☆",
        tip: "主要音节已读出，注意重读位置、元音饱满度与辅音收尾。",
      };
    }
    if (score >= 40) {
      return {
        grade: "C",
        gradeTitle: "C 级 · 仍需巩固",
        gradeClass: "grade-c",
        stars: "★★☆☆☆",
        tip: "音准或语速与标准示范有一定偏差，建议先点听示范音再慢速跟读。",
      };
    }
    return {
      grade: "D",
      gradeTitle: "D 级 · 建议校准重读",
      gradeClass: "grade-d",
      stars: "★☆☆☆☆",
      tip: "识别匹配偏低或读音过快/过轻，请先做一次「校准麦克风」后再完整跟读。",
    };
  }

  function clampScore(v) {
    return Math.max(0, Math.min(100, Math.round(v)));
  }

  async function calibrateMicrophone(onProgress) {
    if (!globalScope.navigator?.mediaDevices?.getUserMedia) {
      throw new Error("当前设备或浏览器不支持麦克风权限");
    }
    const stream = await globalScope.navigator.mediaDevices.getUserMedia({
      audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true },
    });
    const Ctx = globalScope.AudioContext || globalScope.webkitAudioContext;
    if (!Ctx) {
      stream.getTracks().forEach((t) => t.stop());
      throw new Error("当前环境不支持 Web Audio 校准");
    }
    const ctx = new Ctx();
    if (ctx.state === "suspended") await ctx.resume();

    return new Promise((resolve) => {
      const source = ctx.createMediaStreamSource(stream);
      const proc = ctx.createScriptProcessor(1024, 1, 1);
      const frameRms = [];
      const startedAt = performance.now();
      const DURATION_MS = 1400;

      proc.onaudioprocess = (ev) => {
        const input = ev.inputBuffer.getChannelData(0);
        let sq = 0;
        for (let i = 0; i < input.length; i++) sq += input[i] * input[i];
        const rms = Math.sqrt(sq / input.length);
        frameRms.push(rms);
        const pct = Math.min(100, Math.round(((performance.now() - startedAt) / DURATION_MS) * 100));
        if (onProgress) onProgress(pct, Math.min(1, rms * 10));
      };

      source.connect(proc);
      proc.connect(ctx.destination);

      setTimeout(async () => {
        try {
          proc.disconnect();
          source.disconnect();
          stream.getTracks().forEach((t) => t.stop());
          await ctx.close();
        } catch {}

        frameRms.sort((a, b) => a - b);
        const median = frameRms[Math.floor(frameRms.length * 0.5)] || 0.008;
        const p75 = frameRms[Math.floor(frameRms.length * 0.75)] || 0.012;
        const noiseFloorRms = Math.max(0.0015, Math.min(0.08, p75));
        const noiseDb = Math.round(20 * Math.log10(Math.max(1e-5, median)));
        const speechThreshRms = Math.max(0.014, noiseFloorRms * 2.6);

        let envLabel = "正常室内";
        if (noiseDb <= -46) envLabel = "安静环境";
        else if (noiseDb >= -28) envLabel = "环境略噪杂";

        const cal = {
          noiseFloorRms,
          speechThreshRms,
          noiseDb,
          envLabel: `${envLabel} (${noiseDb} dB)`,
          calibratedAt: Date.now(),
        };
        saveCalibration(cal);
        resolve(cal);
      }, DURATION_MS);
    });
  }

  async function startShadowSession({ targetText, accent, rate = 1.0, apiProvider, onLevel, onAsrInterim }) {
    if (!globalScope.navigator?.mediaDevices?.getUserMedia) {
      throw new Error("当前环境不支持麦克风录音");
    }
    const stream = await globalScope.navigator.mediaDevices.getUserMedia({
      audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true },
    });

    const Ctx = globalScope.AudioContext || globalScope.webkitAudioContext;
    const ctx = Ctx ? new Ctx() : null;
    if (ctx && ctx.state === "suspended") await ctx.resume();

    // Start preloading reference audio features in parallel with user speaking
    const refPromise = loadReferenceAudioBuffer(targetText, accent, apiProvider);

    const pcmChunks = [];
    let proc = null;
    let source = null;
    const sampleRate = ctx ? ctx.sampleRate : 16000;

    if (ctx) {
      source = ctx.createMediaStreamSource(stream);
      proc = ctx.createScriptProcessor(2048, 1, 1);
      proc.onaudioprocess = (ev) => {
        const ch = ev.inputBuffer.getChannelData(0);
        pcmChunks.push(Float32Array.from(ch));
        if (onLevel) {
          let sq = 0;
          for (let i = 0; i < ch.length; i++) sq += ch[i] * ch[i];
          const rms = Math.sqrt(sq / ch.length);
          onLevel(Math.min(1, rms * 9));
        }
      };
      source.connect(proc);
      proc.connect(ctx.destination);
    }

    // Also record compressed blob for playback
    let mr = null;
    const mediaChunks = [];
    if (typeof globalScope.MediaRecorder !== "undefined") {
      try {
        mr = new globalScope.MediaRecorder(stream);
        mr.ondataavailable = (ev) => {
          if (ev.data && ev.data.size > 0) mediaChunks.push(ev.data);
        };
        mr.start();
      } catch {
        mr = null;
      }
    }

    // Optional SpeechRecognition running in parallel (best effort, never blocks offline mode)
    let recog = null;
    const asrTranscripts = [];
    const SpeechRec = globalScope.SpeechRecognition || globalScope.webkitSpeechRecognition;
    if (SpeechRec) {
      try {
        recog = new SpeechRec();
        recog.lang = accent === "gb-neural" || accent === "en-GB" ? "en-GB" : "en-US";
        recog.interimResults = true;
        recog.maxAlternatives = 5;
        recog.continuous = true;
        recog.onresult = (ev) => {
          let interim = "";
          for (let i = ev.resultIndex; i < ev.results.length; i++) {
            const res = ev.results[i];
            if (res.isFinal) {
              for (let a = 0; a < res.length; a++) {
                const txt = (res[a]?.transcript || "").trim();
                if (txt) asrTranscripts.push(txt);
              }
            } else {
              interim += res[0]?.transcript || "";
            }
          }
          if (onAsrInterim && (interim || asrTranscripts.length)) {
            onAsrInterim(asrTranscripts[asrTranscripts.length - 1] || interim);
          }
        };
        recog.onerror = () => {};
        recog.start();
      } catch {
        recog = null;
      }
    }

    let stopped = false;

    async function stopAndEvaluate() {
      if (stopped) return null;
      stopped = true;

      let blobPromise = Promise.resolve(null);
      if (mr && mr.state !== "inactive") {
        blobPromise = new Promise((res) => {
          mr.onstop = () => res(new Blob(mediaChunks, { type: mr.mimeType || "audio/webm" }));
          try {
            mr.stop();
          } catch {
            res(null);
          }
        });
      }

      if (recog) {
        try {
          recog.stop();
        } catch {}
        await new Promise((r) => setTimeout(r, 140));
      }

      try {
        if (proc) proc.disconnect();
        if (source) source.disconnect();
        stream.getTracks().forEach((t) => t.stop());
        if (ctx) await ctx.close();
      } catch {}

      const [blob, refFeats] = await Promise.all([blobPromise, refPromise]);

      // Merge PCM chunks
      let totalLen = 0;
      for (const c of pcmChunks) totalLen += c.length;
      const merged = new Float32Array(totalLen);
      let off = 0;
      for (const c of pcmChunks) {
        merged.set(c, off);
        off += c.length;
      }

      const pcm16k = resampleMono(merged, sampleRate, TARGET_SR);
      const evaluation = evaluatePronunciation({
        targetText,
        userPcm16k: pcm16k,
        refFeats,
        asrTranscripts,
        rate,
        calibration: loadCalibration(),
      });

      return { blob, evaluation };
    }

    return { stopAndEvaluate };
  }

  function evaluatePronunciation({ targetText, userPcm16k, refFeats, asrTranscripts, rate = 1.0, calibration }) {
    const cal = calibration || loadCalibration();
    const rawWords = displayWords(targetText);
    const targetTokens = tokenizeWords(targetText);
    const stats = computeSignalStats(userPcm16k);
    const userFeats = extractAcousticFeatures(userPcm16k, cal.speechThreshRms);

    // Gate check: no valid speech detected
    if (userFeats.frames.length < 5 || userFeats.activeSec < 0.14 || userFeats.snrDb < 5.0) {
      const gradeInfo = classifyGrade(
        18,
        userFeats.activeSec < 0.14
          ? "未检测到足够人声，请靠近麦克风清晰朗读后再结束。"
          : "声音偏弱或环境噪音接近语音，请先点击「校准麦克风」后再试。"
      );
      return {
        score: 18,
        ...gradeInfo,
        modeLabel: "环境人声检测未通过",
        recognizedText: asrTranscripts?.[0] || "",
        dimensions: { accuracy: 18, fluency: 20, completeness: 10, clarity: clampScore(userFeats.snrDb * 4) },
        wordResults: rawWords.map((w) => ({ word: w, status: "miss", score: 15 })),
      };
    }

    const snrComponent = Math.min(1, Math.max(0, (userFeats.snrDb - 4) / 16)) * 82;
    const articulationBonus = Math.min(1, userFeats.highBandRatio * 8.0) * 18;
    const clarityBase = clampScore(snrComponent + articulationBonus);
    const clarityScore = stats.clipRatio > 0.06 ? Math.max(45, clarityBase - 20) : clarityBase;

    let accuracyScore = 70;
    let fluencyScore = 72;
    let completenessScore = 72;
    let wordResults = rawWords.map((w) => ({ word: w, status: "warn", score: 70 }));
    let durationPenaltyCap = 100;

    // 1. Acoustic DTW Calibration against Broadcast Reference
    let refSims = null;
    if (refFeats && refFeats.frames.length >= 3) {
      const dtw = alignAcousticDTW(userFeats.frames, refFeats.frames);
      refSims = dtw.refSims;

      // Map cosine similarity (~0.18..0.72 across speakers) smoothly to 30..98
      const spectralScore = clampScore(((dtw.avgSim - 0.14) / 0.56) * 68 + 30);

      // Account for selected playback rate if reference wasn't adjusted, compare natural cadence
      const expectedDur = refFeats.activeSec / Math.max(0.75, Math.min(1.25, rate));
      const durRatio = userFeats.activeSec / Math.max(0.15, expectedDur);

      if (durRatio >= 0.72 && durRatio <= 1.38) {
        fluencyScore = clampScore(96 - Math.abs(1 - durRatio) * 38);
      } else {
        const distOut = durRatio < 0.72 ? 0.72 - durRatio : durRatio - 1.38;
        fluencyScore = clampScore(82 - distOut * 75);
      }

      const sylRatio = Math.min(userFeats.syllables, refFeats.syllables) / Math.max(1, refFeats.syllables);
      const coverage = Math.min(1, dtw.pathCoverage);
      completenessScore = clampScore((0.45 * sylRatio + 0.35 * coverage + 0.20 * Math.min(1, durRatio / 0.85)) * 100);

      if (durRatio < 0.42 || durRatio > 2.35) {
        durationPenaltyCap = 52;
      }

      accuracyScore = spectralScore;

      // Project DTW path alignment across target words for word-by-word visual calibration
      const M = refSims.length;
      const wc = Math.max(1, rawWords.length);
      wordResults = rawWords.map((w, idx) => {
        const startBin = Math.floor((idx * M) / wc);
        const endBin = Math.max(startBin + 1, Math.floor(((idx + 1) * M) / wc));
        let sum = 0;
        for (let b = startBin; b < endBin; b++) sum += refSims[b];
        const wScore = clampScore(((sum / (endBin - startBin) - 0.12) / 0.56) * 68 + 30);
        const finalWordScore = durRatio < 0.5 ? Math.min(wScore, 55) : wScore;
        return {
          word: w,
          status: finalWordScore >= 76 ? "ok" : finalWordScore >= 52 ? "warn" : "miss",
          score: finalWordScore,
        };
      });
    } else {
      // Reference not decoded (rare edge case): fallback duration heuristic
      const expectedSec = Math.max(0.45, targetTokens.length * 0.42);
      const durRatio = userFeats.activeSec / expectedSec;
      fluencyScore = clampScore(92 - Math.abs(1 - durRatio) * 45);
      completenessScore = clampScore(Math.min(1, userFeats.syllables / Math.max(1, targetTokens.length * 1.4)) * 95);
      accuracyScore = clampScore(0.5 * clarityScore + 0.5 * completenessScore);
    }

    // 2. Hybrid fusion with Speech Recognition when available
    const lexical = alignWordsLexical(targetTokens, asrTranscripts);
    let modeLabel = "离线声学校准引擎（已比对播音标准波形）";
    if (lexical) {
      modeLabel = "语音识别 + 声学波形双校准";
      const asrScore = clampScore(lexical.avgWordSim * 100);
      accuracyScore = clampScore(0.62 * asrScore + 0.38 * accuracyScore);
      const matchedCount = lexical.perTokenSim.filter((v) => v >= 0.68).length;
      const asrComplete = clampScore((matchedCount / Math.max(1, targetTokens.length)) * 100);
      completenessScore = clampScore(0.65 * asrComplete + 0.35 * completenessScore);

      wordResults = rawWords.map((w, idx) => {
        const lexSim = lexical.perTokenSim[idx] ?? 0;
        const acScore = wordResults[idx]?.score ?? accuracyScore;
        const blended = clampScore(0.72 * (lexSim * 100) + 0.28 * acScore);
        const status = lexSim >= 0.84 ? "ok" : lexSim >= 0.58 ? "warn" : "miss";
        return { word: w, status, score: blended };
      });
      if (lexical.avgWordSim >= 0.72) durationPenaltyCap = 100;
    }

    const total = Math.min(
      durationPenaltyCap,
      clampScore(0.42 * accuracyScore + 0.22 * fluencyScore + 0.20 * completenessScore + 0.16 * clarityScore)
    );
    const clipTip = stats.clipRatio > 0.06 ? "（检测到轻微爆音，建议稍远离麦克风）" : "";
    const gradeInfo = classifyGrade(total);

    return {
      score: total,
      ...gradeInfo,
      tip: gradeInfo.tip + clipTip,
      modeLabel,
      recognizedText: lexical ? lexical.transcript : "",
      dimensions: {
        accuracy: accuracyScore,
        fluency: fluencyScore,
        completeness: completenessScore,
        clarity: clarityScore,
      },
      wordResults,
      noiseFloorInfo: cal.envLabel,
    };
  }

  globalScope.LingoPronunciation = {
    loadCalibration,
    calibrateMicrophone,
    startShadowSession,
    evaluatePronunciation,
    classifyGrade,
  };

  if (typeof module !== "undefined" && module.exports) {
    module.exports = {
      evaluatePronunciation,
      classifyGrade,
      alignAcousticDTW,
      extractAcousticFeatures,
      alignWordsLexical,
    };
  }
})(typeof globalThis !== "undefined" ? globalThis : window);
