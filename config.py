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


def _getenv_with_fallback(variable: str) -> str | None:
    """Read env vars using original key and '-'/'_' fallback variant."""
    value = os.getenv(variable)
    if value is not None:
        return value

    fallback = variable.replace("-", "_") if "-" in variable else variable.replace("_", "-")
    return os.getenv(fallback)


settings = {}

missing = []

for variable in required_variables:
    value = _getenv_with_fallback(variable)
    if value is None:
        missing.append(variable)
    settings[variable] = value

if missing:
    raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")
