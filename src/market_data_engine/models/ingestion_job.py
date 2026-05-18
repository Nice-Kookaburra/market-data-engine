from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal


IngestionJobStatus = Literal["pending", "running", "completed", "failed"]


@dataclass(frozen=True)
class IngestionJob:
    job_id: str
    symbols: tuple[str, ...]
    start_date: date
    end_date: date
    status: IngestionJobStatus
    run_time: datetime | None = None