from __future__ import annotations

import math
from datetime import date
from typing import Iterable

from market_data_engine.models.price_bar import PriceBar


class CalculationError(ValueError):
    """Raised when a price series cannot be calculated safely."""


def _require_positive_window(window: int) -> None:
    if window < 1:
        raise ValueError("window must be at least 1")


def _sorted_bars(bars: Iterable[PriceBar]) -> list[PriceBar]:
    return sorted(bars, key=lambda bar: bar.day)


def _sample_std(values: list[float]) -> float:
    if len(values) < 2:
        raise CalculationError("need at least 2 values for sample standard deviation")

    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
    return math.sqrt(variance)


def comparable_price(bar: PriceBar) -> float:
    """Return adjusted close when available, otherwise close."""
    if bar.adj_close is not None:
        return bar.adj_close
    return bar.close


def price_series(bars: Iterable[PriceBar]) -> list[float]:
    """Extract comparable prices from bars sorted by day."""
    return [comparable_price(bar) for bar in _sorted_bars(bars)]


def bar_dates(bars: Iterable[PriceBar]) -> list[date]:
    """Return bar dates in the same order as price_series()."""
    return [bar.day for bar in _sorted_bars(bars)]


def simple_returns(prices: Iterable[float]) -> list[float]:
    """Compute (P_t / P_{t-1}) - 1 for consecutive prices."""
    price_list = list(prices)
    if len(price_list) < 2:
        return []

    returns: list[float] = []
    for index in range(1, len(price_list)):
        previous = price_list[index - 1]
        current = price_list[index]
        if previous == 0:
            raise CalculationError(
                f"previous price cannot be zero at index {index - 1}"
            )
        returns.append(current / previous - 1)
    return returns


def log_returns(prices: Iterable[float]) -> list[float]:
    """Compute ln(P_t / P_{t-1}) for consecutive prices."""
    price_list = list(prices)
    if len(price_list) < 2:
        return []

    returns: list[float] = []
    for index in range(1, len(price_list)):
        previous = price_list[index - 1]
        current = price_list[index]
        if previous <= 0 or current <= 0:
            raise CalculationError(
                f"prices must be positive for log returns at index {index - 1}"
            )
        returns.append(math.log(current / previous))
    return returns


def rolling_mean(values: Iterable[float], window: int) -> list[float | None]:
    """Compute a simple moving average over a fixed window size."""
    _require_positive_window(window)
    value_list = list(values)
    if not value_list:
        return []

    result: list[float | None] = [None] * (window - 1)
    for index in range(window - 1, len(value_list)):
        chunk = value_list[index - window + 1 : index + 1]
        result.append(sum(chunk) / window)
    return result


def rolling_volatility(returns: Iterable[float], window: int) -> list[float | None]:
    """Compute rolling sample standard deviation of returns."""
    _require_positive_window(window)
    return_list = list(returns)
    if not return_list:
        return []
    if window < 2:
        raise ValueError("window must be at least 2 for volatility")

    result: list[float | None] = [None] * (window - 1)
    for index in range(window - 1, len(return_list)):
        chunk = return_list[index - window + 1 : index + 1]
        result.append(_sample_std(chunk))
    return result


def annualized_volatility(
    returns: Iterable[float],
    window: int,
    *,
    periods_per_year: int = 252,
) -> list[float | None]:
    """Annualize rolling volatility using sqrt(periods_per_year)."""
    if periods_per_year < 1:
        raise ValueError("periods_per_year must be at least 1")

    scale = math.sqrt(periods_per_year)
    return [
        value * scale if value is not None else None
        for value in rolling_volatility(returns, window)
    ]


def simple_returns_from_bars(bars: Iterable[PriceBar]) -> list[float]:
    """Compute simple returns from comparable bar prices."""
    return simple_returns(price_series(bars))


def log_returns_from_bars(bars: Iterable[PriceBar]) -> list[float]:
    """Compute log returns from comparable bar prices."""
    return log_returns(price_series(bars))


def rolling_mean_from_bars(bars: Iterable[PriceBar], window: int) -> list[float | None]:
    """Compute a rolling mean of comparable bar prices."""
    return rolling_mean(price_series(bars), window)


def rolling_volatility_from_bars(
    bars: Iterable[PriceBar],
    window: int,
    *,
    use_log_returns: bool = True,
) -> list[float | None]:
    """Compute rolling volatility from bar returns."""
    prices = price_series(bars)
    if use_log_returns:
        returns = log_returns(prices)
    else:
        returns = simple_returns(prices)
    return rolling_volatility(returns, window)
