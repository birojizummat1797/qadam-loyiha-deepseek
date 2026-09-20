ENGLISH_ORDER = {"none": 0, "a2": 1, "b1": 2, "b2": 3, "c1": 4}


def calculate_readiness(constraints, prerequisites):
    barriers = []
    score = 100

    dev = constraints.get("device")
    req_dev = prerequisites.get("device")
    if req_dev == "required" and dev in ("smartphone_only", "none"):
        level = "hard" if dev == "none" else "soft"
        barriers.append({
            "type": "device", "level": level,
            "path": "Noutbuk topish yollari - grantlar, kutubxona",
        })
        score -= 30 if dev == "none" else 15

    req_en = prerequisites.get("english", "none")
    user_en = constraints.get("english", "none")
    if ENGLISH_ORDER.get(user_en, 0) < ENGLISH_ORDER.get(req_en, 0):
        gap = ENGLISH_ORDER.get(req_en, 0) - ENGLISH_ORDER.get(user_en, 0)
        barriers.append({
            "type": "language", "level": "soft",
            "path": "Ingliz tilini " + req_en.upper() + " darajaga kotarish (3-6 oy)",
        })
        score -= 10 * gap

    t = constraints.get("time")
    if t in ("lt_1h", "1h"):
        barriers.append({
            "type": "time", "level": "soft",
            "path": "Haftalik jadval tuzish",
        })
        score -= 10

    return {
        "readiness": max(0, score),
        "barriers": barriers,
        "has_hard_barrier": any(b["level"] == "hard" for b in barriers),
    }
