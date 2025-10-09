#!/usr/bin/env python3
"""
Reprocess existing submissions to create work items with fixed business rules
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, Submission, WorkItem, WorkItemStatus, WorkItemPriority, CompanySize
from business_rules import CyberInsuranceValidator
from datetime import datetime
import json

def reprocess_existing_submissions():
    """Reprocess existing submissions to create missing work items"""
    
    print("🔄 REPROCESSING EXISTING SUBMISSIONS")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        # Get submissions without work items (except our test submission)
        submissions = db.query(Submission).filter(
            Submission.subject != "Test Cyber Insurance Submission - Simulated"
        ).all()
        
        submissions_with_work_items = db.query(Submission.id).join(WorkItem).all()
        existing_submission_ids = [s[0] for s in submissions_with_work_items]
        
        print(f"📊 Found {len(submissions)} total submissions")
        print(f"📊 {len(existing_submission_ids)} submissions already have work items")
        
        created_count = 0
        
        for submission in submissions:
            if submission.id in existing_submission_ids:
                print(f"⏭️ Skipping submission {submission.id} - already has work item")
                continue
                
            print(f"\n🔄 Processing submission {submission.id}:")
            print(f"   Subject: {submission.subject}")
            print(f"   From: {submission.sender_email}")
            
            # Check if we have extracted fields
            if not submission.extracted_fields:
                print(f"   ⚠️ No extracted fields - skipping")
                continue
            
            # Parse extracted fields
            if isinstance(submission.extracted_fields, str):
                try:
                    extracted_data = json.loads(submission.extracted_fields)
                except:
                    print(f"   ❌ Could not parse extracted fields - skipping")
                    continue
            else:
                extracted_data = submission.extracted_fields
            
            print(f"   Policy Type: {extracted_data.get('policy_type', 'Unknown')}")
            print(f"   Industry: {extracted_data.get('industry', 'Unknown')}")
            
            # Apply business rules validation
            validation_status, missing_fields, rejection_reason = CyberInsuranceValidator.validate_submission(extracted_data)
            print(f"   Validation: {validation_status}")
            
            if validation_status == "Rejected":
                print(f"   ❌ Still rejected: {rejection_reason}")
                continue
            
            # Calculate risk and assignment
            risk_priority = CyberInsuranceValidator.calculate_risk_priority(extracted_data)
            assigned_underwriter = CyberInsuranceValidator.assign_underwriter(extracted_data)
            risk_categories = CyberInsuranceValidator.generate_risk_categories(extracted_data)
            overall_risk_score = sum(risk_categories.values()) / len(risk_categories) if risk_categories else 0
            
            print(f"   Risk Priority: {risk_priority}")
            print(f"   Assigned: {assigned_underwriter}")
            
            # Create work item
            work_item = WorkItem(
                submission_id=submission.id,
                title=submission.subject,
                description=f"Email from {submission.sender_email}",
                status=WorkItemStatus.PENDING,
                priority=WorkItemPriority.MEDIUM
            )
            
            # Set cyber insurance specific data
            work_item.industry = extracted_data.get('industry')
            work_item.policy_type = extracted_data.get('policy_type')
            work_item.coverage_amount = CyberInsuranceValidator._parse_coverage_amount(extracted_data.get('coverage_amount'))
            
            # Set company size
            if extracted_data.get('employee_count'):
                try:
                    employee_count = int(extracted_data.get('employee_count', 0))
                    if employee_count < 50:
                        work_item.company_size = CompanySize.SMALL
                    elif employee_count < 500:
                        work_item.company_size = CompanySize.MEDIUM
                    else:
                        work_item.company_size = CompanySize.LARGE
                except:
                    work_item.company_size = CompanySize.MEDIUM
            
            # Apply validation results
            if validation_status == "Complete":
                work_item.status = WorkItemStatus.PENDING
            elif validation_status == "Incomplete":
                work_item.status = WorkItemStatus.PENDING
                work_item.description += f"\n\nMissing fields: {', '.join(str(field) for field in missing_fields)}"
            
            # Set priority and assignment
            try:
                work_item.priority = WorkItemPriority(str(risk_priority)) if risk_priority else WorkItemPriority.MEDIUM
            except ValueError:
                work_item.priority = WorkItemPriority.MEDIUM
            
            work_item.assigned_to = str(assigned_underwriter) if assigned_underwriter else None
            work_item.risk_score = float(overall_risk_score) if overall_risk_score else None
            work_item.risk_categories = risk_categories
            
            db.add(work_item)
            db.commit()
            db.refresh(work_item)
            
            print(f"   ✅ Created work item ID: {work_item.id}")
            created_count += 1
        
        print(f"\n🎉 SUMMARY:")
        print(f"   Created {created_count} new work items")
        print(f"   All eligible submissions now have work items!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    reprocess_existing_submissions()