"""
AI API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.modules.ai.service import AIService
from app.modules.ai.schemas import (
    WasteClassificationRequest,
    WasteClassificationResponse,
    SimilarIncidentsRequest,
    SimilarIncidentsResponse,
    KeywordExtractionRequest,
    KeywordExtractionResponse
)
from app.core.logging import logger

router = APIRouter()


@router.post(
    "/classify",
    response_model=WasteClassificationResponse,
    summary="Classify waste type from description"
)
async def classify_waste(request: WasteClassificationRequest):
    """
    Classify waste type using offline AI model.
    
    Uses rule-based classification with keyword matching.
    """
    try:
        ai_service = AIService()
        waste_type, confidence = ai_service.classify_waste_type(request.description)
        
        return WasteClassificationResponse(
            waste_type=waste_type,
            confidence=confidence,
            description=request.description
        )
        
    except Exception as e:
        logger.error(f"Error classifying waste: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to classify waste: {str(e)}"
        )


@router.post(
    "/extract-keywords",
    response_model=KeywordExtractionResponse,
    summary="Extract keywords from text"
)
async def extract_keywords(request: KeywordExtractionRequest):
    """
    Extract important keywords from incident description.
    
    Uses NLP tokenization and frequency analysis.
    """
    try:
        ai_service = AIService()
        keywords = ai_service.extract_keywords(
            request.text,
            top_n=request.top_n
        )
        
        return KeywordExtractionResponse(
            keywords=keywords,
            text=request.text
        )
        
    except Exception as e:
        logger.error(f"Error extracting keywords: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract keywords: {str(e)}"
        )


@router.post(
    "/similar-incidents",
    response_model=SimilarIncidentsResponse,
    summary="Find similar incidents"
)
async def find_similar_incidents(
    request: SimilarIncidentsRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Find similar incidents using semantic similarity.
    
    Uses sentence transformers to generate embeddings and cosine similarity.
    """
    try:
        ai_service = AIService()
        
        # Generate embedding for the description
        embedding = ai_service.generate_embedding(request.description)
        
        # Find similar incidents
        similar = await ai_service.find_similar_incidents(
            db,
            request.incident_id,
            embedding,
            threshold=request.threshold,
            limit=request.limit
        )
        
        return SimilarIncidentsResponse(
            incident_id=request.incident_id,
            similar_incidents=[
                {
                    "id": str(inc.id),
                    "description": inc.description,
                    "location": inc.location,
                    "waste_type": inc.waste_type
                }
                for inc in similar
            ],
            count=len(similar)
        )
        
    except Exception as e:
        logger.error(f"Error finding similar incidents: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to find similar incidents: {str(e)}"
        )
