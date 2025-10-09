#!/usr/bin/env python3
"""
Test the actual Logic Apps endpoint to see if work items are created correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
import requests
from database import SessionLocal, Submission, WorkItem
from sqlalchemy import desc

def test_logic_apps_endpoint():
    """Test the Logic Apps endpoint directly"""
    
    print("🧪 TESTING LOGIC APPS ENDPOINT")
    print("=" * 60)
    
    # Create test payload based on the comprehensive test data
    test_payload = {
        "subject": "Test Cyber Insurance Submission - Fixed Business Rules",
        "from": "test@valuemomentum.com",
        "body": """
        CYBER INSURANCE SUBMISSION FORM
        COMPANY INFORMATION
        Company Name: TechCorp Solutions Inc.
        Named Insured: TechCorp Solutions Incorporated
        Entity Type: Corporation
        Industry: Technology
        Employee Count: 150
        Annual Revenue: $25,000,000
        
        COVERAGE INFORMATION
        Policy Type: Comprehensive Cyber Liability
        Coverage Amount: $5,000,000
        Effective Date: 2024-01-01
        
        CONTACT INFORMATION
        Contact Name: John Smith
        Contact Title: Chief Technology Officer
        Contact Email: j.smith@techcorp.com
        Contact Phone: (555) 123-4567
        
        BUSINESS ADDRESS
        Address: 123 Tech Drive
        City: San Francisco
        State: CA
        ZIP: 94105
        """,
        "receivedDateTime": "2024-01-01T10:00:00Z",
        "attachments": []
    }
    
    print("📤 Sending test payload to Logic Apps endpoint...")
    
    try:
        # Call the endpoint directly
        response = requests.post(
            "http://localhost:8000/api/logicapps/email/intake",
            json=test_payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success Response: {json.dumps(result, indent=2)}")
            
            # Check if work item was created
            submission_ref = result.get("submission_ref")
            if submission_ref:
                print(f"\n🔍 Checking database for submission: {submission_ref}")
                
                with SessionLocal() as db:
                    # Find the submission
                    submission = db.query(Submission).filter(
                        Submission.submission_ref == submission_ref
                    ).first()
                    
                    if submission:
                        print(f"✅ Found submission ID: {submission.id}")
                        
                        # Check for work items
                        work_items = db.query(WorkItem).filter(
                            WorkItem.submission_id == submission.id
                        ).all()
                        
                        if work_items:
                            print(f"🎉 SUCCESS! Work items created: {len(work_items)}")
                            for wi in work_items:
                                print(f"   Work Item ID: {wi.id}")
                                print(f"   Status: {wi.status}")
                                print(f"   Priority: {wi.priority}")
                                print(f"   Assigned: {wi.assigned_to}")
                                print(f"   Industry: {wi.industry}")
                                print(f"   Policy Type: {wi.policy_type}")
                                print(f"   Coverage: ${wi.coverage_amount:,}" if wi.coverage_amount else "Coverage: None")
                        else:
                            print("❌ NO WORK ITEMS FOUND - Something is still wrong")
                    else:
                        print(f"❌ Submission not found: {submission_ref}")
        else:
            print(f"❌ Error Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error - Is the server running on localhost:8000?")
        print("💡 Tip: Run 'python main.py' or 'uvicorn main:app --reload' to start the server")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_logic_apps_endpoint()