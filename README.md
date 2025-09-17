# Property Listing Q&A System - Microservices Architecture

A complete property listing question-answering system built with microservices architecture, featuring web scraping, audio transcription, vector search, and LLM integration.

## 🏗️ Architecture Overview

The system consists of 5 microservices:

1. **Web Scraper Service** (Port 8001) - Scrapes property data from PropertyFinder.ae
2. **Audio Transcription Service** (Port 8002) - Converts voice queries to text
3. **Vector Database Service** (Port 8003) - Handles embeddings and similarity search
4. **LLM Integration Service** (Port 8004) - Processes natural language queries
5. **RAG Service** (Port 8005) - Main orchestrator combining all services

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.9+ (for running scripts locally)
- At least 4GB RAM available for containers

### 1. Clone and Setup
```bash
git clone <repository-url>
cd property-qa-system

# Create required directories
mkdir -p uploads

### 2. Start All Services
```bash
docker-compose up -d
```

This will start:
- PostgreSQL databases (ports 5432, 5433)
- All 5 microservices (ports 8001-8005)

### 3. Wait for Services to Start
```bash
# Check if all services are healthy
docker-compose ps

# Or use the health endpoint
curl http://localhost:8005/health
```

### 4. Populate Sample Data
```bash
# Install dependencies for scripts
pip install httpx

# Populate sample properties and embeddings
python scripts/populate_sample_data.py
```

### 5. Test the System
```bash
# Run integration tests
python scripts/test_integration.py
```

## 📋 API Documentation

### RAG Service (Main Entry Point) - Port 8005

#### Text Query
```bash
curl -X POST "http://localhost:8005/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me 3-bedroom villas in Dubai under AED 2M with swimming pool",
    "include_similar": true,
    "max_results": 5
  }'
```

#### Voice Query (Mock)
```bash
curl -X POST "http://localhost:8005/voice-query-simple"
```

#### Health Check
```bash
curl "http://localhost:8005/health"
```

### Web Scraper Service - Port 8001

#### Scrape Property
```bash
curl -X POST "http://localhost:8001/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://propertyfinder.ae/test-property"}'
```

#### Get Property
```bash
curl "http://localhost:8001/properties/1"
```

#### Get All Properties
```bash
curl "http://localhost:8001/properties"
```

### Audio Transcription Service - Port 8002

#### Mock Transcription
```bash
curl -X POST "http://localhost:8002/transcribe" \
  -H "Content-Type: application/json" \
  -d '{"language": "en"}'
```

#### Upload Audio File
```bash
curl -X POST "http://localhost:8002/upload-audio" \
  -F "file=@audio.wav"
```

### Vector Database Service - Port 8003

#### Create Embedding
```bash
curl -X POST "http://localhost:8003/embed" \
  -H "Content-Type: application/json" \
  -d '{
    "property_id": 1,
    "text": "Luxury villa with swimming pool in Dubai Hills"
  }'
```

#### Search Properties
```bash
curl -X POST "http://localhost:8003/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "luxury villa swimming pool", "limit": 5}'
```

#### Find Similar Properties
```bash
curl -X POST "http://localhost:8003/similarity" \
  -H "Content-Type: application/json" \
  -d '{"property_id": 1, "limit": 3}'
```

### LLM Integration Service - Port 8004

#### Process Query
```bash
curl -X POST "http://localhost:8004/process-query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tell me about 3-bedroom villas in Dubai",
    "temperature": 0.7,
    "max_tokens": 500
  }'
```

#### Chat Completion
```bash
curl -X POST "http://localhost: