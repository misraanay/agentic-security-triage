import uuid
from pydantic import BaseModel, AnyHttpUrl
from uuid import UUID
from datetime import datetime as dt
from pydantic import ConfigDict

class ScanRequest(BaseModel):
    url: AnyHttpUrl


class ScanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    scan_id: UUID
    status: str
    url: AnyHttpUrl
    created_at: dt
