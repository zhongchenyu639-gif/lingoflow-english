"""SM-2 spaced repetition scheduling utilities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


RATING_QUALITY_MAP: dict[str, int] = {
    "again": 1,
    "hard": 3,
    "good": 4,
    "easy": 5,
}


@dataclass(frozen=True)
class SM2Result:
    """Updated spaced repetition state after a single review."""

    ease_factor: float
    interval_days: int
    repetitions: int
    next_review_at: str
    interval_label: str


def _format_interval_label(interval_days: int, is_relearn: bool = False) -> str:
    if is_relearn:
        return "10分钟后"
    if interval_days <= 0:
        return "今天"
    if interval_days == 1:
        return "1天"
    if interval_days < 30:
        return f"{interval_days}天"
    months = round(interval_days / 30)
    return f"{months}个月"


def calculate_sm2(
    ease_factor: float,
    interval_days: int,
    repetitions: int,
    rating: str,
    now: datetime | None = None,
) -> SM2Result:
    """Compute the next SM-2 state for a card given a user rating."""
    if rating not in RATING_QUALITY_MAP:
        raise ValueError(f"Unsupported rating: {rating}")

    quality = RATING_QUALITY_MAP[rating]
    current_time = now or datetime.now(timezone.utc)

    new_ease = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    new_ease = max(1.3, round(new_ease, 2))

    if quality < 3:
        new_repetitions = 0
        new_interval = 0
        next_review = current_time + timedelta(minutes=10)
        label = _format_interval_label(0, is_relearn=True)
    else:
        new_repetitions = repetitions + 1
        if new_repetitions == 1:
            new_interval = 1 if rating != "easy" else 4
        elif new_repetitions == 2:
            new_interval = 6 if rating != "easy" else 8
        else:
            base = max(1, interval_days)
            multiplier = new_ease
            if rating == "hard":
                multiplier = max(1.2, new_ease * 0.8)
            elif rating == "easy":
                multiplier = new_ease * 1.3
            new_interval = max(1, round(base * multiplier))

        next_review = current_time + timedelta(days=new_interval)
        label = _format_interval_label(new_interval, is_relearn=False)

    return SM2Result(
        ease_factor=new_ease,
        interval_days=new_interval,
        repetitions=new_repetitions,
        next_review_at=next_review.isoformat(),
        interval_label=label,
    )


def preview_intervals(
    ease_factor: float,
    interval_days: int,
    repetitions: int,
) -> dict[str, str]:
    """Return human-readable next-review labels for all 4 rating buttons."""
    return {
        rating: calculate_sm2(ease_factor, interval_days, repetitions, rating).interval_label
        for rating in RATING_QUALITY_MAP
    }
