#!/usr/bin/env python3
"""
Check work items directly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, WorkItem
from sqlalchemy import desc

def check_work_items():
    """Check work items directly"""
    
    print("🔍 CHECKING WORK ITEMS DIRECTLY")
    print("=" * 60)
    
    with SessionLocal() as db:
        # Get all work items
        work_items = db.query(WorkItem).order_by(desc(WorkItem.id)).all()
        
        print(f"📊 Total Work Items Found: {len(work_items)}")
        
        if work_items:
            for wi in work_items:
                print(f"\n🎯 Work Item ID: {wi.id}")
                print(f"   Submission ID: {wi.submission_id}")
                print(f"   Title: {wi.title}")
                print(f"   Status: {wi.status}")
                print(f"   Priority: {wi.priority}")
                print(f"   Assigned To: {wi.assigned_to}")
                print(f"   Industry: {wi.industry}")
                print(f"   Policy Type: {wi.policy_type}")
                print(f"   Coverage: ${wi.coverage_amount:,}" if wi.coverage_amount else "Coverage: None")
                print(f"   Risk Score: {wi.risk_score}")
                print(f"   Created: {wi.created_at}")
        else:
            print("❌ NO WORK ITEMS FOUND")

if __name__ == "__main__":
    check_work_items()