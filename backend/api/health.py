import redis
from fastapi import FastAPI

from db.database import database

app = FastAPI()
sample = {
    "ticker": "AAPL",
    "name": "Apple Inc.",
    "incorporation": "USA",
    "sector": "Technology",
    "market_cap": 2000000000000,
}


app.get("/health/")


def health():
    try:
        database.create_company(sample)
        redis_status = redis.ping()
        return {"status": "success", "redis": redis_status}
    except Exception as e:
        return {"status": "error", "details": str(e)}.fetchall()
