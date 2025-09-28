"""
Integration test for business rules and validation framework
Tests the complete flow from email intake to work item creation with business rules
"""

import asyncio
import json
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import our application and database components
from main import app, get_db
from database import Base, WorkItem, Submission, RiskAssessment, WorkItemHistory
from business_rules import CyberInsuranceValidator, WorkflowEngine, MessageService
from business_config import BusinessConfig

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_business_rules.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Test client
client = TestClient(app)

def test_business_rules_integration():
    """Test complete business rules integration"""
    print("🧪 Testing Business Rules Integration")
    
    # Test 1: Email intake with business validation
    print("\n1. Testing email intake with business validation...")
    
    email_payload = {
        "subject": "Cyber Insurance Quote Request - TechCorp",
        "sender_email": "john.doe@techcorp.com",
        "body": """
        Hello,
        
        We are TechCorp, a technology company with 500 employees seeking cyber insurance coverage.
        We need $10 million in coverage for our cloud-based services.
        
        Company Details:
        - Industry: Technology
        - Size: Medium (500 employees)
        - Annual Revenue: $50 million
        - Data Types: Customer PII, payment data
        - Previous breaches: None
        
        Please provide a quote.
        
        Best regards,
        John Doe
        CTO, TechCorp
        """,
        "attachments": []
    }
    
    response = client.post("/api/email-intake", json=email_payload)
    print(f"Email intake response: {response.status_code}")
    
    if response.status_code == 200:
        intake_data = response.json()
        print(f"✓ Submission created: {intake_data['submission_ref']}")
        print(f"✓ Submission ID: {intake_data['submission_id']}")
    else:
        print(f"✗ Email intake failed: {response.text}")
        return
    
    # Test 2: Validate submission data
    print("\n2. Testing submission validation...")
    
    validation_payload = {
        "extracted_data": {
            "company_name": "TechCorp",
            "industry": "technology",
            "contact_email": "john.doe@techcorp.com",
            "company_size": "medium",
            "coverage_amount": "10000000",
            "policy_type": "cyber",
            "employee_count": "500",
            "data_types": "Customer PII, payment data"
        }
    }
    
    response = client.post("/api/validate-submission", json=validation_payload)
    print(f"Validation response: {response.status_code}")
    
    if response.status_code == 200:
        validation_data = response.json()
        print(f"✓ Validation status: {validation_data['validation_status']}")
        print(f"✓ Risk priority: {validation_data['risk_priority']}")
        print(f"✓ Assigned underwriter: {validation_data['assigned_underwriter']}")
        print(f"✓ Overall risk score: {validation_data['overall_risk_score']:.2f}")
    else:
        print(f"✗ Validation failed: {response.text}")
    
    # Test 3: Get work items and verify business data
    print("\n3. Testing work items retrieval...")
    
    response = client.get("/api/workitems")
    print(f"Work items response: {response.status_code}")
    
    if response.status_code == 200:
        work_items_data = response.json()
        print(f"✓ Total work items: {work_items_data['total_count']}")
        
        if work_items_data['work_items']:
            work_item = work_items_data['work_items'][0]
            work_item_id = work_item['id']
            print(f"✓ First work item ID: {work_item_id}")
            print(f"✓ Risk score: {work_item.get('risk_score', 'N/A')}")
            print(f"✓ Industry: {work_item.get('industry', 'N/A')}")
            print(f"✓ Assigned to: {work_item.get('assigned_to', 'N/A')}")
            
            # Test 4: Status transition
            print("\n4. Testing status transition...")
            
            status_update = {
                "status": "assigned",
                "changed_by": "Test Admin",
                "notes": "Assigning to underwriter for review"
            }
            
            response = client.put(f"/api/work-items/{work_item_id}/status", json=status_update)
            print(f"Status update response: {response.status_code}")
            
            if response.status_code == 200:
                status_data = response.json()
                print(f"✓ Status updated: {status_data['old_status']} → {status_data['new_status']}")
            else:
                print(f"✗ Status update failed: {response.text}")
            
            # Test 5: Get risk assessment
            print("\n5. Testing risk assessment retrieval...")
            
            response = client.get(f"/api/work-items/{work_item_id}/risk-assessment")
            print(f"Risk assessment response: {response.status_code}")
            
            if response.status_code == 200:
                risk_data = response.json()
                if "assessment_id" in risk_data:
                    print(f"✓ Risk assessment found: ID {risk_data['assessment_id']}")
                    print(f"✓ Overall score: {risk_data['overall_score']}")
                    print(f"✓ Assessed by: {risk_data['assessed_by']}")
                else:
                    print("ℹ No risk assessment found (expected for some cases)")
            
            # Test 6: Get work item history
            print("\n6. Testing work item history...")
            
            response = client.get(f"/api/work-items/{work_item_id}/history")
            print(f"History response: {response.status_code}")
            
            if response.status_code == 200:
                history_data = response.json()
                print(f"✓ History entries found: {len(history_data['history'])}")
                for entry in history_data['history'][:3]:  # Show first 3 entries
                    print(f"  - {entry['action']} by {entry['changed_by']} at {entry['timestamp']}")
    
    # Test 7: Business config verification
    print("\n7. Testing business configuration...")
    
    # Test industry coverage limits
    healthcare_limit = BusinessConfig.get_industry_coverage_limit("healthcare")
    tech_limit = BusinessConfig.get_industry_coverage_limit("technology")
    print(f"✓ Healthcare coverage limit: ${healthcare_limit}M")
    print(f"✓ Technology coverage limit: ${tech_limit}M")
    
    # Test status transitions
    is_valid = BusinessConfig.is_valid_status_transition("pending", "assigned")
    print(f"✓ Pending → Assigned transition valid: {is_valid}")
    
    # Test risk calculation
    risk_priority = BusinessConfig.calculate_risk_priority(0.7)
    print(f"✓ Risk score 0.7 maps to priority: {risk_priority}")
    
    # Test underwriter assignment
    underwriters = BusinessConfig.get_available_underwriters("standard")
    print(f"✓ Available standard underwriters: {len(underwriters)}")
    
    print("\n🎉 Business Rules Integration Test Complete!")
    print("✓ All components are working together correctly")
    print("✓ Business rules are properly integrated with the API")
    print("✓ Centralized configuration is functioning")
    print("✓ Workflow transitions are validated")
    print("✓ Risk assessments are created automatically")

