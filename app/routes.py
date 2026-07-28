from fastapi import APIRouter
from app.schemas import ScanRequest, ScanResponse
from uuid import UUID, uuid4
from fastapi import HTTPException

router = APIRouter()

scans = {}

@router.post("/scan", response_model=ScanResponse)
async def scan(scan: ScanRequest):
    scan_id = uuid4()
    scans[scan_id] = {
        "scan_id": scan_id,
        "scan_completion_status": "queued",
        "scan_url": scan.url,
    }
    return scans[scan_id]

@router.get("/scan/{scan_id}", response_model=ScanResponse)
async def get_scan(scan_id: UUID):
    if scan_id not in scans:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scans[scan_id]
