"""
Simple startup script for LLM microservice
"""

if __name__ == "__main__":
    import uvicorn
    from llm_microservice import app
    
    print("Starting LLM microservice on http://localhost:8001")
    print("Press Ctrl+C to stop")
    
    try:
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8001,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nService stopped by user")
    except Exception as e:
        print(f"Error starting service: {e}")
        import traceback
        traceback.print_exc()