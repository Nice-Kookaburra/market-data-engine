from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class DataQualityReport:
    asset_id: str
    missing_dates: tuple[date, ...] = field(default_factory=tuple)
    duplicate_dates: tuple[date, ...] = field(default_factory=tuple)
    outlier_dates: tuple[date, ...] = field(default_factory=tuple)
    stale_dates: tuple[date, ...] = field(default_factory=tuple)
    validation_errors: tuple[str, ...] = field(default_factory=tuple)

    @property
    def has_issues(self) -> bool:
        return bool(
            self.missing_dates
            or self.duplicate_dates
            or self.outlier_dates
            or self.stale_dates
            or self.validation_errors
        )
