"""Database models"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, DECIMAL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class Part(Base):
    """Parts table"""
    __tablename__ = "parts"
    
    id = Column(Integer, primary_key=True)
    
    # Part identification
    part_description = Column(Text, nullable=False)
    stock_number = Column(String(100))
    part_type = Column(String(50))
    
    # Pricing
    price = Column(DECIMAL(10, 2))
    grade = Column(String(10))
    
    # Vehicle info
    search_year = Column(Integer)
    search_make = Column(String(50))
    search_model = Column(String(50))
    engine_type = Column(String(20))
    
    # Condition
    mileage = Column(Integer)
    warranty = Column(Text)
    notes = Column(Text)
    interchange_note = Column(Text)
    
    # Seller info
    yard_name = Column(String(200), nullable=False)
    location = Column(String(200))
    phone = Column(String(50))
    distance_miles = Column(DECIMAL(6, 2))
    url = Column(Text)
    
    # Metadata
    first_seen_at = Column(DateTime, default=datetime.utcnow)
    last_seen_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    times_seen = Column(Integer, default=1)
    is_available = Column(Boolean, default=True)


class PriceHistory(Base):
    """Price history table"""
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True)
    part_id = Column(Integer, ForeignKey('parts.id', ondelete='CASCADE'))
    old_price = Column(DECIMAL(10, 2))
    new_price = Column(DECIMAL(10, 2))
    changed_at = Column(DateTime, default=datetime.utcnow)


class SearchRun(Base):
    """Search runs table"""
    __tablename__ = "search_runs"
    
    id = Column(Integer, primary_key=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    total_parts_found = Column(Integer)
    new_parts_added = Column(Integer)
    parts_updated = Column(Integer)
    parts_removed = Column(Integer)
    search_params = Column(Text)  # JSON string
    status = Column(String(20))
    error_message = Column(Text)
