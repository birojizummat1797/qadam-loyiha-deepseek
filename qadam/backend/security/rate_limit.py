"""
Oddiy in-memory rate limiter (MVP uchun).
Production: Redis yoki Upstash'ga o'tish tavsiya etiladi.
"""
import time
from collections import defaultdict

_buckets: dict[str, list[float]] = defaultdict(list)


def check(user_id: int, action: str, max_per_window: int, window_sec: int) -> bool:
    """
    True = ruxsat berilgan. False = rate-limited.
    """
    key = f"{user_id}:{action}"
    now = time.time()
    cutoff = now - window_sec
    _buckets[key] = [t for t in _buckets[key] if t > cutoff]
    if len(_buckets[key]) >= max_per_window:
        return False
    _buckets[key].append(now)
    return True