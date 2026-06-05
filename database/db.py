from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "postgresql://neondb_owner:npg_P4Wxq6fncSZw@ep-damp-wind-ap9g8hhb.c-7.us-east-1.aws.neon.tech/neondb?sslmode=require"

# Create engine for PostgreSQL
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# SessionLocal class will act as a database session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class used to create database models
Base = declarative_base()

# Dependency to get a database session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
