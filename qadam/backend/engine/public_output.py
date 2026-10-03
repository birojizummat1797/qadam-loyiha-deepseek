"""Remove unsupported numbers from anything a user can see (PM Q3, 2026-10-03).

Salary (and the income-boost percentages around it) has no data passport
(source, date, geography, sample size, period, seniority, gross/net, method),
so it never reaches the Mini App, PDF or public API until it does.
"""
import re

UNSUPPORTED_KEYS = frozenset({
    "salary_uzs",
    "salary_usd",
    "junior_salary_uzs",
    "remote_salary_usd",
    "income_factors",
})


# Money amounts inside editorial text (e.g. "Mahalliy bozor: 3-6 mln", "$300/oy").
MONEY_RE = re.compile(
    r"\d[\d\s.,\-–]*\s*(mln|million|ming|so['’]?m|sum|usd|dollar)\b|\$\s?\d",
    re.IGNORECASE,
)


def mentions_money(value) -> bool:
    if isinstance(value, str):
        return bool(MONEY_RE.search(value))
    if isinstance(value, (list, tuple)):
        return any(mentions_money(v) for v in value)
    if isinstance(value, dict):
        return any(mentions_money(v) for v in value.values())
    return False


def strip_unsupported(obj):
    """Deep copy without salary / income keys, and without list items that quote money."""
    if isinstance(obj, dict):
        return {k: strip_unsupported(v) for k, v in obj.items() if k not in UNSUPPORTED_KEYS}
    if isinstance(obj, list):
        return [strip_unsupported(v) for v in obj if not mentions_money(v)]
    return obj
