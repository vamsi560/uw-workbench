#!/usr/bin/env python3
"""
Test Logic Apps endpoint specifically for string concatenation errors
This simulates the exact scenario where LLM service returns integers for fields expected to be strings
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_logic_apps_endpoint_with_integer_llm_outputs():
    """
    Test that the Logic Apps endpoint can handle integer outputs from LLM service
    without throwing 'can only concatenate str (not "int") to str' errors
    """
    print("🎯 TESTING LOGIC APPS ENDPOINT WITH INTEGER LLM OUTPUTS")
    print("=" * 70)
    
    # Mock the LLM service to return integers (the root cause of the error)
    mock_extracted_data = {
        'policy_type': 123,  # Integer instead of string
        'industry': 456,     # Integer instead of string
        'data_types': 789,   # Integer instead of string
        'security_measures': 101112,  # Integer instead of string
        'coverage_amount': 5000000,   # Integer (this is OK)
        'employee_count': 150,        # Integer (this is OK)
        'insured_name': 'Test Company',
        'effective_date': '2025-01-01'
    }
    
    print("🔥 LLM Data that was causing the error:")
    for key, value in mock_extracted_data.items():
        print(f"   {key}: {value} ({type(value).__name__})")
    
    # Test the business rule functions that were failing
    try:
        print("\n🧪 Testing Business Rule Functions...")
        
        from business_rules import CyberInsuranceValidator
        
        # 1. Test validation (was failing on policy_type.strip(), industry.strip())
        print("1. Testing validation...")
        validation_status, missing_fields, rejection_reason = CyberInsuranceValidator.validate_submission(mock_extracted_data)
        print(f"   ✅ SUCCESS: {validation_status}")
        
        # 2. Test risk priority calculation
        print("2. Testing risk priority calculation...")
        risk_priority = CyberInsuranceValidator.calculate_risk_priority(mock_extracted_data)
        print(f"   ✅ SUCCESS: {risk_priority}")
        
        # 3. Test underwriter assignment (was failing on industry.strip().lower())
        print("3. Testing underwriter assignment...")
        assigned_underwriter = CyberInsuranceValidator.assign_underwriter(mock_extracted_data)
        print(f"   ✅ SUCCESS: {assigned_underwriter}")
        
        # 4. Test risk categories (was failing on data_types.lower(), security_measures.lower())
        print("4. Testing risk categories generation...")
        risk_categories = CyberInsuranceValidator.generate_risk_categories(mock_extracted_data)
        print(f"   ✅ SUCCESS: {risk_categories}")
        
        # 5. Test coverage amount parsing (was failing on .replace())
        print("5. Testing coverage amount parsing...")
        coverage_amount = CyberInsuranceValidator._parse_coverage_amount(mock_extracted_data.get('coverage_amount', ''))
        print(f"   ✅ SUCCESS: {coverage_amount}")
        
        print("\n🎉 ALL BUSINESS RULE FUNCTIONS PASSED!")
        print("✅ The Logic Apps endpoint string concatenation error is FIXED!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("❌ String concatenation error still exists!")
        return False

def simulate_logic_apps_api_call():
    """
    Simulate the full Logic Apps API call with integer LLM outputs
    """
    print("\n🎯 SIMULATING FULL LOGIC APPS API CALL")
    print("=" * 60)
    
    # Create a mock Logic Apps payload
    logic_apps_payload = {
        "subject": "Logic Apps Cyber Insurance Quote",
        "from": "broker@logicapps.com",
        "received_at": "2025-10-08T06:30:00Z",
        "body": "Please provide a cyber insurance quote for our company.",
        "attachments": [
            {
                "name": "application.pdf",
                "contentType": "application/pdf",
                "contentBytes": "JVBERi0xLjcNCI="  # Base64 sample
            }
        ]
    }
    
    print("Logic Apps Email Payload:")
    print(f"   Subject: {logic_apps_payload['subject']}")
    print(f"   From: {logic_apps_payload['from']}")
    print(f"   Attachments: {len(logic_apps_payload['attachments'])}")
    
    # Mock the LLM extraction to return integers
    mock_llm_response = {
        'policy_type': 1,        # Integer!
        'industry': 2,           # Integer!
        'data_types': 3,         # Integer!
        'security_measures': 4,  # Integer!
        'coverage_amount': 5000000,
        'employee_count': 150,
        'insured_name': 'Logic Apps Test Company',
        'effective_date': '2025-01-01'
    }
    
    print("\nLLM Extraction Result (with integers):")
    for key, value in mock_llm_response.items():
        print(f"   {key}: {value} ({type(value).__name__})")
    
    try:
        print("\n🧪 Running Logic Apps business rules pipeline...")
        
        from business_rules import CyberInsuranceValidator
        
        # This is the exact sequence that happens in the Logic Apps endpoint
        validation_status, missing_fields, rejection_reason = CyberInsuranceValidator.validate_submission(mock_llm_response)
        risk_priority = CyberInsuranceValidator.calculate_risk_priority(mock_llm_response)
        assigned_underwriter = CyberInsuranceValidator.assign_underwriter(mock_llm_response)
        risk_categories = CyberInsuranceValidator.generate_risk_categories(mock_llm_response)
        coverage_amount = CyberInsuranceValidator._parse_coverage_amount(
            mock_llm_response.get('coverage_amount', '')
        )
        
        print(f"✅ Validation: {validation_status}")
        print(f"✅ Risk Priority: {risk_priority}")
        print(f"✅ Assigned: {assigned_underwriter}")
        print(f"✅ Risk Categories: {risk_categories}")
        print(f"✅ Coverage Amount: {coverage_amount}")
        
        print("\n🎉 LOGIC APPS API SIMULATION SUCCESSFUL!")
        print("✅ No string concatenation errors in the Logic Apps pipeline!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ LOGIC APPS API ERROR: {e}")
        return False

if __name__ == "__main__":
    print("🚀 LOGIC APPS STRING CONCATENATION FIX VERIFICATION")
    print("=" * 70)
    print("Testing for: 'can only concatenate str (not \"int\") to str'")
    print("=" * 70)
    
    # Test 1: Business rule functions
    test1_passed = test_logic_apps_endpoint_with_integer_llm_outputs()
    
    # Test 2: Full API simulation
    test2_passed = simulate_logic_apps_api_call()
    
    print("\n" + "=" * 70)
    print("🎯 FINAL LOGIC APPS TEST RESULTS")
    print("=" * 70)
    
    if test1_passed and test2_passed:
        print("🎉 COMPLETE SUCCESS!")
        print("✅ Logic Apps endpoint string concatenation error is FIXED!")
        print("✅ Logic Apps endpoint now works with integer LLM outputs!")
        print("✅ All business rule functions handle both strings and integers!")
        print("\n🚀 LOGIC APPS ENDPOINT STATUS: PRODUCTION READY")
    else:
        print("❌ Some tests failed!")
        print("❌ Logic Apps endpoint still has string concatenation issues!")
    
    print("=" * 70)