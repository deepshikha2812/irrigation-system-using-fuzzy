"""SQLite connection setup (SQLAlchemy)."""
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_PATH = Path(__file__).resolve().parent.parent / "irrigation.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    """Parent class of all database models."""


def get_db():
    """FastAPI dependency: opens a session for one request and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
