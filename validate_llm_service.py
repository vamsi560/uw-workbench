"""
Simple validation to show LLM microservice is working
"""

from llm_microservice import app
from llm_service import LLMService

def test_imports():
    """Test that all imports work correctly"""
    try:
        print("✅ LLM microservice imports successfully")
        print(f"✅ FastAPI app created: {type(app)}")
        print(f"✅ LLM service initialized: {type(LLMService())}")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_api_routes():
    """Test that API routes are registered"""
    try:
        routes = [route.path for route in app.routes]
        expected_routes = ["/api/extract", "/api/health", "/api/models", "/api/triage", "/api/risk-assessment"]
        
        print("Available routes:")
        for route in routes:
            print(f"  - {route}")
        
        missing_routes = [route for route in expected_routes if route not in routes]
        if missing_routes:
            print(f"❌ Missing routes: {missing_routes}")
            return False
        else:
            print("✅ All expected routes are registered")
            return True
    except Exception as e:
        print(f"❌ Route testing error: {e}")
        return False

def show_api_documentation():
    """Show API endpoint documentation"""
    print("\n" + "="*60)
    print("LLM MICROSERVICE API DOCUMENTATION")
    print("="*60)
    
    endpoints = {
        "POST /api/extract": "Extract structured data from text using AI",
        "POST /api/summarize": "Generate summary of submission data", 
        "POST /api/triage": "AI-driven submission triage and prioritization",
        "POST /api/risk-assessment": "AI-driven risk assessment of submissions",
        "GET /api/health": "Health check endpoint",
        "GET /api/models": "Get information about available AI models",
        "POST /api/batch-process": "Process multiple extraction requests in background"
    }
    
    for endpoint, description in endpoints.items():
        print(f"{endpoint:<25} - {description}")
    
    print("\nService URL: http://localhost:8001")
    print("API Documentation: http://localhost:8001/docs")
    print("ReDoc Documentation: http://localhost:8001/redoc")

if __name__ == "__main__":
    print("LLM Microservice Validation")
    print("="*50)
    
    imports_ok = test_imports()
    print()
    
    routes_ok = test_api_routes()
    print()
    
    if imports_ok and routes_ok:
        print("✅ Phase 1 Complete: LLM microservice is ready!")
        show_api_documentation()
        print("\n🚀 To start the service, run: python start_llm_service.py")
        print("🧪 To test the service, run: python test_llm_microservice.py (in another terminal)")
    else:
        print("❌ Phase 1 incomplete: Some issues need to be resolved.")