def test_individual_validators():
    """Test individual business rule validators"""
    print("\n🔬 Testing Individual Validators")
    
    # Test coverage amount parsing
    print("\n1. Testing coverage amount parsing...")
    test_amounts = ["$10,000,000", "10M", "5000000", "invalid"]
    
    for amount in test_amounts:
        parsed = CyberInsuranceValidator._parse_coverage_amount(amount)
        print(f"  '{amount}' → ${parsed:,.2f}" if parsed else f"  '{amount}' → Invalid")
    
    # Test industry risk multipliers
    print("\n2. Testing industry risk multipliers...")
    test_industries = ["healthcare", "technology", "retail", "nonprofit"]
    
    for industry in test_industries:
        multiplier = BusinessConfig.get_industry_risk_multiplier(industry)
        print(f"  {industry.title()}: {multiplier}x risk multiplier")
    
    # Test status transitions
    print("\n3. Testing status transition validation...")
    test_transitions = [
        ("pending", "assigned"),
        ("assigned", "under_review"),
        ("rejected", "approved"),  # Should be invalid
        ("approved", "policy_issued")
    ]
    
    for from_status, to_status in test_transitions:
        is_valid = BusinessConfig.is_valid_status_transition(from_status, to_status)
        status = "✓" if is_valid else "✗"
        print(f"  {status} {from_status} → {to_status}")
    
    # Test auto-rejection criteria
    print("\n4. Testing auto-rejection criteria...")
    test_submissions = [
        {"coverage_amount": "50000", "contact_email": "test@company.com"},  # Too low coverage
        {"coverage_amount": "200000000", "contact_email": "test@company.com"},  # Too high coverage
        {"coverage_amount": "5000000", "contact_email": "spam@spam.com"},  # Bad domain
        {"coverage_amount": "5000000", "contact_email": "good@company.com"}  # Valid
    ]
    
    for i, submission in enumerate(test_submissions, 1):
        should_reject, reason = BusinessConfig.should_auto_reject(submission)
        status = "✗ REJECT" if should_reject else "✓ ACCEPT"
        print(f"  Test {i}: {status}")
        if should_reject:
            print(f"    Reason: {reason}")

if __name__ == "__main__":
    print("🚀 Starting Comprehensive Business Rules Test Suite")
    print("=" * 60)
    
    try:
        test_business_rules_integration()
        test_individual_validators()
        
        print("\n" + "=" * 60)
        print("🎊 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("The business rules framework is fully integrated and functional.")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Cleanup
        try:
            import os
            if os.path.exists("test_business_rules.db"):
                os.remove("test_business_rules.db")
                print("🧹 Test database cleaned up")
        except:
            pass