import uuid
from pydantic import BaseModel, AnyHttpUrl
from uuid import uuid4, UUID

class ScanRequest(BaseModel):
    url: AnyHttpUrl


class ScanResponse(BaseModel):
    scan_id: UUID
    scan_completion_status: str = "queued"
    scan_url: AnyHttpUrl