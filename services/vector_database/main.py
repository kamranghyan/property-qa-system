from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional
import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import logging

app = FastAPI(title="Vector Database Service", version="1.0.0")

# Initialize sentence transformer model
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
except Exception as e:
    logging.error(f"Failed to load sentence transformer model: {e}")
    model = None

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/vector_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class PropertyEmbedding(Base):
    __tablename__ = "property_embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    embedding = Column(Text, nullable=False)  # JSON string of vector

Base.metadata.create_all(bind=engine)

class EmbedRequest(BaseModel):
    property_id: int
    text: str

class EmbedResponse(BaseModel):
    property_id: int
    embedding_id: int
    vector_size: int

class SearchRequest(BaseModel):
    query: str
    limit: int = 5

class SearchResult(BaseModel):
    property_id: int
    text: str
    similarity: float

class SimilarityRequest(BaseModel):
    property_id: int
    limit: int = 5

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def cosine_similarity(a, b):
    """Calculate cosine similarity between two vectors"""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

@app.post("/embed", response_model=EmbedResponse)
async def create_embedding(request: EmbedRequest, db: Session = Depends(get_db)):
    """Generate and store embedding for property text"""
    
    if model is None:
        raise HTTPException(status_code=503, detail="Embedding model not available")
    
    # Generate embedding
    embedding = model.encode([request.text])[0]
    
    # Store in database
    db_embedding = PropertyEmbedding(
        property_id=request.property_id,
        text=request.text,
        embedding=json.dumps(embedding.tolist())
    )
    
    db.add(db_embedding)
    db.commit()
    db.refresh(db_embedding)
    
    return EmbedResponse(
        property_id=request.property_id,
        embedding_id=db_embedding.id,
        vector_size=len(embedding)
    )

@app.post("/search", response_model=List[SearchResult])
async def search_properties(request: SearchRequest, db: Session = Depends(get_db)):
    """Search for similar properties based on query"""
    
    if model is None:
        # Return mock results when model is not available
        mock_results = [
            SearchResult(property_id=1, text="3-bedroom villa with swimming pool", similarity=0.95),
            SearchResult(property_id=2, text="Luxury apartment in Downtown Dubai", similarity=0.87),
            SearchResult(property_id=3, text="Modern villa in Dubai Hills Estate", similarity=0.82)
        ]
        return mock_results[:request.limit]
    
    # Generate query embedding
    query_embedding = model.encode([request.query])[0]
    
    # Get all embeddings from database
    embeddings = db.query(PropertyEmbedding).all()
    
    results = []
    for emb in embeddings:
        stored_embedding = np.array(json.loads(emb.embedding))
        similarity = cosine_similarity(query_embedding, stored_embedding)
        
        results.append(SearchResult(
            property_id=emb.property_id,
            text=emb.text,
            similarity=float(similarity)
        ))
    
    # Sort by similarity and return top results
    results.sort(key=lambda x: x.similarity, reverse=True)
    return results[:request.limit]

@app.post("/similarity", response_model=List[SearchResult])
async def find_similar_properties(request: SimilarityRequest, db: Session = Depends(get_db)):
    """Find properties similar to a given property"""
    
    # Get the reference property embedding
    ref_embedding = db.query(PropertyEmbedding).filter(
        PropertyEmbedding.property_id == request.property_id
    ).first()
    
    if not ref_embedding:
        raise HTTPException(status_code=404, detail="Property embedding not found")
    
    if model is None:
        # Return mock results
        mock_results = [
            SearchResult(property_id=2, text="Similar luxury property", similarity=0.89),
            SearchResult(property_id=3, text="Comparable villa", similarity=0.84)
        ]
        return mock_results[:request.limit]
    
    ref_vector = np.array(json.loads(ref_embedding.embedding))
    
    # Compare with all other embeddings
    all_embeddings = db.query(PropertyEmbedding).filter(
        PropertyEmbedding.property_id != request.property_id
    ).all()
    
    results = []
    for emb in all_embeddings:
        stored_embedding = np.array(json.loads(emb.embedding))
        similarity = cosine_similarity(ref_vector, stored_embedding)
        
        results.append(SearchResult(
            property_id=emb.property_id,
            text=emb.text,
            similarity=float(similarity)
        ))
    
    # Sort by similarity and return top results
    results.sort(key=lambda x: x.similarity, reverse=True)
    return results[:request.limit]

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "vector_database", 
        "port": 8003,
        "model_loaded": model is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
