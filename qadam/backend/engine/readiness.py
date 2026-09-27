"""
Readiness — PM spec (PHASE G).

Readiness(c) = Base × P_computer × P_english × P_time

P_computer = 0.5     (agar device 'required' va user'da yo'q)
P_english  = 0.85^k  (k = yetishmayotgan darajalar soni)
P_time     = min(1, user_vaqti / career_minimal_vaqti)
"""

BASE_READINESS = 100.0

ENGLISH_ORDER = {"none": 0, "a2": 1, "b1": 2, "b2": 3, "c1": 4}

# Foydalanuvchi vaqti (kunlik soat) → numeric
TIME_TO_HOURS = {
    "lt_1h": 0.5,
    "1h": 1.0,
    "2_3h": 2.5,
    "4h_plus": 4.5,
    "full_time": 8.0,
}

# Career minimal vaqti (kunlik soat) — default
DEFAULT_MIN_HOURS = 2.0


def _p_computer(constraints, prerequisites):
    req = prerequisites.get("device")
    user = constraints.get("device")
    if req != "required":
        return 1.0
    if user in ("laptop", "both"):
        return 1.0
    if user == "smartphone_only":
        return 0.5
    return 0.5  # "none" ham


def _p_english(constraints, prerequisites):
    req = prerequisites.get("english", "none")
    user = constraints.get("english", "none")
    gap = ENGLISH_ORDER.get(req, 0) - ENGLISH_ORDER.get(user, 0)
    if gap <= 0:
        return 1.0
    return 0.85 ** gap


def _p_time(constraints, prerequisites):
    user_t = constraints.get("time", "2_3h")
    user_hours = TIME_TO_HOURS.get(user_t, 2.5)
    min_hours = prerequisites.get("min_hours", DEFAULT_MIN_HOURS)
    if min_hours <= 0:
        return 1.0
    return min(1.0, user_hours / min_hours)


def calculate_readiness(constraints, prerequisites):
    p_c = _p_computer(constraints, prerequisites)
    p_e = _p_english(constraints, prerequisites)
    p_t = _p_time(constraints, prerequisites)

    readiness = BASE_READINESS * p_c * p_e * p_t

    # Barrier ro'yxati (frontend uchun)
    barriers = []
    if p_c < 1.0:
        barriers.append({
            "type": "device",
            "level": "hard" if constraints.get("device") == "none" else "soft",
            "path": "Noutbuk topish yollari — grantlar, kutubxona, ijaraga olish",
        })
    if p_e < 1.0:
        req = prerequisites.get("english", "")
        barriers.append({
            "type": "language",
            "level": "soft",
            "path": f"Ingliz tilini {req.upper()} darajaga ko'tarish (3-6 oy)",
        })
    if p_t < 1.0:
        barriers.append({
            "type": "time",
            "level": "soft",
            "path": "Haftalik jadval tuzish, vaqt ajratish",
        })

    return {
        "readiness": round(readiness, 2),
        "p_computer": round(p_c, 3),
        "p_english": round(p_e, 3),
        "p_time": round(p_t, 3),
        "barriers": barriers,
        "has_hard_barrier": any(b["level"] == "hard" for b in barriers),
    }
