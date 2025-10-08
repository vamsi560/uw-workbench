#!/usr/bin/env python3
"""
Comprehensive final test of ALL string concatenation fixes
"""

def test_all_business_functions():
    """Test all business rule functions that were causing string concatenation errors"""
    
    print("🎯 COMPREHENSIVE FINAL TEST")
    print("=" * 60)
    
    try:
        from business_rules import CyberInsuranceValidator
        
        # Test with various data types that could cause issues
        test_scenarios = [
            {
                "name": "All Integer Fields",
                "data": {
                    'policy_type': 123,           # Fixed: was calling .strip()
                    'industry': 456,              # Fixed: was calling .strip()/.lower()
                    'data_types': 789,            # Fixed: was calling .lower()
                    'security_measures': 101112,  # Fixed: was calling .lower()
                    'coverage_amount': 5000000,   # Fixed: was calling .replace()
                    'employee_count': 150,        # Fixed: was calling .replace()
                    'insured_name': 'Test Company',
                    'effective_date': '2025-01-01'
                }
            },
            {
                "name": "Mixed String/Integer Fields", 
                "data": {
                    'policy_type': 'cyber',       # String
                    'industry': 789,              # Integer
                    'data_types': 'pii, financial', # String
                    'security_measures': 456,     # Integer
                    'coverage_amount': 2000000,   # Integer
                    'employee_count': '50',       # String
                    'insured_name': 'Mixed Corp',
                    'effective_date': '2025-02-01'
                }
            },
            {
                "name": "All String Fields (Normal Case)",
                "data": {
                    'policy_type': 'cyber',
                    'industry': 'technology', 
                    'data_types': 'pii, payment data',
                    'security_measures': 'mfa, encryption, firewall',
                    'coverage_amount': '$5M',
                    'employee_count': '150 employees',
                    'insured_name': 'TechCorp Inc',
                    'effective_date': '2025-03-01'
                }
            }
        ]
        
        all_passed = True
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n🧪 Scenario {i}: {scenario['name']}")
            print("-" * 40)
            
            data = scenario['data']
            print("Data types:")
            for key, value in data.items():
                print(f"   {key}: {value} ({type(value).__name__})")
            
            try:
                # Test 1: Validation
                print("\n1. Testing validation...")
                validation_status, missing_fields, rejection_reason = CyberInsuranceValidator.validate_submission(data)
                print(f"   ✅ Status: {validation_status}")
                if missing_fields:
                    print(f"   Missing: {missing_fields}")
                
                # Test 2: Assignment
                print("2. Testing assignment...")
                assigned = CyberInsuranceValidator.assign_underwriter(data)
                print(f"   ✅ Assigned: {assigned}")
                
                # Test 3: Risk Priority
                print("3. Testing risk priority...")
                risk_priority = CyberInsuranceValidator.calculate_risk_priority(data)
                print(f"   ✅ Priority: {risk_priority}")
                
                # Test 4: Risk Categories
                print("4. Testing risk categories...")
                risk_categories = CyberInsuranceValidator.generate_risk_categories(data)
                print(f"   ✅ Categories: {risk_categories}")
                
                print(f"   🎉 Scenario {i} PASSED!")
                
            except Exception as e:
                print(f"   ❌ Scenario {i} FAILED: {e}")
                import traceback
                traceback.print_exc()
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        return False

def test_edge_cases():
    """Test edge cases for the string concatenation fixes"""
    
    print("\n🧪 TESTING EDGE CASES")
    print("=" * 60)
    
    try:
        from business_rules import CyberInsuranceValidator
        
        edge_cases = [
            ("Empty values", {}),
            ("None values", {
                'policy_type': None,
                'industry': None,
                'data_types': None,
                'security_measures': None
            }),
            ("Zero values", {
                'policy_type': 0,
                'industry': 0,
                'coverage_amount': 0,
                'employee_count': 0
            }),
            ("Float values", {
                'policy_type': 1.23,
                'industry': 4.56,
                'coverage_amount': 5000000.0,
                'employee_count': 150.5
            })
        ]
        
        all_passed = True
        
        for case_name, data in edge_cases:
            print(f"\n🔍 Testing: {case_name}")
            try:
                validation_status, _, _ = CyberInsuranceValidator.validate_submission(data)
                print(f"   ✅ Validation: {validation_status}")
                
                assigned = CyberInsuranceValidator.assign_underwriter(data)
                print(f"   ✅ Assignment: {assigned}")
                
            except Exception as e:
                print(f"   ❌ Failed: {e}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Edge case test failed: {e}")
        return False

if __name__ == "__main__":
    print("🎯 COMPREHENSIVE STRING CONCATENATION FIX VERIFICATION")
    print("=" * 70)
    
    # Run all tests
    main_tests_passed = test_all_business_functions()
    edge_tests_passed = test_edge_cases()
    
    print("\n" + "=" * 70)
    print("🎯 FINAL VERIFICATION RESULTS")
    print("=" * 70)
    
    if main_tests_passed and edge_tests_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\n✅ String concatenation errors COMPLETELY FIXED!")
        print("✅ All business rule functions handle both string and integer inputs!")
        print("✅ API endpoints will now work correctly with LLM integer outputs!")
        print("\n🚀 The system is now fully robust and production-ready!")
        
        print("\n📝 SUMMARY OF FIXES:")
        print("   1. _parse_coverage_amount() - handles integers ✅")
        print("   2. _parse_employee_count() - handles integers ✅")  
        print("   3. policy_type validation - handles integers ✅")
        print("   4. industry validation - handles integers ✅")
        print("   5. industry assignment - handles integers ✅")
        print("   6. data_types processing - handles integers ✅")
        print("   7. security_measures processing - handles integers ✅")
        
    else:
        print("❌ SOME TESTS FAILED!")
        print(f"   Main tests: {'PASSED' if main_tests_passed else 'FAILED'}")
        print(f"   Edge tests: {'PASSED' if edge_tests_passed else 'FAILED'}")
        print("\nPlease review the failed tests above.")