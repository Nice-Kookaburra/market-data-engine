from __future__ import annotations

import math
from datetime import date
from typing import Iterable

from market_data_engine.models.data_quality_report import DataQualityReport
from market_data_engine.models.price_bar import Interval, PriceBar
from market_data_engine.services.calculations import comparable_price, simple_returns
from market_data_engine.services.validation import (
    find_duplicate_bars,
    find_missing_weekdays,
    validate_price_bar,
)


def find_duplicate_dates(
    bars: Iterable[PriceBar],
    asset_id: str,
    *,
    interval: Interval = "1d",
) -> tuple[date, ...]:
    seen_keys: set[tuple[str, Interval, date]] = set()
    duplicate_days: list[date] = []

    for bar in bars:
        if bar.asset_id != asset_id or bar.interval != interval:
            continue
        key = (bar.asset_id, bar.interval, bar.day)
        if key in seen_keys:
            duplicate_days.append(bar.day)
        seen_keys.add(key)

    return tuple(sorted(set(duplicate_days)))


def collect_validation_errors(
    bars: Iterable[PriceBar],
    asset_id: str,
    *,
    interval: Interval = "1d",
) -> tuple[str, ...]:
    errors: list[str] = []
    for bar in bars:
        if bar.asset_id == asset_id and bar.interval == interval:
            errors.extend(validate_price_bar(bar))
    return tuple(errors)


def find_stale_dates(
    bars: Iterable[PriceBar],
    asset_id: str,
    end: date,
    *,
    interval: Interval = "1d",
    max_lag_days: int = 5,
) -> tuple[date, ...]:
    asset_bars = [bar for bar in bars if bar.asset_id == asset_id and bar.interval == interval]
    if not asset_bars or max_lag_days < 0:
        return ()

    last_day = max(bar.day for bar in asset_bars)
    if (end - last_day).days > max_lag_days:
        return (last_day,)
    return ()


def find_outlier_dates(
    bars: Iterable[PriceBar],
    asset_id: str,
    *,
    interval: Interval = "1d",
    std_multiplier: float = 3.0,
    min_returns: int = 5,
) -> tuple[date, ...]:
    if std_multiplier <= 0 or min_returns < 2:
        return ()

    asset_bars = sorted(
        (bar for bar in bars if bar.asset_id == asset_id and bar.interval == interval),
        key=lambda bar: bar.day,
    )
    if len(asset_bars) < min_returns:
        return ()

    prices = [comparable_price(bar) for bar in asset_bars]
    returns = simple_returns(prices)
    if len(returns) < 2:
        return ()

    mean = sum(returns) / len(returns)
    variance = sum((value - mean) ** 2 for value in returns) / (len(returns) - 1)
    std = math.sqrt(variance)
    if std == 0:
        return ()

    outlier_days: list[date] = []
    for bar, return_value in zip(asset_bars[1:], returns):
        if abs(return_value - mean) > std_multiplier * std:
            outlier_days.append(bar.day)
    return tuple(outlier_days)


def build_data_quality_report(
    asset_id: str,
    bars: Iterable[PriceBar],
    start: date,
    end: date,
    *,
    interval: Interval = "1d",
    max_lag_days: int = 5,
    outlier_std_multiplier: float = 3.0,
) -> DataQualityReport:
    bars_list = list(bars)
    return DataQualityReport(
        asset_id=asset_id,
        missing_dates=find_missing_weekdays(
            bars_list,
            start,
            end,
            asset_id=asset_id,
            interval=interval,
        ),
        duplicate_dates=find_duplicate_dates(bars_list, asset_id, interval=interval),
        outlier_dates=find_outlier_dates(
            bars_list,
            asset_id,
            interval=interval,
            std_multiplier=outlier_std_multiplier,
        ),
        stale_dates=find_stale_dates(
            bars_list,
            asset_id,
            end,
            interval=interval,
            max_lag_days=max_lag_days,
        ),
        validation_errors=collect_validation_errors(bars_list, asset_id, interval=interval),
    )


def build_data_quality_reports(
    bars: Iterable[PriceBar],
    start: date,
    end: date,
    *,
    interval: Interval = "1d",
    asset_ids: Iterable[str] | None = None,
    max_lag_days: int = 5,
    outlier_std_multiplier: float = 3.0,
) -> list[DataQualityReport]:
    bars_list = list(bars)
    if asset_ids is None:
        ids = sorted({bar.asset_id for bar in bars_list if bar.interval == interval})
    else:
        ids = sorted(set(asset_ids))

    return [
        build_data_quality_report(
            asset_id,
            bars_list,
            start,
            end,
            interval=interval,
            max_lag_days=max_lag_days,
            outlier_std_multiplier=outlier_std_multiplier,
        )
        for asset_id in ids
    ]


def assess_data_quality(
    bars: Iterable[PriceBar],
    start: date,
    end: date,
    *,
    interval: Interval = "1d",
    asset_ids: Iterable[str] | None = None,
    max_lag_days: int = 5,
    outlier_std_multiplier: float = 3.0,
) -> list[DataQualityReport]:
    """Build per-asset quality reports for soft diagnostics (does not raise)."""
    return build_data_quality_reports(
        bars,
        start,
        end,
        interval=interval,
        asset_ids=asset_ids,
        max_lag_days=max_lag_days,
        outlier_std_multiplier=outlier_std_multiplier,
    )
