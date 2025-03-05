from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import (
    PG_HOST, PG_PORT, PG_DATABASE, PG_USER, PG_PASSWORD
)


# Database connection for the primary backend
SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get the database session
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()