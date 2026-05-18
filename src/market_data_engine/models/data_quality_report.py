from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class DataQualityReport:
    asset_id: str
    missing_dates: tuple[date, ...] = field(default_factory=tuple)
    outlier_dates: tuple[date, ...] = field(default_factory=tuple)
    stale_dates: tuple[date, ...] = field(default_factory=tuple)