from dataclasses import dataclass
from datetime import date
from typing import Literal

Interval = Literal["1d", "1wk", "1mo"]

@dataclass(frozen=True)
class PriceBar:
    asset_id: str
    day: date
    interval: Interval
    open: float
    high: float
    low: float
    close: float
    adj_close: float | None = None
    volume: float | None = None
    currency: str | None = None