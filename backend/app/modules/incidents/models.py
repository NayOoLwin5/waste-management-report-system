"""
Incident Database Models
"""
from sqlalchemy import Column, String, DateTime, Float, Text, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from datetime import datetime
import uuid
from pgvector.sqlalchemy import Vector

from app.core.database import Base


class Incident(Base):
    """Waste Incident Model"""
    __tablename__ = "incidents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(Text, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    location = Column(String(500), nullable=False, index=True)
    
    # Coordinates (optional)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # AI-generated fields
    waste_type = Column(String(100), nullable=True, index=True)
    waste_type_confidence = Column(Float, nullable=True)
    embedding = Column(Vector(384), nullable=True)  # all-MiniLM-L6-v2 produces 384-dim vectors
    keywords = Column(ARRAY(String), nullable=True)
    
    # Similar incidents
    similar_incident_ids = Column(ARRAY(UUID(as_uuid=True)), nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_timestamp_desc', timestamp.desc()),
        Index('idx_waste_type', waste_type),
        Index('idx_location', location),
    )
    
    def __repr__(self):
        return f"<Incident(id={self.id}, waste_type={self.waste_type}, location={self.location})>"
