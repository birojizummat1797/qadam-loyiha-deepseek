"""Remove unsupported numbers from anything a user can see (PM Q3, 2026-10-03).

Salary (and the income-boost percentages around it) has no data passport
(source, date, geography, sample size, period, seniority, gross/net, method),
so it never reaches the Mini App, PDF or public API until it does.
"""
import json
import re
from pathlib import Path

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


def mentions_money(text) -> bool:
    return isinstance(text, str) and bool(MONEY_RE.search(text))


# Reviewed audit of evidence-less factual claims in the roadmap KB.
CLAIMS_AUDIT = json.loads(
    (Path(__file__).parent.parent / "data" / "kb_claims_audit_v1.json").read_text(encoding="utf-8")
)
SUPPRESSED = {c["text"] for c in CLAIMS_AUDIT["claims"] if c["action"] == "suppress"}
REWRITES = {c["text"]: c["replacement"] for c in CLAIMS_AUDIT["claims"] if c["action"] == "rewrite"}


def _text_suppressed(text) -> bool:
    return isinstance(text, str) and (text in SUPPRESSED or mentions_money(text))


def is_suppressed(item) -> bool:
    """Should this list item disappear? Shallow on purpose: a string, a [problem, solution]
    pair, or a {problem, solution} dict whose own text is a money quote or an audited claim.
    A larger container (a whole stage or career) is never dropped because of a nested line."""
    if isinstance(item, str):
        return _text_suppressed(item)
    if isinstance(item, (list, tuple)):
        return any(_text_suppressed(v) for v in item)
    if isinstance(item, dict):
        return any(_text_suppressed(v) for v in item.values())
    return False


def strip_unsupported(obj):
    """Deep copy for users: no salary/income keys, no money quotes, no evidence-less claims."""
    if isinstance(obj, dict):
        return {k: strip_unsupported(v) for k, v in obj.items() if k not in UNSUPPORTED_KEYS}
    if isinstance(obj, list):
        return [strip_unsupported(v) for v in obj if not is_suppressed(v)]
    if isinstance(obj, str):
        return REWRITES.get(obj, obj)
    return obj
