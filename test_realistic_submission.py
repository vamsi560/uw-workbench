"""
Test processing of a realistic cyber insurance submission email
This demonstrates how the business rules engine processes a comprehensive submission
"""

import json
from business_rules import CyberInsuranceValidator, WorkflowEngine, MessageService
from business_config import BusinessConfig

def test_realistic_submission():
    """Test processing of the realistic MedTech Solutions submission"""
    
    print("🏥 Processing MedTech Solutions Cyber Insurance Submission")
    print("=" * 70)
    
    # Simulated data that would be extracted from the email by LLM
    extracted_data = {
        "company_name": "MedTech Solutions Inc.",
        "industry": "healthcare",
        "contact_email": "sarah.johnson@medtechsolutions.com",
        "contact_name": "Sarah Johnson",
        "contact_title": "Chief Information Security Officer",
        "company_size": "medium",
        "employee_count": "350",
        "annual_revenue": "45000000",
        "years_in_operation": "8",
        "coverage_amount": "30000000",
        "policy_type": "comprehensive_cyber_liability",
        "deductible": "100000",
        "effective_date": "2026-01-01",
        "data_types": "PHI, PII, PCI, Electronic Health Records, Medical device data",
        "security_measures": "SOC 2 Type II, HIPAA, ISO 27001, Penetration testing, 24/7 SOC, MFA, Encryption",
        "compliance_certifications": "HIPAA, SOC 2 Type II, ISO 27001, PCI DSS Level 1, GDPR, FDA 510(k)",
        "previous_incidents": "none",
        "previous_breach": "no",
        "business_type": "saas",
        "customer_count": "500+",
        "cloud_usage": "yes",
        "remote_workforce": "40%",
        "current_coverage": "15000000",
        "credit_rating": "A-"
    }
    
    print("📧 Email Data Extracted:")
    print(f"  Company: {extracted_data['company_name']}")
    print(f"  Industry: {extracted_data['industry'].title()}")
    print(f"  Coverage Requested: ${int(extracted_data['coverage_amount']):,}")
    print(f"  Contact: {extracted_data['contact_name']} ({extracted_data['contact_title']})")
    
    print("\n🔍 Running Business Rules Validation...")
    
    # Step 1: Validate submission
    validation_status, missing_fields, rejection_reason = CyberInsuranceValidator.validate_submission(extracted_data)
    
    print(f"\n✅ Validation Results:")
    print(f"  Status: {validation_status}")
    if missing_fields:
        print(f"  Missing Fields: {', '.join(missing_fields)}")
    if rejection_reason:
        print(f"  Rejection Reason: {rejection_reason}")
    
    # Step 2: Calculate risk priority
    risk_priority = CyberInsuranceValidator.calculate_risk_priority(extracted_data)
    print(f"  Risk Priority: {risk_priority.upper()}")
    
    # Step 3: Generate risk assessment
    risk_categories = CyberInsuranceValidator.generate_risk_categories(extracted_data)
    overall_risk_score = sum(risk_categories.values()) / len(risk_categories)
    
    print(f"\n📊 Risk Assessment:")
    print(f"  Overall Risk Score: {overall_risk_score:.2f}")
    print("  Risk Categories:")
    for category, score in risk_categories.items():
        print(f"    {category.title()}: {score:.2f}")
    
    # Step 4: Check industry limits
    industry_limit = BusinessConfig.get_industry_coverage_limit("healthcare")
    requested_coverage = int(extracted_data["coverage_amount"]) / 1_000_000
    
    print(f"\n🏭 Industry Analysis:")
    print(f"  Healthcare Industry Limit: ${industry_limit}M")
    print(f"  Requested Coverage: ${requested_coverage:.0f}M")
    
    if requested_coverage <= industry_limit:
        print(f"  ✅ Within industry limits")
    else:
        print(f"  ⚠️ Exceeds industry limit by ${requested_coverage - industry_limit:.0f}M")
    
    # Step 5: Assign underwriter
    assigned_underwriter = CyberInsuranceValidator.assign_underwriter(extracted_data)
    print(f"\n👤 Underwriter Assignment:")
    print(f"  Assigned to: {assigned_underwriter}")
    
    # Determine underwriter level based on assignment
    senior_underwriters = BusinessConfig.get_available_underwriters("senior")
    standard_underwriters = BusinessConfig.get_available_underwriters("standard")
    
    if assigned_underwriter in senior_underwriters:
        underwriter_level = "Senior"
    elif assigned_underwriter in standard_underwriters:
        underwriter_level = "Standard"
    else:
        underwriter_level = "Junior"
    
    print(f"  Level: {underwriter_level} Underwriter")
    print(f"  Reason: Healthcare industry, ${requested_coverage:.0f}M coverage")
    
    # Step 6: Business rules summary
    print(f"\n📋 Business Rules Applied:")
    
    # Check if high-risk industry
    risk_multiplier = BusinessConfig.get_industry_risk_multiplier("healthcare")
    print(f"  Industry Risk Multiplier: {risk_multiplier}x")
    
    if risk_multiplier >= 1.6:
        print(f"  Classification: High-risk industry")
    else:
        print(f"  Classification: Standard industry")
    
    # Auto-rejection check
    should_reject, auto_reject_reason = BusinessConfig.should_auto_reject(extracted_data)
    if should_reject:
        print(f"  ❌ Auto-rejection triggered: {auto_reject_reason}")
    else:
        print(f"  ✅ Passes auto-rejection criteria")
    
    # Step 7: Workflow recommendations
    print(f"\n🔄 Workflow Recommendations:")
    
    if validation_status == "Complete":
        print(f"  Next Status: ASSIGNED")
        print(f"  Action: Route to {assigned_underwriter} for technical review")
        
        if risk_priority == "high":
            print(f"  Priority: HIGH - Expedite review process")
            print(f"  SLA: Initial review within 24 hours")
        else:
            print(f"  Priority: {risk_priority.upper()}")
            print(f"  SLA: Initial review within 72 hours")
            
    elif validation_status == "Incomplete":
        print(f"  Next Status: PENDING_INFO")
        print(f"  Action: Request missing information from broker")
        print(f"  Required: {', '.join(missing_fields)}")
        
    else:
        print(f"  Next Status: REJECTED")
        print(f"  Action: Send rejection notification")
        print(f"  Reason: {rejection_reason}")
    
    # Step 8: Estimated processing
    print(f"\n⏱️ Processing Estimates:")
    
    if validation_status == "Complete":
        if risk_priority == "high":
            print(f"  Quote Turnaround: 3-5 business days")
            print(f"  Underwriting Review: 1-2 days")
        else:
            print(f"  Quote Turnaround: 5-7 business days")
            print(f"  Underwriting Review: 2-3 days")
        
        print(f"  Technical Review: Required (healthcare data sensitivity)")
        print(f"  Compliance Review: Required (HIPAA, SOC2)")
        
        if requested_coverage > 25:
            print(f"  Senior Management Approval: Required (>${requested_coverage:.0f}M)")
    
    # Step 9: Communication preview
    print(f"\n📬 Automated Communications:")
    
    if validation_status == "Complete":
        # Assignment notification
        assignment_result = MessageService.send_assignment_notification(assigned_underwriter, type('WorkItem', (), {
            'id': 12345,
            'title': extracted_data['company_name'],
            'industry': extracted_data['industry'],
            'coverage_amount': int(extracted_data['coverage_amount']),
            'priority': risk_priority,
            'risk_score': overall_risk_score
        })())
        
        print(f"  ✉️ Assignment notification sent to {assigned_underwriter}")
        print(f"     Subject: {assignment_result['subject']}")
        
    elif validation_status == "Incomplete":
        # Info request
        info_request_result = MessageService.send_info_request(
            extracted_data['contact_email'],
            type('WorkItem', (), {'title': extracted_data['company_name']})(),
            assigned_underwriter,
            missing_fields
        )
        
        print(f"  ✉️ Information request sent to {extracted_data['contact_email']}")
        print(f"     Subject: {info_request_result['subject']}")
        
    else:
        # Rejection notification
        rejection_result = MessageService.send_rejection_notification(
            extracted_data['contact_email'],
            type('WorkItem', (), {'title': extracted_data['company_name']})(),
            rejection_reason
        )
        
        print(f"  ✉️ Rejection notification sent to {extracted_data['contact_email']}")
        print(f"     Subject: {rejection_result['subject']}")
    
    # Summary
    print(f"\n🎯 Processing Summary:")
    print(f"  Submission: {validation_status}")
    print(f"  Risk Level: {overall_risk_score:.2f} ({risk_priority.upper()})")
    print(f"  Assignment: {assigned_underwriter} ({underwriter_level})")
    print(f"  Industry Compliance: Healthcare regulations apply")
    print(f"  Coverage Assessment: Within industry limits")
    
    print(f"\n" + "=" * 70)
    print(f"✅ MedTech Solutions submission processed successfully!")
    print(f"🚀 Business rules engine automated the entire workflow")

if __name__ == "__main__":
    test_realistic_submission()