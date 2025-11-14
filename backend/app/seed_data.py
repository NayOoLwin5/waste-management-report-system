"""
Database Seeding Script - Generate Realistic Mock Data

This script generates realistic waste incident data for demonstration purposes:
- Various waste types distributed realistically
- Multiple locations with some hotspots
- Time distribution over past 60 days
- Realistic descriptions using templates
"""
import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.modules.incidents.models import Incident
from app.modules.ai.service import AIService
from app.core.logging import logger


# Realistic incident templates by waste type
INCIDENT_TEMPLATES = {
    "plastic": [
        "Large pile of plastic bottles and bags near {location}",
        "PET bottles and plastic packaging scattered around {location}",
        "Plastic waste including bottles, straws, and containers dumped at {location}",
        "Discarded plastic bags and food containers found in {location}",
        "Plastic bottles and packaging waste accumulating at {location}",
        "Single-use plastic waste including cups and utensils at {location}",
        "Plastic shopping bags and beverage bottles littering {location}",
    ],
    "organic": [
        "Food waste and organic materials rotting near {location}",
        "Spoiled vegetables and food scraps dumped at {location}",
        "Rotten food waste attracting pests at {location}",
        "Kitchen waste including vegetable peels and food leftovers at {location}",
        "Decomposing organic waste creating odor problems at {location}",
        "Restaurant food waste improperly disposed at {location}",
        "Garden waste and organic materials piled up at {location}",
    ],
    "paper": [
        "Cardboard boxes and paper waste discarded at {location}",
        "Old newspapers and magazines dumped near {location}",
        "Paper packaging and cardboard scattered around {location}",
        "Pizza boxes and paper waste left at {location}",
        "Stacks of cardboard and paper materials at {location}",
        "Paper cups and cardboard containers littering {location}",
        "Office paper waste and documents found at {location}",
    ],
    "electronic": [
        "Old computer monitors and keyboards dumped at {location}",
        "Broken smartphones and electronic devices at {location}",
        "E-waste including cables and electronic components at {location}",
        "Discarded television and computer equipment near {location}",
        "Electronic waste including phones and chargers at {location}",
        "Old laptops and electronic gadgets abandoned at {location}",
        "Broken electronics and circuit boards found at {location}",
    ],
    "glass": [
        "Broken glass bottles and jars scattered at {location}",
        "Beer and wine bottles discarded near {location}",
        "Broken glass containers creating safety hazard at {location}",
        "Glass bottles and jars dumped at {location}",
        "Shattered glass and bottle fragments at {location}",
        "Empty liquor bottles and glass waste at {location}",
        "Glass containers and broken windowpane at {location}",
    ],
    "metal": [
        "Aluminum cans and metal scraps at {location}",
        "Discarded metal containers and tin cans near {location}",
        "Rusty metal parts and aluminum waste at {location}",
        "Steel cans and metal packaging dumped at {location}",
        "Metal scrap and aluminum beverage cans at {location}",
        "Iron debris and metal waste materials at {location}",
        "Aluminum foil and metal containers littering {location}",
    ],
    "hazardous": [
        "Chemical containers and hazardous materials at {location}",
        "Paint cans and chemical waste improperly stored at {location}",
        "Batteries and hazardous waste requiring special disposal at {location}",
        "Medical waste and syringes found near {location}",
        "Chemical spill and hazardous materials at {location}",
        "Toxic substances and dangerous waste at {location}",
        "Pharmaceutical waste and expired medications at {location}",
    ],
    "textile": [
        "Old clothes and fabric waste dumped at {location}",
        "Discarded clothing and shoes piled at {location}",
        "Textile waste including torn fabrics and garments at {location}",
        "Used clothing and fabric scraps at {location}",
        "Worn-out shoes and textile materials at {location}",
        "Unwanted clothing and fabric waste near {location}",
        "Textile scraps and old garments dumped at {location}",
    ],
    "construction": [
        "Construction debris and building materials at {location}",
        "Concrete rubble and construction waste dumped at {location}",
        "Wood planks and construction debris near {location}",
        "Building materials and renovation waste at {location}",
        "Demolished concrete and construction rubble at {location}",
        "Timber and construction material waste at {location}",
        "Broken tiles and construction debris at {location}",
    ],
}

# Locations with weighted probabilities (some are hotspots)
LOCATIONS = [
    # Hotspots (higher probability)
    ("Central Park", 0.15, 13.7563, 100.5018),
    ("Downtown Plaza", 0.12, 13.7650, 100.5380),
    ("Riverside Park", 0.10, 13.7270, 100.5240),
    
    # Medium frequency
    ("Market Street", 0.08, 13.7560, 100.5020),
    ("Industrial Area", 0.08, 13.7890, 100.5670),
    ("Shopping Mall", 0.07, 13.7450, 100.5340),
    ("Beach Road", 0.07, 13.7200, 100.4980),
    
    # Lower frequency
    ("University Campus", 0.05, 13.7920, 100.5780),
    ("Hospital District", 0.05, 13.7340, 100.5120),
    ("Business Park", 0.04, 13.7780, 100.5890),
    ("Residential Area A", 0.04, 13.7430, 100.4870),
    ("Residential Area B", 0.04, 13.7510, 100.5450),
    ("Sports Complex", 0.03, 13.7690, 100.5560),
    ("Train Station", 0.03, 13.7820, 100.5230),
    ("Airport Road", 0.02, 13.8100, 100.6020),
    ("Suburb District", 0.02, 13.7120, 100.4750),
    ("Village Center", 0.01, 13.6980, 100.4560),
]

