#!/usr/bin/env python3
"""Debug LLM extraction to see raw responses"""

from llm_service import LLMService
import json

def debug_extraction():
    llm = LLMService()
    
    email_content = '''Subject: Cyber Insurance Quote Request - MedTech Solutions LLC
From: sarah.johnson@medtechsolutions.com

Company Details:
- Business Name: MedTech Solutions LLC
- Industry: Medical Device Manufacturing  
- Employee Count: 850 employees
- Annual Revenue: $45 million

Coverage Requirements:
We are requesting coverage with a limit of $30 million.
'''
    
    # Let's manually check what the prompt looks like
    prompt = llm._create_extraction_prompt(email_content)
    print("=== PROMPT ===")
    print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
    print("\n=== EXTRACTING ===")
    
    try:
        details = llm.extract_insurance_data(email_content)
        print("=== EXTRACTED DATA ===")
        print(json.dumps(details, indent=2))
        
        # Check specific fields
        print("\n=== KEY FIELDS ===")
        print(f"Coverage Amount: '{details.get('coverage_amount')}'")
        print(f"Annual Revenue: '{details.get('annual_revenue')}'")
        print(f"Company Name: '{details.get('company_name')}'")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_extraction()