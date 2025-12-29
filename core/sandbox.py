import os
from typing import Tuple, Optional

import psycopg2
import pymysql
import cx_Oracle


def run_postgres(sql: str) -> Tuple[bool, Optional[int], Optional[str]]:
    s = sql.strip().lower()
    if not s.startswith("select"):
        return False, None, "NOT_SELECT"

    try:
        conn = psycopg2.connect(
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT", 5432),
            dbname=os.getenv("PG_DB"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
        )
        cur = conn.cursor()
        cur.execute(sql)

        try:
            rows = cur.fetchall()
            count = len(rows)
        except Exception:
            count = None

        conn.close()
        return True, count, None

    except Exception as e:
        return False, None, str(e)


def run_mysql(sql: str) -> Tuple[bool, Optional[int], Optional[str]]:
    s = sql.strip().lower()
    if not s.startswith("select"):
        return False, None, "NOT_SELECT"

    try:
        conn = pymysql.connect(
            host=os.getenv("MY_HOST"),
            port=int(os.getenv("MY_PORT", 3306)),
            db=os.getenv("MY_DB"),
            user=os.getenv("MY_USER"),
            password=os.getenv("MY_PASSWORD"),
            charset="utf8",
            cursorclass=pymysql.cursors.Cursor,
        )

        cur = conn.cursor()
        cur.execute(sql)

        try:
            rows = cur.fetchall()
            count = len(rows)
        except Exception:
            count = None

        conn.close()
        return True, count, None

    except Exception as e:
        return False, None, str(e)


def run_oracle(sql: str):
    s = sql.strip().lower()
    if not s.startswith("select"):
        return False, None, "NOT_SELECT"

    try:
        dsn = cx_Oracle.makedsn(
            os.getenv("ORACLE_HOST"),
            int(os.getenv("ORACLE_PORT")),
            service_name=os.getenv("ORACLE_SERVICE"),
        )

        conn = cx_Oracle.connect(
            user=os.getenv("ORACLE_USER"),
            password=os.getenv("ORACLE_PASSWORD"),
            dsn=dsn,
        )

        cur = conn.cursor()
        cur.execute(sql)

        try:
            rows = cur.fetchall()
            count = len(rows)
        except Exception:
            count = None

        conn.close()
        return True, count, None

    except Exception as e:
        return False, None, str(e)

def run_tibero(sql: str):
    # Tibero는 라이선스 필요 - 추후 설치해서 사용
    return False, None, "Tibero not configured (DB not installed)"

# 정상 설치 후 활성화해 사용
# def run_tibero(sql: str) -> Tuple[bool, Optional[int], Optional[str]]:
#     s = sql.strip().lower()
#     if not s.startswith("select"):
#         return False, None, "NOT_SELECT"

#     try:
#         dsn = cx_Oracle.makedsn(
#             os.getenv("TB_HOST"),
#             int(os.getenv("TB_PORT")),
#             service_name=os.getenv("TB_SERVICE"),
#         )

#         conn = cx_Oracle.connect(
#             user=os.getenv("TB_USER"),
#             password=os.getenv("TB_PASSWORD"),
#             dsn=dsn,
#         )

#         cur = conn.cursor()
#         cur.execute(sql)

#         try:
#             rows = cur.fetchall()
#             count = len(rows)
#         except Exception:
#             count = None

#         conn.close()
#         return True, count, None

#     except Exception as e:
#         return False, None, str(e)