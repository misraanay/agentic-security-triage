from app.database import Base
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
import datetime as dt
from uuid import UUID, uuid4

from enum import Enum

class ScanStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class Scan(Base):
    __tablename__ = "scans"
    scan_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    status: Mapped[ScanStatus] = mapped_column(sa.Enum(ScanStatus), nullable=False, default=ScanStatus.QUEUED)
    url: Mapped[str] = mapped_column(sa.String, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now()
     )

Base.metadata.create_all(bind=engine)

