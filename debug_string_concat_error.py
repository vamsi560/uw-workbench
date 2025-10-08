#!/usr/bin/env python3
"""
Test to reproduce the string concatenation error
"""

import json
import traceback
from datetime import datetime
from models import EmailIntakePayload, LogicAppsEmailPayload, AttachmentPayload, LogicAppsAttachment

def test_string_concatenation_error():
    """Test to find where string concatenation error occurs"""
    
    print("🔍 Testing String Concatenation Error Reproduction")
    print("=" * 60)
    
    # Test payload that might cause the error
    test_payload = {
        "subject": "Test Cyber Insurance Application",
        "sender_email": "broker@testcompany.com",
        "body": "Please provide a cyber insurance quote for our client.",
        "attachments": []
    }
    
    try:
        # Test EmailIntakePayload creation
        print("1. Testing EmailIntakePayload creation...")
        email_payload = EmailIntakePayload(**test_payload)
        print("   ✅ EmailIntakePayload created successfully")
        
        # Test LogicAppsEmailPayload creation
        print("2. Testing LogicAppsEmailPayload creation...")
        logic_apps_payload = {
            "subject": "Test Cyber Insurance Application",
            "from": "broker@testcompany.com",
            "received_at": "2025-10-08T06:30:00Z",
            "body": "Please provide a cyber insurance quote for our client.",
            "attachments": []
        }
        
        logic_payload = LogicAppsEmailPayload(**logic_apps_payload)
        print("   ✅ LogicAppsEmailPayload created successfully")
        
        # Test potential string operations
        print("3. Testing submission_id operations...")
        
        # Simulate what might happen in the API
        submission_id = 123  # This is an integer
        submission_ref = "test-uuid-ref"
        
        # Test various string operations that might fail
        test_cases = [
            lambda: f"submission_id: {submission_id}",
            lambda: f"ref: {submission_ref} id: {submission_id}",
            lambda: str(submission_id),
            lambda: f"Processing submission {submission_id}",
            lambda: "submission_" + str(submission_id),  # This should work
            # lambda: "submission_" + submission_id,  # This would fail
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            try:
                result = test_case()
                print(f"   ✅ Test case {i}: {result}")
            except Exception as e:
                print(f"   ❌ Test case {i} failed: {e}")
                return False
        
        # Test potential concatenation that might cause the error
        print("4. Testing potential error scenarios...")
        
        # This would cause the error
        try:
            # This is what might be happening somewhere in the code
            error_prone_concat = "submission_" + submission_id  # This will fail!
        except TypeError as e:
            print(f"   🎯 Found likely error pattern: {e}")
            print("   This is probably what's happening in the code!")
            
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        traceback.print_exc()
        return False

def find_string_concatenation_in_imports():
    """Check if any imported modules might be doing string concatenation"""
    
    print("\n🔍 Testing Imported Module String Operations")
    print("=" * 60)
    
    try:
        # Test business_rules module
        print("1. Testing business_rules module...")
        from business_rules import CyberInsuranceValidator, WorkflowEngine
        
        # Create dummy extracted data that might cause issues
        test_data = {
            'coverage_amount': 1000000,  # This is an integer
            'company_size': 'medium',
            'industry': 'technology'
        }
        
        # Test validation - this might be where the error occurs
        validation_status, missing_fields, rejection_reason = CyberInsuranceValidator.validate_submission(test_data)
        print(f"   ✅ Validation completed: {validation_status}")
        
        # Test risk priority calculation
        risk_priority = CyberInsuranceValidator.calculate_risk_priority(test_data)
        print(f"   ✅ Risk priority: {risk_priority}")
        
        # Test coverage amount parsing - this might be the issue
        coverage_str = CyberInsuranceValidator._parse_coverage_amount("$1,000,000")
        print(f"   ✅ Coverage parsing: {coverage_str}")
        
        # Test with integer input that might cause concatenation error
        try:
            coverage_int = CyberInsuranceValidator._parse_coverage_amount(1000000)  # Integer input
            print(f"   ✅ Coverage parsing (int input): {coverage_int}")
        except Exception as e:
            print(f"   🎯 Found potential error in coverage parsing: {e}")
            return "coverage_parsing"
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing business_rules: {e}")
        traceback.print_exc()
        return False

def test_llm_service():
    """Test LLM service for string concatenation issues"""
    
    print("\n🔍 Testing LLM Service String Operations")
    print("=" * 60)
    
    try:
        from llm_service import LLMExtractionService
        
        # Test LLM service
        llm_service = LLMExtractionService()
        
        # This might cause string concatenation issues
        test_text = "Test email content for extraction"
        
        print("1. Testing LLM extraction...")
        result = llm_service.extract_insurance_data(test_text)
        print(f"   ✅ LLM extraction completed: {type(result)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing LLM service: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🎯 String Concatenation Error Investigation")
    print("=" * 70)
    
    tests = [
        ("Basic String Operations", test_string_concatenation_error),
        ("Business Rules Module", find_string_concatenation_in_imports),
        ("LLM Service", test_llm_service),
    ]
    
    results = []
    error_sources = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 40)
        try:
            result = test_func()
            results.append(result)
            if isinstance(result, str):  # Error source identified
                error_sources.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 70)
    print("🎯 INVESTIGATION SUMMARY")
    print("=" * 70)
    
    if error_sources:
        print("🎯 POTENTIAL ERROR SOURCES IDENTIFIED:")
        for test_name, error_type in error_sources:
            print(f"   - {test_name}: {error_type}")
    else:
        print("✅ No obvious string concatenation errors found in test cases")
        print("💡 The error might be happening in a specific code path not tested here")
    
    passed = sum(1 for r in results if r is True)
    total = len(results)
    print(f"\n📊 Tests passed: {passed}/{total}")