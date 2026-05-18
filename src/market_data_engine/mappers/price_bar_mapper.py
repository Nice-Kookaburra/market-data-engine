from __future__ import annotations
from market_data_engine.models.price_bar import PriceBar
from market_data_engine.db_models.price_bar_row import PriceBarRow

def row_to_domain(r: PriceBarRow) -> PriceBar:
    return PriceBar(
        asset_id=r.asset_id,
        day=r.day,
        interval=r.interval,
        open=r.open,
        high=r.high,
        low=r.low,
        close=r.close,
        adj_close=r.adj_close,
        volume=r.volume,
        currency=r.currency
    )

def domain_to_row(d: PriceBar) -> PriceBarRow:
    return PriceBarRow(
        asset_id=d.asset_id,
        interval=d.interval,
        day=d.day,
        open=d.open,
        high=d.high,
        low=d.low,
        close=d.close,
        adj_close=d.adj_close,
        volume=d.volume,
        currency=d.currency
    )