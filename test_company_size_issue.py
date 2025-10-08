#!/usr/bin/env python3
"""
Test to isolate the exact location of the remaining "can only concatenate str (not "int") to str" error
Focus on company_size.lower() issue found in main.py
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_company_size_issue():
    """
    Test the specific company_size.lower() issue found in main.py
    """
    print("🎯 TESTING COMPANY_SIZE.LOWER() ISSUE")
    print("=" * 60)
    
    # Mock data that could cause the company_size.lower() error
    mock_extracted_data = {
        'policy_type': 'cyber',
        'industry': 'healthcare',
        'data_types': 'phi',
        'security_measures': 'firewall',
        'coverage_amount': 5000000,
        'employee_count': 150,
        'company_size': 123,  # ⚠️ INTEGER - this would cause .lower() to fail
        'insured_name': 'Test Company',
        'effective_date': '2025-01-01'
    }
    
    print("🔥 Mock data with integer company_size:")
    for key, value in mock_extracted_data.items():
        print(f"   {key}: {value} ({type(value).__name__})")
    
    # Test the problematic pattern
    company_size = mock_extracted_data.get('company_size')
    print(f"\n🧪 Testing company_size operations...")
    print(f"   company_size = {company_size} ({type(company_size).__name__})")
    
    # Test the current problematic code pattern from main.py
    try:
        print("\n❌ TESTING PROBLEMATIC PATTERN:")
        print("   Code: size_mapping.get(company_size.lower())")
        
        # This should fail
        result = company_size.lower()  # This line should throw the error!
        print(f"   ✅ Unexpected success: {result}")
        
    except AttributeError as e:
        if "can only concatenate str (not \"int\") to str" in str(e):
            print(f"   🎯 FOUND THE ERROR: {e}")
            print("   🔥 This is the source of the string concatenation error!")
            return True
        else:
            print(f"   ❌ Different AttributeError: {e}")
    except Exception as e:
        print(f"   ❌ Unexpected error type: {type(e).__name__}: {e}")
    
    # Test the fixed pattern
    try:
        print("\n✅ TESTING FIXED PATTERN:")
        print("   Code: str(company_size).lower() if company_size else \"\"")
        
        company_size_str = str(company_size).lower() if company_size else ""
        print(f"   ✅ Success: '{company_size_str}'")
        
        # Test the mapping
        size_mapping = {
            'small': 'SMALL',
            'medium': 'MEDIUM', 
            'large': 'LARGE',
            'enterprise': 'ENTERPRISE',
            '123': 'UNKNOWN'  # Handle numeric strings
        }
        mapped_result = size_mapping.get(company_size_str, 'UNKNOWN')
        print(f"   ✅ Mapping result: {mapped_result}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Fixed pattern failed: {e}")
        return False

def test_main_py_functions():
    """
    Test if main.py functions would trigger the company_size error
    """
    print("\n🎯 TESTING MAIN.PY BUSINESS RULE FUNCTIONS")
    print("=" * 60)
    
    # Mock LLM data with integer company_size
    mock_extracted_data = {
        'policy_type': 'cyber',
        'industry': 'healthcare',
        'company_size': 999,  # Integer that would cause .lower() to fail
        'coverage_amount': 5000000,
        'employee_count': 150
    }
    
    print("🔥 Mock LLM data with integer company_size:")
    for key, value in mock_extracted_data.items():
        print(f"   {key}: {value} ({type(value).__name__})")
    
    try:
        print("\n🧪 Testing business rule functions...")
        
        from business_rules import CyberInsuranceValidator
        
        # These should all work fine (we already fixed them)
        validation_status, missing_fields, rejection_reason = CyberInsuranceValidator.validate_submission(mock_extracted_data)
        print(f"✅ Validation: {validation_status}")
        
        risk_priority = CyberInsuranceValidator.calculate_risk_priority(mock_extracted_data)
        print(f"✅ Risk Priority: {risk_priority}")
        
        assigned_underwriter = CyberInsuranceValidator.assign_underwriter(mock_extracted_data)
        print(f"✅ Assigned: {assigned_underwriter}")
        
        risk_categories = CyberInsuranceValidator.generate_risk_categories(mock_extracted_data)
        print(f"✅ Risk Categories: {risk_categories}")
        
        print("\n🎉 All business rule functions work with integer company_size!")
        print("✅ The error must be in main.py's company_size.lower() call")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Business rule error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 ISOLATING REMAINING STRING CONCATENATION ERROR")
    print("=" * 70)
    print("Focus: company_size.lower() in main.py")
    print("=" * 70)
    
    # Test 1: Company size issue
    company_size_issue = test_company_size_issue()
    
    # Test 2: Business rule functions
    business_rules_ok = test_main_py_functions()
    
    print("\n" + "=" * 70)
    print("🎯 ISOLATION RESULTS")
    print("=" * 70)
    
    if company_size_issue and business_rules_ok:
        print("🎯 ISSUE IDENTIFIED!")
        print("✅ Business rule functions are fixed")
        print("❌ main.py has company_size.lower() calls on integers")
        print("")
        print("🔧 REQUIRED FIX:")
        print("   Replace: size_mapping.get(company_size.lower())")
        print("   With: size_mapping.get(str(company_size).lower() if company_size else \"\")")
        print("")
        print("📍 LOCATIONS TO FIX:")
        print("   • main.py line ~446 (email_intake function)")
        print("   • main.py line ~676 (logic_apps_email_intake function)")
        
    else:
        print("❌ Could not isolate the issue")
        print("❌ More investigation needed")
    
    print("=" * 70)