#!/usr/bin/env python3
"""Test complete business rules integration with improved LLM extraction"""

from llm_service import LLMService
from business_rules import CyberInsuranceValidator, WorkflowEngine
import json

def test_complete_integration():
    """Test the complete flow: LLM extraction → Business rules validation → Workflow"""
    
    # Initialize components
    llm = LLMService()
    validator = CyberInsuranceValidator()
    workflow = WorkflowEngine()
    
    # Test email with comprehensive information
    email_content = '''Subject: Cyber Insurance Quote Request - MedTech Solutions LLC
From: sarah.johnson@medtechsolutions.com

Dear Underwriting Team,

I am Sarah Johnson, Chief Information Officer at MedTech Solutions LLC. We are seeking comprehensive cyber insurance coverage for our medical device company.

Company Details:
- Business Name: MedTech Solutions LLC
- Industry: Medical Device Manufacturing  
- Employee Count: 850 employees
- Annual Revenue: $45 million
- Business Description: We manufacture FDA-approved medical diagnostic devices

Coverage Requirements:
We are requesting coverage with a limit of $30 million for comprehensive cyber protection covering data breach response, business interruption, and third-party liability.

Technical Environment:
- AWS cloud infrastructure
- HIPAA compliance maintained
- Multi-factor authentication implemented
- Regular penetration testing

Previous Claims: No prior cyber incidents in past 5 years.

Best regards,
Sarah Johnson
Chief Information Officer
MedTech Solutions LLC
'''

    print("=== 1. LLM EXTRACTION ===")
    extracted_data = llm.extract_insurance_data(email_content)
    print(f"Company: {extracted_data.get('company_name')}")
    print(f"Coverage Amount: ${int(extracted_data.get('coverage_amount', 0)):,}")
    print(f"Annual Revenue: ${int(extracted_data.get('annual_revenue', 0)):,}")
    print(f"Employee Count: {extracted_data.get('employee_count')}")
    print(f"Industry: {extracted_data.get('industry')}")
    
    print("\n=== 2. BUSINESS RULES VALIDATION ===")
    # validate_submission returns (status, missing_fields, reason)
    status, missing_fields, reason = validator.validate_submission(extracted_data)
    print(f"Status: {status}")
    print(f"Missing Fields: {missing_fields}")
    if reason:
        print(f"Reason: {reason}")
    
    # Calculate risk assessment
    risk_priority = validator.calculate_risk_priority(extracted_data)
    risk_categories = validator.generate_risk_categories(extracted_data)
    print(f"Risk Priority: {risk_priority}")
    print(f"Risk Categories: {risk_categories}")
    
    # Create validation result dict for workflow
    validation_result = {
        'is_valid': status not in ['Rejected', 'Incomplete'],
        'status': status,
        'missing_fields': missing_fields,
        'reason': reason,
        'risk_priority': risk_priority,
        'risk_categories': risk_categories
    }
    
    print("\n=== 3. WORKFLOW PROCESSING ===")
    # Simple workflow simulation
    if validation_result['is_valid']:
        # Assign underwriter based on risk and coverage
        underwriter = validator.assign_underwriter(
            extracted_data.get('industry', ''),
            int(extracted_data.get('coverage_amount', 0)),
            risk_priority
        )
        workflow_status = 'under_review'
        next_actions = ['Underwriter assigned', 'Risk assessment initiated']
    else:
        underwriter = 'Not assigned'
        workflow_status = 'rejected'
        next_actions = ['Rejection notice sent']
    
    print(f"Status: {workflow_status}")
    print(f"Priority: {risk_priority}")
    print(f"Assigned Underwriter: {underwriter}")
    
    if next_actions:
        print("Next Actions:")
        for action in next_actions:
            print(f"  - {action}")
    
    print("\n=== 4. SUMMARY ===")
    print(f"✅ Extraction: Company '{extracted_data.get('company_name')}' requesting ${int(extracted_data.get('coverage_amount', 0)):,}")
    print(f"✅ Validation: {'PASSED' if validation_result['is_valid'] else 'FAILED'} (Risk: {risk_priority})")
    print(f"✅ Workflow: {workflow_status} → {underwriter}")

if __name__ == "__main__":
    test_complete_integration()