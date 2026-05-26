from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Iterable

from market_data_engine.models.price_bar import PriceBar
from market_data_engine.services.calculations import (
    bar_dates,
    log_returns_from_bars,
    price_series,
    rolling_mean_from_bars,
    rolling_volatility_from_bars,
    simple_returns_from_bars,
)

if TYPE_CHECKING:
    from matplotlib.figure import Figure


class VisualizationError(ImportError):
    """Raised when matplotlib is required but not installed."""


def _import_pyplot():
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise VisualizationError(
            "matplotlib is required for plotting. Install it with: pip install matplotlib"
        ) from exc
    return plt


def _sorted_bars(bars: Iterable[PriceBar]) -> list[PriceBar]:
    return sorted(bars, key=lambda bar: bar.day)


def _default_title(bars: Iterable[PriceBar], suffix: str) -> str:
    bars_list = _sorted_bars(bars)
    if not bars_list:
        return suffix
    return f"{bars_list[0].asset_id} {suffix}"


def _return_dates(dates: list[date]) -> list[date]:
    return dates[1:]


def _aligned_series(
    dates: list[date],
    values: list[float | None],
) -> tuple[list[date], list[float]]:
    aligned_dates: list[date] = []
    aligned_values: list[float] = []
    for day, value in zip(dates, values):
        if value is not None:
            aligned_dates.append(day)
            aligned_values.append(value)
    return aligned_dates, aligned_values


def _finalize_figure(
    fig: Figure,
    *,
    show: bool = False,
    save_path: str | None = None,
) -> Figure:
    if save_path:
        fig.savefig(save_path, bbox_inches="tight")
    if show:
        _import_pyplot().show()
    return fig


def plot_price_history(
    bars: Iterable[PriceBar],
    *,
    title: str | None = None,
    show: bool = False,
    save_path: str | None = None,
) -> Figure:
    """Plot comparable price history from validated PriceBar data."""
    plt = _import_pyplot()
    dates = bar_dates(bars)
    prices = price_series(bars)

    fig, axis = plt.subplots(figsize=(10, 5))
    axis.plot(dates, prices, label="Price")
    axis.set_title(title or _default_title(bars, "Price History"))
    axis.set_xlabel("Date")
    axis.set_ylabel("Price")
    axis.legend()
    axis.grid(True, alpha=0.3)
    fig.autofmt_xdate()
    fig.tight_layout()
    return _finalize_figure(fig, show=show, save_path=save_path)


def plot_returns(
    bars: Iterable[PriceBar],
    *,
    use_log_returns: bool = False,
    title: str | None = None,
    show: bool = False,
    save_path: str | None = None,
) -> Figure:
    """Plot simple or log returns derived from PriceBar data."""
    plt = _import_pyplot()
    dates = bar_dates(bars)
    if use_log_returns:
        returns = log_returns_from_bars(bars)
        label = "Log Return"
        default_suffix = "Log Returns"
    else:
        returns = simple_returns_from_bars(bars)
        label = "Simple Return"
        default_suffix = "Simple Returns"

    return_dates = _return_dates(dates)

    fig, axis = plt.subplots(figsize=(10, 5))
    if return_dates and returns:
        axis.plot(return_dates, returns, label=label)
    axis.axhline(0.0, color="black", linewidth=0.8, alpha=0.5)
    axis.set_title(title or _default_title(bars, default_suffix))
    axis.set_xlabel("Date")
    axis.set_ylabel(label)
    axis.legend()
    axis.grid(True, alpha=0.3)
    fig.autofmt_xdate()
    fig.tight_layout()
    return _finalize_figure(fig, show=show, save_path=save_path)


