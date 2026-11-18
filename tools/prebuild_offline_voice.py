"""Pre-synthesize offline MP3 voice pack locally using Edge-TTS + OpenVoice V2."""

from __future__ import annotations

import asyncio
import concurrent.futures
import ctypes
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"

import edge_tts
import torch
from openvoice.api import OpenVoiceBaseClass, ToneColorConverter

torch.set_num_threads(1)
try:
    torch.set_num_interop_threads(1)
except Exception:
    pass

try:
    ctypes.windll.kernel32.SetPriorityClass(
        ctypes.windll.kernel32.GetCurrentProcess(), 0x00000040
    )
except Exception:
    pass


class FastToneColorConverter(ToneColorConverter):
    """ToneColorConverter without optional wavmark watermark dependency."""

    def __init__(self, config_path: str, device: str = "cpu") -> None:
        OpenVoiceBaseClass.__init__(self, config_path, device=device)
        self.watermark_model = None
        self.version = getattr(self.hps, "_version_", "v1")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.seed_data import SEED_DIALOGUES, SEED_GRAMMAR, SEED_WORDS

FFMPEG = r"C:\反重力\ComfyUI\venv\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v9.0.2.exe"
PROMPT_WAV = ROOT / "frontend" / "assets" / "user_voice_prompt.wav"
OV_CFG = ROOT / "tools" / "openvoice_v2" / "config.json"
OV_CKPT = ROOT / "tools" / "openvoice_v2" / "checkpoint.pth"
OUT_DIR = ROOT / "frontend" / "assets" / "offline_voice"
MANIFEST_JS = ROOT / "frontend" / "offline_voice_manifest.js"

BASE_VOICE = "en-US-AndrewNeural"


def collect_texts(limit: int | None = None) -> list[str]:
    texts: list[str] = []
    seen: set[str] = set()

    def add(t: str) -> None:
        clean = (t or "").strip()
        key = clean.lower()
        if clean and key not in seen:
            seen.add(key)
            texts.append(clean)

    for w in SEED_WORDS:
        add(w[0])
    for d in SEED_DIALOGUES:
        for line in d["lines"]:
            add(line["en"])
        for p in d["key_phrases"]:
            add(p["en"])
    for g in SEED_GRAMMAR:
        for ex in g["examples"]:
            add(ex["en"])

    return texts[:limit] if limit else texts


async def _tts_one(text: str, out_path: Path) -> None:
    comm = edge_tts.Communicate(text, voice=BASE_VOICE)
    await comm.save(str(out_path))


async def generate_base_audio_batch(items: list[tuple[str, Path]], concurrency: int = 8) -> None:
    sem = asyncio.Semaphore(concurrency)

    async def worker(text: str, path: Path) -> None:
        if path.is_file() and path.stat().st_size > 200:
            return
        async with sem:
            for attempt in range(3):
                try:
                    await _tts_one(text, path)
                    return
                except Exception:
                    if attempt == 2:
                        raise
                    await asyncio.sleep(0.5 * (attempt + 1))

    await asyncio.gather(*(worker(t, p) for t, p in items))


def wav_to_mp3(wav_path: Path, mp3_path: Path) -> None:
    subprocess.run(
        [
            FFMPEG,
            "-y",
            "-i",
            str(wav_path),
            "-ac",
            "1",
            "-ar",
            "24000",
            "-b:a",
            "32k",
            str(mp3_path),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=0x00000040 | getattr(subprocess, "CREATE_NO_WINDOW", 0),
        check=True,
    )


def write_manifest(mapping: dict[str, str]) -> None:
    content = (
        "(function (g) {\n"
        "  g.OFFLINE_VOICE_MAP = "
        + json.dumps(mapping, ensure_ascii=False, indent=2)
        + ";\n"
        "})(typeof globalThis !== 'undefined' ? globalThis : window);\n"
    )
    MANIFEST_JS.write_text(content, encoding="utf-8")


def main() -> None:
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tmp_dir = ROOT / "tools" / "_voice_tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    texts = collect_texts(limit)
    t0 = time.time()

    print(f"Preparing {len(texts)} items...", flush=True)
    if True:
        ref_base = tmp_dir / "src_ref.mp3"
        if not ref_base.is_file():
            asyncio.run(
                _tts_one(
                    "Consistent practice is the key to mastering a new language. Let us begin today.",
                    ref_base,
                )
            )

        # Step 1: Fetch base English audio concurrently via Edge-TTS
        pending: list[tuple[str, Path, Path]] = []
        mapping: dict[str, str] = {}
        for text in texts:
            key = text.strip().lower()
            h = hashlib.sha1(key.encode("utf-8")).hexdigest()[:16]
            mp3_name = f"{h}.mp3"
            mp3_path = OUT_DIR / mp3_name
            if mp3_path.is_file() and mp3_path.stat().st_size > 200:
                mapping[key] = f"assets/offline_voice/{mp3_name}"
            else:
                pending.append((text, tmp_dir / f"{h}_base.mp3", mp3_path))

        if pending:
            print(f"Synthesizing {len(pending)} base clips via Edge-TTS...", flush=True)
            asyncio.run(generate_base_audio_batch([(t, bp) for t, bp, _ in pending], concurrency=10))
            print(f"Base clips ready in {time.time()-t0:.1f}s. Loading OpenVoiceV2...", flush=True)

            converter = FastToneColorConverter(str(OV_CFG), device="cpu")
            converter.load_ckpt(str(OV_CKPT))
            src_se = converter.extract_se([str(ref_base)])
            tgt_se = converter.extract_se([str(PROMPT_WAV)])

            for idx, (text, base_mp3, final_mp3) in enumerate(pending, 1):
                key = text.strip().lower()
                out_wav = tmp_dir / f"{final_mp3.stem}_ov.wav"
                converter.convert(
                    audio_src_path=str(base_mp3),
                    src_se=src_se,
                    tgt_se=tgt_se,
                    output_path=str(out_wav),
                    tau=0.35,
                )
                wav_to_mp3(out_wav, final_mp3)
                mapping[key] = f"assets/offline_voice/{final_mp3.name}"
                time.sleep(0.35)
                if idx % 20 == 0 or idx == len(pending):
                    write_manifest(mapping)
                    print(f"Converted {idx}/{len(pending)} | elapsed {time.time()-t0:.1f}s", flush=True)

        write_manifest(mapping)
        total_kb = sum(p.stat().st_size for p in OUT_DIR.glob("*.mp3")) // 1024
        print(f"DONE: {len(mapping)}/{len(texts)} offline MP3s ready ({total_kb} KB)", flush=True)


if __name__ == "__main__":
    main()
