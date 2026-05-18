from __future__ import annotations
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

class Base(DeclarativeBase):
    pass

def make_engine(db_url: str):
    # Example of db_url
    # db_url = "postgresql+psycopg2://user:pass@localhost:5432/market"
    
    return create_engine(db_url, future=True)

def make_session_factory(engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)