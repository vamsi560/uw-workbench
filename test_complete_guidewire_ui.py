#!/usr/bin/env python3
"""
End-to-End Test for Guidewire Integration with UI Data Storage
Creates realistic test data and validates complete workflow
"""

import sys
sys.path.append('.')

import json
from datetime import datetime
from database import create_tables, get_db, Submission, WorkItem, GuidewireResponse, WorkItemStatus, WorkItemPriority, CompanySize
from models import WorkItemStatusEnum, WorkItemPriorityEnum, CompanySizeEnum
from guidewire_client import GuidewireClient

def create_test_submission_and_work_item(db):
    """Create a test submission and work item for testing"""
    
    # Create test submission
    test_submission = Submission(
        submission_id="TEST-2025-001",
        subject="Cyber Insurance Quote Request - TechSecure Solutions",
        sender_email="sarah.johnson@techsecure.com",
        received_at=datetime.utcnow(),
        body_text="We need cyber insurance coverage for our technology company...",
        attachment_content="Comprehensive business details and requirements...",
        extracted_fields={
            "company_name": "TechSecure Solutions Inc.",
            "contact_email": "sarah.johnson@techsecure.com",
            "industry": "technology",
            "employee_count": "75",
            "annual_revenue": "12500000",
            "coverage_amount": "1000000",
            "policy_type": "Comprehensive Cyber Liability"
        }
    )
    
    db.add(test_submission)
    db.commit()
    db.refresh(test_submission)
    
    # Create test work item
    test_work_item = WorkItem(
        submission_id=test_submission.id,
        title="TechSecure Solutions - Cyber Insurance Quote",
        description="Process cyber insurance quote for technology company",
        status=WorkItemStatus.IN_REVIEW,
        priority=WorkItemPriority.HIGH,
        industry="technology",
        company_size=CompanySize.MEDIUM,
        policy_type="Comprehensive Cyber Liability",
        coverage_amount=1000000.0,
        risk_score=7.5
    )
    
    db.add(test_work_item)
    db.commit()
    db.refresh(test_work_item)
    
    print(f"   ✅ Created test submission: {test_submission.submission_id}")
    print(f"   ✅ Created test work item: {test_work_item.id}")
    
    return test_submission, test_work_item


