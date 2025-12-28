"""
Health check endpoints for the API.

Provides:
- A database health check by inserting a sample company record.
- A Redis connection health check.
"""

from fastapi import FastAPI

from backend.utils.redis_client import redis_client
from db.repositories.company_repository import CompanyRepository

app = FastAPI()

sample = {
    "ticker": "AAPL",
    "name": "Apple Inc.",
    "incorporation": "USA",
    "sector": "Technology",
    "market_cap": 2_000_000_000_000,
}


@app.get("/health/db_redis/")
def health():
    """Health check: insert sample company and ping Redis."""
    try:
        # DB check
        repo = CompanyRepository()
        repo.create_company(sample)

        # Redis check
        redis_status = False
        if redis_client:
            redis_status = redis_client.ping()

        return {"status": "success", "redis": redis_status}
    except Exception as e:
        return {"status": "error", "details": str(e)}
