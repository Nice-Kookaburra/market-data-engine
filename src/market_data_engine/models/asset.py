from dataclasses import dataclass


@dataclass(frozen=True)
class Asset:
    asset_id: str
    ticker: str
    exchange: str
    name: str
    currency: str
    asset_type: str
