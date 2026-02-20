import os

from dotenv import load_dotenv

load_dotenv()

required_variables = {
    "FINANCIAL-PREP-API-KEY": ("FINANCIAL-PREP-API-KEY",),
    "CURRANCY-API-KEY": ("CURRANCY-API-KEY",),
    "POLYGON-API-KEY": ("POLYGON-API-KEY", "POLYGON_API_KEY"),
    "GEMINI-API-KEY": ("GEMINI-API-KEY",),
    "DB_HOST": ("DB_HOST",),
    "DB_PORT": ("DB_PORT",),
    "DB-NAME": ("DB-NAME", "DB_NAME"),
    "DB-USER": ("DB-USER", "DB_USER"),
    "DB_PASSWORD": ("DB_PASSWORD",),
    "DB_POOL_SIZE": ("DB_POOL_SIZE",),
    "REDIS-HOST": ("REDIS-HOST", "REDIS_HOST"),
    "REDIS-PORT": ("REDIS-PORT", "REDIS_PORT"),
    "REDIS-DB": ("REDIS-DB", "REDIS_DB"),
    "REDIS-PASSWORD": ("REDIS-PASSWORD", "REDIS_PASSWORD"),
}

settings = {}

missing = []

for variable, aliases in required_variables.items():
    value = next((os.getenv(alias) for alias in aliases if os.getenv(alias) is not None), None)
    if value is None:
        missing.append(variable)
    settings[variable] = value

if missing:
    raise RuntimeError(f"Missing environment variables: {", ".join(missing)}")
