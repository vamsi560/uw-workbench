#!/usr/bin/env python3
"""
More targeted test for remaining string concatenation issues
"""

def test_specific_string_operations():
    """Test the specific string operations that might fail"""
    
    print("🧪 TESTING SPECIFIC STRING OPERATIONS")
    print("=" * 60)
    
    # Test each problematic pattern directly
    test_cases = [
        ("policy_type.strip()", 123, lambda x: str(x).strip()),
        ("industry.strip()", 456, lambda x: str(x).strip()),
        ("industry.strip().lower()", 789, lambda x: str(x).strip().lower()),
        ("data_types.lower()", 101112, lambda x: str(x).lower()),
        ("security_measures.lower()", 131415, lambda x: str(x).lower()),
    ]
    
    print("Testing direct string operations on integers:")
    
    for operation, test_value, safe_operation in test_cases:
        print(f"\n🔍 Testing: {operation}")
        print(f"   Input: {test_value} ({type(test_value).__name__})")
        
        # Test the unsafe operation
        try:
            if "strip().lower()" in operation:
                result = test_value.strip().lower()  # This should fail
            elif "strip()" in operation:
                result = test_value.strip()  # This should fail
            elif "lower()" in operation:
                result = test_value.lower()  # This should fail
            
            print(f"   ❌ Unexpected success: {result}")
            
        except AttributeError as e:
            print(f"   ✅ Expected failure: {e}")
            
            # Test the safe operation
            safe_result = safe_operation(test_value)
            print(f"   ✅ Safe alternative: {safe_result}")

def test_business_rules_with_integer_fields():
    """Test business rules with actual integer fields"""
    
    print("\n🧪 TESTING BUSINESS RULES WITH INTEGER STRING FIELDS")
    print("=" * 60)
    
    try:
        from business_rules import CyberInsuranceValidator
        
        # Test data where string fields are integers
        test_data = {
            'policy_type': 123,           # Should be string like "cyber" 
            'industry': 456,              # Should be string like "technology"
            'data_types': 789,            # Should be string like "pii, financial"
            'security_measures': 101112,  # Should be string like "mfa, encryption"
            'coverage_amount': 5000000,   # Numeric field (already fixed)
            'employee_count': 150,        # Numeric field (already fixed)
        }
        
        print("Testing with integer values in string fields:")
        for key, value in test_data.items():
            print(f"   {key}: {value} ({type(value).__name__})")
        
        print("\n1. Testing validation...")
        try:
            validation_status, missing_fields, rejection_reason = CyberInsuranceValidator.validate_submission(test_data)
            print(f"   Result: {validation_status}")
            if missing_fields:
                print(f"   Missing: {missing_fields}")
            if rejection_reason:
                print(f"   Rejection: {rejection_reason}")
        except Exception as e:
            print(f"   ❌ Validation failed: {e}")
            return True  # Error found
        
        print("\n2. Testing assignment...")
        try:
            assigned = CyberInsuranceValidator.assign_underwriter(test_data)
            print(f"   Assigned: {assigned}")
        except Exception as e:
            print(f"   ❌ Assignment failed: {e}")
            return True  # Error found
        
        print("\n3. Testing risk calculation...")
        try:
            risk_categories = CyberInsuranceValidator.generate_risk_categories(test_data)
            print(f"   Risk categories: {risk_categories}")
        except Exception as e:
            print(f"   ❌ Risk calculation failed: {e}")
            return True  # Error found
        
        print("\n✅ All business rule functions completed without string errors")
        return False  # No errors
        
    except Exception as e:
        print(f"❌ Error testing business rules: {e}")
        import traceback
        traceback.print_exc()
        return True

if __name__ == "__main__":
    print("🎯 TARGETED STRING OPERATION TESTING")
    print("=" * 70)
    
    print("Part 1: Direct string operations")
    test_specific_string_operations()
    
    print("\nPart 2: Business rules integration")
    has_errors = test_business_rules_with_integer_fields()
    
    print("\n" + "=" * 70)
    print("🎯 TARGETED TEST RESULTS")
    print("=" * 70)
    
    if has_errors:
        print("🚨 CONFIRMED: String concatenation errors still exist!")
        print("   The business rules functions need additional fixes")
    else:
        print("✅ All tests passed - no string concatenation errors found")
        print("   The default empty string handling may be preventing errors")
    
    print("\n💡 RECOMMENDATION:")
    print("   Even if no errors occur now, it's still best practice to fix")
    print("   all string operations to handle both string and integer inputs")
    print("   for robustness and to prevent future issues.")