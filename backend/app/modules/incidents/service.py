"""
Incident Service - Business Logic Layer
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import math

from app.modules.incidents.models import Incident
from app.modules.incidents.schemas import IncidentCreate, IncidentUpdate
from app.core.logging import logger, audit_logger


class IncidentService:
    """Service for handling incident business logic"""
    
    @staticmethod
    async def create_incident(
        db: AsyncSession,
        incident_data: IncidentCreate
    ) -> Incident:
        """Create a new incident"""
        incident = Incident(
            description=incident_data.description,
            timestamp=incident_data.timestamp,
            location=incident_data.location,
            latitude=incident_data.latitude,
            longitude=incident_data.longitude
        )
        
        db.add(incident)
        await db.flush()
        await db.refresh(incident)
        
        audit_logger.log_action(
            action="create",
            resource="incident",
            resource_id=str(incident.id),
            status="success"
        )
        
        logger.info(
            "Incident created",
            incident_id=str(incident.id),
            location=incident.location
        )
        
        return incident
    
    @staticmethod
    async def get_incident(
        db: AsyncSession,
        incident_id: UUID
    ) -> Optional[Incident]:
        """Get incident by ID"""
        result = await db.execute(
            select(Incident).where(Incident.id == incident_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def list_incidents(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 20,
        waste_type: Optional[str] = None,
        location: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> tuple[List[Incident], int]:
        """List incidents with pagination and filters"""
        
        # Build query with filters
        query = select(Incident)
        filters = []
        
        if waste_type:
            # Use partial matching (case-insensitive) for waste type filter
            filters.append(Incident.waste_type.ilike(f"%{waste_type}%"))
        
        if location:
            filters.append(Incident.location.ilike(f"%{location}%"))
        
        if start_date:
            filters.append(Incident.timestamp >= start_date)
        
        if end_date:
            filters.append(Incident.timestamp <= end_date)
        
        if filters:
            query = query.where(and_(*filters))
        
        # Get total count
        count_query = select(func.count()).select_from(Incident)
        if filters:
            count_query = count_query.where(and_(*filters))
        
        total = await db.scalar(count_query)
        
        # Apply pagination and ordering
        query = query.order_by(Incident.timestamp.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await db.execute(query)
        incidents = result.scalars().all()
        
        return list(incidents), total or 0
    
    @staticmethod
    async def update_incident(
        db: AsyncSession,
        incident_id: UUID,
        incident_data: IncidentUpdate
    ) -> Optional[Incident]:
        """Update an incident"""
        incident = await IncidentService.get_incident(db, incident_id)
        
        if not incident:
            return None
        
        # Update fields
        update_data = incident_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(incident, field, value)
        
        incident.updated_at = datetime.utcnow()
        
        await db.flush()
        await db.refresh(incident)
        
        audit_logger.log_action(
            action="update",
            resource="incident",
            resource_id=str(incident.id),
            details=update_data,
            status="success"
        )
        
        return incident
    
    @staticmethod
    async def delete_incident(
        db: AsyncSession,
        incident_id: UUID
    ) -> bool:
        """Delete an incident"""
        incident = await IncidentService.get_incident(db, incident_id)
        
        if not incident:
            return False
        
        await db.delete(incident)
        
        audit_logger.log_action(
            action="delete",
            resource="incident",
            resource_id=str(incident_id),
            status="success"
        )
        
        return True
    
    @staticmethod
    async def update_ai_fields(
        db: AsyncSession,
        incident_id: UUID,
        waste_type: str,
        confidence: float,
        embedding: List[float],
        keywords: List[str],
        similar_incident_ids: List[UUID] = None
    ) -> Optional[Incident]:
        """Update AI-generated fields for an incident"""
        incident = await IncidentService.get_incident(db, incident_id)
        
        if not incident:
            return None
        
        incident.waste_type = waste_type
        incident.waste_type_confidence = confidence
        incident.embedding = embedding
        incident.keywords = keywords
        
        if similar_incident_ids:
            incident.similar_incident_ids = [str(id) for id in similar_incident_ids]
        
        await db.flush()
        await db.refresh(incident)
        
        logger.info(
            "AI fields updated",
            incident_id=str(incident.id),
            waste_type=waste_type,
            confidence=confidence
        )
        
        return incident
