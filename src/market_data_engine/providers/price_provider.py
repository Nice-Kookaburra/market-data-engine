from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Iterable, List

from market_data_engine.models.price_bar import PriceBar, Interval


class PriceProvider(ABC):
    @abstractmethod
    def fetch(
        self,
        symbols: Iterable[str],
        start: date,
        end: date,
        interval: Interval = "1d",
    ) -> List[PriceBar]:
        """Return normalized PriceBars for all symbols in [start, end]."""
        raise NotImplementedError
