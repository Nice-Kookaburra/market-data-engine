from datetime import date
from unittest import TestCase

from market_data_engine.models.price_bar import PriceBar
from market_data_engine.services.validation import (
    PriceValidationError,
    build_data_quality_report,
    find_missing_weekdays,
    validate_bars,
    validate_missing_weekdays,
)


class PriceValidationTests(TestCase):
    def test_validate_bars_reports_missing_required_price_fields(self) -> None:
        bar = PriceBar(
            asset_id="AAPL",
            day=date(2024, 1, 2),
            interval="1d",
            open=None,  # type: ignore[arg-type]
            high=None,  # type: ignore[arg-type]
            low=180.0,
            close=181.0,
        )

        with self.assertRaises(PriceValidationError) as exc_info:
            validate_bars([bar])

        self.assertIn("open is required for AAPL on 2024-01-02", exc_info.exception.errors)
        self.assertIn("high is required for AAPL on 2024-01-02", exc_info.exception.errors)

    def test_validate_bars_reports_required_field_errors_before_range_checks(self) -> None:
        bar = PriceBar(
            asset_id="MSFT",
            day=date(2024, 1, 2),
            interval="1d",
            open=410.0,
            high=415.0,
            low=None,  # type: ignore[arg-type]
            close=412.0,
        )

        with self.assertRaises(PriceValidationError) as exc_info:
            validate_bars([bar])

        self.assertEqual(exc_info.exception.errors, ("low is required for MSFT on 2024-01-02",))

    def test_validate_bars_detects_duplicate_records(self) -> None:
        bar = PriceBar(
            asset_id="AAPL",
            day=date(2024, 1, 2),
            interval="1d",
            open=180.0,
            high=182.0,
            low=179.0,
            close=181.0,
        )

        with self.assertRaises(PriceValidationError) as exc_info:
            validate_bars([bar, bar])

        self.assertIn(
            "duplicate price bar for asset=AAPL, interval=1d, day=2024-01-02",
            exc_info.exception.errors,
        )

    def test_find_missing_weekdays_skips_weekends(self) -> None:
        bars = [
            PriceBar(
                asset_id="AAPL",
                day=date(2024, 1, 2),
                interval="1d",
                open=180.0,
                high=182.0,
                low=179.0,
                close=181.0,
            )
        ]

        missing = find_missing_weekdays(
            bars,
            start=date(2024, 1, 2),
            end=date(2024, 1, 5),
            asset_id="AAPL",
        )

        self.assertEqual(missing, (date(2024, 1, 3), date(2024, 1, 4), date(2024, 1, 5)))

    def test_validate_bars_can_check_missing_weekdays(self) -> None:
        bar = PriceBar(
            asset_id="AAPL",
            day=date(2024, 1, 2),
            interval="1d",
            open=180.0,
            high=182.0,
            low=179.0,
            close=181.0,
        )

        with self.assertRaises(PriceValidationError) as exc_info:
            validate_bars(
                [bar],
                start=date(2024, 1, 2),
                end=date(2024, 1, 5),
                check_missing_weekdays=True,
            )

        self.assertIn(
            "missing daily bar for asset=AAPL on 2024-01-03",
            exc_info.exception.errors,
        )

    def test_build_data_quality_report(self) -> None:
        bar = PriceBar(
            asset_id="AAPL",
            day=date(2024, 1, 2),
            interval="1d",
            open=180.0,
            high=182.0,
            low=179.0,
            close=181.0,
        )

        report = build_data_quality_report(
            "AAPL",
            [bar],
            start=date(2024, 1, 1),
            end=date(2024, 1, 3),
        )

        self.assertEqual(report.asset_id, "AAPL")
        self.assertEqual(report.missing_dates, (date(2024, 1, 1), date(2024, 1, 3)))

    def test_validate_missing_weekdays_returns_error_messages(self) -> None:
        bar = PriceBar(
            asset_id="AAPL",
            day=date(2024, 1, 2),
            interval="1d",
            open=180.0,
            high=182.0,
            low=179.0,
            close=181.0,
        )

        errors = validate_missing_weekdays(
            [bar],
            start=date(2024, 1, 1),
            end=date(2024, 1, 3),
        )

        self.assertEqual(
            errors,
            [
                "missing daily bar for asset=AAPL on 2024-01-01",
                "missing daily bar for asset=AAPL on 2024-01-03",
            ],
        )
