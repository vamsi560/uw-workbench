#!/usr/bin/env python3
"""
Check database for recent submissions and their extracted data
"""

from database import SessionLocal, Submission, WorkItem
from sqlalchemy import desc
import json

def check_recent_submissions():
    """Check recent submissions in the database"""
    db = SessionLocal()
    try:
        print("Checking recent submissions...")
        
        # Get the 5 most recent submissions
        recent_submissions = db.query(Submission).order_by(desc(Submission.created_at)).limit(5).all()
        
        if not recent_submissions:
            print("No submissions found in database.")
            return
        
        for i, sub in enumerate(recent_submissions, 1):
            print(f"\n{'='*60}")
            print(f"Submission #{i}")
            print(f"{'='*60}")
            print(f"ID: {sub.submission_id}")
            print(f"Ref: {sub.submission_ref}")
            print(f"Subject: {sub.subject}")
            print(f"From: {sub.sender_email}")
            print(f"Body Text: {sub.body_text}")
            print(f"Task Status: {sub.task_status}")
            print(f"Created: {sub.created_at}")
            print(f"Received: {sub.received_at}")
            
            # Show attachment content
            if hasattr(sub, 'attachment_content') and sub.attachment_content:
                print(f"Attachment Content (first 200 chars): {sub.attachment_content[:200]}...")
            else:
                print(f"Attachment Content: None")
            
            # Show extracted fields
            if sub.extracted_fields:
                print(f"\nExtracted Fields:")
                if isinstance(sub.extracted_fields, dict):
                    for key, value in sub.extracted_fields.items():
                        print(f"  {key}: {value}")
                else:
                    print(f"  Raw: {sub.extracted_fields}")
            else:
                print(f"\nExtracted Fields: None")
            
            # Check for corresponding work items (use internal database ID, not submission_id field)
            work_items = db.query(WorkItem).filter(WorkItem.submission_id == sub.id).all()
            if work_items:
                print(f"\nWork Items: {len(work_items)}")
                for wi in work_items:
                    print(f"  - ID: {wi.id}, Status: {wi.status}, Priority: {wi.priority}")
                    print(f"    Title: {wi.title}")
                    print(f"    Assigned to: {wi.assigned_to}")
            else:
                print(f"\nWork Items: None")
                
    except Exception as e:
        print(f"Database error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_recent_submissions()