"""Extract ~15,000 graded & high-frequency words from tools/ecdict.csv into backend/ecdict_core.json.gz."""

from __future__ import annotations

import csv
import gzip
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "tools" / "ecdict.csv"
OUT_PATH = ROOT / "backend" / "ecdict_core.json.gz"


def clean_translation(raw: str) -> str:
    lines = [ln.strip() for ln in raw.replace("\\n", "\n").splitlines() if ln.strip()]
    joined = "；".join(lines)
    joined = re.sub(r"\s+", " ", joined).strip()
    if len(joined) > 64:
        joined = joined[:61].rstrip("；;，, ") + "..."
    return joined


def pick_category_and_diff(tags: set[str], oxford: str, collins: int) -> tuple[str, int]:
    if "zk" in tags:
        return ("中考核心", 1)
    if "gk" in tags:
        return ("高考核心", 1)
    if "cet4" in tags:
        return ("大学四级", 2)
    if "cet6" in tags:
        return ("大学六级", 2)
    if "ky" in tags:
        return ("考研英语", 2)
    if "ielts" in tags or "toefl" in tags:
        return ("雅思托福", 3)
    if "gre" in tags:
        return ("GRE进阶", 3)
    if oxford == "1":
        return ("牛津核心", 1)
    return ("高频拓展", 2 if collins >= 4 else 3)


def extract_pos(translation: str, pos_field: str) -> str:
    m = re.match(r"^([a-z]+\.)\s*", translation)
    if m:
        return m.group(1)
    if pos_field:
        first = pos_field.split("/")[0].split(":")[0].strip()
        if first:
            return f"{first}."
    return ""


def main() -> None:
    entries = []
    seen = set()

    with CSV_PATH.open("r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            w = (row.get("word") or "").strip()
            tr_raw = (row.get("translation") or "").strip()
            ph = (row.get("phonetic") or "").strip()
            tag_str = (row.get("tag") or "").strip()
            ox = (row.get("oxford") or "").strip()
            col_str = (row.get("collins") or "").strip()
            col = int(col_str) if col_str.isdigit() else 0

            if not w or not tr_raw or not w.isascii() or " " in w or len(w) < 2:
                continue
            if not re.match(r"^[A-Za-z][A-Za-z\-']*$", w):
                continue

            tags = set(tag_str.split())
            is_graded = bool(tags & {"zk", "gk", "cet4", "cet6", "ky", "ielts", "toefl", "gre"})
            if not is_graded and ox != "1" and col < 3:
                continue

            key = w.lower()
            if key in seen:
                continue
            seen.add(key)

            tr = clean_translation(tr_raw)
            if not tr:
                continue

            phonetic = f"/{ph.strip('/')}/" if ph else ""
            pos = extract_pos(tr, (row.get("pos") or "").strip())
            cat, diff = pick_category_and_diff(tags, ox, col)
            entries.append([w, phonetic, pos, tr, cat, diff])

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(OUT_PATH, "wt", encoding="utf-8") as gz:
        json.dump(entries, gz, ensure_ascii=False, separators=(",", ":"))

    size_kb = OUT_PATH.stat().st_size // 1024
    print(f"Extracted {len(entries)} words -> {OUT_PATH} ({size_kb} KB)")


if __name__ == "__main__":
    main()
