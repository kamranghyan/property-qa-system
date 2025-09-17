from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional
import os
import requests
from datetime import datetime
import json

app = FastAPI(title="Web Scraper Service", version="1.0.0")

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/property_qa")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class PropertyDB(Base):
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String, default="AED")
    bedrooms = Column(Integer)
    bathrooms = Column(Integer)
    area = Column(Float)
    property_type = Column(String)
    location = Column(String)
    description = Column(Text)
    amenities = Column(Text)  # JSON string
    url = Column(String)
    scraped_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

class PropertyModel(BaseModel):
    id: Optional[int] = None
    title: str
    price: float
    currency: str = "AED"
    bedrooms: int
    bathrooms: int
    area: float
    property_type: str
    location: str
    description: str
    amenities: List[str] = []
    url: Optional[str] = None

class ScrapeRequest(BaseModel):
    url: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/scrape", response_model=PropertyModel)
async def scrape_property(request: ScrapeRequest, db: Session = Depends(get_db)):
    """Mock property scraping - in reality would parse PropertyFinder.ae"""
    
    # Mock scraped data (in production, would actually scrape the URL)
    mock_properties = [
        {
            "title": "Luxurious 3BR Villa in Dubai Hills",
            "price": 1850000,
            "bedrooms": 3,
            "bathrooms": 4,
            "area": 2500.0,
            "property_type": "Villa",
            "location": "Dubai Hills Estate",
            "description": "Beautiful 3-bedroom villa with modern amenities, private garden, and swimming pool. Located in the prestigious Dubai Hills Estate with golf course views.",
            "amenities": ["Swimming Pool", "Private Garden", "Golf Course View", "Maid's Room", "Covered Parking"]
        },
        {
            "title": "Modern 2BR Apartment in Downtown Dubai",
            "price": 1200000,
            "bedrooms": 2,
            "bathrooms": 2,
            "area": 1200.0,
            "property_type": "Apartment",
            "location": "Downtown Dubai",
            "description": "Stunning 2-bedroom apartment with Burj Khalifa views. Premium finishes and access to world-class amenities.",
            "amenities": ["Burj Khalifa View", "Gym", "Swimming Pool", "Concierge", "Valet Parking"]
        }
    ]
    
    import random
    property_data = random.choice(mock_properties)
    
    # Save to database
    db_property = PropertyDB(
        title=property_data["title"],
        price=property_data["price"],
        bedrooms=property_data["bedrooms"],
        bathrooms=property_data["bathrooms"],
        area=property_data["area"],
        property_type=property_data["property_type"],
        location=property_data["location"],
        description=property_data["description"],
        amenities=json.dumps(property_data["amenities"]),
        url=request.url
    )
    
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    
    return PropertyModel(
        id=db_property.id,
        title=db_property.title,
        price=db_property.price,
        currency=db_property.currency,
        bedrooms=db_property.bedrooms,
        bathrooms=db_property.bathrooms,
        area=db_property.area,
        property_type=db_property.property_type,
        location=db_property.location,
        description=db_property.description,
        amenities=json.loads(db_property.amenities),
        url=db_property.url
    )

@app.get("/properties/{property_id}", response_model=PropertyModel)
async def get_property(property_id: int, db: Session = Depends(get_db)):
    property_obj = db.query(PropertyDB).filter(PropertyDB.id == property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")
    
    return PropertyModel(
        id=property_obj.id,
        title=property_obj.title,
        price=property_obj.price,
        currency=property_obj.currency,
        bedrooms=property_obj.bedrooms,
        bathrooms=property_obj.bathrooms,
        area=property_obj.area,
        property_type=property_obj.property_type,
        location=property_obj.location,
        description=property_obj.description,
        amenities=json.loads(property_obj.amenities) if property_obj.amenities else [],
        url=property_obj.url
    )

@app.get("/properties", response_model=List[PropertyModel])
async def get_all_properties(db: Session = Depends(get_db)):
    properties = db.query(PropertyDB).all()
    return [
        PropertyModel(
            id=prop.id,
            title=prop.title,
            price=prop.price,
            currency=prop.currency,
            bedrooms=prop.bedrooms,
            bathrooms=prop.bathrooms,
            area=prop.area,
            property_type=prop.property_type,
            location=prop.location,
            description=prop.description,
            amenities=json.loads(prop.amenities) if prop.amenities else [],
            url=prop.url
        )
        for prop in properties
    ]

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "web_scraper", "port": 8001}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
