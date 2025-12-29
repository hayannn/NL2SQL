import sqlite3
from typing import Optional, Tuple
from .config import DB_PATH


def is_safe_select(sql: str) -> bool:
    s = sql.strip().lower()

    if not s.startswith("select"):
        return False

    banned = [
        "insert", "update", "delete",
        "drop", "truncate", "alter",
        "create", "merge", "grant", "revoke"
    ]

    return not any(b in s for b in banned)


def execute_safe_select(sql: str) -> Tuple[bool, Optional[int], Optional[str], bool]:
    if not DB_PATH:
        return False, None, "DB not configured", False

    if not is_safe_select(sql):
        return False, None, "SKIPPED (non-select)", False

    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        conn.close()
        return True, len(rows), None, True
    except Exception as e:
        return False, None, str(e), True