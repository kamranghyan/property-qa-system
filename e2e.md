How to Run the Project End-to-End
Prerequisites Check

Ensure Docker and Docker Compose are installed
Verify you have at least 4GB RAM available
Check that ports 5432, 5433, and 8001-8005 are free

Step-by-Step Execution
1. Environment Setup
bash# Navigate to project directory
cd property-qa-system

# Create necessary directories
mkdir -p uploads sample_data scripts services/web_scraper services/audio_transcription services/vector_database services/llm_integration services/rag_service
2. Start the Infrastructure
bash# Start all services with Docker Compose
docker-compose up -d

# Monitor startup logs
docker-compose logs -f
3. Verify Services Are Running
bash# Check container status
docker-compose ps

# Verify all services are healthy (wait 2-3 minutes for full startup)
curl http://localhost:8005/health
4. Initialize Data
bash# Install Python dependencies for scripts
pip install httpx

# Populate sample data and create embeddings
python scripts/populate_sample_data.py
Testing the System
Automated Integration Tests
bash# Run comprehensive integration tests
python scripts/test_integration.py
Manual API Testing
Test the main RAG pipeline:
bash# Text-based property query
curl -X POST "http://localhost:8005/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me 3-bedroom villas in Dubai under AED 2M with swimming pool",
    "include_similar": true,
    "max_results": 5
  }'
Test voice query (mock):
bashcurl -X POST "http://localhost:8005/voice-query-simple"
Test individual services:
bash# Web scraper
curl -X POST "http://localhost:8001/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://propertyfinder.ae/test-property"}'

# Audio transcription
curl -X POST "http://localhost:8002/transcribe" \
  -H "Content-Type: application/json" \
  -d '{"language": "en"}'

# Vector search
curl -X POST "http://localhost:8003/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "luxury villa swimming pool", "limit": 5}'

# LLM processing
curl -X POST "http://localhost:8004/process-query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about 3-bedroom villas in Dubai"}'
Understanding the Data Flow

Property Ingestion: Web scraper service collects property data and stores in PostgreSQL
Embedding Creation: Vector database service generates embeddings for property descriptions
Query Processing: RAG service orchestrates the entire pipeline:

Audio queries → transcription service → text
Text queries → vector search for relevant properties
Context + query → LLM service → natural language response


Response Assembly: Combined results with matching properties and similar suggestions

Expected Behavior
Successful Startup

All containers should show "healthy" status
Health endpoint should return status for all 5 services
Sample data script should confirm property additions and embeddings

Query Responses

Text queries should return structured responses with property matches
Voice queries should include transcription confidence scores
Similar properties should be ranked by similarity scores
Processing times should typically be under 2-3 seconds

Common Issues and Solutions
Service Connectivity Issues:

Wait longer for services to fully initialize (up to 5 minutes)
Check Docker container logs for specific errors
Verify database connections are established

Vector Database Model Loading:

The sentence transformer model downloads on first run
May take several minutes depending on internet connection
Falls back to mock responses if model fails to load

Memory Issues:

Ensure sufficient RAM is available
Consider reducing the number of concurrent services during development

Monitoring and Debugging
View logs:
bash# All services
docker-compose logs

# Specific service
docker-compose logs web_scraper
Database access:
bash# Connect to main database
docker exec -it property-qa-system_postgres_1 psql -U postgres -d property_qa

# Connect to vector database
docker exec -it property-qa-system_postgres_vector_1 psql -U postgres -d vector_db
This microservices architecture provides a scalable foundation for property search with natural language processing capabilities. Each service can be independently scaled, updated, or replaced while maintaining the overall system functionality.