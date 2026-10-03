"""Remove unsupported numbers from anything a user can see (PM Q3, 2026-10-03).

Salary (and the income-boost percentages around it) has no data passport
(source, date, geography, sample size, period, seniority, gross/net, method),
so it never reaches the Mini App, PDF or public API until it does.
"""

UNSUPPORTED_KEYS = frozenset({
    "salary_uzs",
    "salary_usd",
    "junior_salary_uzs",
    "remote_salary_usd",
    "income_factors",
})


def strip_unsupported(obj):
    """Deep copy without salary / income keys (dicts and lists, recursively)."""
    if isinstance(obj, dict):
        return {k: strip_unsupported(v) for k, v in obj.items() if k not in UNSUPPORTED_KEYS}
    if isinstance(obj, list):
        return [strip_unsupported(v) for v in obj]
    return obj
