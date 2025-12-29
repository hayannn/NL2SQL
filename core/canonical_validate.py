import re
from typing import Tuple


SAFE_SELECT_ONLY = re.compile(r"^\s*select\b", re.IGNORECASE)

BANNED_KEYWORDS = [
    "insert", "update", "delete", "drop", "alter",
    "truncate", "grant", "revoke", "merge", "create"
]


def check_safe_statement(sql: str) -> Tuple[bool, str]:
    s = sql.strip().lower()

    if not SAFE_SELECT_ONLY.match(s):
        return False, "ONLY SELECT allowed"

    for kw in BANNED_KEYWORDS:
        if kw in s:
            return False, f"dangerous keyword detected: {kw}"

    return True, ""


def check_basic_structure(sql: str) -> Tuple[bool, str]:
    s = sql.lower()

    if "from" not in s:
        return False, "missing FROM clause"

    # GROUP BY but no aggregation?
    if "group by" in s and "count" not in s and "sum" not in s and "avg" not in s:
        return False, "GROUP BY present but no aggregate detected"

    return True, ""


def validate_canonical(sql: str) -> Tuple[bool, list[str]]:
    reasons = []

    ok, msg = check_safe_statement(sql)
    if not ok:
        reasons.append(msg)

    ok, msg = check_basic_structure(sql)
    if not ok:
        reasons.append(msg)

    return len(reasons) == 0, reasons