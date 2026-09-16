from langgraph.graph import StateGraph

from app.models import Scan
from app.database import SessionLocal
from uuid import UUID
from app.celery_app import app
from app.models import Scan, ScanStatus, Finding
import os
import tempfile
import subprocess
import json
from app.agent.graph import security_graph, SecurityState

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
                result = subprocess.run(
                    ["semgrep", "--config=auto", "--json", tmpdir],
                    capture_output=True,
                    text=True
                )
                data = json.loads(result.stdout)
                findings = data["results"]
                saved_findings = []
                for finding in findings:
                    new_finding = Finding(
                        scan_id=scan_id,
                        check_id=finding["check_id"],
                        path=os.path.relpath(finding["path"], tmpdir),
                        start_line=finding["start"]["line"],
                        end_line=finding["end"]["line"],
                        message=finding["extra"]["message"],
                        severity=finding["extra"]["severity"],
                    )
                    db.add(new_finding)
                    saved_findings.append(new_finding)
                db.commit()

                for finding in saved_findings[:1]:
                    init_state = SecurityState(
                        scan_id=finding.scan_id,
                        finding_id=finding.finding_id,
                        repo_path=tmpdir,
                        analysis=None,
                        relevant_files=[],
                        patch=None,
                        validation_error=None,
                        validation_passed=None,
                        retry_count=0
                    )
                    result = security_graph.invoke(init_state)
                    print("LangGraph result:", result)
            except subprocess.CalledProcessError as e:
                success = False
        if success:
            scan.status = ScanStatus.COMPLETED
        else:
            scan.status = ScanStatus.FAILED
        db.commit()












