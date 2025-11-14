"""
Analytics Module Schemas
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class SummaryStatistics(BaseModel):
    """Summary statistics for dashboard"""
    total_incidents: int
    recent_incidents_7d: int
    waste_type_distribution: Dict[str, int]
    top_locations: List[Dict[str, Any]]
    period: Dict[str, Optional[str]]


class TimeSeriesDataPoint(BaseModel):
    """Time series data point"""
    period: str
    count: int


class TimeSeriesResponse(BaseModel):
    """Time series response"""
    data: List[TimeSeriesDataPoint]
    group_by: str
    days: int


class WasteTypeTrend(BaseModel):
    """Waste type trend data"""
    date: str
    count: int


class WasteTypeTrendsResponse(BaseModel):
    """Waste type trends response"""
    trends: Dict[str, List[Dict[str, Any]]]
    days: int


class HeatmapDataPoint(BaseModel):
    """Heatmap data point"""
    location: str
    latitude: float
    longitude: float
    count: int


class HeatmapResponse(BaseModel):
    """Heatmap response"""
    data: List[HeatmapDataPoint]
    total_points: int


class Anomaly(BaseModel):
    """Anomaly detection result"""
    location: str
    count: int
    mean: float
    threshold: float
    severity: str


class AnomalyResponse(BaseModel):
    """Anomaly detection response"""
    anomalies: List[Anomaly]
    total_anomalies: int


class KeywordFrequency(BaseModel):
    """Keyword frequency data"""
    keyword: str
    count: int


class KeywordFrequencyResponse(BaseModel):
    """Keyword frequency response"""
    keywords: List[KeywordFrequency]
    total_keywords: int
