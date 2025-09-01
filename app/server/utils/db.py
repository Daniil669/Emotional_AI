import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_URL = os.getenv("DATABASE_URL", "sqlite:///data/app.db")
_is_sqlite = DB_URL.startswith("sqlite:")

engine = create_engine(DB_URL, connect_args={"check_same_thread": False} if _is_sqlite else {})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# FastAPI dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
