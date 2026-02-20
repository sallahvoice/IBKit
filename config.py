import os

from dotenv import load_dotenv

load_dotenv()

# canonical key -> accepted env names (canonical first)
required_variables = {
    "FINANCIAL_PREP_API_KEY": ("FINANCIAL_PREP_API_KEY", "FINANCIAL-PREP-API-KEY"),
    "CURRENCY_API_KEY": (
        "CURRENCY_API_KEY",
        "CURRENCY-API-KEY",
        "CURRANCY-API-KEY",
    ),
    "POLYGON_API_KEY": ("POLYGON_API_KEY", "POLYGON-API-KEY"),
    "GEMINI_API_KEY": ("GEMINI_API_KEY", "GEMINI-API-KEY"),
    "DB_HOST": ("DB_HOST",),
    "DB_PORT": ("DB_PORT",),
    "DB_NAME": ("DB_NAME", "DB-NAME"),
    "DB_USER": ("DB_USER", "DB-USER"),
    "DB_PASSWORD": ("DB_PASSWORD",),
    "DB_POOL_SIZE": ("DB_POOL_SIZE",),
    "REDIS_HOST": ("REDIS_HOST", "REDIS-HOST"),
    "REDIS_PORT": ("REDIS_PORT", "REDIS-PORT"),
    "REDIS_DB": ("REDIS_DB", "REDIS-DB"),
    "REDIS_PASSWORD": ("REDIS_PASSWORD", "REDIS-PASSWORD"),
}

settings = {}
missing = []

for canonical_name, aliases in required_variables.items():
    value = None
    for env_name in aliases:
        value = os.getenv(env_name)
        if value is not None:
            break

    if value is None:
        missing.append(canonical_name)

    settings[canonical_name] = value

if missing:
    raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")
