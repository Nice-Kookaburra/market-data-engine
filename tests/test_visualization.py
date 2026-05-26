import tempfile
import unittest
from datetime import date
from pathlib import Path

from market_data_engine.models.price_bar import PriceBar


def _bars() -> list[PriceBar]:
    days = [date(2024, 1, 2), date(2024, 1, 3), date(2024, 1, 4), date(2024, 1, 5), date(2024, 1, 8)]
    prices = [100.0, 101.0, 102.0, 101.5, 103.0]
    return [
        PriceBar(
            asset_id="AAPL",
            day=day,
            interval="1d",
            open=price,
            high=price + 1,
            low=price - 1,
            close=price,
        )
        for day, price in zip(days, prices)
    ]


class VisualizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        try:
            import matplotlib

            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            cls._plt = plt
        except ImportError:
            raise unittest.SkipTest("matplotlib is not installed")

    def _close(self, fig) -> None:
        self._plt.close(fig)

    def test_plot_functions_return_figure(self) -> None:
        from market_data_engine.services.visualization import (
            plot_price_history,
            plot_returns,
            plot_rolling_mean,
            plot_rolling_volatility,
            plot_symbol_overview,
        )

        bars = _bars()
        for plot_func in (
            lambda: plot_price_history(bars),
            lambda: plot_returns(bars),
            lambda: plot_returns(bars, use_log_returns=True),
            lambda: plot_rolling_mean(bars, window=2),
            lambda: plot_rolling_volatility(bars, window=2),
            lambda: plot_symbol_overview(bars, window=2),
        ):
            fig = plot_func()
            self.assertIsNotNone(fig)
            self._close(fig)

    def test_plot_can_save_to_file(self) -> None:
        from market_data_engine.services.visualization import plot_symbol_overview

        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "overview.png"
            fig = plot_symbol_overview(_bars(), window=2, save_path=str(output))
            self.assertTrue(output.exists())
            self.assertGreater(output.stat().st_size, 0)
            self._close(fig)

    def test_visualization_error_without_matplotlib(self) -> None:
        from market_data_engine.services import visualization as viz_module

        original = viz_module._import_pyplot

        def _raise_import_error():
            raise viz_module.VisualizationError("matplotlib missing")

        viz_module._import_pyplot = _raise_import_error
        try:
            with self.assertRaises(viz_module.VisualizationError):
                viz_module.plot_price_history(_bars())
        finally:
            viz_module._import_pyplot = original


if __name__ == "__main__":
    unittest.main()
