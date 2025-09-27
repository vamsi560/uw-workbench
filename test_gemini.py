#!/usr/bin/env python3
"""
Test script to verify Gemini LLM integration
"""

import json
from llm_service import llm_service

def test_gemini_extraction():
    """Test Gemini LLM extraction with sample insurance text"""
    
    sample_text = """
    Insurance Application
    
    Insured Name: ABC Manufacturing Company
    Policy Type: General Liability Insurance
    Coverage Amount: $2,000,000 per occurrence
    Effective Date: March 1, 2024
    Broker: John Smith Insurance Agency
    
    This application is for general liability coverage for our manufacturing operations.
    We need coverage for product liability and premises liability.
    """
    
    print("Testing Gemini LLM extraction...")
    print("=" * 50)
    print("Sample text:")
    print(sample_text)
    print("=" * 50)
    
    try:
        result = llm_service.extract_insurance_data(sample_text)
        
        print("Extracted data:")
        print(json.dumps(result, indent=2))
        
        # Validate required fields
        required_fields = ["insured_name", "policy_type", "coverage_amount", "effective_date", "broker"]
        missing_fields = [field for field in required_fields if field not in result]
        
        if missing_fields:
            print(f"\n⚠️  Missing fields: {missing_fields}")
        else:
            print("\n✓ All required fields extracted successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing Gemini: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_gemini_extraction()
    
    if success:
        print("\n✓ Gemini integration test passed!")
    else:
        print("\n✗ Gemini integration test failed!")
        exit(1)
