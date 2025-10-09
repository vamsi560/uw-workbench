#!/usr/bin/env python3
"""
Test the Logic Apps work item creation logic specifically
"""

import sys
sys.path.append('.')

from database import SessionLocal, Submission, WorkItem, WorkItemStatus, WorkItemPriority
from business_rules import CyberInsuranceValidator
import json

def test_work_item_creation():
    """Test work item creation for existing submissions"""
    db = SessionLocal()
    
    try:
        # Get the most recent submission
        latest_submission = db.query(Submission).order_by(Submission.created_at.desc()).first()
        
        if not latest_submission:
            print("❌ No submissions found")
            return
        
        print(f"🧪 Testing work item creation for submission ID: {latest_submission.id}")
        print(f"   Subject: {latest_submission.subject}")
        print(f"   From: {latest_submission.sender_email}")
        
        # Test the extracted data
        extracted_data = latest_submission.extracted_fields
        if isinstance(extracted_data, str):
            try:
                extracted_data = json.loads(extracted_data)
            except:
                print(f"❌ Could not parse extracted_fields JSON")
                return
        
        print(f"   Extracted data type: {type(extracted_data)}")
        
        # Test business rules validation
        try:
            validation_status, missing_fields, rejection_reason = CyberInsuranceValidator.validate_submission(extracted_data or {})
            print(f"   ✅ Validation Status: {validation_status}")
            print(f"   Missing fields: {missing_fields}")
            print(f"   Rejection reason: {rejection_reason}")
        except Exception as e:
            print(f"   ❌ Validation error: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Test risk priority calculation
        try:
            risk_priority = CyberInsuranceValidator.calculate_risk_priority(extracted_data or {})
            print(f"   ✅ Risk Priority: {risk_priority}")
        except Exception as e:
            print(f"   ❌ Risk priority error: {e}")
            return
        
        # Test underwriter assignment
        try:
            assigned_underwriter = None
            if validation_status == "Complete":
                assigned_underwriter = CyberInsuranceValidator.assign_underwriter(extracted_data or {})
            print(f"   ✅ Assigned Underwriter: {assigned_underwriter}")
        except Exception as e:
            print(f"   ❌ Underwriter assignment error: {e}")
            return
        
        # Test risk categories
        try:
            risk_categories = CyberInsuranceValidator.generate_risk_categories(extracted_data or {})
            overall_risk_score = sum(risk_categories.values()) / len(risk_categories) if risk_categories else 0
            print(f"   ✅ Risk Categories: {risk_categories}")
            print(f"   ✅ Overall Risk Score: {overall_risk_score}")
        except Exception as e:
            print(f"   ❌ Risk categories error: {e}")
            return
        
        # Test work item creation
        try:
            print(f"\n🏭 Creating test work item...")
            
            work_item = WorkItem(
                submission_id=latest_submission.id,
                title=latest_submission.subject,
                description=f"Email from {latest_submission.sender_email}",
                status=WorkItemStatus.PENDING,
                priority=WorkItemPriority.MEDIUM
            )
            
            # Apply extracted data
            if extracted_data and isinstance(extracted_data, dict):
                work_item.industry = extracted_data.get('industry')
                work_item.policy_type = extracted_data.get('policy_type')
                work_item.coverage_amount = CyberInsuranceValidator._parse_coverage_amount(
                    extracted_data.get('coverage_amount') or ''
                )
            
            print(f"   ✅ Work item created in memory")
            print(f"   Title: {work_item.title}")
            print(f"   Industry: {work_item.industry}")
            print(f"   Policy Type: {work_item.policy_type}")
            print(f"   Coverage Amount: {work_item.coverage_amount}")
            
            # Try to save to database
            db.add(work_item)
            db.flush()
            
            print(f"   ✅ Work item saved to database with ID: {work_item.id}")
            
            # Rollback the test transaction
            db.rollback()
            print(f"   🔄 Test transaction rolled back (work item not permanently saved)")
            
        except Exception as e:
            print(f"   ❌ Work item creation error: {e}")
            import traceback
            traceback.print_exc()
            db.rollback()
            return
        
        print(f"\n✅ Work item creation logic is working!")
        print(f"❓ The issue must be in the endpoint exception handling or transaction commit")
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    test_work_item_creation()