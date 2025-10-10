from fastapi import APIRouter, Depends, HTTPException
from db.repositories.comparable_repository import CompanyRepository
from typing import Dict
from pydantic import BaseModel

comparable_repo = CompanyRepository()

router = APIRouter(prefix="/comparable")

class ComparableSetCreate(BaseModel):
    ticker: str
    name: str
    forward_price_to_book: float
    forward_pe: float
    trailing_pe: float
    forward_price_to_sales: float
    trailing_ev_to_ebit: float
    trailing_ev_to_sales: float



router.post("/")
def read_comparable(comparable: ComparableSetCreate, repo: CompanyRepository = Depends(lambda: comparable_repo)):
    comparable_id = repo.create_comparable(comparable.dict())
    try:
        return {"id": comparable_id, "message": "Comparable company added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/set/{set_id}")
def get_comparables_for_set(set_id: int, repo: CompanyRepository = Depends(lambda: comparable_repo)):
    comparable = repo.get_comparables_for_set(set_id)
    try:
        return {"set_id": set_id, "comparables": comparable}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/{ticker}")
def get_comparable_by_ticker(ticker: str, repo: CompanyRepository = Depends(lambda: comparable_repo)):
    comparable = repo.get_comparable_by_ticker(ticker)
    if not comparable:
        raise HTTPException(status_code=404, detail="Comparable company not found")
    return comparable