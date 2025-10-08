#!/usr/bin/env python3
"""
Debug script to test the actual LLM extraction and business rules processing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm_service import llm_service
from business_rules import CyberInsuranceValidator, WorkflowEngine
from bs4 import BeautifulSoup

def test_html_to_text():
    """Test HTML processing"""
    html_content = """<html><head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"><style type="text/css" style="display:none">
<!--
p
	{margin-top:0;
	margin-bottom:0}
-->
</style></head><body dir="ltr"><div class="elementToProof" style="font-family:Aptos,Aptos_EmbeddedFont,Aptos_MSFontService,Calibri,Helvetica,sans-serif; font-size:11pt; color:rgb(0,0,0)">New Submission</div><div class="elementToProof" style="font-family:Aptos,Aptos_EmbeddedFont,Aptos_MSFontService,Calibri,Helvetica,sans-serif; font-size:11pt; color:rgb(0,0,0)"><br></div></body></html>"""
    
    print("1. HTML Processing Test")
    print("="*50)
    
    # Process HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    text_content = soup.get_text(strip=True, separator=' ')
    
    print(f"Original HTML length: {len(html_content)}")
    print(f"Extracted text: '{text_content}'")
    print(f"Extracted text length: {len(text_content)}")
    
    return text_content

def test_llm_extraction():
    """Test LLM extraction with the actual content that would be sent"""
    print("\n2. LLM Extraction Test")
    print("="*50)
    
    # This is what the LLM would receive
    combined_text = """Email Subject: Submission – Orion Data Technologies Inc.
From: Vamsi.Sapireddy@valuemomentum.com
Email Body:
New Submission

Attachment Content:
[No attachment content for this test]"""
    
    print("Input to LLM:")
    print(combined_text)
    print("\n" + "-"*40)
    
    try:
        extracted_data = llm_service.extract_insurance_data(combined_text)
        print("LLM Extracted Data:")
        if isinstance(extracted_data, dict):
            for key, value in extracted_data.items():
                print(f"  {key}: {value}")
        else:
            print(f"  Raw result: {extracted_data}")
        return extracted_data
    except Exception as e:
        print(f"LLM Extraction Error: {e}")
        return {}

def test_business_rules(extracted_data):
    """Test business rules processing"""
    print("\n3. Business Rules Test")
    print("="*50)
    
    try:
        print("Testing validation...")
        validation_status, missing_fields, rejection_reason = CyberInsuranceValidator.validate_submission(extracted_data or {})
        print(f"Validation Status: {validation_status}")
        print(f"Missing Fields: {missing_fields}")
        print(f"Rejection Reason: {rejection_reason}")
        
        print("\nTesting risk calculation...")
        risk_priority = CyberInsuranceValidator.calculate_risk_priority(extracted_data or {})
        print(f"Risk Priority: {risk_priority}")
        
        print("\nTesting underwriter assignment...")
        assigned_underwriter = None
        if validation_status == "Complete":
            assigned_underwriter = CyberInsuranceValidator.assign_underwriter(extracted_data or {})
        print(f"Assigned Underwriter: {assigned_underwriter}")
        
        print("\nTesting risk categories...")
        risk_categories = CyberInsuranceValidator.generate_risk_categories(extracted_data or {})
        print(f"Risk Categories: {risk_categories}")
        
        if risk_categories:
            overall_risk_score = sum(risk_categories.values()) / len(risk_categories)
            print(f"Overall Risk Score: {overall_risk_score}")
        
    except Exception as e:
        print(f"Business Rules Error: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("Testing Logic Apps Processing Pipeline")
    print("="*60)
    
    # Test HTML processing
    text_content = test_html_to_text()
    
    # Test LLM extraction
    extracted_data = test_llm_extraction()
    
    # Test business rules
    test_business_rules(extracted_data)

if __name__ == "__main__":
    main()