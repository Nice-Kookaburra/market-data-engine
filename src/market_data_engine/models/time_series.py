from dataclasses import dataclass, field

from market_data_engine.models.asset import Asset
from market_data_engine.models.price_bar import Interval, PriceBar


@dataclass(frozen=True)
class TimeSeries:
    asset: Asset
    price_bars: tuple[PriceBar, ...] = field(default_factory=tuple)
    frequency: Interval = "1d"
