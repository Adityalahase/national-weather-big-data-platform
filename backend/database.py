"""
Database connection setup.

Uses SQLite for simplicity (zero setup, single file: weather_platform.db).
To move to PostgreSQL later, just change SQLALCHEMY_DATABASE_URL, e.g.:
    "postgresql://user:password@localhost/weather_platform"
and add `psycopg2-binary` to requirements.txt. Nothing else in the app changes.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./weather_platform.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # only needed for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
