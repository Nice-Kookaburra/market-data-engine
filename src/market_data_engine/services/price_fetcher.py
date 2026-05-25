from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable, List, Protocol

from market_data_engine.models.data_quality_report import DataQualityReport
from market_data_engine.models.price_bar import Interval, PriceBar
from market_data_engine.providers.price_provider import PriceProvider
from market_data_engine.services.data_quality import assess_data_quality
from market_data_engine.services.validation import validate_bars


class PriceRepositoryLike(Protocol):
    def upsert_prices(self, bars: Iterable[PriceBar]) -> int:
        """Persist price bars and return the number of affected rows."""


@dataclass(frozen=True)
class FetchResult:
    bars: tuple[PriceBar, ...]
    quality_reports: tuple[DataQualityReport, ...]


@dataclass(frozen=True)
class PriceFetcher:
    """Coordinate provider fetches, validation, and optional persistence."""

    provider: PriceProvider
    repository: PriceRepositoryLike | None = None

    def fetch_prices(
        self,
        symbols: Iterable[str],
        start: date,
        end: date,
        interval: Interval = "1d",
        persist: bool = False,
        *,
        check_missing_weekdays: bool = False,
        include_quality_report: bool = False,
    ) -> List[PriceBar] | FetchResult:
        symbol_list = list(symbols)
        if not symbol_list:
            if include_quality_report:
                return FetchResult(bars=(), quality_reports=())
            return []
        if start > end:
            raise ValueError("start must be before or equal to end")

        bars = self.provider.fetch(
            symbols=symbol_list,
            start=start,
            end=end,
            interval=interval,
        )
        validate_bars(
            bars,
            start=start,
            end=end,
            check_missing_weekdays=check_missing_weekdays,
        )

        clean_bars = sorted(bars, key=lambda b: (b.asset_id, b.interval, b.day))
        if persist:
            if self.repository is None:
                raise ValueError("repository is required when persist=True")
            self.repository.upsert_prices(clean_bars)

        if include_quality_report:
            reports = assess_data_quality(
                clean_bars,
                start,
                end,
                interval=interval,
                asset_ids=symbol_list,
            )
            return FetchResult(
                bars=tuple(clean_bars),
                quality_reports=tuple(reports),
            )

        return clean_bars

    def fetch_price_history(
        self,
        symbol: str,
        start: date,
        end: date,
        interval: Interval = "1d",
        persist: bool = False,
        *,
        check_missing_weekdays: bool = False,
        include_quality_report: bool = False,
    ) -> List[PriceBar] | FetchResult:
        return self.fetch_prices(
            symbols=[symbol],
            start=start,
            end=end,
            interval=interval,
            persist=persist,
            check_missing_weekdays=check_missing_weekdays,
            include_quality_report=include_quality_report,
        )
