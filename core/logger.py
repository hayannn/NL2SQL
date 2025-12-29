import os
import csv
from datetime import datetime
from typing import List
from .config import OUTPUT_FILE


HEADER = [
    "timestamp",
    "sql_name",
    "canonical_sql",
    "tibero_sql",
    "oracle_sql",
    "postgresql_sql",
    "mysql_sql",
    "validation_ok",
    "validation_reasons",
    "exec_ran",
    "exec_success",
    "exec_row_count",
    "exec_error",
    "tokens_in",
    "tokens_out",
    "cost_usd",
    "status",
    "error",
]


def write_header_if_needed():
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    if not os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL, escapechar="\\")
            writer.writerow(HEADER)


def log_row(row: List):
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    must_write_header = (
        not os.path.exists(OUTPUT_FILE) or os.path.getsize(OUTPUT_FILE) == 0
    )

    with open(OUTPUT_FILE, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL, escapechar="\\")

        if must_write_header:
            writer.writerow(HEADER)

        writer.writerow(row)


def now():
    return datetime.utcnow().isoformat()