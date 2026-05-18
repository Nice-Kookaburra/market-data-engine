from __future__ import annotations
from datetime import date
from sqlalchemy import String, Date, Float
from sqlalchemy.orm import Mapped, mapped_column
from market_data_engine.sessions.session import Base

class PriceBarRow(Base):
    __tablename__ = "price_bars"

    # Composite PK
    asset_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    interval: Mapped[str] = mapped_column(String(8), primary_key=True)
    day: Mapped[date] = mapped_column(Date, primary_key=True) # might be "date" instead of date from datetime

    # Other attributes / columns
    open: Mapped[float] = mapped_column(Float, nullable=False)
    high: Mapped[float] = mapped_column(Float, nullable=False)
    low: Mapped[float] = mapped_column(Float, nullable=False)
    close: Mapped[float] = mapped_column(Float, nullable=False)

    adj_close: Mapped[float | None] = mapped_column(Float, nullable=True)
    volume: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[float | None] = mapped_column(String(16), nullable=True)