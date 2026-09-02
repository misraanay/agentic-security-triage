import uuid
from pydantic import BaseModel, AnyHttpUrl
from uuid import uuid4, UUID
from datetime import datetime as dt

class ScanRequest(BaseModel):
    url: AnyHttpUrl


class ScanResponse(BaseModel):
    scan_id: UUID
    status: str
    url: AnyHttpUrl
    created_at: dt
