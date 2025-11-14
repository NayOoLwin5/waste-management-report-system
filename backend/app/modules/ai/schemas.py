"""
AI Module Schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID


class WasteClassificationRequest(BaseModel):
    """Request schema for waste classification"""
    description: str = Field(..., min_length=10, description="Incident description")


class WasteClassificationResponse(BaseModel):
    """Response schema for waste classification"""
    waste_type: str
    confidence: float
    description: str


class KeywordExtractionRequest(BaseModel):
    """Request schema for keyword extraction"""
    text: str = Field(..., min_length=10, description="Text to extract keywords from")
    top_n: int = Field(5, ge=1, le=20, description="Number of keywords to extract")


class KeywordExtractionResponse(BaseModel):
    """Response schema for keyword extraction"""
    keywords: List[str]
    text: str


class SimilarIncidentsRequest(BaseModel):
    """Request schema for finding similar incidents"""
    incident_id: UUID = Field(..., description="Current incident ID")
    description: str = Field(..., min_length=10, description="Incident description")
    threshold: float = Field(0.75, ge=0.0, le=1.0, description="Similarity threshold")
    limit: int = Field(5, ge=1, le=20, description="Maximum number of similar incidents")


class SimilarIncidentItem(BaseModel):
    """Schema for a similar incident item"""
    id: str
    description: str
    location: str
    waste_type: Optional[str] = None


class SimilarIncidentsResponse(BaseModel):
    """Response schema for similar incidents"""
    incident_id: UUID
    similar_incidents: List[SimilarIncidentItem]
    count: int
