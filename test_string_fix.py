#!/usr/bin/env python3
"""
Test the fixed string concatenation issue
"""

def test_fixed_coverage_parsing():
    """Test that the fixed coverage parsing works with both strings and integers"""
    
    print("🧪 Testing Fixed Coverage Amount Parsing")
    print("=" * 60)
    
    try:
        from business_rules import CyberInsuranceValidator
        
        # Test cases that would have caused the original error
        test_cases = [
            ("String input: '$1,000,000'", "$1,000,000", 1000000.0),
            ("Integer input: 1000000", 1000000, 1000000.0),
            ("Float input: 1000000.0", 1000000.0, 1000000.0),
            ("String with M: '5M'", "5M", 5000000.0),
            ("String with million: '2 million'", "2 million", 2000000.0),
            ("Zero integer: 0", 0, 0.0),
            ("Empty string: ''", "", None),
            ("None input", None, None),
        ]
        
        print("Testing _parse_coverage_amount with various inputs:")
        all_passed = True
        
        for description, input_val, expected in test_cases:
            try:
                result = CyberInsuranceValidator._parse_coverage_amount(input_val)
                if result == expected:
                    print(f"   ✅ {description}: {result}")
                else:
                    print(f"   ❌ {description}: got {result}, expected {expected}")
                    all_passed = False
            except Exception as e:
                print(f"   ❌ {description}: ERROR - {e}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Error testing coverage parsing: {e}")
        return False

def test_fixed_employee_parsing():
    """Test that the fixed employee count parsing works with both strings and integers"""
    
    print("\n🧪 Testing Fixed Employee Count Parsing")
    print("=" * 60)
    
    try:
        from business_rules import CyberInsuranceValidator
        
        # Test cases that would have caused the original error
        test_cases = [
            ("String input: '500'", "500", 500),
            ("Integer input: 500", 500, 500),
            ("Float input: 500.0", 500.0, 500),
            ("String with K: '2K'", "2K", 2000),
            ("String with range: '100-200'", "100-200", 200),
            ("Zero integer: 0", 0, 0),
            ("Empty string: ''", "", None),
            ("None input", None, None),
        ]
        
        print("Testing _parse_employee_count with various inputs:")
        all_passed = True
        
        for description, input_val, expected in test_cases:
            try:
                result = CyberInsuranceValidator._parse_employee_count(input_val)
                if result == expected:
                    print(f"   ✅ {description}: {result}")
                else:
                    print(f"   ❌ {description}: got {result}, expected {expected}")
                    all_passed = False
            except Exception as e:
                print(f"   ❌ {description}: ERROR - {e}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Error testing employee count parsing: {e}")
        return False

def test_email_intake_simulation():
    """Simulate the email intake process that was causing the error"""
    
    print("\n🧪 Testing Email Intake Simulation")
    print("=" * 60)
    
    try:
        from business_rules import CyberInsuranceValidator
        
        # Simulate LLM extraction data that might contain integers
        extracted_data = {
            'coverage_amount': 5000000,  # Integer - this was causing the error!
            'annual_revenue': 10000000,  # Integer
            'employee_count': 150,       # Integer
            'company_size': 'medium',    # String
            'industry': 'technology'     # String
        }
        
        print("Simulating LLM extracted data with integer values:")
        print(f"   Input data: {extracted_data}")
        
        # Test the functions that were causing the error
        print("\n1. Testing coverage amount parsing...")
        coverage = CyberInsuranceValidator._parse_coverage_amount(
            extracted_data.get('coverage_amount')
        )
        print(f"   ✅ Coverage amount: {coverage}")
        
        print("2. Testing revenue parsing...")
        revenue = CyberInsuranceValidator._parse_revenue(
            extracted_data.get('annual_revenue')
        )
        print(f"   ✅ Annual revenue: {revenue}")
        
        print("3. Testing employee count parsing...")
        employees = CyberInsuranceValidator._parse_employee_count(
            extracted_data.get('employee_count')
        )
        print(f"   ✅ Employee count: {employees}")
        
        print("4. Testing full validation...")
        validation_status, missing_fields, rejection_reason = CyberInsuranceValidator.validate_submission(extracted_data)
        print(f"   ✅ Validation status: {validation_status}")
        
        print("5. Testing risk priority calculation...")
        risk_priority = CyberInsuranceValidator.calculate_risk_priority(extracted_data)
        print(f"   ✅ Risk priority: {risk_priority}")
        
        print("\n🎉 Email intake simulation completed successfully!")
        print("   The string concatenation error should now be fixed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in email intake simulation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🎯 Testing Fixed String Concatenation Error")
    print("=" * 70)
    
    tests = [
        test_fixed_coverage_parsing,
        test_fixed_employee_parsing,
        test_email_intake_simulation,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 70)
    print("🎯 FIX VERIFICATION SUMMARY")
    print("=" * 70)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 ALL TESTS PASSED ({passed}/{total})")
        print("\n✅ String concatenation error FIXED!")
        print("✅ Email intake should now work with integer values from LLM!")
        print("✅ Both string and numeric inputs are now handled correctly!")
    else:
        print(f"⚠️  SOME TESTS FAILED ({passed}/{total})")
        for i, result in enumerate(results, 1):
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   Test {i}: {status}")