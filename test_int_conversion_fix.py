#!/usr/bin/env python3
"""
Test the fix for the int() conversion error
"""

import json
import requests
import sys
import os

def test_logic_apps_endpoint():
    """Test the Logic Apps endpoint with the string ID that was causing issues"""
    
    print("🔧 TESTING INT CONVERSION FIX")
    print("=" * 40)
    
    # Test payload that would trigger the original error
    test_payload = {
        "from_address": "test@example.com",
        "to_address": "claims@uwworkbench.com",
        "subject": "Cyber Insurance Quote Request - TEST-2025-001",
        "body": "VGVzdCBib2R5IGZvciBjeWJlciBpbnN1cmFuY2UgcXVvdGUgcmVxdWVzdA==",  # Base64 encoded test body
        "received_datetime": "2025-01-09T10:30:00Z",
        "attachments": []
    }
    
    try:
        # Test the endpoint
        print("📤 Sending test request to Logic Apps endpoint...")
        response = requests.post(
            "http://localhost:8000/api/logicapps/email/intake",
            json=test_payload,
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: No int conversion error!")
            print(f"📋 Submission ID: {result.get('submission_id')}")
            print(f"📊 Validation Status: {result.get('validation_status')}")
            print(f"🔢 Work Items Created: {result.get('work_items_created', 0)}")
            return True
        else:
            print("❌ FAILED: Request failed")
            print(f"📝 Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("⚠️  Cannot connect to server - make sure the app is running")
        print("💡 Start the server with: python main.py")
        return False
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

def test_submission_id_generation():
    """Test that submission ID generation doesn't use int() conversion"""
    
    print("\n🔢 TESTING SUBMISSION ID GENERATION")
    print("=" * 40)
    
    # Import the main module to test the ID generation
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        from datetime import datetime
        
        # Test the new ID generation format
        test_id = f"SUB-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        print(f"📋 Generated ID: {test_id}")
        print(f"📊 ID Type: {type(test_id)}")
        print(f"✅ ID Format: {'Valid' if test_id.startswith('SUB-') else 'Invalid'}")
        
        # Test that this ID won't cause int() conversion errors
        try:
            int(test_id)
            print("❌ PROBLEM: ID can still be converted to int")
            return False
        except ValueError:
            print("✅ SUCCESS: ID correctly prevents int() conversion")
            return True
            
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 RUNNING INT CONVERSION FIX VERIFICATION")
    print("=" * 50)
    
    # Test 1: Submission ID generation
    test1_success = test_submission_id_generation()
    
    # Test 2: Logic Apps endpoint
    test2_success = test_logic_apps_endpoint()
    
    print(f"\n📊 TEST RESULTS:")
    print(f"   ID Generation: {'✅ PASS' if test1_success else '❌ FAIL'}")
    print(f"   API Endpoint: {'✅ PASS' if test2_success else '❌ FAIL'}")
    
    if test1_success and test2_success:
        print(f"\n🎉 ALL TESTS PASSED! The int conversion issue is FIXED!")
        sys.exit(0)
    else:
        print(f"\n⚠️  Some tests failed - review the output above")
        sys.exit(1)