"""
SQLAlchemy base configuration for Qteria database.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set. " "Please configure it in your .env file."
    )

# Create SQLAlchemy engine
# pool_pre_ping=True ensures connections are healthy before using them
# echo=False in production (set to True for SQL debugging)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=os.getenv("PYTHON_ENV") == "development",
)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base for models
Base = declarative_base()


def get_db():
    """
    Dependency function for FastAPI to get database sessions.
    Usage: def endpoint(db: Session = Depends(get_db))
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
