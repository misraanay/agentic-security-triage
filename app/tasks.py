from app.celery_app import app as celery_app
from app.models import Scan
from app.database import SessionLocal
from uuid import UUID
from app.celery_app import app
from app.models import ScanStatus

@app.task()
def process_scan(scan_id: UUID):
    with SessionLocal() as db:
        #set session status as complete
        scan = db.get(Scan, scan_id)

        if scan is None:
            raise ValueError(f"Scan {scan_id} not found")

        scan.status = ScanStatus.RUNNING
        db.commit()

        # background logic call delay for 5 seconds
        import time
        time.sleep(60)

        success = True
        if success:
            scan.status = ScanStatus.COMPLETED
        else:
            scan.status = ScanStatus.FAILED
        db.commit()












