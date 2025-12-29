# # for gpt
# import os
# from dotenv import load_dotenv

# load_dotenv()

# API_KEY = os.getenv("OPENAI_API_KEY")
# MODEL = os.getenv("MODEL", "gpt-5.2")
# DAILY_TOKEN_LIMIT = int(os.getenv("DAILY_LIMIT_TOKENS", 500000))

# PRICE_INPUT_PER_1K = float(os.getenv("PRICE_INPUT_PER_1K", "0.0"))
# PRICE_OUTPUT_PER_1K = float(os.getenv("PRICE_OUTPUT_PER_1K", "0.0"))

# DB_PATH = os.getenv("DB_PATH")
# OUTPUT_FILE = "sql_transform_logs.csv"

# HEADERS = {
#     "Authorization": f"Bearer {API_KEY}",
#     "Content-Type": "application/json"
# }

# TARGET_DBMS = ["TIBERO", "ORACLE", "POSTGRESQL", "MYSQL"]
# # -------------------------------------------------------------------------------------------

# core/config.py

import os
import uuid
from dotenv import load_dotenv

load_dotenv()

# =========================
# CLOVA (HCX-005)
# =========================
CLOVA_URL = os.getenv("CLOVA_URL")
HCX_API_KEY = os.getenv("HCX_API_KEY")

HEADERS = {
    "Authorization": f"Bearer {HCX_API_KEY}",
    "X-NCP-CLOVASTUDIO-REQUEST-ID": str(uuid.uuid4()),
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# =========================
# RUNTIME SETTINGS
# =========================
DAILY_TOKEN_LIMIT = int(os.getenv("DAILY_LIMIT_TOKENS", 500000))
PRICE_INPUT_PER_1K = float(os.getenv("PRICE_INPUT_PER_1K", "0.0"))
PRICE_OUTPUT_PER_1K = float(os.getenv("PRICE_OUTPUT_PER_1K", "0.0"))

DB_PATH = os.getenv("DB_PATH")
OUTPUT_FILE = "/home/dlgkd/dev2/NL2SQL/log/sql_transform_logs.csv"
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

TARGET_DBMS = ["TIBERO", "ORACLE", "POSTGRESQL", "MYSQL"]