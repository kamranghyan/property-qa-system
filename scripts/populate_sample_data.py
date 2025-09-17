#!/usr/bin/env python3
import asyncio
import httpx
import json
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

async def populate_sample_data():
    """Populate the system with sample property data and embeddings"""
    
    # Load sample properties
    with open('sample_data/properties.json', 'r') as f:
        properties = json.load(f)
    
    async with httpx.AsyncClient() as client:
        print("🏠 Populating sample property data...")
        
        # Add properties via web scraper service
        for i, prop in enumerate(properties):
            try:
                # Simulate scraping by posting to scrape endpoint
                response = await client.post(
                    "http://localhost:8001/scrape",
                    json={"url": prop.get("url", f"https://example.com/property-{i+1}")}
                )
                
                if response.status_code == 200:
                    property_data = response.json()
                    print(f"✅ Added property: {property_data['title']}")
                    
                    # Create embeddings for this property
                    embedding_text = f"{property_data['title']} {property_data['description']} {property_data['location']} {property_data['property_type']}"
                    
                    embed_response = await client.post(
                        "http://localhost:8003/embed",
                        json={
                            "property_id": property_data["id"],
                            "text": embedding_text
                        }
                    )
                    
                    if embed_response.status_code == 200:
                        print(f"🔍 Created embedding for property {property_data['id']}")
                    else:
                        print(f"⚠️  Failed to create embedding for property {property_data['id']}")
                        
                else:
                    print(f"❌ Failed to add property: {prop['title']}")
                    
            except Exception as e:
                print(f"❌ Error adding property {prop['title']}: {e}")
        
        print("\n🎉 Sample data population completed!")

if __name__ == "__main__":
    asyncio.run(populate_sample_data())
