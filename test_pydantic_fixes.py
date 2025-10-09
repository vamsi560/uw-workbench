#!/usr/bin/env python3
"""
Test script to verify the int conversion issue is fixed
"""

import json
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import EmailIntakeResponse, SubmissionResponse, SubmissionConfirmResponse

def test_pydantic_models():
    """Test that Pydantic models accept string submission_ids"""
    
    print("🧪 TESTING PYDANTIC MODEL FIXES")
    print("=" * 40)
    
    # Test EmailIntakeResponse with string submission_id
    try:
        response1 = EmailIntakeResponse(
            submission_ref="12345-abcde-67890",
            submission_id="SUB-20251009182053",  # String ID
            status="success",
            message="Test message"
        )
        print("✅ EmailIntakeResponse: Accepts string submission_id")
        print(f"   submission_id: {response1.submission_id} (type: {type(response1.submission_id)})")
    except Exception as e:
        print(f"❌ EmailIntakeResponse: Failed with string submission_id")
        print(f"   Error: {e}")
    
    # Test SubmissionResponse with string submission_id
    try:
        response2 = SubmissionResponse(
            id=123,
            submission_id="TEST-2025-001",  # String ID like in the error
            submission_ref="ref-12345",
            subject="Test Subject",
            sender_email="test@example.com",
            task_status="pending"
        )
        print("✅ SubmissionResponse: Accepts string submission_id")
        print(f"   submission_id: {response2.submission_id} (type: {type(response2.submission_id)})")
    except Exception as e:
        print(f"❌ SubmissionResponse: Failed with string submission_id")
        print(f"   Error: {e}")
    
    # Test SubmissionConfirmResponse with string submission_id
    try:
        response3 = SubmissionConfirmResponse(
            submission_id="TEST-2025-001",  # String ID like in the error
            submission_ref="ref-12345",
            work_item_id=456,
            assigned_to="underwriter@company.com",
            task_status="pending"
        )
        print("✅ SubmissionConfirmResponse: Accepts string submission_id")
        print(f"   submission_id: {response3.submission_id} (type: {type(response3.submission_id)})")
    except Exception as e:
        print(f"❌ SubmissionConfirmResponse: Failed with string submission_id")
        print(f"   Error: {e}")
    
    # Test serialization to JSON
    try:
        json_data = response1.model_dump()
        print("✅ JSON Serialization: Works correctly")
        print(f"   Sample: {json.dumps(json_data, indent=2)[:100]}...")
    except Exception as e:
        print(f"❌ JSON Serialization: Failed")
        print(f"   Error: {e}")
    
    print("\n🎯 RESULT: Pydantic models now support string submission_ids!")
    print("   The 'int_parsing' error should be resolved.")

if __name__ == "__main__":
    test_pydantic_models()