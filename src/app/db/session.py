"""
PostgreSQL database connection configuration and session management.

This module creates the SQLAlchemy Engine, manages connection pooling,
and provides the Base class for all ORM models using SQLAlchemy 2.0 standards.
"""

from typing import Generator
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from src.app.core.config import settings

# Construct the standard URL for database connection
# Using psycopg (v3) which is highly optimized for modern PostgreSQL and SQLAlchemy
SQLALCHEMY_DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=settings.database_user,
    password=settings.database_password,
    host=settings.database_host,
    port=settings.database_port,
    database=settings.database_name,
)

# Create the database engine with production-ready connection pooling
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,           # Set to True to log SQL queries to the console for debugging
    pool_pre_ping=True,   # Verifies connection health before using it from the pool
    pool_size=5,          # Default number of connections to keep open
    max_overflow=10,      # Max extra connections allowed if the pool is exhausted
)

# Configure the database session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    Every table model in the application must inherit from this class.
    """

    pass


def get_db() -> Generator[Session, None, None]:
    """
    Dependency Injection for FastAPI API routes.

    Opens a database session for a request and safely closes it
    after the request is completed, even if an exception occurs.

    Yields:
        Session: An active SQLAlchemy database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
