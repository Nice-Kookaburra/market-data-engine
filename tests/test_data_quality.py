from datetime import date
from unittest import TestCase

from market_data_engine.models.price_bar import PriceBar
from market_data_engine.services.data_quality import (
    assess_data_quality,
    build_data_quality_report,
    find_duplicate_dates,
    find_outlier_dates,
    find_stale_dates,
)
from market_data_engine.services.price_fetcher import FetchResult, PriceFetcher


def _bar(
    day: date,
    close: float,
    *,
    asset_id: str = "AAPL",
    adj_close: float | None = None,
) -> PriceBar:
    return PriceBar(
        asset_id=asset_id,
        day=day,
        interval="1d",
        open=close,
        high=close,
        low=close,
        close=close,
        adj_close=adj_close,
    )


class DataQualityTests(TestCase):
    def test_build_data_quality_report_includes_all_issue_types(self) -> None:
        bars = [
            _bar(date(2024, 1, 1), 100.0),
            _bar(date(2024, 1, 2), 100.0),
            _bar(date(2024, 1, 2), 101.0),
            _bar(date(2024, 1, 3), 200.0),
            _bar(date(2024, 1, 4), 201.0),
            _bar(date(2024, 1, 5), 202.0),
            _bar(date(2024, 1, 8), 203.0),
        ]

        report = build_data_quality_report(
            "AAPL",
            bars,
            start=date(2024, 1, 1),
            end=date(2024, 1, 10),
            max_lag_days=1,
            outlier_std_multiplier=1.0,
        )

        self.assertEqual(report.asset_id, "AAPL")
        self.assertIn(date(2024, 1, 2), report.duplicate_dates)
        self.assertIn(date(2024, 1, 8), report.stale_dates)
        self.assertTrue(report.has_issues)

    def test_find_duplicate_dates(self) -> None:
        bars = [_bar(date(2024, 1, 1), 100.0), _bar(date(2024, 1, 1), 101.0)]
        self.assertEqual(find_duplicate_dates(bars, "AAPL"), (date(2024, 1, 1),))

    def test_find_stale_dates(self) -> None:
        bars = [_bar(date(2024, 1, 1), 100.0)]
        self.assertEqual(
            find_stale_dates(bars, "AAPL", date(2024, 1, 10), max_lag_days=2),
            (date(2024, 1, 1),),
        )

    def test_find_outlier_dates(self) -> None:
        bars = [
            _bar(date(2024, 1, 1), 100.0),
            _bar(date(2024, 1, 2), 100.0),
            _bar(date(2024, 1, 3), 100.0),
            _bar(date(2024, 1, 4), 100.0),
            _bar(date(2024, 1, 5), 200.0),
        ]
        outliers = find_outlier_dates(bars, "AAPL", std_multiplier=1.4, min_returns=3)
        self.assertEqual(outliers, (date(2024, 1, 5),))

    def test_assess_data_quality_includes_requested_symbols_without_bars(self) -> None:
        reports = assess_data_quality(
            [_bar(date(2024, 1, 2), 100.0)],
            start=date(2024, 1, 1),
            end=date(2024, 1, 3),
            asset_ids=["AAPL", "MSFT"],
        )

        self.assertEqual([report.asset_id for report in reports], ["AAPL", "MSFT"])
        self.assertEqual(reports[1].missing_dates, (date(2024, 1, 1), date(2024, 1, 2), date(2024, 1, 3)))

    def test_price_fetcher_can_return_quality_reports(self) -> None:
        class FakeProvider:
            def fetch(self, symbols, start, end, interval="1d"):
                return [
                    _bar(date(2024, 1, 2), 100.0, asset_id=symbols[0]),
                    _bar(date(2024, 1, 3), 101.0, asset_id=symbols[0]),
                ]

        fetcher = PriceFetcher(provider=FakeProvider())
        result = fetcher.fetch_prices(
            ["AAPL"],
            start=date(2024, 1, 1),
            end=date(2024, 1, 5),
            include_quality_report=True,
        )

        self.assertIsInstance(result, FetchResult)
        self.assertEqual(len(result.bars), 2)
        self.assertEqual(len(result.quality_reports), 1)
        self.assertEqual(result.quality_reports[0].asset_id, "AAPL")
        self.assertTrue(result.quality_reports[0].has_issues)
