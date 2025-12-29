import json
import requests
from typing import Dict, Tuple
# from .config import MODEL, HEADERS, PRICE_INPUT_PER_1K, PRICE_OUTPUT_PER_1K #GPT용
from core.config import CLOVA_URL, HEADERS, HCX_API_KEY

def build_transform_prompt(canonical_sql: str) -> str:
    return f"""
Convert canonical SQL to dialects (TIBERO, ORACLE, POSTGRESQL, MYSQL)

Canonical SQL:

```sql
{canonical_sql}
Rules:

Keep the same semantics across all dialects.

Do not include trailing semicolons.

Use only functions supported by each DB.

Do NOT use reserved words (like DATE) as aliases in Oracle/Tibero.

Oracle/Tibero:

No LIMIT. Use FETCH FIRST n ROWS ONLY if needed.

Dates: use SYSDATE and arithmetic (SYSDATE - 7).

PostgreSQL:

Use CURRENT_DATE instead of SYSDATE.

MySQL:

Use CURDATE().

Output JSON EXACTLY in this format:

{{
"tibero": "<sql>",
"oracle": "<sql>",
"postgresql": "<sql>",
"mysql": "<sql>"
}}
""".strip()

# # call_model for gpt
# def call_model(prompt: str) -> Tuple[str, int, int]:
#     resp = requests.post(
#         "https://api.openai.com/v1/chat/completions",
#         headers=HEADERS,
#         json={
#             "model": MODEL,
#             "messages": [
#             {"role": "system", "content": "JSON only"},
#             {"role": "user", "content": prompt}
#             ],
#             "temperature": 0.1
#         },
#         timeout=60
#     )

#     data = resp.json()
#     content = data["choices"][0]["message"]["content"]
#     usage = data.get("usage", {})
#     return content, usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)
# # --------------------------------------------------------------------------------------------------

def call_model(prompt: str) -> Tuple[str, int, int]:
    payload = {
        "messages": [
            {
                "role": "system",
                "content": [
                    {"type": "text", "text": "JSON only"}
                ],
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt}
                ],
            },
        ],
        "topP": 0.8,
        "topK": 0,
        "maxTokens": 512,
        "temperature": 0.5,
        "repetitionPenalty": 1.1,
        "stop": [],
        "seed": 0,
        "includeAiFilters": True,
    }

    resp = requests.post(
        CLOVA_URL,
        headers=HEADERS,
        json=payload,
        timeout=60,
    )

    print("STATUS =", resp.status_code)
    print("RAW TEXT (앞 400자) =", resp.text[:400])

    resp.raise_for_status()
    data = resp.json()

    result = data.get("result", {})
    message = result.get("message", {})
    content = message.get("content", "")

    text = ""

    if isinstance(content, str):
        text = content
    elif isinstance(content, list):
        parts = []
        for c in content:
            if not isinstance(c, dict):
                continue
            if c.get("type") == "text":
                parts.append(c.get("text", ""))
        text = "".join(parts)

    if not text:
        print("DEBUG FULL DATA =", json.dumps(data, ensure_ascii=False)[:800])

    usage = data.get("usage", {})
    t_in = usage.get("inputTokens", 0)
    t_out = usage.get("outputTokens", 0)

    return text, t_in, t_out


def parse_dialect_json(text: str) -> Dict[str, str]:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()[1:-1]
        text = "\n".join(lines)

    data = json.loads(text)

    return {
        "tibero": data.get("tibero", ""),
        "oracle": data.get("oracle", ""),
        "postgresql": data.get("postgresql", ""),
        "mysql": data.get("mysql", "")
    }

# GPT용
# def calc_cost_usd(t_in: int, t_out: int) -> float:
#     return round((t_in / 1000) * PRICE_INPUT_PER_1K + (t_out / 1000) * PRICE_OUTPUT_PER_1K, 6)