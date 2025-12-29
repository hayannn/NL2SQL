import time
import random

from core.config import DAILY_TOKEN_LIMIT
from core.logger import write_header_if_needed, log_row, now
from core.transform import (
    build_transform_prompt,
    call_model,
    parse_dialect_json,
    calc_cost_usd
)
from core.validate import validate_with_llm
from core.execute import execute_safe_select


def load_canonical_sql():
    with open("sql/canonical.sql", "r", encoding="utf-8") as f:
        return [s.strip() for s in f.read().split(";") if s.strip()]


def main():
    write_header_if_needed()

    canonical_list = load_canonical_sql()
    canonical_list = canonical_list * 100   #  → 반복 = 호출 개수 증가

    total_tokens = 0

    for canonical in canonical_list:

        transform_prompt = build_transform_prompt(canonical)
        content, t_in, t_out = call_model(transform_prompt)

        dialects = parse_dialect_json(content)

        validation = validate_with_llm(canonical, dialects)

        validation_ok = validation.get("ok", False)
        reasons = "; ".join(validation.get("reasons", []))

        exec_ran = False
        exec_success = False
        exec_row_count = None
        exec_error = None

        if validation_ok:
            exec_success, exec_row_count, exec_error, exec_ran = \
                execute_safe_select(canonical)
        else:
            exec_error = f"VALIDATION_FAIL: {reasons}"

        cost = calc_cost_usd(t_in, t_out)
        tokens_used = t_in + t_out
        total_tokens += tokens_used

        log_row([
            now(),
            "canonical",
            canonical,
            dialects["tibero"],
            dialects["oracle"],
            dialects["postgresql"],
            dialects["mysql"],
            validation_ok,
            reasons,
            exec_ran,
            exec_success,
            exec_row_count,
            exec_error,
            t_in,
            t_out,
            cost,
            "OK" if validation_ok else "BLOCKED",
            ""
        ])

        print(f"[OK] tokens={tokens_used}, validated={validation_ok}")

        if total_tokens >= DAILY_TOKEN_LIMIT:
            print("Token limit reached — stopping")
            break

        time.sleep(4 + random.uniform(0, 2))


if __name__ == "__main__":
    main()