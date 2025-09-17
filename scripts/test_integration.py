import asyncio
import httpx
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

async def test_integration():
    """Test the complete integration between all services"""
    
    print("🧪 Starting Integration Tests\n")
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Health checks for all services
        print("1️⃣ Testing service health...")
        services = [
            ("Web Scraper", "http://localhost:8001/health"),
            ("Audio Transcription", "http://localhost:8002/health"),
            ("Vector Database", "http://localhost:8003/health"),
            ("LLM Integration", "http://localhost:8004/health"),
            ("RAG Service", "http://localhost:8005/health")
        ]
        
        for name, url in services:
            try:
                response = await client.get(url, timeout=10.0)
                if response.status_code == 200:
                    print(f"   ✅ {name}: Healthy")
                else:
                    print(f"   ❌ {name}: Unhealthy (HTTP {response.status_code})")
            except Exception as e:
                print(f"   ❌ {name}: Unreachable ({e})")
        
        print()
        
        # Test 2: Text-based query
        print("2️⃣ Testing text query: '3-bedroom villa with swimming pool'")
        try:
            response = await client.post(
                "http://localhost:8005/query",
                json={
                    "query": "Show me 3-bedroom villas in Dubai under AED 2M with swimming pool",
                    "include_similar": True,
                    "max_results": 3
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Query processed successfully")
                print(f"   📝 Answer: {result['answer'][:100]}...")
                print(f"   🏠 Found {len(result['matching_properties'])} matching properties")
                print(f"   🔍 Found {len(result['similar_properties'])} similar properties")
                print(f"   ⏱️  Processing time: {result['processing_time']:.2f}s")
            else:
                print(f"   ❌ Query failed (HTTP {response.status_code})")
                
        except Exception as e:
            print(f"   ❌ Query error: {e}")
        
        print()
        
        # Test 3: Voice query (mock)
        print("3️⃣ Testing voice query (mock transcription)")
        try:
            response = await client.post("http://localhost:8005/voice-query-simple")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Voice query processed successfully")
                print(f"   🎤 Transcription: {result['transcription']}")
                print(f"   📝 Answer: {result['answer'][:100]}...")
                print(f"   🏠 Found {len(result['matching_properties'])} matching properties")
                print(f"   🎯 Confidence: {result['confidence']}")
                print(f"   ⏱️  Processing time: {result['processing_time']:.2f}s")
            else:
                print(f"   ❌ Voice query failed (HTTP {response.status_code})")
                
        except Exception as e:
            print(f"   ❌ Voice query error: {e}")
        
        print()
        
        # Test 4: Individual service tests
        print("4️⃣ Testing individual services")
        
        # Test property scraping
        try:
            response = await client.post(
                "http://localhost:8001/scrape",
                json={"url": "https://propertyfinder.ae/test-property"}
            )
            if response.status_code == 200:
                print("   ✅ Property scraping works")
            else:
                print(f"   ❌ Property scraping failed (HTTP {response.status_code})")
        except Exception as e:
            print(f"   ❌ Property scraping error: {e}")
        
        # Test transcription
        try:
            response = await client.post(
                "http://localhost:8002/transcribe",
                json={"language": "en"}
            )
            if response.status_code == 200:
                print("   ✅ Audio transcription works")
            else:
                print(f"   ❌ Audio transcription failed (HTTP {response.status_code})")
        except Exception as e:
            print(f"   ❌ Audio transcription error: {e}")
        
        # Test vector search
        try:
            response = await client.post(
                "http://localhost:8003/search",
                json={"query": "luxury villa", "limit": 3}
            )
            if response.status_code == 200:
                print("   ✅ Vector search works")
            else:
                print(f"   ❌ Vector search failed (HTTP {response.status_code})")
        except Exception as e:
            print(f"   ❌ Vector search error: {e}")
        
        # Test LLM processing
        try:
            response = await client.post(
                "http://localhost:8004/process-query",
                json={"query": "Tell me about luxury properties in Dubai"}
            )
            if response.status_code == 200:
                print("   ✅ LLM processing works")
            else:
                print(f"   ❌ LLM processing failed (HTTP {response.status_code})")
        except Exception as e:
            print(f"   ❌ LLM processing error: {e}")
    
    print("\n🎉 Integration testing completed!")

if __name__ == "__main__":
    asyncio.run(test_integration())