"""
Incident Pydantic Schemas
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List
from uuid import UUID


class IncidentBase(BaseModel):
    """Base incident schema"""
    description: str = Field(..., min_length=10, max_length=5000, description="Incident description")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Incident timestamp")
    location: str = Field(..., min_length=3, max_length=500, description="Incident location")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude coordinate")
    
    @field_validator('timestamp', mode='before')
    @classmethod
    def remove_timezone(cls, v):
        """Remove timezone info to match PostgreSQL TIMESTAMP WITHOUT TIME ZONE"""
        if v is None:
            return datetime.utcnow()
        if isinstance(v, str):
            # Parse ISO string and remove timezone
            dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
            return dt.replace(tzinfo=None)
        if isinstance(v, datetime):
            # If timezone-aware, convert to UTC and remove tzinfo
            if v.tzinfo is not None:
                return v.replace(tzinfo=None)
        return v


class IncidentCreate(IncidentBase):
    """Schema for creating an incident"""
    pass


class IncidentUpdate(BaseModel):
    """Schema for updating an incident"""
    description: Optional[str] = Field(None, min_length=10, max_length=5000)
    location: Optional[str] = Field(None, min_length=3, max_length=500)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)


class IncidentResponse(IncidentBase):
    """Schema for incident response"""
    id: UUID
    waste_type: Optional[str] = None
    waste_type_confidence: Optional[float] = None
    keywords: Optional[List[str]] = None
    similar_incident_ids: Optional[List[UUID]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class IncidentListResponse(BaseModel):
    """Schema for paginated incident list"""
    items: List[IncidentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class SimilarIncident(BaseModel):
    """Schema for similar incident detection"""
    incident: IncidentResponse
    similarity_score: float
