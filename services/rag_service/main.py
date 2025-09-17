from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import httpx
import os
from typing import List, Dict, Optional
import asyncio
import json

app = FastAPI(title="RAG Service - Main Orchestrator", version="1.0.0")

# Service URLs
WEB_SCRAPER_URL = os.getenv("WEB_SCRAPER_URL", "http://localhost:8001")
AUDIO_TRANSCRIPTION_URL = os.getenv("AUDIO_TRANSCRIPTION_URL", "http://localhost:8002")
VECTOR_DATABASE_URL = os.getenv("VECTOR_DATABASE_URL", "http://localhost:8003")
LLM_INTEGRATION_URL = os.getenv("LLM_INTEGRATION_URL", "http://localhost:8004")

class QueryRequest(BaseModel):
    query: str
    include_similar: bool = True
    max_results: int = 5

class QueryResponse(BaseModel):
    query: str
    answer: str
    matching_properties: List[Dict]
    similar_properties: List[Dict]
    processing_time: float

class VoiceQueryResponse(BaseModel):
    transcription: str
    query: str
    answer: str
    matching_properties: List[Dict]
    confidence: float
    processing_time: float

@app.post("/query", response_model=QueryResponse)
async def process_text_query(request: QueryRequest):
    """Process text-based property query using RAG pipeline"""
    
    import time
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient() as client:
            # Step 1: Get all properties from web scraper
            properties_response = await client.get(f"{WEB_SCRAPER_URL}/properties")
            properties = properties_response.json() if properties_response.status_code == 200 else []
            
            # Step 2: Search for relevant properties using vector database
            search_response = await client.post(
                f"{VECTOR_DATABASE_URL}/search",
                json={"query": request.query, "limit": request.max_results}
            )
            search_results = search_response.json() if search_response.status_code == 200 else []
            
            # Step 3: Prepare context for LLM
            context = []
            matching_properties = []
            
            # Match search results with actual property data
            for result in search_results:
                for prop in properties:
                    if prop["id"] == result["property_id"]:
                        matching_properties.append({
                            **prop,
                            "similarity_score": result["similarity"]
                        })
                        context.append({
                            "property_id": prop["id"],
                            "title": prop["title"],
                            "price": prop["price"],
                            "details": f"{prop['bedrooms']}BR, {prop['bathrooms']}BA, {prop['area']}sqft in {prop['location']}"
                        })
                        break
            
            # Step 4: Get LLM response
            llm_response = await client.post(
                f"{LLM_INTEGRATION_URL}/process-query",
                json={"query": request.query, "context": context}
            )
            llm_result = llm_response.json() if llm_response.status_code == 200 else {"response": "Sorry, I couldn't process your query at the moment."}
            
            # Step 5: Find similar properties if requested
            similar_properties = []
            if request.include_similar and matching_properties:
                for prop in matching_properties[:2]:  # Get similar to top 2 matches
                    similar_response = await client.post(
                        f"{VECTOR_DATABASE_URL}/similarity",
                        json={"property_id": prop["id"], "limit": 3}
                    )
                    if similar_response.status_code == 200:
                        similar_results = similar_response.json()
                        for sim_result in similar_results:
                            for p in properties:
                                if p["id"] == sim_result["property_id"]:
                                    similar_properties.append({
                                        **p,
                                        "similarity_score": sim_result["similarity"]
                                    })
                                    break
            
            processing_time = time.time() - start_time
            
            return QueryResponse(
                query=request.query,
                answer=llm_result.get("response", "No response available"),
                matching_properties=matching_properties,
                similar_properties=similar_properties[:5],  # Limit similar results
                processing_time=processing_time
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/voice-query", response_model=VoiceQueryResponse)
async def process_voice_query(file: UploadFile = File(...)):
    """Process voice-based property query"""
    
    import time
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient() as client:
            # Step 1: Upload audio file to transcription service
            files = {"file": (file.filename, await file.read(), file.content_type)}
            upload_response = await client.post(
                f"{AUDIO_TRANSCRIPTION_URL}/upload-audio",
                files=files
            )
            
            if upload_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to upload audio file")
            
            upload_result = upload_response.json()
            
            # Step 2: Transcribe the audio
            transcription_response = await client.post(
                f"{AUDIO_TRANSCRIPTION_URL}/transcribe-file/{upload_result['file_id']}"
            )
            
            if transcription_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to transcribe audio")
            
            transcription_result = transcription_response.json()
            transcribed_text = transcription_result["transcription"]
            confidence = transcription_result["confidence"]
            
            # Step 3: Process the transcribed text as a regular query
            query_request = QueryRequest(query=transcribed_text)
            text_query_result = await process_text_query(query_request)
            
            processing_time = time.time() - start_time
            
            return VoiceQueryResponse(
                transcription=transcribed_text,
                query=transcribed_text,
                answer=text_query_result.answer,
                matching_properties=text_query_result.matching_properties,
                confidence=confidence,
                processing_time=processing_time
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing voice query: {str(e)}")

@app.post("/voice-query-simple")
async def process_voice_query_simple():
    """Process voice query with mock transcription for testing"""
    
    import time
    start_time = time.time()
    
    try:
        async with httpx.AsyncClient() as client:
            # Step 1: Get mock transcription
            transcription_response = await client.post(
                f"{AUDIO_TRANSCRIPTION_URL}/transcribe",
                json={"language": "en"}
            )
            
            if transcription_response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to get transcription")
            
            transcription_result = transcription_response.json()
            transcribed_text = transcription_result["transcription"]
            
            # Step 2: Process as text query
            query_request = QueryRequest(query=transcribed_text)
            text_query_result = await process_text_query(query_request)
            
            processing_time = time.time() - start_time
            
            return VoiceQueryResponse(
                transcription=transcribed_text,
                query=transcribed_text,
                answer=text_query_result.answer,
                matching_properties=text_query_result.matching_properties,
                confidence=transcription_result["confidence"],
                processing_time=processing_time
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing voice query: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check that also verifies connectivity to all services"""
    
    service_status = {
        "rag_service": {"status": "healthy", "port": 8005}
    }
    
    # Check connectivity to all services
    services = {
        "web_scraper": WEB_SCRAPER_URL,
        "audio_transcription": AUDIO_TRANSCRIPTION_URL,
        "vector_database": VECTOR_DATABASE_URL,
        "llm_integration": LLM_INTEGRATION_URL
    }
    
    async with httpx.AsyncClient() as client:
        for service_name, service_url in services.items():
            try:
                response = await client.get(f"{service_url}/health", timeout=5.0)
                if response.status_code == 200:
                    service_status[service_name] = response.json()
                else:
                    service_status[service_name] = {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
            except Exception as e:
                service_status[service_name] = {"status": "unreachable", "error": str(e)}
    
    return service_status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