def plot_rolling_mean(
    bars: Iterable[PriceBar],
    window: int = 20,
    *,
    title: str | None = None,
    show: bool = False,
    save_path: str | None = None,
) -> Figure:
    """Plot price history with a rolling mean overlay."""
    plt = _import_pyplot()
    dates = bar_dates(bars)
    prices = price_series(bars)
    rolling = rolling_mean_from_bars(bars, window)
    rolling_dates, rolling_values = _aligned_series(dates, rolling)

    fig, axis = plt.subplots(figsize=(10, 5))
    axis.plot(dates, prices, label="Price", alpha=0.7)
    if rolling_dates:
        axis.plot(rolling_dates, rolling_values, label=f"{window}-day SMA")
    axis.set_title(title or _default_title(bars, f"{window}-Day Rolling Mean"))
    axis.set_xlabel("Date")
    axis.set_ylabel("Price")
    axis.legend()
    axis.grid(True, alpha=0.3)
    fig.autofmt_xdate()
    fig.tight_layout()
    return _finalize_figure(fig, show=show, save_path=save_path)


def plot_rolling_volatility(
    bars: Iterable[PriceBar],
    window: int = 20,
    *,
    use_log_returns: bool = True,
    title: str | None = None,
    show: bool = False,
    save_path: str | None = None,
) -> Figure:
    """Plot rolling volatility derived from bar returns."""
    plt = _import_pyplot()
    dates = bar_dates(bars)
    rolling_vol = rolling_volatility_from_bars(bars, window, use_log_returns=use_log_returns)
    return_dates = _return_dates(dates)
    vol_dates, vol_values = _aligned_series(return_dates, rolling_vol)

    fig, axis = plt.subplots(figsize=(10, 5))
    if vol_dates:
        axis.plot(vol_dates, vol_values, label=f"{window}-day Rolling Vol")
    axis.set_title(title or _default_title(bars, f"{window}-Day Rolling Volatility"))
    axis.set_xlabel("Date")
    axis.set_ylabel("Volatility")
    axis.legend()
    axis.grid(True, alpha=0.3)
    fig.autofmt_xdate()
    fig.tight_layout()
    return _finalize_figure(fig, show=show, save_path=save_path)


def plot_symbol_overview(
    bars: Iterable[PriceBar],
    window: int = 20,
    *,
    use_log_returns: bool = True,
    title: str | None = None,
    show: bool = False,
    save_path: str | None = None,
) -> Figure:
    """Plot price, returns, rolling mean, and rolling volatility in one figure."""
    plt = _import_pyplot()
    bars_list = _sorted_bars(bars)
    dates = bar_dates(bars_list)
    prices = price_series(bars_list)

    if use_log_returns:
        returns = log_returns_from_bars(bars_list)
        return_label = "Log Return"
    else:
        returns = simple_returns_from_bars(bars_list)
        return_label = "Simple Return"

    return_dates = _return_dates(dates)
    rolling = rolling_mean_from_bars(bars_list, window)
    rolling_dates, rolling_values = _aligned_series(dates, rolling)
    rolling_vol = rolling_volatility_from_bars(bars_list, window, use_log_returns=use_log_returns)
    vol_dates, vol_values = _aligned_series(return_dates, rolling_vol)

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle(title or _default_title(bars_list, "Overview"))

    axes[0, 0].plot(dates, prices)
    axes[0, 0].set_title("Price History")
    axes[0, 0].grid(True, alpha=0.3)

    if return_dates and returns:
        axes[0, 1].plot(return_dates, returns)
    axes[0, 1].axhline(0.0, color="black", linewidth=0.8, alpha=0.5)
    axes[0, 1].set_title(return_label)
    axes[0, 1].grid(True, alpha=0.3)

    axes[1, 0].plot(dates, prices, alpha=0.5, label="Price")
    if rolling_dates:
        axes[1, 0].plot(rolling_dates, rolling_values, label=f"{window}-day SMA")
    axes[1, 0].set_title(f"{window}-Day Rolling Mean")
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    if vol_dates:
        axes[1, 1].plot(vol_dates, vol_values)
    axes[1, 1].set_title(f"{window}-Day Rolling Volatility")
    axes[1, 1].grid(True, alpha=0.3)

    for axis in axes.flat:
        axis.tick_params(axis="x", rotation=30)

    fig.tight_layout()
    return _finalize_figure(fig, show=show, save_path=save_path)
