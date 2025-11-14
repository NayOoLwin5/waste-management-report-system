"""
Analytics API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from app.core.database import get_db
from app.modules.analytics.service import AnalyticsService
from app.modules.analytics.schemas import (
    SummaryStatistics,
    TimeSeriesResponse,
    WasteTypeTrendsResponse,
    HeatmapResponse,
    AnomalyResponse,
    KeywordFrequencyResponse
)
from app.core.logging import logger

router = APIRouter()


@router.get(
    "/summary",
    response_model=SummaryStatistics,
    summary="Get summary statistics"
)
async def get_summary_statistics(
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get summary statistics for the dashboard including:
    - Total incidents
    - Recent incidents (last 7 days)
    - Waste type distribution
    - Top locations
    """
    try:
        stats = await AnalyticsService.get_summary_statistics(
            db,
            start_date=start_date,
            end_date=end_date
        )
        return stats
        
    except Exception as e:
        logger.error(f"Error getting summary statistics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get summary statistics: {str(e)}"
        )


@router.get(
    "/time-series",
    response_model=TimeSeriesResponse,
    summary="Get time series data"
)
async def get_time_series(
    days: int = Query(30, ge=1, le=365, description="Number of days"),
    group_by: str = Query("day", regex="^(day|week|month)$", description="Grouping period"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get time series data for trend visualization.
    
    Can be grouped by day, week, or month.
    """
    try:
        data = await AnalyticsService.get_time_series_data(
            db,
            days=days,
            group_by=group_by
        )
        
        return TimeSeriesResponse(
            data=data,
            group_by=group_by,
            days=days
        )
        
    except Exception as e:
        logger.error(f"Error getting time series data: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get time series data: {str(e)}"
        )


@router.get(
    "/waste-type-trends",
    response_model=WasteTypeTrendsResponse,
    summary="Get waste type trends"
)
async def get_waste_type_trends(
    days: int = Query(30, ge=1, le=365, description="Number of days"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get trends for each waste type over time.
    """
    try:
        trends = await AnalyticsService.get_waste_type_trends(db, days=days)
        
        return WasteTypeTrendsResponse(
            trends=trends,
            days=days
        )
        
    except Exception as e:
        logger.error(f"Error getting waste type trends: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get waste type trends: {str(e)}"
        )


@router.get(
    "/heatmap",
    response_model=HeatmapResponse,
    summary="Get location heatmap data"
)
async def get_heatmap_data(
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get location-based data for heatmap visualization.
    
    Returns incidents with coordinates grouped by location.
    """
    try:
        data = await AnalyticsService.get_location_heatmap_data(
            db,
            start_date=start_date,
            end_date=end_date
        )
        
        return HeatmapResponse(
            data=data,
            total_points=len(data)
        )
        
    except Exception as e:
        logger.error(f"Error getting heatmap data: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get heatmap data: {str(e)}"
        )


@router.get(
    "/anomalies",
    response_model=AnomalyResponse,
    summary="Detect anomalies"
)
async def detect_anomalies(
    threshold_multiplier: float = Query(2.0, ge=1.0, le=5.0, description="Threshold multiplier"),
    db: AsyncSession = Depends(get_db)
):
    """
    Detect anomalies - locations with unusually high incident counts.
    
    Uses statistical analysis to identify outliers.
    """
    try:
        anomalies = await AnalyticsService.detect_anomalies(
            db,
            threshold_multiplier=threshold_multiplier
        )
        
        return AnomalyResponse(
            anomalies=anomalies,
            total_anomalies=len(anomalies)
        )
        
    except Exception as e:
        logger.error(f"Error detecting anomalies: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to detect anomalies: {str(e)}"
        )


@router.get(
    "/keywords",
    response_model=KeywordFrequencyResponse,
    summary="Get keyword frequency"
)
async def get_keyword_frequency(
    limit: int = Query(20, ge=1, le=100, description="Number of keywords"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get most frequent keywords across all incidents.
    
    Useful for identifying common themes.
    """
    try:
        keywords = await AnalyticsService.get_keyword_frequency(db, limit=limit)
        
        return KeywordFrequencyResponse(
            keywords=keywords,
            total_keywords=len(keywords)
        )
        
    except Exception as e:
        logger.error(f"Error getting keyword frequency: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get keyword frequency: {str(e)}"
        )


@router.get(
    "/trends",
    summary="Analyze waste type trends (AI-powered)"
)
async def analyze_trends(
    days: int = Query(30, ge=7, le=365, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """
    AI-powered trend analysis to identify rising and falling waste type patterns.
    
    Returns:
    - Rising trends (waste types increasing over time)
    - Falling trends (waste types decreasing over time)
    - Stable trends (no significant change)
    - New waste types
    - Spike detection (unusual daily activity)
    """
    try:
        trends = await AnalyticsService.analyze_trends(db, days=days)
        return trends
        
    except Exception as e:
        logger.error(f"Error analyzing trends: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze trends: {str(e)}"
        )


@router.get(
    "/admin-summary",
    summary="AI-generated admin summary"
)
async def get_admin_summary(
    days: int = Query(7, ge=1, le=90, description="Number of days to summarize"),
    db: AsyncSession = Depends(get_db)
):
    """
    AI-generated natural language summary of recent waste incident activity.
    
    Provides:
    - Executive summary paragraph
    - Key insights and alerts
    - Trend analysis
    - Hotspot detection
    - Actionable recommendations
    
    No external APIs used - all processing done offline.
    """
    try:
        summary = await AnalyticsService.generate_admin_summary(db, days=days)
        return summary
        
    except Exception as e:
        logger.error(f"Error generating admin summary: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate admin summary: {str(e)}"
        )
