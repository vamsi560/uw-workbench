#!/usr/bin/env python3
"""
Test attachment content storage functionality without server
"""

from database import SessionLocal, Submission, create_tables
from datetime import datetime
import uuid

def test_attachment_storage():
    """Test storing attachment content in the database"""
    print("Testing attachment content storage...")
    
    # Ensure tables are created with the new column
    create_tables()
    print("✅ Database tables created/updated")
    
    # Create a test submission with attachment content
    db = SessionLocal()
    try:
        # Sample attachment content (simulating parsed PDF)
        sample_attachment_content = """
Company Information:
Company Name: Orion Data Technologies Inc.
Industry: Technology Services
Contact Email: admin@oriondata.com
Phone: (555) 123-4567

Coverage Request:
Policy Type: Cyber Liability Insurance
Coverage Amount: $5,000,000
Effective Date: January 1, 2026
Term: 12 months

Risk Assessment:
Employees: 150
Annual Revenue: $25M
Data Types: Customer PII, Financial Records, Healthcare Data
Cloud Services: AWS, Microsoft 365
Security Measures: MFA, Encryption, Firewall, SIEM
Previous Incidents: None reported
        """
        
        # Create submission with attachment content
        test_submission = Submission(
            submission_id=999,
            submission_ref=str(uuid.uuid4()),
            subject="Test Submission - Orion Data Technologies Inc.",
            sender_email="test@oriondata.com",
            body_text="Test email body with HTML content processed",
            attachment_content=sample_attachment_content.strip(),
            extracted_fields={
                "company_name": "Orion Data Technologies Inc.",
                "industry": "Technology Services",
                "policy_type": "Cyber Liability Insurance",
                "coverage_amount": "5000000",
                "contact_email": "admin@oriondata.com"
            },
            task_status="pending"
        )
        
        db.add(test_submission)
        db.commit()
        db.refresh(test_submission)
        
        print(f"✅ Test submission created with ID: {test_submission.id}")
        print(f"   - Subject: {test_submission.subject}")
        print(f"   - Attachment content length: {len(test_submission.attachment_content) if test_submission.attachment_content else 0} chars")
        
        # Verify retrieval
        retrieved = db.query(Submission).filter(Submission.id == test_submission.id).first()
        if retrieved and retrieved.attachment_content:
            print(f"✅ Attachment content successfully stored and retrieved")
            print(f"   - First 100 chars: {retrieved.attachment_content[:100]}...")
            print(f"   - Contains company name: {'Orion Data Technologies Inc.' in retrieved.attachment_content}")
            print(f"   - Contains policy type: {'Cyber Liability' in retrieved.attachment_content}")
        else:
            print("❌ Attachment content not found in database")
            
        # Cleanup test data
        db.delete(test_submission)
        db.commit()
        print("✅ Test data cleaned up")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        db.rollback()
    finally:
        db.close()

def verify_schema():
    """Verify the database schema has the attachment_content column"""
    print("\nVerifying database schema...")
    
    db = SessionLocal()
    try:
        # Check if we can query the attachment_content column
        result = db.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'submissions' AND column_name = 'attachment_content'")
        column_exists = result.fetchone() is not None
        
        if column_exists:
            print("✅ attachment_content column exists in submissions table")
        else:
            print("❌ attachment_content column not found in submissions table")
            
    except Exception as e:
        print(f"⚠️  Could not verify schema: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_schema()
    test_attachment_storage()
    print("\n🎉 Attachment content storage test completed!")