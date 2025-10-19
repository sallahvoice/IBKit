from fastapi import APIRouter, Depends, HTTPException
from db.repositories.snpashot_repository import SnapshotRepository
from pydantic import BaseModel

snapshot_repo = SnapshotRepository()

router = APIRouter(prefix="/comparable")

class SnapshotCreate(BaseModel):
    
    company_id: int
    snapshot_date: str  # YYYY-MM-DD
    marginal_tax_rate: float

    last_annual_revenue: float 
    last_annual_ebit: float 
    last_annual_net_income: float 
    last_annual_interest_expense: float 
    last_annual_tax_paid: float 
    trailing_sales: float 
    trailing_ebit: float 

    last_annual_debt: float 
    last_annual_cash: float 
    last_annual_equity: float 

    last_annual_capex: float 
    last_annual_chng_wc: float 
    last_annual_da: float 

    market_cap: float 
    current_shares_outstanding: float 
    current_beta: float 


router.post("/")
def read_snapshot(snapshot: SnapshotCreate, repo: SnapshotRepository = Depends(lambda: snapshot_repo)):
    snapshot_id = repo.create_snapshot(snapshot)
    try:
        return {"id": snapshot_id, "message": "Snapshot added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{company_id}")
def get_latest_snapshot(company_id: int, repo: SnapshotRepository = Depends(lambda: snapshot_repo)):
    snapshot = repo.get_latest_snapshot(company_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    return snapshot

@router.get("/date/{company_id}/{snapshot_date}")
def get_snapshot_by_date(company_id: str, snapshot_date: str, repo: SnapshotRepository = Depends(lambda: snapshot_repo)):
    snapshot = repo.get_snapshot_by_date(company_id, snapshot_date)
    if not snapshot:
        raise HTTPException(status_code=404, detail="snapshot not found for this date")
    return snapshot