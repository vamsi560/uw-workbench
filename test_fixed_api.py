#!/usr/bin/env python3
"""
Test the fixed API with database migration
"""

import json
from datetime import datetime

def test_email_intake_payload():
    """Test creating email intake payload that would trigger the error"""
    
    print("🧪 Testing Email Intake API (Logic Apps Format)")
    print("=" * 60)
    
    # This is the payload that was causing the error
    logic_apps_payload = {
        "subject": "New Cyber Insurance Submission – Orion Data Technologies Inc.",
        "from": "broker@oriondata.com",
        "received_at": "2025-10-08T06:30:00Z",
        "body": "We are requesting a cyber insurance quote for Orion Data Technologies Inc. Please find the application attached.",
        "attachments": [
            {
                "name": "cyber_insurance_application.pdf",
                "contentType": "application/pdf",
                "contentBytes": "JVBERi0xLjcKJcOkw7zDqwoyMCAyIG9iagpbL0lDQ0Jhc2VkIDMgMCBSXQplbmRvYmoKMyAwIG9iagpbL0lDQ0Jhc2VkIDQgMCBSXQplbmRvYmoKNCAwIG9iagpbL0lDQ0Jhc2VkIDUgMCBSXQplbmRvYmoKNSAwIG9iagpbL0lDQ0Jhc2VkIDYgMCBSXQplbmRvYmo="
            }
        ]
    }
    
    # Test that the models can be created
    try:
        from models import LogicAppsEmailPayload
        
        model = LogicAppsEmailPayload(**logic_apps_payload)
        print("✅ LogicAppsEmailPayload model created successfully")
        print(f"   Subject: {model.subject}")
        print(f"   From: {model.from_}")
        print(f"   Received at: {model.received_at}")
        print(f"   Attachments: {len(model.attachments)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Model creation failed: {e}")
        return False

def test_database_query():
    """Test that database queries work with new columns"""
    
    print("\n🧪 Testing Database Query")
    print("=" * 60)
    
    try:
        from database import get_db, Submission
        from datetime import datetime, timedelta
        
        # Test query similar to what caused the error
        db = next(get_db())
        
        # This query was failing before migration
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        
        query_result = db.query(Submission).filter(
            Submission.subject == "Test Subject",
            Submission.sender_email == "test@example.com", 
            Submission.created_at > one_hour_ago
        ).first()
        
        print("✅ Database query executed successfully")
        print("✅ No 'received_at does not exist' error")
        
        # Test that we can create a new submission with all fields
        from sqlalchemy import text
        
        # Check table structure
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'submissions'
            ORDER BY column_name;
        """))
        
        columns = [row[0] for row in result.fetchall()]
        required_columns = ['created_at', 'received_at', 'task_status', 'updated_at']
        
        print(f"✅ Available columns: {sorted(columns)}")
        
        for col in required_columns:
            if col in columns:
                print(f"✅ {col} column exists")
            else:
                print(f"❌ {col} column missing")
                return False
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Database query failed: {e}")
        return False

def test_submission_creation():
    """Test creating a submission with new fields"""
    
    print("\n🧪 Testing Submission Creation")
    print("=" * 60)
    
    try:
        from database import get_db, Submission
        from datetime import datetime
        import uuid
        
        db = next(get_db())
        
        # Create a test submission with all new fields
        test_submission = Submission(
            submission_id=99999,  # Test ID
            submission_ref=str(uuid.uuid4()),
            subject="Test Migration Submission",
            sender_email="test@migration.com",
            body_text="This is a test submission after migration",
            received_at=datetime.utcnow(),
            task_status="pending"
            # created_at and updated_at should be set automatically
        )
        
        print("✅ Submission object created with new fields")
        print(f"   Subject: {test_submission.subject}")
        print(f"   Sender: {test_submission.sender_email}")
        print(f"   Task Status: {test_submission.task_status}")
        print(f"   Received At: {test_submission.received_at}")
        
        # We won't actually save it to avoid test data in production
        # But this tests that the model works
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Submission creation failed: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Testing Fixed API After Database Migration")
    print("=" * 70)
    
    tests = [
        test_email_intake_payload,
        test_database_query,
        test_submission_creation
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 70)
    print("🎯 TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 ALL TESTS PASSED ({passed}/{total})")
        print("\n✅ Database migration successful!")
        print("✅ API should now work without 'received_at' errors!")
        print("✅ Logic Apps integration ready!")
    else:
        print(f"⚠️  SOME TESTS FAILED ({passed}/{total})")
        print("Please check the failed tests above")