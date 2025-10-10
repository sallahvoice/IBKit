import redis
from fastapi import FastAPI, Request,APIRouter, Depends, HTTPException, status
from db.database import database 


app = FastAPI()
sample = {"ticker": "AAPL",
          "name": "Apple Inc.",
          "incorporation": "USA",
          "sector": "Technology",
          "market_cap": 2000000000000}


app.get("/health/")
def health(test):
    try:
        database().create_company(sample)
        redis_status = redis.ping()
        return {"status": "success", "redis": redis_status}
    except Exception as e:
        return {"status": "error", "details": str(e)}.fetchall()