# Waste type distribution (realistic mix)
WASTE_TYPE_WEIGHTS = {
    "plastic": 0.30,  # Most common
    "organic": 0.20,
    "paper": 0.15,
    "glass": 0.10,
    "metal": 0.08,
    "electronic": 0.06,
    "construction": 0.05,
    "textile": 0.04,
    "hazardous": 0.02,  # Least common
}


class DataSeeder:
    """Generate and insert realistic mock data"""
    
    def __init__(self):
        self.ai_service = None
    
    async def initialize(self):
        """Initialize AI service"""
        self.ai_service = AIService()
        await self.ai_service.initialize()
        logger.info("AI Service initialized for seeding")
    
    def generate_weighted_choice(self, items: List[tuple], weights: List[float]) -> Any:
        """Choose item based on weights"""
        return random.choices(items, weights=weights, k=1)[0]
    
    def generate_timestamp(self, days_ago_range: tuple = (0, 60)) -> datetime:
        """Generate random timestamp within range"""
        min_days, max_days = days_ago_range
        days_ago = random.randint(min_days, max_days)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        
        return datetime.utcnow() - timedelta(
            days=days_ago,
            hours=hours_ago,
            minutes=minutes_ago
        )
    
    def generate_incident_description(self, waste_type: str, location: str) -> str:
        """Generate realistic incident description"""
        if waste_type in INCIDENT_TEMPLATES:
            template = random.choice(INCIDENT_TEMPLATES[waste_type])
            return template.format(location=location)
        return f"Waste incident at {location}"
    
    async def create_incident(
        self,
        db: AsyncSession,
        description: str,
        location: str,
        latitude: float,
        longitude: float,
        timestamp: datetime
    ) -> Incident:
        """Create single incident with AI processing"""
        try:
            # Process with AI
            ai_result = await self.ai_service.process_incident(description, location)
            
            # Create incident
            incident = Incident(
                description=description,
                timestamp=timestamp,
                location=location,
                latitude=latitude,
                longitude=longitude,
                waste_type=ai_result['waste_type'],
                waste_type_confidence=ai_result['confidence'],
                keywords=ai_result['keywords'],
                embedding=ai_result['embedding']
            )
            
            db.add(incident)
            return incident
            
        except Exception as e:
            logger.error(f"Error creating incident: {str(e)}")
            raise
    
    async def seed_incidents(
        self,
        db: AsyncSession,
        count: int = 100,
        create_trends: bool = True
    ):
        """
        Seed database with realistic incidents
        
        Args:
            count: Number of incidents to create
            create_trends: Whether to create trending patterns
        """
        logger.info(f"Starting to seed {count} incidents...")
        
        incidents_created = 0
        
        # Generate incidents with time distribution
        for i in range(count):
            try:
                # Select waste type based on weights
                waste_types = list(WASTE_TYPE_WEIGHTS.keys())
                weights = list(WASTE_TYPE_WEIGHTS.values())
                
                # Create recent trend for plastic (last 2 weeks)
                if create_trends and i < count * 0.3 and random.random() < 0.6:
                    # 30% of incidents in last 2 weeks, 60% plastic for trend
                    waste_type = "plastic"
                    timestamp = self.generate_timestamp((0, 14))
                else:
                    waste_type = random.choices(waste_types, weights=weights, k=1)[0]
                    timestamp = self.generate_timestamp((0, 60))
                
                # Select location based on weights
                location_weights = [loc[1] for loc in LOCATIONS]
                location_data = self.generate_weighted_choice(LOCATIONS, location_weights)
                location, _, latitude, longitude = location_data
                
                # Generate description
                description = self.generate_incident_description(waste_type, location)
                
                # Create incident
                await self.create_incident(
                    db,
                    description,
                    location,
                    latitude,
                    longitude,
                    timestamp
                )
                
                incidents_created += 1
                
                # Commit in batches for performance
                if (i + 1) % 10 == 0:
                    await db.commit()
                    logger.info(f"Created {incidents_created}/{count} incidents...")
                    
            except Exception as e:
                logger.error(f"Error creating incident {i}: {str(e)}")
                await db.rollback()
                continue
        
        # Final commit
        await db.commit()
        logger.info(f"✅ Successfully seeded {incidents_created} incidents!")
        
        return incidents_created
    
    async def seed_database(self, count: int = 100):
        """Main seeding function"""
        logger.info("="*60)
        logger.info("DATABASE SEEDING STARTED")
        logger.info("="*60)
        
        await self.initialize()
        
        async with AsyncSessionLocal() as db:
            try:
                # Check if data already exists
                from sqlalchemy import select, func
                result = await db.execute(select(func.count(Incident.id)))
                existing_count = result.scalar() or 0
                
                if existing_count > 0:
                    logger.warning(f"Database already has {existing_count} incidents")
                    logger.info("Skipping seeding. To re-seed, clear database first.")
                    return
                
                # Seed data
                incidents_created = await self.seed_incidents(db, count=count)
                await db.commit()
                
                logger.info("="*60)
                logger.info("DATABASE SEEDING COMPLETED")
                logger.info(f"Total incidents created: {incidents_created}")
                logger.info("="*60)
            except Exception as e:
                await db.rollback()
                logger.error(f"Failed to seed database: {e}")
                raise


async def main():
    """CLI entry point"""
    import sys
    
    count = 100
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            logger.error("Invalid count argument. Using default: 100")
    
    seeder = DataSeeder()
    await seeder.seed_database(count=count)


if __name__ == "__main__":
    asyncio.run(main())
