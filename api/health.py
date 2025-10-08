import redis
from fastapi import FastAPI, Request,APIRouter, Depends, HTTPException, status
from db.migrations.company_repository import CompanyRepository as CompanyRepo


app = FastAPI()
sample = {"ticker": "AAPL",
          "name": "Apple Inc.",
          "incorporation": "USA",
          "sector": "Technology",
          "market_cap": 2000000000000}


app.get("/health/")
async def health(test):
    try:
        await CompanyRepo().create_company(sample)
        redis_status = await redis.ping()
        return {"status": "success", "redis": redis_status}
    except Exception as e:
        return {"status": "error", "details": str(e)}.fetchall()