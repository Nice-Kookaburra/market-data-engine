from __future__ import annotations
from datetime import date
from typing import Iterable, List

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from market_data_engine.models.price_bar import PriceBar, Interval
from market_data_engine.db_models.price_bar_row import PriceBarRow
from market_data_engine.mappers.price_bar_mapper import row_to_domain

class PriceRepository:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def get_prices(
            self,
            asset_id: str,
            start: date,
            end: date,
            interval: Interval = "1d"
    ) -> List[PriceBar]:
        with self.session_factory() as session:
            statement = (
                select(PriceBarRow)
                .where(PriceBarRow.asset_id == asset_id)
                .where(PriceBarRow.interval == interval)
                .where(PriceBarRow.day >= start)
                .where(PriceBarRow.day <= end)
                .order_by(PriceBarRow.day.asc())
            )
            rows = session.execute(statement).scalars().all()
            return [row_to_domain(r) for r in rows]
        
    def upsert_prices(self, bars: Iterable[PriceBar]) -> int:
        bars = list(bars)
        if not bars: 
            return 0
        
        values = [
            dict(
                asset_id=b.asset_id,
                interval=b.interval,
                day=b.day,
                open=b.open,
                high=b.high,
                low=b.low,
                close=b.close,
                adj_close=b.adj_close,
                volume=b.volume,
                currency=b.currency
            )
            for b in bars
        ]

        with self.session_factory() as session:
            statement = pg_insert(PriceBarRow).values(values)

            # If same composite key, update fields
            update_cols = {
                "open": statement.excluded.open,
                "high": statement.excluded.high,
                "low": statement.excluded.low,
                "close": statement.excluded.close,
                "adj_close": statement.excluded.adj_close,
                "volume": statement.excluded.volume,
                "currency": statement.excluded.currency
            }

            statement = statement.on_conflict_do_update(
                index_elements=[PriceBarRow.asset_id, PriceBarRow.interval, PriceBarRow.day],
                set_=update_cols
            )

            result = session.execute(statement)
            session.commit()
            return result.rowcount or 0