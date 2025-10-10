from fastapi import APIRouter, Depends
from db.repositories.snapshot_repository import SnapshotRepository
from typing import Dict

snapshot_repo = SnapshotRepository()

router = APIRouter(prefix="/comparable")

router.post("/")
def read_snapshot(snapshot_data: Dict, repo: SnapshotRepository = Depends(lambda: snapshot_repo)):
    return repo.create_snapshot(snapshot_data)
#other endpoints can be added here as needed, such as fetching snapshots by ticker or date.