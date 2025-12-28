"""file that manages routes for comparable sets, get data by set id or ticker"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from db.repositories.company_repository import CompanyRepository

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


def read_comparable(
    comparable: ComparableSetCreate,
    repo: CompanyRepository = Depends(lambda: comparable_repo),
):  # pylint: disable=missing-function-docstring
    comparable_id = repo.create_comparable(comparable.dict())
    try:
        return {"id": comparable_id, "message": "Comparable company added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) # pylint: disable=raise-missing-from


@router.get("/set/{set_id}")
def get_comparables_for_set(
    set_id: int, repo: CompanyRepository = Depends(lambda: comparable_repo)
):  # pylint: disable=missing-function-docstring
    comparable = repo.get_comparables_for_set(set_id)
    try:
        return {"set_id": set_id, "comparables": comparable}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{ticker}")
def get_comparable_by_ticker(
    ticker: str, repo: CompanyRepository = Depends(lambda: comparable_repo)
):  # pylint: disable=missing-function-docstring
    comparable = repo.get_comparable_by_ticker(ticker)
    if not comparable:
        raise HTTPException(status_code=404, detail="Comparable company not found")
    return comparable
