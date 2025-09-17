from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import json
import random

app = FastAPI(title="LLM Integration Service", version="1.0.0")

class QueryRequest(BaseModel):
    query: str
    context: Optional[List[Dict]] = []
    temperature: float = 0.7
    max_tokens: int = 500

class QueryResponse(BaseModel):
    response: str
    model: str
    tokens_used: int
    confidence: float

class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    temperature: float = 0.7
    max_tokens: int = 500

class ChatResponse(BaseModel):
    response: str
    model: str
    tokens_used: int

@app.post("/process-query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process natural language query about properties"""
    
    # Mock LLM responses based on query patterns
    query_lower = request.query.lower()
    
    if "3-bedroom" in query_lower and "villa" in query_lower:
        response = """Based on your search for 3-bedroom villas, I found several excellent options:

1. **Luxurious 3BR Villa in Dubai Hills** - AED 1,850,000
   - 3 bedrooms, 4 bathrooms
   - 2,500 sq ft with private garden and swimming pool
   - Golf course views in prestigious Dubai Hills Estate

2. **Modern Villa in Emirates Hills** - AED 2,200,000
   - 3 bedrooms, 3 bathrooms  
   - Premium location with luxury amenities
   - Private swimming pool and garden

These properties match your criteria and offer excellent value in Dubai's premium residential areas."""

    elif "2-bedroom" in query_lower and "apartment" in query_lower:
        response = """Here are the best 2-bedroom apartments I found:

1. **Modern 2BR Apartment in Downtown Dubai** - AED 1,200,000
   - Stunning Burj Khalifa views
   - Premium finishes and world-class amenities
   - Access to gym, swimming pool, and concierge services

2. **Luxury Apartment in Dubai Marina** - AED 950,000
   - Marina and sea views
   - Modern design with high-end appliances
   - Resort-style amenities

Both properties offer excellent investment potential and lifestyle amenities."""

    elif "swimming pool" in query_lower:
        response = """I found several properties with swimming pools:

1. **Villa in Dubai Hills** - Features private swimming pool and garden
2. **Downtown Apartment** - Access to building's luxury pool and spa
3. **Marina Residence** - Resort-style pool deck with city views

All these properties include swimming pool access as part of their premium amenities package."""

    else:
        response = f"""I understand you're looking for properties in Dubai. Based on your query "{request.query}", I can help you find suitable options. 

Our current inventory includes:
- Luxury villas in Dubai Hills Estate and Emirates Hills
- Modern apartments in Downtown Dubai and Dubai Marina  
- Properties ranging from AED 800K to AED 2.5M
- Various amenities including swimming pools, gyms, and concierge services

Would you like me to provide more specific recommendations based on your budget, preferred location, or desired amenities?"""
    
    return QueryResponse(
        response=response,
        model="gpt-4-turbo-preview",
        tokens_used=random.randint(150, 400),
        confidence=0.92
    )

@app.post("/chat", response_model=ChatResponse)
async def chat_completion(request: ChatRequest):
    """Chat completion endpoint for conversational queries"""
    
    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")
    
    last_message = request.messages[-1]
    
    if last_message.role != "user":
        raise HTTPException(status_code=400, detail="Last message must be from user")
    
    # Generate contextual response based on conversation
    user_message = last_message.content.lower()
    
    if any(word in user_message for word in ["hello", "hi", "hey"]):
        response = "Hello! I'm here to help you find the perfect property in Dubai. What type of property are you looking for today?"
    
    elif "budget" in user_message:
        response = "I'd be happy to help you find properties within your budget. Our current listings range from AED 800,000 for studio apartments to AED 2.5M for luxury villas. What's your preferred price range?"
    
    elif "location" in user_message:
        response = "We have excellent properties in several prime Dubai locations including Downtown Dubai, Dubai Marina, Dubai Hills Estate, Emirates Hills, and Palm Jumeirah. Which area interests you most?"
    
    elif any(word in user_message for word in ["thank", "thanks"]):
        response = "You're welcome! I'm here whenever you need assistance with your property search. Feel free to ask about specific requirements, financing options, or schedule a viewing."
    
    else:
        # Default to processing as a property query
        query_request = QueryRequest(query=last_message.content)
        query_response = await process_query(query_request)
        response = query_response.response
    
    return ChatResponse(
        response=response,
        model="gpt-4-turbo-preview", 
        tokens_used=random.randint(100, 300)
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "llm_integration", "port": 8004}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
