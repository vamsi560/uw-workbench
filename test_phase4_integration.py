#!/usr/bin/env python3
"""
Phase 4 Testing Script - Java Backend Verification
This script tests the Java backend endpoints to ensure they're ready for frontend integration.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
JAVA_BACKEND_URL = "http://localhost:8080"
PYTHON_LLM_URL = "http://localhost:8001"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")

def test_endpoint(url, method="GET", data=None, description=""):
    """Test a single endpoint and return the result"""
    try:
        print(f"\n🔗 Testing: {method} {url}")
        if description:
            print(f"   Description: {description}")
        
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=10)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Success")
            if isinstance(result, dict) and len(result) <= 5:
                print(f"   Response: {json.dumps(result, indent=2)}")
            elif isinstance(result, list):
                print(f"   Response: Array with {len(result)} items")
                if result and len(result) > 0:
                    print(f"   First item: {json.dumps(result[0], indent=2)}")
            return True, result
        else:
            print(f"   ❌ Failed: {response.text}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection Error - Service not running on {url}")
        return False, None
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False, None

def test_java_backend():
    """Test Java backend endpoints"""
    print_section("JAVA BACKEND TESTING")
    
    # Test health endpoint
    success, health_data = test_endpoint(
        f"{JAVA_BACKEND_URL}/api/health",
        description="Health check with LLM service status"
    )
    
    if not success:
        print("❌ Java backend is not running or not accessible")
        print(f"Please start the Java backend on {JAVA_BACKEND_URL}")
        return False
    
    # Test LLM status endpoint
    test_endpoint(
        f"{JAVA_BACKEND_URL}/api/llm/status",
        description="LLM service status and available models"
    )
    
    # Test work items polling
    test_endpoint(
        f"{JAVA_BACKEND_URL}/api/workitems/poll",
        description="Poll for work items"
    )
    
    # Test work items polling with parameters
    test_endpoint(
        f"{JAVA_BACKEND_URL}/api/workitems/poll?limit=10",
        description="Poll for work items with limit"
    )
    
    # Test work items needing attention
    test_endpoint(
        f"{JAVA_BACKEND_URL}/api/workitems/attention",
        description="Get work items needing attention"
    )
    
    return True

def test_email_intake():
    """Test email intake functionality"""
    print_section("EMAIL INTAKE TESTING")
    
    test_email = {
        "sender_email": "test@example.com",
        "subject": "Test Insurance Submission",
        "email_content": """
        Dear Underwriter,
        
        We would like to submit an application for General Liability insurance.
        
        Company: Test Technology Corp
        Industry: Technology
        Policy Type: General Liability
        Coverage Amount: $2,000,000
        
        Please review and let us know the next steps.
        
        Best regards,
        John Doe
        """
    }
    
    success, response = test_endpoint(
        f"{JAVA_BACKEND_URL}/api/email/intake",
        method="POST",
        data=test_email,
        description="Submit test email for processing"
    )
    
    if success:
        print("✅ Email intake successful!")
        submission_id = response.get('submission_id')
        work_item_id = response.get('work_item_id')
        
        if submission_id and work_item_id:
            print(f"   Created submission ID: {submission_id}")
            print(f"   Created work item ID: {work_item_id}")
            
            # Test getting the created work item
            test_endpoint(
                f"{JAVA_BACKEND_URL}/api/workitems/{work_item_id}",
                description=f"Get created work item {work_item_id}"
            )
            
            # Test getting work items for the submission
            test_endpoint(
                f"{JAVA_BACKEND_URL}/api/submissions/{submission_id}/workitems",
                description=f"Get work items for submission {submission_id}"
            )
            
            return work_item_id
    
    return None

def test_work_item_operations(work_item_id):
    """Test work item operations"""
    if not work_item_id:
        print("⚠️  Skipping work item operations - no work item ID available")
        return
    
    print_section("WORK ITEM OPERATIONS TESTING")
    
    # Test status update
    test_endpoint(
        f"{JAVA_BACKEND_URL}/api/workitems/{work_item_id}/status",
        method="PUT",
        data={"status": "IN_PROGRESS"},
        description=f"Update work item {work_item_id} status to IN_PROGRESS"
    )
    
    # Test assignment
    test_endpoint(
        f"{JAVA_BACKEND_URL}/api/workitems/{work_item_id}/assign",
        method="PUT",
        data={"assigned_to": "test.underwriter@example.com"},
        description=f"Assign work item {work_item_id} to underwriter"
    )
    
    # Test priority update
    test_endpoint(
        f"{JAVA_BACKEND_URL}/api/workitems/{work_item_id}/priority",
        method="PUT",
        data={"priority": "HIGH"},
        description=f"Update work item {work_item_id} priority to HIGH"
    )

def test_python_llm_service():
    """Test Python LLM service availability"""
    print_section("PYTHON LLM SERVICE TESTING")
    
    success, _ = test_endpoint(
        f"{PYTHON_LLM_URL}/api/health",
        description="Python LLM service health check"
    )
    
    if success:
        print("✅ Python LLM service is running")
        
        # Test available models
        test_endpoint(
            f"{PYTHON_LLM_URL}/api/models",
            description="Get available AI models"
        )
        
    else:
        print("⚠️  Python LLM service is not running")
        print("   This is optional for Java backend testing, but required for full functionality")
    
    return success

def run_comprehensive_test():
    """Run comprehensive testing of the Java backend"""
    print("🚀 Starting Phase 4 - Java Backend Verification")
    print(f"Testing Java Backend: {JAVA_BACKEND_URL}")
    print(f"Testing Python LLM Service: {PYTHON_LLM_URL}")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test services
    java_success = test_java_backend()
    python_success = test_python_llm_service()
    
    if not java_success:
        return False
    
    # Test email intake flow
    work_item_id = test_email_intake()
    
    # Test work item operations
    test_work_item_operations(work_item_id)
    
    # Summary
    print_section("TEST SUMMARY")
    print(f"✅ Java Backend: {'✅ Running' if java_success else '❌ Not Running'}")
    print(f"✅ Python LLM Service: {'✅ Running' if python_success else '⚠️  Not Running'}")
    print(f"✅ Email Intake: {'✅ Working' if work_item_id else '❌ Failed'}")
    print(f"✅ Work Item Operations: {'✅ Tested' if work_item_id else '⚠️  Skipped'}")
    
    if java_success:
        print("\n🎉 Java backend is ready for frontend integration!")
        print("\nNext steps:")
        print("1. Update frontend environment variables to point to Java backend")
        print("2. Deploy frontend with new configuration")
        print("3. Test end-to-end functionality")
        
        if not python_success:
            print("\n⚠️  Note: Python LLM service is not running.")
            print("   Start it with: python start_llm_service.py")
            print("   This will enable AI features like data extraction and risk assessment.")
    
    return java_success

if __name__ == "__main__":
    success = run_comprehensive_test()
    exit(0 if success else 1)