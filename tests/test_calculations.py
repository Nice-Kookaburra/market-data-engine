import math
from datetime import date
from unittest import TestCase

from market_data_engine.models.price_bar import PriceBar
from market_data_engine.services.calculations import (
    CalculationError,
    annualized_volatility,
    bar_dates,
    comparable_price,
    log_returns,
    log_returns_from_bars,
    price_series,
    rolling_mean,
    rolling_mean_from_bars,
    rolling_volatility,
    rolling_volatility_from_bars,
    simple_returns,
    simple_returns_from_bars,
)


def _bar(day: date, close: float, adj_close: float | None = None) -> PriceBar:
    return PriceBar(
        asset_id="AAPL",
        day=day,
        interval="1d",
        open=close,
        high=close,
        low=close,
        close=close,
        adj_close=adj_close,
    )


class CalculationTests(TestCase):
    def test_comparable_price_prefers_adjusted_close(self) -> None:
        bar = _bar(date(2024, 1, 2), close=100.0, adj_close=95.0)
        self.assertEqual(comparable_price(bar), 95.0)

    def test_comparable_price_falls_back_to_close(self) -> None:
        bar = _bar(date(2024, 1, 2), close=100.0)
        self.assertEqual(comparable_price(bar), 100.0)

    def test_price_series_sorts_bars_by_day(self) -> None:
        bars = [
            _bar(date(2024, 1, 3), close=102.0),
            _bar(date(2024, 1, 1), close=100.0),
            _bar(date(2024, 1, 2), close=105.0, adj_close=101.0),
        ]

        self.assertEqual(price_series(bars), [100.0, 101.0, 102.0])
        self.assertEqual(
            bar_dates(bars),
            [date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3)],
        )

    def test_simple_returns(self) -> None:
        returns = simple_returns([100.0, 105.0, 102.0])
        self.assertAlmostEqual(returns[0], 0.05)
        self.assertAlmostEqual(returns[1], 102.0 / 105.0 - 1)
        self.assertEqual(simple_returns([100.0]), [])
        self.assertEqual(simple_returns([]), [])

    def test_simple_returns_rejects_zero_previous_price(self) -> None:
        with self.assertRaises(CalculationError):
            simple_returns([0.0, 10.0])

    def test_log_returns(self) -> None:
        returns = log_returns([100.0, 105.0])
        self.assertAlmostEqual(returns[0], math.log(105.0 / 100.0))

    def test_log_returns_rejects_non_positive_prices(self) -> None:
        with self.assertRaises(CalculationError):
            log_returns([100.0, 0.0])

    def test_rolling_mean(self) -> None:
        self.assertEqual(
            rolling_mean([1.0, 2.0, 3.0, 4.0], window=2),
            [None, 1.5, 2.5, 3.5],
        )

    def test_rolling_volatility(self) -> None:
        returns = [0.01, -0.02, 0.03, 0.0]
        values = rolling_volatility(returns, window=2)

        self.assertIsNone(values[0])
        self.assertAlmostEqual(values[1], _sample_std([0.01, -0.02]))
        self.assertAlmostEqual(values[2], _sample_std([-0.02, 0.03]))
        self.assertAlmostEqual(values[3], _sample_std([0.03, 0.0]))

    def test_annualized_volatility_scales_rolling_volatility(self) -> None:
        returns = [0.01, -0.02, 0.03]
        rolling = rolling_volatility(returns, window=2)
        annualized = annualized_volatility(returns, window=2, periods_per_year=252)

        self.assertIsNone(annualized[0])
        self.assertAlmostEqual(
            annualized[1],
            rolling[1] * math.sqrt(252),
        )

    def test_bar_level_wrappers(self) -> None:
        bars = [
            _bar(date(2024, 1, 1), close=100.0),
            _bar(date(2024, 1, 2), close=105.0),
            _bar(date(2024, 1, 3), close=102.0),
        ]

        self.assertEqual(simple_returns_from_bars(bars), simple_returns([100.0, 105.0, 102.0]))
        self.assertEqual(log_returns_from_bars(bars), log_returns([100.0, 105.0, 102.0]))
        self.assertEqual(
            rolling_mean_from_bars(bars, window=2),
            rolling_mean([100.0, 105.0, 102.0], window=2),
        )
        self.assertEqual(
            rolling_volatility_from_bars(bars, window=2, use_log_returns=False),
            rolling_volatility(simple_returns([100.0, 105.0, 102.0]), window=2),
        )


def _sample_std(values: list[float]) -> float:
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
    return math.sqrt(variance)
