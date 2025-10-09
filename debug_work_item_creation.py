#!/usr/bin/env python3
"""
Debug work item creation in the Logic Apps endpoint
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, Submission, WorkItem
from sqlalchemy import desc

def debug_work_item_creation():
    """Debug work item creation by examining the database state"""
    
    print("🔍 DEBUGGING WORK ITEM CREATION")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # Get recent submissions
        print("\n📊 RECENT SUBMISSIONS:")
        submissions = db.query(Submission).order_by(desc(Submission.created_at)).limit(10).all()
        
        for sub in submissions:
            print(f"\n📝 Submission ID: {sub.submission_id} | Ref: {sub.submission_ref}")
            print(f"   Subject: {sub.subject}")
            print(f"   Status: {sub.task_status}")
            print(f"   Created: {sub.created_at}")
            
            # Check for work items
            work_items = db.query(WorkItem).filter(WorkItem.submission_id == sub.id).all()
            
            if work_items:
                print(f"   ✅ Work Items Found: {len(work_items)}")
                for wi in work_items:
                    print(f"      🎯 Work Item ID: {wi.id}")
                    print(f"         Status: {wi.status}")
                    print(f"         Priority: {wi.priority}")
                    print(f"         Assigned: {wi.assigned_to}")
                    print(f"         Risk Score: {wi.risk_score}")
                    
                    # Show extracted data
                    if sub.extracted_fields:
                        validation_info = sub.extracted_fields.get('validation_status', 'Unknown')
                        policy_type = sub.extracted_fields.get('policy_type', 'Unknown')
                        print(f"         Validation: {validation_info}")
                        print(f"         Policy Type: {policy_type}")
            else:
                print(f"   ❌ NO WORK ITEMS FOUND")
                
                # Check extracted data for clues
                if sub.extracted_fields:
                    print(f"   📊 Extracted Fields Available: {len(sub.extracted_fields)} fields")
                    policy_type = sub.extracted_fields.get('policy_type')
                    if policy_type:
                        print(f"      Policy Type: {policy_type}")
                    
                    # Check if it might have been rejected
                    for key, value in sub.extracted_fields.items():
                        if 'comprehensive' in str(value).lower():
                            print(f"      🚨 POTENTIAL ISSUE: {key} = {value}")
        
        print(f"\n📈 SUMMARY:")
        total_submissions = db.query(Submission).count()
        total_work_items = db.query(WorkItem).count()
        print(f"   Total Submissions: {total_submissions}")
        print(f"   Total Work Items: {total_work_items}")
        print(f"   Missing Work Items: {total_submissions - total_work_items}")
    
    finally:
        db.close()

if __name__ == "__main__":
    debug_work_item_creation()