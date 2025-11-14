"""
Analytics Service - Dashboard Data and Insights
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import Counter

from app.modules.incidents.models import Incident
from app.core.logging import logger


class AnalyticsService:
    """Service for generating analytics and dashboard data"""
    
    @staticmethod
    async def get_summary_statistics(
        db: AsyncSession,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get summary statistics for dashboard
        """
        # Build base query
        filters = []
        if start_date:
            filters.append(Incident.timestamp >= start_date)
        if end_date:
            filters.append(Incident.timestamp <= end_date)
        
        # Total incidents
        total_query = select(func.count(Incident.id))
        if filters:
            total_query = total_query.where(and_(*filters))
        total_incidents = await db.scalar(total_query) or 0
        
        # Incidents by waste type
        waste_type_query = (
            select(
                Incident.waste_type,
                func.count(Incident.id).label('count')
            )
            .where(Incident.waste_type.isnot(None))
        )
        if filters:
            waste_type_query = waste_type_query.where(and_(*filters))
        waste_type_query = waste_type_query.group_by(Incident.waste_type)
        
        result = await db.execute(waste_type_query)
        waste_type_distribution = {
            row[0]: row[1] for row in result.fetchall()
        }
        
        # Recent incidents count (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_query = select(func.count(Incident.id)).where(
            Incident.timestamp >= seven_days_ago
        )
        recent_incidents = await db.scalar(recent_query) or 0
        
        # Most common locations
        location_query = (
            select(
                Incident.location,
                func.count(Incident.id).label('count')
            )
            .group_by(Incident.location)
            .order_by(desc('count'))
            .limit(10)
        )
        if filters:
            location_query = location_query.where(and_(*filters))
        
        result = await db.execute(location_query)
        top_locations = [
            {"location": row[0], "count": row[1]}
            for row in result.fetchall()
        ]
        
        return {
            "total_incidents": total_incidents,
            "recent_incidents_7d": recent_incidents,
            "waste_type_distribution": waste_type_distribution,
            "top_locations": top_locations,
            "period": {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
        }
    
    @staticmethod
    async def get_time_series_data(
        db: AsyncSession,
        days: int = 30,
        group_by: str = "day"
    ) -> List[Dict[str, Any]]:
        """
        Get time series data for trend analysis
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Query incidents grouped by time period
        if group_by == "day":
            time_format = func.date(Incident.timestamp)
        elif group_by == "week":
            time_format = func.date_trunc('week', Incident.timestamp)
        else:  # month
            time_format = func.date_trunc('month', Incident.timestamp)
        
        query = (
            select(
                time_format.label('period'),
                func.count(Incident.id).label('count')
            )
            .where(Incident.timestamp >= start_date)
            .group_by('period')
            .order_by('period')
        )
        
        result = await db.execute(query)
        
        time_series = [
            {
                "period": row[0].isoformat() if hasattr(row[0], 'isoformat') else str(row[0]),
                "count": row[1]
            }
            for row in result.fetchall()
        ]
        
        return time_series
    
    @staticmethod
    async def get_waste_type_trends(
        db: AsyncSession,
        days: int = 30
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get waste type trends over time
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = (
            select(
                func.date(Incident.timestamp).label('date'),
                Incident.waste_type,
                func.count(Incident.id).label('count')
            )
            .where(
                and_(
                    Incident.timestamp >= start_date,
                    Incident.waste_type.isnot(None)
                )
            )
            .group_by('date', Incident.waste_type)
            .order_by('date')
        )
        
        result = await db.execute(query)
        
        # Organize by waste type
        trends = {}
        for row in result.fetchall():
            waste_type = row[1]
            if waste_type not in trends:
                trends[waste_type] = []
            
            trends[waste_type].append({
                "date": row[0].isoformat(),
                "count": row[2]
            })
        
        return trends
    
    @staticmethod
    async def get_location_heatmap_data(
        db: AsyncSession,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get location-based incident data for heatmap visualization
        """
        filters = [
            Incident.latitude.isnot(None),
            Incident.longitude.isnot(None)
        ]
        
        if start_date:
            filters.append(Incident.timestamp >= start_date)
        if end_date:
            filters.append(Incident.timestamp <= end_date)
        
        query = (
            select(
                Incident.location,
                Incident.latitude,
                Incident.longitude,
                func.count(Incident.id).label('count')
            )
            .where(and_(*filters))
            .group_by(Incident.location, Incident.latitude, Incident.longitude)
        )
        
        result = await db.execute(query)
        
        heatmap_data = [
            {
                "location": row[0],
                "latitude": float(row[1]),
                "longitude": float(row[2]),
                "count": row[3]
            }
            for row in result.fetchall()
        ]
        
        return heatmap_data
    
    @staticmethod
    async def detect_anomalies(
        db: AsyncSession,
        threshold_multiplier: float = 2.0
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies - locations or time periods with unusually high incident counts
        """
        # Get incidents per location
        location_query = (
            select(
                Incident.location,
                func.count(Incident.id).label('count')
            )
            .group_by(Incident.location)
        )
        
        result = await db.execute(location_query)
        location_counts = [row[1] for row in result.fetchall()]
        
        if not location_counts:
            return []
        
        # Calculate mean and threshold
        mean_count = sum(location_counts) / len(location_counts)
        threshold = mean_count * threshold_multiplier
        
        # Find anomalous locations
        anomaly_query = (
            select(
                Incident.location,
                func.count(Incident.id).label('count')
            )
            .group_by(Incident.location)
            .having(func.count(Incident.id) > threshold)
        )
        
        result = await db.execute(anomaly_query)
        
        anomalies = [
            {
                "location": row[0],
                "count": row[1],
                "mean": round(mean_count, 2),
                "threshold": round(threshold, 2),
                "severity": "high" if row[1] > threshold * 1.5 else "medium"
            }
            for row in result.fetchall()
        ]
        
        logger.info(f"Detected {len(anomalies)} anomalous locations")
        
        return anomalies
    
    @staticmethod
    async def get_keyword_frequency(
        db: AsyncSession,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get most frequent keywords across all incidents
        """
        query = select(Incident.keywords).where(Incident.keywords.isnot(None))
        result = await db.execute(query)
        
        # Flatten all keywords
        all_keywords = []
        for row in result.fetchall():
            if row[0]:
                all_keywords.extend(row[0])
        
        # Count frequencies
        keyword_counts = Counter(all_keywords)
        
        # Get top N
        top_keywords = [
            {"keyword": keyword, "count": count}
            for keyword, count in keyword_counts.most_common(limit)
        ]
        
        return top_keywords
    
    @staticmethod
    async def analyze_trends(
        db: AsyncSession,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        AI-powered trend analysis - identify rising/falling waste type patterns
        
        Uses statistical analysis to detect:
        - Rising waste types (increasing over time)
        - Falling waste types (decreasing over time)
        - Stable waste types (no significant change)
        - Spikes (sudden increases)
        """
        # Get data for current period and previous period
        current_end = datetime.utcnow()
        current_start = current_end - timedelta(days=days)
        previous_start = current_start - timedelta(days=days)
        
        # Get waste type counts for current period
        current_query = (
            select(
                Incident.waste_type,
                func.count(Incident.id).label('count')
            )
            .where(
                and_(
                    Incident.timestamp >= current_start,
                    Incident.timestamp <= current_end,
                    Incident.waste_type.isnot(None)
                )
            )
            .group_by(Incident.waste_type)
        )
        
        result = await db.execute(current_query)
        current_counts = {row[0]: row[1] for row in result.fetchall()}
        
        # Get waste type counts for previous period
        previous_query = (
            select(
                Incident.waste_type,
                func.count(Incident.id).label('count')
            )
            .where(
                and_(
                    Incident.timestamp >= previous_start,
                    Incident.timestamp < current_start,
                    Incident.waste_type.isnot(None)
                )
            )
            .group_by(Incident.waste_type)
        )
        
        result = await db.execute(previous_query)
        previous_counts = {row[0]: row[1] for row in result.fetchall()}
        
        # Analyze trends
        rising_trends = []
        falling_trends = []
        stable_trends = []
        new_types = []
        
        all_waste_types = set(current_counts.keys()) | set(previous_counts.keys())
        
        for waste_type in all_waste_types:
            current = current_counts.get(waste_type, 0)
            previous = previous_counts.get(waste_type, 0)
            
            if previous == 0 and current > 0:
                # New waste type appeared
                new_types.append({
                    "waste_type": waste_type,
                    "count": current,
                    "trend": "new"
                })
            elif previous > 0:
                # Calculate percentage change
                change = ((current - previous) / previous) * 100
                
                trend_item = {
                    "waste_type": waste_type,
                    "current_count": current,
                    "previous_count": previous,
                    "change_percentage": round(change, 1),
                    "change_absolute": current - previous
                }
                
                # Classify trend (threshold: 20% change)
                if change > 20:
                    trend_item["trend"] = "rising"
                    trend_item["severity"] = "high" if change > 50 else "medium"
                    rising_trends.append(trend_item)
                elif change < -20:
                    trend_item["trend"] = "falling"
                    trend_item["severity"] = "high" if change < -50 else "medium"
                    falling_trends.append(trend_item)
                else:
                    trend_item["trend"] = "stable"
                    stable_trends.append(trend_item)
        
        # Sort by absolute change
        rising_trends.sort(key=lambda x: abs(x['change_percentage']), reverse=True)
        falling_trends.sort(key=lambda x: abs(x['change_percentage']), reverse=True)
        
        # Detect spikes (day-over-day analysis for last 7 days)
        spikes = await AnalyticsService._detect_daily_spikes(db, days=7)
        
        logger.info(
            "Trend analysis completed",
            rising=len(rising_trends),
            falling=len(falling_trends),
            stable=len(stable_trends),
            new=len(new_types),
            spikes=len(spikes)
        )
        
        return {
            "period_days": days,
            "analysis_date": current_end.isoformat(),
            "rising_trends": rising_trends,
            "falling_trends": falling_trends,
            "stable_trends": stable_trends,
            "new_waste_types": new_types,
            "spikes": spikes,
            "summary": {
                "total_waste_types": len(all_waste_types),
                "trending_up": len(rising_trends),
                "trending_down": len(falling_trends),
                "stable": len(stable_trends)
            }
        }
    
    @staticmethod
    async def _detect_daily_spikes(
        db: AsyncSession,
        days: int = 7,
        spike_threshold: float = 2.5
    ) -> List[Dict[str, Any]]:
        """
        Detect daily spikes - days with unusually high incident counts
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get daily counts
        query = (
            select(
                func.date(Incident.timestamp).label('date'),
                func.count(Incident.id).label('count')
            )
            .where(Incident.timestamp >= start_date)
            .group_by('date')
            .order_by('date')
        )
        
        result = await db.execute(query)
        daily_counts = [(row[0], row[1]) for row in result.fetchall()]
        
        if len(daily_counts) < 3:
            return []
        
        # Calculate mean and standard deviation
        counts = [count for _, count in daily_counts]
        mean_count = sum(counts) / len(counts)
        variance = sum((x - mean_count) ** 2 for x in counts) / len(counts)
        std_dev = variance ** 0.5
        
        threshold = mean_count + (spike_threshold * std_dev)
        
        # Find spikes
        spikes = []
        for date, count in daily_counts:
            if count > threshold:
                spikes.append({
                    "date": date.isoformat(),
                    "count": count,
                    "mean": round(mean_count, 1),
                    "threshold": round(threshold, 1),
                    "severity": "high" if count > mean_count + (4 * std_dev) else "medium"
                })
        
        return spikes
    
    @staticmethod
    async def generate_admin_summary(
        db: AsyncSession,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        AI-Generated Admin Summary - Natural language summary of recent activity
        
        Generates insights using:
        - Statistical analysis
        - Trend detection
        - Keyword extraction
        - Pattern recognition
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get basic statistics
        stats = await AnalyticsService.get_summary_statistics(
            db,
            start_date=start_date,
            end_date=end_date
        )
        
        # Get trends
        trends = await AnalyticsService.analyze_trends(db, days=days)
        
        # Get anomalies
        anomalies = await AnalyticsService.detect_anomalies(db, threshold_multiplier=2.0)
        
        # Get top keywords
        keywords = await AnalyticsService.get_keyword_frequency(db, limit=10)
        
        # Generate natural language insights
        insights = []
        
        # Overview insight
        total = stats['total_incidents']
        if total > 0:
            insights.append({
                "type": "overview",
                "severity": "info",
                "text": f"📊 {total} incident{'s' if total != 1 else ''} reported in the last {days} days",
                "data": {"count": total, "period_days": days}
            })
        
        # Rising trends insights
        if trends['rising_trends']:
            top_rising = trends['rising_trends'][0]
            insights.append({
                "type": "trend_rising",
                "severity": "warning" if top_rising.get('severity') == 'high' else "info",
                "text": f"📈 {top_rising['waste_type'].title()} waste is rising: {top_rising['change_percentage']:+.0f}% increase ({top_rising['current_count']} incidents, up from {top_rising['previous_count']})",
                "data": top_rising
            })
        
        # Falling trends insights
        if trends['falling_trends']:
            top_falling = trends['falling_trends'][0]
            insights.append({
                "type": "trend_falling",
                "severity": "success",
                "text": f"📉 {top_falling['waste_type'].title()} waste is declining: {top_falling['change_percentage']:.0f}% decrease (good progress!)",
                "data": top_falling
            })
        
        # New waste types
        if trends['new_waste_types']:
            new_types = [t['waste_type'] for t in trends['new_waste_types']]
            insights.append({
                "type": "new_category",
                "severity": "info",
                "text": f"🆕 New waste type{'s' if len(new_types) > 1 else ''} detected: {', '.join(new_types)}",
                "data": trends['new_waste_types']
            })
        
        # Spike detection
        if trends['spikes']:
            recent_spike = trends['spikes'][-1]  # Most recent spike
            insights.append({
                "type": "spike",
                "severity": "warning",
                "text": f"⚠️ Unusual activity spike detected on {recent_spike['date']}: {recent_spike['count']} incidents (normally {recent_spike['mean']:.0f})",
                "data": recent_spike
            })
        
        # Anomaly detection
        if anomalies:
            top_anomaly = anomalies[0]
            insights.append({
                "type": "hotspot",
                "severity": "error" if top_anomaly.get('severity') == 'high' else "warning",
                "text": f"🔥 Hotspot alert: {top_anomaly['location']} has {top_anomaly['count']} incidents (well above average of {top_anomaly['mean']})",
                "data": top_anomaly
            })
        
        # Most common waste type
        if stats['waste_type_distribution']:
            most_common = max(
                stats['waste_type_distribution'].items(),
                key=lambda x: x[1]
            )
            percentage = (most_common[1] / total * 100) if total > 0 else 0
            insights.append({
                "type": "dominant_type",
                "severity": "info",
                "text": f"🏆 Most common waste type: {most_common[0].title()} ({most_common[1]} incidents, {percentage:.0f}% of total)",
                "data": {"waste_type": most_common[0], "count": most_common[1], "percentage": round(percentage, 1)}
            })
        
        # Top keywords insight
        if keywords:
            top_5_keywords = [k['keyword'] for k in keywords[:5]]
            insights.append({
                "type": "keywords",
                "severity": "info",
                "text": f"🔑 Common themes: {', '.join(top_5_keywords)}",
                "data": {"keywords": top_5_keywords}
            })
        
        # Location hotspots
        if stats['top_locations']:
            top_loc = stats['top_locations'][0]
            insights.append({
                "type": "location",
                "severity": "info",
                "text": f"📍 Most affected location: {top_loc['location']} ({top_loc['count']} incidents)",
                "data": top_loc
            })
        
        # Generate executive summary (single paragraph)
        executive_summary = AnalyticsService._generate_executive_summary(
            total, trends, anomalies, stats, days
        )
        
        logger.info(f"Generated admin summary with {len(insights)} insights")
        
        return {
            "generated_at": end_date.isoformat(),
            "period_days": days,
            "executive_summary": executive_summary,
            "insights": insights,
            "statistics": stats,
            "trends": trends,
            "anomalies": anomalies
        }
    
    @staticmethod
    def _generate_executive_summary(
        total: int,
        trends: Dict[str, Any],
        anomalies: List[Dict[str, Any]],
        stats: Dict[str, Any],
        days: int
    ) -> str:
        """
        Generate a concise executive summary paragraph
        """
        parts = []
        
        # Opening
        parts.append(f"In the past {days} days, {total} waste incident{'s were' if total != 1 else ' was'} reported")
        
        # Trending information
        if trends['rising_trends']:
            top_rising = trends['rising_trends'][0]
            parts.append(f"with {top_rising['waste_type']} waste showing a significant increase of {top_rising['change_percentage']:+.0f}%")
        
        # Hotspot information
        if anomalies:
            parts.append(f"A hotspot was identified at {anomalies[0]['location']} with {anomalies[0]['count']} incidents")
        
        # Most common type
        if stats['waste_type_distribution']:
            most_common = max(stats['waste_type_distribution'].items(), key=lambda x: x[1])
            parts.append(f"{most_common[0].title()} waste remains the most common type with {most_common[1]} incidents")
        
        # Positive trend if exists
        if trends['falling_trends']:
            parts.append(f"while {trends['falling_trends'][0]['waste_type']} waste has decreased by {abs(trends['falling_trends'][0]['change_percentage']):.0f}%")
        
        summary = ". ".join(parts) + "."
        
        return summary
