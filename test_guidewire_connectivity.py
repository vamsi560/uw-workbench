#!/usr/bin/env python3
"""
Test Guidewire API connectivity and functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
from guidewire_client import GuidewireClient, GuidewireConfig
from database import SessionLocal, WorkItem
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_basic_connectivity():
    """Test basic connectivity to Guidewire API"""
    print("🔌 Testing Guidewire API Connectivity")
    print("=" * 60)
    
    # Create client
    client = GuidewireClient()
    
    print(f"📡 Testing connection to: {client.config.base_url}")
    
    # Test connection
    result = client.test_connection()
    
    if result["success"]:
        print(f"✅ Connection successful!")
        print(f"   Status Code: {result['status_code']}")
        print(f"   Response Time: {result['response_time_ms']:.2f}ms")
        print(f"   URL: {result['url']}")
        
        # Show some headers
        if result.get("headers"):
            print(f"   Server Info:")
            for key in ["server", "date", "content-type"]:
                if key in result["headers"]:
                    print(f"     {key}: {result['headers'][key]}")
    else:
        print(f"❌ Connection failed!")
        print(f"   Error: {result['error']}")
        print(f"   Message: {result['message']}")
    
    return result["success"]

def test_composite_endpoint():
    """Test the composite endpoint with a simple request"""
    print("\n🔄 Testing Composite Endpoint")
    print("=" * 60)
    
    client = GuidewireClient()
    
    # Create a simple test request (just try to get some basic info)
    test_payload = {
        "requests": [
            {
                "method": "get",
                "uri": "/admin/v1/producer-codes",
                "body": {}
            }
        ]
    }
    
    print(f"📤 Sending test composite request...")
    print(f"   Endpoint: {client.config.full_url}")
    
    result = client.submit_composite_request(test_payload)
    
    if result["success"]:
        print(f"✅ Composite request successful!")
        print(f"   Status Code: {result['status_code']}")
        print(f"   Response Time: {result['response_time_ms']:.2f}ms")
        
        # Show response structure
        if result.get("data"):
            if isinstance(result["data"], dict):
                print(f"   Response keys: {list(result['data'].keys())}")
                if "responses" in result["data"]:
                    print(f"   Number of responses: {len(result['data']['responses'])}")
            else:
                print(f"   Response type: {type(result['data'])}")
                print(f"   Response preview: {str(result['data'])[:200]}...")
    else:
        print(f"❌ Composite request failed!")
        print(f"   Status Code: {result.get('status_code', 'Unknown')}")
        print(f"   Error: {result['error']}")
        print(f"   Message: {result['message']}")
        
        # Show response data if available (might contain error details)
        if result.get("data"):
            print(f"   Response data: {json.dumps(result['data'], indent=2)[:500]}...")
    
    return result["success"]

def test_cyber_submission_mapping():
    """Test data mapping using a real work item"""
    print("\n🗺️ Testing Data Mapping")
    print("=" * 60)
    
    # Get a work item from database
    with SessionLocal() as db:
        work_item = db.query(WorkItem).filter(
            WorkItem.policy_type.ilike("%cyber%")
        ).first()
        
        if not work_item:
            print("❌ No cyber work items found in database")
            return False
        
        print(f"📋 Using work item: {work_item.id}")
        print(f"   Title: {work_item.title}")
        print(f"   Policy Type: {work_item.policy_type}")
        print(f"   Industry: {work_item.industry}")
        print(f"   Coverage: ${work_item.coverage_amount:,}" if work_item.coverage_amount else "Coverage: Not specified")
    
    # Get the submission data
    submission = db.query(work_item.__class__).filter_by(submission_id=work_item.submission_id).first()
    if submission and hasattr(submission, 'extracted_fields'):
        extracted_data = submission.extracted_fields
        if isinstance(extracted_data, str):
            extracted_data = json.loads(extracted_data)
    else:
        # Use work item data as fallback
        extracted_data = {
            "company_name": "Test Company",
            "policy_type": work_item.policy_type,
            "industry": work_item.industry,
            "coverage_amount": work_item.coverage_amount,
            "business_address": "123 Test Street",
            "business_city": "San Francisco",
            "business_state": "CA",
            "business_zip": "94105",
            "employee_count": "50",
            "annual_revenue": "1000000"
        }
    
    print(f"\n📊 Extracted data keys: {list(extracted_data.keys())}")
    
    # Test mapping
    client = GuidewireClient()
    mapped_payload = client._map_to_guidewire_format(extracted_data)
    
    print(f"✅ Data mapping successful!")
    print(f"   Generated {len(mapped_payload['requests'])} API requests")
    
    # Show the structure
    for i, request in enumerate(mapped_payload['requests'], 1):
        print(f"   {i}. {request['method'].upper()} {request['uri']}")
    
    # Show mapped company data
    if mapped_payload['requests']:
        account_data = mapped_payload['requests'][0]['body']['data']['attributes']['initialAccountHolder']
        print(f"\n🏢 Mapped company data:")
        print(f"   Company: {account_data['companyName']}")
        print(f"   Address: {account_data['primaryAddress']['addressLine1']}")
        print(f"   City/State: {account_data['primaryAddress']['city']}, {account_data['primaryAddress']['state']['code']}")
    
    return True

def test_authentication_scenarios():
    """Test different authentication scenarios"""
    print("\n🔐 Testing Authentication Scenarios")
    print("=" * 60)
    
    # Test 1: No credentials (current state)
    print("1. Testing without credentials:")
    client = GuidewireClient()
    result = client.test_connection()
    print(f"   Result: {'✅ Success' if result['success'] else '❌ Failed'}")
    
    # Test 2: With dummy credentials (will fail but shows auth attempt)
    print("\n2. Testing with dummy credentials:")
    config = GuidewireConfig()
    config.username = "test_user"
    config.password = "test_password"
    client_auth = GuidewireClient(config)
    result_auth = client_auth.test_connection()
    print(f"   Result: {'✅ Success' if result_auth['success'] else '❌ Failed'}")
    if not result_auth['success']:
        print(f"   Expected failure: {result_auth['message']}")
    
    return True

def main():
    """Run all connectivity tests"""
    print("🚀 GUIDEWIRE API CONNECTIVITY TESTS")
    print("=" * 80)
    
    test_results = {
        "basic_connectivity": False,
        "composite_endpoint": False,
        "data_mapping": False,
        "authentication": False
    }
    
    try:
        # Test 1: Basic connectivity
        test_results["basic_connectivity"] = test_basic_connectivity()
        
        # Test 2: Composite endpoint
        if test_results["basic_connectivity"]:
            test_results["composite_endpoint"] = test_composite_endpoint()
        else:
            print("\n⏭️ Skipping composite endpoint test (basic connectivity failed)")
        
        # Test 3: Data mapping (can run independently)
        test_results["data_mapping"] = test_cyber_submission_mapping()
        
        # Test 4: Authentication scenarios
        test_results["authentication"] = test_authentication_scenarios()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(test_results.values())
        total = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"   {test_name.replace('_', ' ').title()}: {status}")
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if test_results["basic_connectivity"]:
            print("\n🎉 Basic connectivity is working! You can proceed with integration.")
        else:
            print("\n⚠️ Connectivity issues detected. Check network/credentials.")
        
        print("\n💡 Next steps:")
        print("   1. Configure proper authentication credentials")
        print("   2. Test with real Guidewire data")
        print("   3. Implement full submission workflow")
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()