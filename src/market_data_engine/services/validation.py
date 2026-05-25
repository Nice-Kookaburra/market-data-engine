from __future__ import annotations

from datetime import date, timedelta
from typing import Iterable

from market_data_engine.models.price_bar import Interval, PriceBar


class PriceValidationError(ValueError):
    def __init__(self, errors: Iterable[str]):
        self.errors = tuple(errors)
        message = "Invalid price data: " + "; ".join(self.errors)
        super().__init__(message)


def validate_price_bar(bar: PriceBar) -> list[str]:
    errors: list[str] = []

    if not bar.asset_id.strip():
        errors.append(f"asset_id is required for bar on {bar.day}")

    required_price_fields = {
        "open": bar.open,
        "high": bar.high,
        "low": bar.low,
        "close": bar.close,
    }

    for field_name, value in required_price_fields.items():
        if value is None:
            errors.append(f"{field_name} is required for {bar.asset_id} on {bar.day}")
        elif value < 0:
            errors.append(f"{field_name} cannot be negative for {bar.asset_id} on {bar.day}")

    if bar.adj_close is not None and bar.adj_close < 0:
        errors.append(f"adj_close cannot be negative for {bar.asset_id} on {bar.day}")

    if bar.volume is not None and bar.volume < 0:
        errors.append(f"volume cannot be negative for {bar.asset_id} on {bar.day}")

    if any(value is None for value in required_price_fields.values()):
        return errors

    if bar.high < bar.low:
        errors.append(f"high must be greater than or equal to low for {bar.asset_id} on {bar.day}")

    if not bar.low <= bar.open <= bar.high:
        errors.append(f"open must be between low and high for {bar.asset_id} on {bar.day}")

    if not bar.low <= bar.close <= bar.high:
        errors.append(f"close must be between low and high for {bar.asset_id} on {bar.day}")

    if bar.adj_close is not None and not bar.low <= bar.adj_close <= bar.high:
        errors.append(
            f"adj_close must be between low and high for {bar.asset_id} on {bar.day}"
        )

    return errors


def find_duplicate_bars(bars: Iterable[PriceBar]) -> list[str]:
    errors: list[str] = []
    seen_keys: set[tuple[str, Interval, date]] = set()

    for bar in bars:
        key = (bar.asset_id, bar.interval, bar.day)
        if key in seen_keys:
            errors.append(
                f"duplicate price bar for asset={bar.asset_id}, "
                f"interval={bar.interval}, day={bar.day.isoformat()}"
            )
        seen_keys.add(key)

    return errors


def iter_weekdays(start: date, end: date) -> Iterable[date]:
    current = start
    while current <= end:
        if current.weekday() < 5:
            yield current
        current += timedelta(days=1)


def find_missing_weekdays(
    bars: Iterable[PriceBar],
    start: date,
    end: date,
    *,
    asset_id: str | None = None,
    interval: Interval = "1d",
) -> tuple[date, ...]:
    if interval != "1d" or start > end:
        return ()

    present_days = {
        bar.day
        for bar in bars
        if bar.interval == interval and (asset_id is None or bar.asset_id == asset_id)
    }
    missing = [day for day in iter_weekdays(start, end) if day not in present_days]
    return tuple(missing)


def find_missing_weekdays_by_asset(
    bars: Iterable[PriceBar],
    start: date,
    end: date,
    *,
    interval: Interval = "1d",
) -> dict[str, tuple[date, ...]]:
    bars_list = list(bars)
    asset_ids = {bar.asset_id for bar in bars_list if bar.interval == interval}

    return {
        asset: find_missing_weekdays(
            bars_list,
            start,
            end,
            asset_id=asset,
            interval=interval,
        )
        for asset in sorted(asset_ids)
    }


def validate_missing_weekdays(
    bars: Iterable[PriceBar],
    start: date,
    end: date,
    *,
    interval: Interval = "1d",
) -> list[str]:
    if interval != "1d":
        return []

    errors: list[str] = []
    for asset_id, missing_dates in find_missing_weekdays_by_asset(
        bars,
        start,
        end,
        interval=interval,
    ).items():
        for missing_day in missing_dates:
            errors.append(
                f"missing daily bar for asset={asset_id} on {missing_day.isoformat()}"
            )
    return errors


def validate_bars(
    bars: Iterable[PriceBar],
    *,
    start: date | None = None,
    end: date | None = None,
    check_missing_weekdays: bool = False,
) -> None:
    bars_list = list(bars)
    errors: list[str] = []

    for bar in bars_list:
        errors.extend(validate_price_bar(bar))
    errors.extend(find_duplicate_bars(bars_list))

    if check_missing_weekdays and start is not None and end is not None:
        errors.extend(validate_missing_weekdays(bars_list, start, end))

    if errors:
        raise PriceValidationError(errors)
