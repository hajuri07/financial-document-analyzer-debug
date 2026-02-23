import os
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./financial_analyzer.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class AnalysisResult(Base):
    """Stores each financial document analysis"""
    __tablename__ = "analysis_results"

    id           = Column(String, primary_key=True, index=True)
    filename     = Column(String, nullable=False)
    query        = Column(Text, nullable=False)
    status       = Column(String, default="completed")
    result       = Column(Text, nullable=True)
    created_at   = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Create all tables on startup"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency to get a DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
