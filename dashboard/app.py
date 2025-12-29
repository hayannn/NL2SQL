import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))
    
    
from core.logger import log_row, now

import streamlit as st

from core.transform import call_model
from core.validate import validate_with_llm
from core.canonical_validate import validate_canonical
from core.sandbox import (
    run_postgres,
    run_mysql,
    run_oracle,
    run_tibero,
)


st.set_page_config(page_title="NL → SQL (Safe Pipeline)", layout="wide")

st.title("🍋 DB Agent")


def clean_sql(text: str) -> str:
    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()[1:-1]
        text = "\n".join(lines)

    if text.endswith(";"):
        text = text[:-1]

    return text.strip()

def prompt_nl_to_sql(nl: str) -> str:
    return f"""
Convert the following natural language request to ANSI-style SQL.

\"\"\"{nl}\"\"\"

Output ONLY SQL.
""".strip()


def prompt_convert_sql(canonical: str, target: str) -> str:
    return f"""
Convert this canonical SQL to {target} dialect.

```sql
{canonical}
```

Output ONLY SQL.
""".strip()


natural_text = st.text_area(
    "질문 입력",
    value="지난 7일 동안 주문 수를 날짜별로 집계해줘",
    height=160,
)

dbms = st.selectbox(
    "타겟 DBMS",
    ["TIBERO", "ORACLE", "POSTGRESQL", "MYSQL"],
)

run = st.button("🚀 실행")


if run:
    log = {
        "timestamp": now(),
        "sql_name": natural_text[:60],

        "canonical_sql": "",
        "tibero_sql": "",
        "oracle_sql": "",
        "postgresql_sql": "",
        "mysql_sql": "",

        "validation_ok": False,
        "validation_reasons": "",

        "exec_ran": False,
        "exec_success": False,
        "exec_row_count": None,
        "exec_error": "",

        "tokens_in": 0,
        "tokens_out": 0,
        "cost_usd": 0.0,

        "status": "running",
        "error": "",
    }

    if not natural_text.strip():
        st.warning("자연어 먼저 입력하세요.")
        st.stop()

    try:
        # ---------------------------------- 기본 SQL문 생성 ----------------------------------------------
        st.info("Canonical SQL 생성 중...")

        canon_prompt = prompt_nl_to_sql(natural_text)
        canonical_sql, _, _ = call_model(canon_prompt)

        canonical_sql = clean_sql(canonical_sql)

        st.subheader("📌 Canonical SQL")
        st.code(canonical_sql, language="sql")

        # ----------------------------- 생성한 기본 SQL문 검증 ----------------------------------------------
        st.info("Canonical 정적 검증 중...")

        ok, reasons = validate_canonical(canonical_sql)

        if not ok:
            st.error("🚫 Canonical SQL 검증 실패 (정적 분석)")
            for r in reasons:
                st.write(f"- {r}")
            st.stop()

        st.success("✔️ Canonical — 안전성 & 구조 검증 통과")

        # ------------------------------------ 타겟 DBMS로 변환 ---------------------------------------------
        st.info(f"{dbms} 변환 중...")

        conv_prompt = prompt_convert_sql(canonical_sql, dbms)
        target_sql, _, _ = call_model(conv_prompt)

        target_sql = clean_sql(target_sql)

        st.subheader(f"🎯 {dbms} SQL")
        st.code(target_sql, language="sql")

        # ---------------------------------------- LLM으로 의미 검증 ----------------------------------------
        st.info("Dialect 의미 검증 중...")

        dialects = {
            "tibero": target_sql if dbms == "TIBERO" else "",
            "oracle": target_sql if dbms == "ORACLE" else "",
            "postgresql": target_sql if dbms == "POSTGRESQL" else "",
            "mysql": target_sql if dbms == "MYSQL" else "",
        }

        validation = validate_with_llm(canonical_sql, dialects)

        if not validation.get("ok", False):
            st.error("❌ 변환된 SQL이 Canonical 의미와 일치하지 않거나 위험합니다.")
            st.write(validation.get("reasons"))
            st.stop()

        st.success("✔️ LLM 의미 검증 통과")

        # -------------------------------- 타겟 DBMS에서 직접 검증(임시) ------------------------------------
        st.info("DBMS 실행 검증 (Sandbox Hook)…")

        if dbms == "POSTGRESQL":
            ok, rows, err = run_postgres(target_sql)
        elif dbms == "MYSQL":
            ok, rows, err = run_mysql(target_sql)
        elif dbms == "ORACLE":
            ok, rows, err = run_oracle(target_sql)
        elif dbms == "TIBERO":
            ok, rows, err = run_tibero(target_sql)
        else:
            ok, rows, err = False, None, "sandbox not implemented"

        if err:
            st.warning(f"⚠️ 실행 검증 오류: {err}")
        elif ok:
            st.success(f"✔️ 실행 성공 — {rows} 행 조회")
        else:
            st.error("❌ 실행 실패")
            
    finally:
        log_row(list(log.values()))