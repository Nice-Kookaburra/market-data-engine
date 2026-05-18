from __future__ import annotations

from datetime import date
from typing import Iterable, List

import pandas as pd
import yfinance as yf

from market_data_engine.models.price_bar import PriceBar, Interval
from market_data_engine.providers.price_provider import PriceProvider


class YahooPriceProvider(PriceProvider):
    def fetch(
        self,
        symbols: Iterable[str],
        start: date,
        end: date,
        interval: Interval = "1d",
    ) -> List[PriceBar]:
        symbol_list = list(symbols)
        if not symbol_list:
            return []

        tickers = " ".join(symbol_list)
        df = yf.download(
            tickers=tickers,
            start=start.isoformat(),
            end=end.isoformat(),
            interval=interval,
            group_by="ticker",
            auto_adjust=False,
            progress=False,
            threads=True,
        )

        bars: List[PriceBar] = []
        if df.empty:
            return bars

        if isinstance(df.columns, pd.MultiIndex):
            for s in symbol_list:
                if s not in df.columns.get_level_values(0):
                    continue
                sub = df[s].dropna(how="all")
                bars.extend(self._df_to_bars(s, sub, interval))
        else:
            s = symbol_list[0]
            bars.extend(self._df_to_bars(s, df.dropna(how="all"), interval))

        return bars

    def _df_to_bars(
        self,
        symbol: str,
        df: pd.DataFrame,
        interval: Interval,
    ) -> List[PriceBar]:
        out: List[PriceBar] = []
        required_columns = ("Open", "High", "Low", "Close")

        for ts, row in df.iterrows():
            if any(column not in row or pd.isna(row[column]) for column in required_columns):
                continue

            day = pd.Timestamp(ts).date()
            out.append(
                PriceBar(
                    asset_id=symbol,
                    day=day,
                    interval=interval,
                    open=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=float(row["Close"]),
                    adj_close=(
                        float(row["Adj Close"])
                        if "Adj Close" in row and pd.notna(row["Adj Close"])
                        else None
                    ),
                    volume=(
                        float(row["Volume"])
                        if "Volume" in row and pd.notna(row.get("Volume"))
                        else None
                    ),
                    currency=None,
                )
            )

        return out