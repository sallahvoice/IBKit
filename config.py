import os
from dotenv import load_dotenv

load_dotenv()

required_variables = [
    "FINANCIAL-PREP-API-KEY",
    "CURRANCY-API-KEY",
    "POLYGON-API-KEY",
    "GEMINI-API-KEY",

    "DB_HOST",
    "DB_PORT",
    "DB-NAME",
    "DB-USER",
    "DB_PASSWORD",
    "DB_POOL_SIZE",

    "REDIS-HOST",
    "REDIS-PORT",
    "REDIS-DB",
    "REDIS-PASSWORD",
]

settings = {}

missing = []

for variable in required_variables:
    value = os.getenv(variable)
    if value is None:
        missing.append(variable)
    settings[variable] = value

if missing:
    raise RuntimeError(f"Missing environment variables: {", ".join(missing)}")