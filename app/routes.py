from fastapi import APIRouter
from app.schemas import ScanRequest, ScanResponse
from uuid import UUID, uuid4
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Scan, ScanStatus

router = APIRouter()

@router.post("/scan", response_model=ScanResponse)
async def scan(scan: ScanRequest, db: Session = Depends(get_db)):
    new_scan = Scan(url = scan.url)
    db.add(new_scan)
    db.commit()
    db.refresh(new_scan)
    return new_scan

@router.get("/scan/{scan_id}", response_model=ScanResponse)
async def get_scan(scan_id: UUID, db: Session = Depends(get_db)):
    scan_id = db.query(Scan).filter(Scan.scan_id == scan_id).first()
    if not scan_id:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scan_id


