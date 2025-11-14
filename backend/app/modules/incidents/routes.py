"""
Incident API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from uuid import UUID
from datetime import datetime
import math

from app.core.database import get_db
from app.modules.incidents.schemas import (
    IncidentCreate,
    IncidentUpdate,
    IncidentResponse,
    IncidentListResponse
)
from app.modules.incidents.service import IncidentService
from app.core.logging import logger

router = APIRouter()


@router.post(
    "/",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new incident"
)
async def create_incident(
    incident_data: IncidentCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new waste incident report.
    
    The incident will be automatically processed by AI to:
    - Classify waste type
    - Extract keywords
    - Detect similar incidents
    """
    try:
        # Create incident
        incident = await IncidentService.create_incident(db, incident_data)
        
        # Process with AI in background (we'll trigger this after creation)
        from app.modules.ai.service import AIService
        ai_service = AIService()
        
        # Ensure AI service is initialized (lazy loading)
        await ai_service.initialize()
        
        # Process AI features
        ai_result = await ai_service.process_incident(incident.description, incident.location)
        
        # Update incident with AI results
        await IncidentService.update_ai_fields(
            db,
            incident.id,
            waste_type=ai_result["waste_type"],
            confidence=ai_result["confidence"],
            embedding=ai_result["embedding"],
            keywords=ai_result["keywords"]
        )
        
        # Find similar incidents
        similar_incidents = await ai_service.find_similar_incidents(
            db,
            incident.id,
            ai_result["embedding"]
        )
        
        if similar_incidents:
            await IncidentService.update_ai_fields(
                db,
                incident.id,
                waste_type=ai_result["waste_type"],
                confidence=ai_result["confidence"],
                embedding=ai_result["embedding"],
                keywords=ai_result["keywords"],
                similar_incident_ids=[inc.id for inc in similar_incidents]
            )
        
        await db.commit()
        await db.refresh(incident)
        
        return incident
        
    except Exception as e:
        logger.error(f"Error creating incident: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create incident: {str(e)}"
        )


@router.get(
    "/",
    response_model=IncidentListResponse,
    summary="List all incidents"
)
async def list_incidents(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    waste_type: Optional[str] = Query(None, description="Filter by waste type"),
    location: Optional[str] = Query(None, description="Filter by location"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    db: AsyncSession = Depends(get_db)
):
    """
    List all incidents with pagination and optional filters.
    """
    try:
        incidents, total = await IncidentService.list_incidents(
            db,
            page=page,
            page_size=page_size,
            waste_type=waste_type,
            location=location,
            start_date=start_date,
            end_date=end_date
        )
        
        total_pages = math.ceil(total / page_size) if total > 0 else 0
        
        return IncidentListResponse(
            items=incidents,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"Error listing incidents: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list incidents: {str(e)}"
        )


@router.get(
    "/{incident_id}",
    response_model=IncidentResponse,
    summary="Get incident by ID"
)
async def get_incident(
    incident_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific incident by ID.
    """
    incident = await IncidentService.get_incident(db, incident_id)
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident {incident_id} not found"
        )
    
    return incident


@router.put(
    "/{incident_id}",
    response_model=IncidentResponse,
    summary="Update an incident"
)
async def update_incident(
    incident_id: UUID,
    incident_data: IncidentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing incident.
    """
    incident = await IncidentService.update_incident(db, incident_id, incident_data)
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident {incident_id} not found"
        )
    
    await db.commit()
    
    return incident


@router.delete(
    "/{incident_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an incident"
)
async def delete_incident(
    incident_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an incident.
    """
    success = await IncidentService.delete_incident(db, incident_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident {incident_id} not found"
        )
    
    await db.commit()
    
    return None


@router.get(
    "/search/semantic",
    response_model=List[IncidentResponse],
    summary="Semantic search for similar incidents"
)
async def semantic_search(
    query: str = Query(..., description="Natural language search query"),
    threshold: float = Query(0.70, ge=0.0, le=1.0, description="Similarity threshold (0-1)"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    db: AsyncSession = Depends(get_db)
):
    """
    Search for incidents using natural language semantic similarity.
    
    This endpoint uses AI embeddings to find incidents similar to your query,
    understanding the meaning rather than just matching keywords.
    
    Example queries:
    - "plastic waste near parks"
    - "hazardous chemical spills"
    - "electronic waste disposal"
    """
    try:
        from app.modules.ai.service import AIService
        from app.modules.incidents.models import Incident
        from sqlalchemy import select
        import numpy as np
        from sklearn.metrics.pairwise import cosine_similarity
        
        # Initialize AI service
        ai_service = AIService()
        await ai_service.initialize()
        
        # Generate embedding for search query
        query_embedding = ai_service.generate_embedding(query)
        
        # Get all incidents with embeddings
        result = await db.execute(
            select(Incident).where(Incident.embedding.isnot(None))
        )
        all_incidents = result.scalars().all()
        
        if not all_incidents:
            return []
        
        # Calculate similarities
        query_vector = np.array(query_embedding).reshape(1, -1)
        similarities = []
        
        for incident in all_incidents:
            if incident.embedding is not None and len(incident.embedding) > 0:
                incident_vector = np.array(incident.embedding).reshape(1, -1)
                similarity = cosine_similarity(query_vector, incident_vector)[0][0]
                
                if similarity >= threshold:
                    similarities.append((incident, float(similarity)))
        
        # Sort by similarity (descending) and return top N
        similarities.sort(key=lambda x: x[1], reverse=True)
        results = [inc for inc, sim in similarities[:limit]]
        
        logger.info(
            "Semantic search completed",
            query=query,
            threshold=threshold,
            results_count=len(results)
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Error in semantic search: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Semantic search failed: {str(e)}"
        )
