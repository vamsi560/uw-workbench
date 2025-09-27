from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, JSON, ForeignKey, UUID as SQLAlchemyUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import uuid

from config import settings

# Create database engine
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Submission(Base):
    __tablename__ = "submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, index=True)  # Internal submission ID
    submission_ref = Column(SQLAlchemyUUID, unique=True, index=True, default=uuid.uuid4)
    subject = Column(Text, nullable=False)
    sender_email = Column(Text, nullable=False)
    body_text = Column(Text)
    extracted_fields = Column(JSON)  # JSONB equivalent
    assigned_to = Column(Text)  # underwriter email/name
    task_status = Column(Text, default="pending")  # pending, in_progress, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    work_items = relationship("WorkItem", back_populates="submission")


class WorkItem(Base):
    __tablename__ = "work_items"
    
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False)
    assigned_to = Column(String, nullable=False)  # underwriter email/name
    status = Column(String, default="pending")  # pending, in_progress, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    submission = relationship("Submission", back_populates="work_items")


# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)
