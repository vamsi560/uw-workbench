#!/usr/bin/env python3
"""
Identify ALL remaining string concatenation issues in business_rules.py
"""

def find_string_operation_issues():
    """Find all places where string operations might fail on integer inputs"""
    
    print("🔍 COMPREHENSIVE STRING OPERATION ANALYSIS")
    print("=" * 60)
    
    issues_found = []
    
    # Issue 1: policy_type field
    print("🚨 ISSUE 1: policy_type field (line 72)")
    print('   Code: policy_type = extracted_fields.get("policy_type", "").strip()')
    print("   Problem: If LLM returns integer, .strip() will fail")
    issues_found.append("policy_type")
    
    # Issue 2: industry field (validation function)
    print("\n🚨 ISSUE 2: industry field (line 77)")
    print('   Code: industry = extracted_fields.get("industry", "").strip()')
    print("   Problem: If LLM returns integer, .strip() will fail")
    issues_found.append("industry")
    
    # Issue 3: industry field (assignment function)
    print("\n🚨 ISSUE 3: industry field (line 110)")
    print('   Code: industry = extracted_fields.get("industry", "").strip().lower()')
    print("   Problem: If LLM returns integer, .strip().lower() will fail")
    issues_found.append("industry_assignment")
    
    # Issue 4: data_types field
    print("\n🚨 ISSUE 4: data_types field (line 168)")
    print('   Code: data_types = extracted_fields.get("data_types", "").lower()')
    print("   Problem: If LLM returns integer, .lower() will fail")
    issues_found.append("data_types")
    
    # Issue 5: security_measures field
    print("\n🚨 ISSUE 5: security_measures field (line 177)")
    print('   Code: security_measures = extracted_fields.get("security_measures", "").lower()')
    print("   Problem: If LLM returns integer, .lower() will fail")
    issues_found.append("security_measures")
    
    print(f"\n📊 TOTAL ISSUES FOUND: {len(issues_found)}")
    print("=" * 60)
    
    return issues_found

def test_potential_failures():
    """Test what happens when LLM returns integers for these fields"""
    
    print("\n🧪 TESTING POTENTIAL FAILURES")
    print("=" * 60)
    
    # Simulate LLM data that might cause errors
    problematic_data = {
        'policy_type': 123,           # Integer instead of string
        'industry': 456,              # Integer instead of string  
        'data_types': 789,            # Integer instead of string
        'security_measures': 101112,  # Integer instead of string
        'coverage_amount': 5000000,   # Integer (already fixed)
        'employee_count': 150,        # Integer (already fixed)
    }
    
    print("Simulating LLM extraction with integer values:")
    for key, value in problematic_data.items():
        print(f"   {key}: {value} ({type(value).__name__})")
    
    try:
        from business_rules import CyberInsuranceValidator
        
        print("\n🔥 Testing validation (this should fail)...")
        validation_status, missing_fields, rejection_reason = CyberInsuranceValidator.validate_submission(problematic_data)
        print(f"   Unexpected success: {validation_status}")
        return False
        
    except Exception as e:
        print(f"   ✅ Expected failure: {e}")
        if "can only concatenate str" in str(e) or "has no attribute" in str(e):
            print("   🎯 Confirmed: String concatenation error!")
            return True
        else:
            print(f"   ❓ Different error: {e}")
            return False

if __name__ == "__main__":
    print("🎯 FINDING REMAINING STRING CONCATENATION ISSUES")
    print("=" * 70)
    
    issues = find_string_operation_issues()
    failure_confirmed = test_potential_failures()
    
    print("\n" + "=" * 70)
    print("🎯 ANALYSIS SUMMARY")
    print("=" * 70)
    
    if failure_confirmed:
        print("🚨 CONFIRMED: Additional string concatenation errors exist!")
        print(f"📍 {len(issues)} fields need to be fixed:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        
        print("\n🔧 NEXT STEPS:")
        print("   1. Fix all string operations to handle both string and integer inputs")
        print("   2. Add type checking before calling string methods")
        print("   3. Convert to string when needed: str(field_value)")
        
    else:
        print("✅ No additional string concatenation errors found")
        print("🎉 All issues appear to be resolved!")
    
    print("\n" + "=" * 70)