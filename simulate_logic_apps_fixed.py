#!/usr/bin/env python3
"""
Simulate the actual Logic Apps processing to test work item creation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, Submission, WorkItem, WorkItemStatus, WorkItemPriority, CompanySize
from business_rules import CyberInsuranceValidator
import uuid
from datetime import datetime
import json

def simulate_logic_apps_processing():
    """Simulate the exact Logic Apps processing logic"""
    
    print("🧪 SIMULATING LOGIC APPS PROCESSING")
    print("=" * 60)
    
    # Create the exact extracted data from the comprehensive submission
    extracted_data = {
        "agency_id": "TR-12345",
        "agency_name": "TechRisk Insurance Partners",
        "company_name": "TechCorp Solutions Inc.",
        "named_insured": "TechCorp Solutions Incorporated",
        "entity_type": "Corporation",
        "industry": "technology",
        "employee_count": "150",
        "annual_revenue": "25000000",
        "policy_type": "Comprehensive Cyber Liability",  # This was being rejected before
        "coverage_amount": "5000000",
        "effective_date": "2024-01-01",
        "contact_name": "John Smith",
        "contact_title": "Chief Technology Officer",
        "contact_email": "j.smith@techcorp.com",
        "contact_phone": "(555) 123-4567"
    }
    
    print("📊 Extracted Data:")
    print(f"   Company: {extracted_data.get('company_name')}")
    print(f"   Industry: {extracted_data.get('industry')}")
    print(f"   Policy Type: {extracted_data.get('policy_type')}")
    print(f"   Coverage: ${int(extracted_data.get('coverage_amount', 0)):,}")
    
    # Test business rules validation
    validation_status, missing_fields, rejection_reason = CyberInsuranceValidator.validate_submission(extracted_data)
    print(f"\n✅ Validation Results:")
    print(f"   Status: {validation_status}")
    print(f"   Missing Fields: {missing_fields}")
    print(f"   Rejection Reason: {rejection_reason}")
    
    if validation_status == "Rejected":
        print("❌ SUBMISSION REJECTED - Work items should not be created")
        return
    
    # Calculate risk and assignment
    risk_priority = CyberInsuranceValidator.calculate_risk_priority(extracted_data)
    assigned_underwriter = CyberInsuranceValidator.assign_underwriter(extracted_data)
    risk_categories = CyberInsuranceValidator.generate_risk_categories(extracted_data)
    overall_risk_score = sum(risk_categories.values()) / len(risk_categories) if risk_categories else 0
    
    print(f"   Risk Priority: {risk_priority}")
    print(f"   Assigned Underwriter: {assigned_underwriter}")
    print(f"   Overall Risk Score: {overall_risk_score:.2f}")
    
    db = SessionLocal()
    try:
        # Create submission (like the Logic Apps endpoint does)
        submission_ref = str(uuid.uuid4())
        next_submission_id = 25  # Use a test ID
        
        submission = Submission(
            submission_id=next_submission_id,
            submission_ref=submission_ref,
            subject="Test Cyber Insurance Submission - Simulated",
            sender_email="test@techcorp.com",
            body_text="Simulated test submission",
            attachment_content="",
            extracted_fields=extracted_data,  # This should be a dict
            received_at=datetime.utcnow(),
            task_status="pending"
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
        
        print(f"\n📝 Created Submission:")
        print(f"   ID: {submission.id}")
        print(f"   Ref: {submission.submission_ref}")
        
        # Create work item (exactly like the Logic Apps endpoint)
        work_item = WorkItem(
            submission_id=submission.id,
            title="Test Cyber Insurance Submission - Simulated",
            description=f"Email from test@techcorp.com",
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
        elif validation_status == "Rejected":
            work_item.status = WorkItemStatus.REJECTED
            work_item.description += f"\n\nRejection reason: {str(rejection_reason) if rejection_reason else ''}"
        
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
        
        print(f"\n🎉 SUCCESS! Work Item Created:")
        print(f"   ID: {work_item.id}")
        print(f"   Status: {work_item.status}")
        print(f"   Priority: {work_item.priority}")
        print(f"   Assigned To: {work_item.assigned_to}")
        print(f"   Industry: {work_item.industry}")
        print(f"   Policy Type: {work_item.policy_type}")
        print(f"   Coverage Amount: ${work_item.coverage_amount:,}" if work_item.coverage_amount else "Coverage: None")
        print(f"   Risk Score: {work_item.risk_score}")
        
        # Verify in database
        verification = db.query(WorkItem).filter(WorkItem.id == work_item.id).first()
        if verification:
            print(f"\n✅ VERIFICATION: Work item {verification.id} confirmed in database")
        else:
            print(f"\n❌ VERIFICATION FAILED: Work item not found in database")
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    simulate_logic_apps_processing()