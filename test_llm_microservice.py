"""
Test script for LLM microservice endpoints
"""

import requests
import json

# Test health endpoint
def test_health():
    try:
        response = requests.get("http://localhost:8001/api/health")
        print(f"Health endpoint status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

# Test extraction endpoint
def test_extraction():
    try:
        test_data = {
            "text": "We are a small tech company looking for cyber insurance. We have 50 employees and use cloud services extensively.",
            "email_subject": "Cyber Insurance Quote Request",
            "sender_email": "john@techcorp.com"
        }
        
        response = requests.post("http://localhost:8001/api/extract", json=test_data)
        print(f"Extraction endpoint status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Extracted fields: {json.dumps(result['extracted_fields'], indent=2)}")
            print(f"Processing time: {result['processing_time_ms']}ms")
        else:
            print(f"Error: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Extraction test failed: {e}")
        return False

# Test models endpoint
def test_models():
    try:
        response = requests.get("http://localhost:8001/api/models")
        print(f"Models endpoint status: {response.status_code}")
        print(f"Available models: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Models test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing LLM Microservice...")
    print("=" * 50)
    
    health_ok = test_health()
    print("\n" + "=" * 50)
    
    models_ok = test_models()
    print("\n" + "=" * 50)
    
    if health_ok:
        extraction_ok = test_extraction()
        print("\n" + "=" * 50)
        
        if health_ok and models_ok and extraction_ok:
            print("✅ All tests passed! LLM microservice is working correctly.")
        else:
            print("❌ Some tests failed.")
    else:
        print("❌ Service is not running or not responding.")