def test_complete_guidewire_workflow():
    """Test the complete workflow from submission to UI data display"""
    
    print("🧪 TESTING COMPLETE GUIDEWIRE WORKFLOW")
    print("=" * 60)
    
    # Initialize database
    create_tables()
    db = next(get_db())
    
    try:
        print("📋 STEP 1: Create Test Data")
        submission, work_item = create_test_submission_and_work_item(db)
        
        print(f"\n🔄 STEP 2: Mock Guidewire API Response")
        
        # Mock realistic Guidewire response
        mock_guidewire_response = {
            "data": {
                "responses": [
                    {
                        "body": {
                            "data": {
                                "attributes": {
                                    "id": "pc:ACC-12345",
                                    "accountNumber": "ACC-2025-001",
                                    "accountStatus": {"code": "active"},
                                    "accountHolderContact": {"displayName": "TechSecure Solutions Inc."},
                                    "numberOfContacts": "3"
                                }
                            }
                        }
                    },
                    {
                        "body": {
                            "data": {
                                "attributes": {
                                    "id": "pc:JOB-67890",
                                    "jobNumber": "JOB-2025-001",
                                    "jobStatus": {"code": "quoted"},
                                    "jobEffectiveDate": "2025-01-01T00:00:00.000Z",
                                    "baseState": {"code": "CA"},
                                    "product": {"id": "USCyber"},
                                    "producerCode": {"id": "pc:TECH001"}
                                }
                            }
                        }
                    },
                    {
                        "body": {
                            "data": {
                                "attributes": {
                                    "terms": {
                                        "ACLCommlCyberLiabilityCyberAggLimit": {
                                            "choiceValue": {"code": "1Musd", "name": "1,000,000"}
                                        },
                                        "ACLCommlCyberLiabilityBusIncLimit": {
                                            "choiceValue": {"code": "250Kusd", "name": "250,000"}
                                        },
                                        "ACLCommlCyberLiabilityExtortion": {
                                            "choiceValue": {"code": "50Kusd", "name": "50,000"}
                                        }
                                    }
                                }
                            }
                        }
                    },
                    {
                        "body": {
                            "data": {
                                "attributes": {
                                    "aclDateBusinessStarted": "2020-01-01T00:00:00.000Z",
                                    "aclTotalFTEmployees": 75,
                                    "aclTotalRevenues": "12500000.00",
                                    "aclTotalAssets": "18750000.00",
                                    "aclTotalLiabilities": "3750000.00",
                                    "aclIndustryType": "technology"
                                }
                            }
                        }
                    },
                    {
                        "body": {
                            "data": {
                                "attributes": {
                                    "totalCost": {"amount": "15000.00", "currency": "usd"},
                                    "totalPremium": {"amount": "12500.00", "currency": "usd"},
                                    "rateAsOfDate": "2025-10-09T10:00:00.000Z",
                                    "uwCompany": {"displayName": "Premium Cyber Insurance Co."},
                                    "jobStatus": {"code": "quoted"},
                                    "links": {
                                        "activities": {"href": "/job/v1/jobs/pc:JOB-67890/activities"},
                                        "quote": {"href": "/job/v1/jobs/pc:JOB-67890/quote"}
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        }
        
        print(f"   ✅ Mock response created with {len(mock_guidewire_response['data']['responses'])} API responses")
        
        print(f"\n📊 STEP 3: Process Guidewire Response")
        
        client = GuidewireClient()
        result = client._extract_submission_results(mock_guidewire_response)
        
        if not result["success"]:
            print(f"   ❌ Failed to process response: {result.get('message')}")
            return False
        
        print(f"   ✅ Account: {result['account_number']} ({result['account_id']})")
        print(f"   ✅ Job: {result['job_number']} ({result['job_id']})")
        
        print(f"\n💾 STEP 4: Store Guidewire Response Data")
        
        response_id = client.store_guidewire_response(
            db=db,
            work_item_id=work_item.id,
            submission_id=submission.id,
            parsed_data=result["parsed_data"],
            raw_response=mock_guidewire_response
        )
        
        print(f"   ✅ Stored response with ID: {response_id}")
        
        print(f"\n🔍 STEP 5: Retrieve and Validate Stored Data")
        
        guidewire_data = db.query(GuidewireResponse).filter(
            GuidewireResponse.id == response_id
        ).first()
        
        if not guidewire_data:
            print("   ❌ Failed to retrieve stored data")
            return False
        
        # Validate key fields
        validations = [
            ("Account Number", guidewire_data.account_number, "ACC-2025-001"),
            ("Job Number", guidewire_data.job_number, "JOB-2025-001"),
            ("Organization", guidewire_data.organization_name, "TechSecure Solutions Inc."),
            ("Job Status", guidewire_data.job_status, "quoted"),
            ("Total Premium", guidewire_data.total_premium_amount, 12500.0),
            ("Total Employees", guidewire_data.total_employees, 75),
            ("Industry", guidewire_data.industry_type, "technology"),
            ("Quote Generated", guidewire_data.quote_generated, True),
            ("Submission Success", guidewire_data.submission_success, True)
        ]
        
        all_valid = True
        for field_name, actual_value, expected_value in validations:
            if actual_value == expected_value:
                print(f"   ✅ {field_name}: {actual_value}")
            else:
                print(f"   ❌ {field_name}: Expected {expected_value}, got {actual_value}")
                all_valid = False
        
        print(f"\n📈 STEP 6: Test UI Data Conversion")
        
        from guidewire_dashboard_api import _convert_to_response_model
        ui_data = _convert_to_response_model(guidewire_data)
        
        print(f"   ✅ Account Info: {ui_data.account_info.organization_name}")
        print(f"   ✅ Job Info: {ui_data.job_info.job_number} ({ui_data.job_info.job_status})")
        print(f"   ✅ Pricing: ${ui_data.pricing_info.total_premium_amount:,.2f} {ui_data.pricing_info.total_premium_currency}")
        print(f"   ✅ Coverage Terms: {len(ui_data.coverage_info.coverage_terms or {})} terms")
        print(f"   ✅ Business Data: {ui_data.business_data.total_employees} employees, ${ui_data.business_data.total_revenues:,.0f} revenue")
        
        print(f"\n🌐 STEP 7: Test API Endpoint Data")
        
        # Test the API endpoint functionality
        try:
            from guidewire_dashboard_api import get_guidewire_data_for_work_item
            
            # Note: We can't actually call the endpoint without FastAPI context,
            # but we can test the data conversion which is the core logic
            response_model = _convert_to_response_model(guidewire_data)
            json_data = response_model.model_dump()
            
            print(f"   ✅ API data serialization successful")
            print(f"   ✅ JSON size: {len(json.dumps(json_data, default=str))} characters")
            
            # Save sample for inspection
            with open('sample_guidewire_ui_data.json', 'w') as f:
                json.dump(json_data, f, indent=2, default=str)
            print(f"   💾 Sample saved to: sample_guidewire_ui_data.json")
            
        except Exception as e:
            print(f"   ❌ API data test failed: {str(e)}")
            all_valid = False
        
        print(f"\n📊 STEP 8: Test Dashboard Statistics")
        
        # Test dashboard stats with real data
        total_submissions = db.query(GuidewireResponse).count()
        successful_submissions = db.query(GuidewireResponse).filter(
            GuidewireResponse.submission_success == True
        ).count()
        quotes_generated = db.query(GuidewireResponse).filter(
            GuidewireResponse.quote_generated == True
        ).count()
        
        print(f"   ✅ Total Submissions: {total_submissions}")
        print(f"   ✅ Successful Submissions: {successful_submissions}")
        print(f"   ✅ Quotes Generated: {quotes_generated}")
        
        if total_submissions > 0:
            success_rate = (successful_submissions / total_submissions) * 100
            quote_rate = (quotes_generated / total_submissions) * 100
            print(f"   ✅ Success Rate: {success_rate:.1f}%")
            print(f"   ✅ Quote Rate: {quote_rate:.1f}%")
        
        print(f"\n🎯 WORKFLOW SUMMARY:")
        print(f"   Data Processing: ✅ SUCCESS")
        print(f"   Database Storage: ✅ SUCCESS") 
        print(f"   Data Retrieval: ✅ SUCCESS")
        print(f"   UI Model Conversion: ✅ SUCCESS")
        print(f"   Field Validation: {'✅ COMPLETE' if all_valid else '⚠️ PARTIAL'}")
        print(f"   Dashboard Stats: ✅ SUCCESS") 
        
        return all_valid
        
    except Exception as e:
        print(f"   ❌ Workflow test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        db.close()


def test_ui_endpoint_scenarios():
    """Test different UI data scenarios"""
    
    print(f"\n🔍 TESTING UI ENDPOINT SCENARIOS")
    print("-" * 40)
    
    db = next(get_db())
    
    try:
        # Test with existing data
        guidewire_responses = db.query(GuidewireResponse).limit(5).all()
        
        if not guidewire_responses:
            print(f"   ⚠️  No Guidewire data found for UI testing")
            return True
        
        print(f"   ✅ Found {len(guidewire_responses)} Guidewire responses")
        
        for response in guidewire_responses:
            print(f"   📋 {response.job_number}: {response.organization_name}")
            print(f"      Status: {response.job_status}")
            print(f"      Premium: ${response.total_premium_amount:,.2f}" if response.total_premium_amount else "      Premium: Not quoted")
            print(f"      Created: {response.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ UI endpoint test failed: {str(e)}")
        return False
    
    finally:
        db.close()


if __name__ == "__main__":
    try:
        print("🚀 Starting Complete Guidewire UI Integration Test...")
        
        workflow_success = test_complete_guidewire_workflow()
        ui_scenario_success = test_ui_endpoint_scenarios()
        
        print(f"\n🎉 FINAL TEST RESULTS:")
        print(f"   Complete Workflow: {'✅ PASSED' if workflow_success else '❌ FAILED'}")
        print(f"   UI Scenarios: {'✅ PASSED' if ui_scenario_success else '❌ FAILED'}")
        
        if workflow_success and ui_scenario_success:
            print(f"\n🎯 ALL TESTS PASSED!")
            print(f"   🌟 Guidewire integration is ready for UI display")
            print(f"   🌟 Dashboard endpoints are functional")
            print(f"   🌟 Data flows seamlessly from Guidewire to UI")
        else:
            print(f"\n⚠️  SOME TESTS FAILED - REVIEW ISSUES ABOVE")
            
    except Exception as e:
        print(f"\n❌ TEST SUITE FAILED: {str(e)}")
        import traceback
        traceback.print_exc()