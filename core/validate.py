import json
from typing import Dict
from .transform import call_model


def build_validator_prompt(canonical_sql: str, dialects: Dict[str, str]) -> str:
    return f"""
Validate safety + semantic match.

Canonical:
{canonical_sql}

TIBERO:
{dialects['tibero']}

ORACLE:
{dialects['oracle']}

POSTGRESQL:
{dialects['postgresql']}

MYSQL:
{dialects['mysql']}

Check:
- SELECT only
- no destructive ops
- semantics match

Return JSON:

{{
  "ok": true,
  "reasons": ["..."]
}}
""".strip()



def validate_with_llm(canonical_sql: str, dialects: Dict[str, str]):
    prompt = build_validator_prompt(canonical_sql, dialects)
    content, _, _ = call_model(prompt)

    text = content.strip()
    if text.startswith("```"):
        text = "\n".join(text.splitlines()[1:-1])

    return json.loads(text)