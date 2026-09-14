from app.models import Scan
from app.database import SessionLocal
from uuid import UUID
from app.celery_app import app
from app.models import ScanStatus
import os
import tempfile
import subprocess

@app.task()
def process_scan(scan_id: UUID):
    with SessionLocal() as db:
        #set session status as complete
        scan = db.get(Scan, scan_id)
        if scan is None:
            raise ValueError(f"Scan {scan_id} not found")
        scan.status = ScanStatus.RUNNING
        db.commit()
        url = scan.url
        success = True
        # background logic git clone into a temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            try:
                subprocess.run(["git", "clone", "--depth", "1", url, tmpdir], check=True)
            except subprocess.CalledProcessError as e:
                success = False
        if success:
            scan.status = ScanStatus.COMPLETED
        else:
            scan.status = ScanStatus.FAILED
        db.commit()












