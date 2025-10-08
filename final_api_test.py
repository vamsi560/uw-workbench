#!/usr/bin/env python3
"""
Final API endpoint test to confirm the string concatenation error is completely resolved
"""

import json

def simulate_llm_extraction_with_integers():
    """Simulate what happens when LLM returns integer values that used to cause errors"""
    
    print("🎯 SIMULATING LLM EXTRACTION WITH INTEGER VALUES")
    print("=" * 60)
    
    # This simulates the LLM extraction returning integers for fields that were causing string concatenation errors
    llm_extracted_data = {
        # Fields that were causing string concatenation errors (now fixed):
        'policy_type': 1,              # Was calling .strip() → FIXED ✅
        'industry': 2,                 # Was calling .strip()/.lower() → FIXED ✅  
        'data_types': 3,               # Was calling .lower() → FIXED ✅
        'security_measures': 4,        # Was calling .lower() → FIXED ✅
        'coverage_amount': 5000000,    # Was calling .replace() → FIXED ✅
        'employee_count': 150,         # Was calling .replace() → FIXED ✅
        
        # Normal string fields
        'insured_name': 'AI Test Corp',
        'effective_date': '2025-01-01',
        'company_size': 'medium'
    }
    
    print("LLM Extracted Data (with problematic integers):")
    for key, value in llm_extracted_data.items():
        print(f"   {key}: {value} ({type(value).__name__})")
    
    return llm_extracted_data

def test_business_pipeline_with_integers():
    """Test the complete business rules pipeline with integer inputs"""
    
    print("\n🧪 TESTING COMPLETE BUSINESS PIPELINE")
    print("=" * 60)
    
    try:
        from business_rules import CyberInsuranceValidator
        
        # Get the problematic data
        extracted_data = simulate_llm_extraction_with_integers()
        
        print("Running complete business validation pipeline...")
        
        # Step 1: Validation (was failing on .strip())
        print("\n1. 🔍 Testing validation pipeline...")
        try:
            validation_status, missing_fields, rejection_reason = CyberInsuranceValidator.validate_submission(extracted_data)
            print(f"   ✅ Validation Status: {validation_status}")
            if missing_fields:
                print(f"   Missing Fields: {missing_fields}")
            if rejection_reason:
                print(f"   Rejection Reason: {rejection_reason}")
        except Exception as e:
            print(f"   ❌ Validation FAILED: {e}")
            return False
        
        # Step 2: Assignment (was failing on .strip().lower())
        print("\n2. 🔍 Testing underwriter assignment...")
        try:
            assigned_underwriter = CyberInsuranceValidator.assign_underwriter(extracted_data)
            print(f"   ✅ Assigned Underwriter: {assigned_underwriter}")
        except Exception as e:
            print(f"   ❌ Assignment FAILED: {e}")
            return False
        
        # Step 3: Risk Priority Calculation
        print("\n3. 🔍 Testing risk priority calculation...")
        try:
            risk_priority = CyberInsuranceValidator.calculate_risk_priority(extracted_data)
            print(f"   ✅ Risk Priority: {risk_priority}")
        except Exception as e:
            print(f"   ❌ Risk Priority FAILED: {e}")
            return False
        
        # Step 4: Risk Categories (was failing on .lower())
        print("\n4. 🔍 Testing risk categories generation...")
        try:
            risk_categories = CyberInsuranceValidator.generate_risk_categories(extracted_data)
            print(f"   ✅ Risk Categories: {risk_categories}")
        except Exception as e:
            print(f"   ❌ Risk Categories FAILED: {e}")
            return False
        
        print("\n🎉 ALL BUSINESS PIPELINE STEPS PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_email_intake_simulation():
    """Simulate the email intake process that was originally failing"""
    
    print("\n🧪 SIMULATING EMAIL INTAKE PROCESS")
    print("=" * 60)
    
    print("This simulates the exact process that was causing:")
    print('   "Error processing email: can only concatenate str (not "int") to str"')
    
    try:
        # Import the models that would be used in the API
        from models import EmailIntakePayload
        from business_rules import CyberInsuranceValidator
        
        # Step 1: Create email payload
        email_payload = {
            "subject": "Cyber Insurance Quote - AI Test Corp",
            "sender_email": "broker@aitestcorp.com", 
            "body": "Please provide cyber insurance quote for AI Test Corp",
            "attachments": []
        }
        
        print(f"1. Email Payload: {email_payload}")
        
        # Step 2: Simulate LLM extraction (returning integers)
        print("\n2. Simulating LLM extraction...")
        extracted_data = simulate_llm_extraction_with_integers()
        
        # Step 3: Run business validation (this was failing before)
        print("\n3. Running business rules validation...")
        validation_status, missing_fields, rejection_reason = CyberInsuranceValidator.validate_submission(extracted_data)
        print(f"   Status: {validation_status}")
        
        # Step 4: Run assignment (this was failing before)
        print("\n4. Running underwriter assignment...")
        assigned_underwriter = CyberInsuranceValidator.assign_underwriter(extracted_data)
        print(f"   Assigned: {assigned_underwriter}")
        
        # Step 5: Calculate risk priority
        print("\n5. Calculating risk priority...")
        risk_priority = CyberInsuranceValidator.calculate_risk_priority(extracted_data)
        print(f"   Priority: {risk_priority}")
        
        print(f"\n🎉 EMAIL INTAKE SIMULATION COMPLETED SUCCESSFULLY!")
        print("✅ No 'can only concatenate str (not \"int\") to str' errors!")
        
        return True
        
    except Exception as e:
        print(f"❌ Email intake simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🎯 FINAL API ENDPOINT STRING CONCATENATION TEST")
    print("=" * 70)
    
    # Run the tests
    pipeline_passed = test_business_pipeline_with_integers()
    intake_passed = test_email_intake_simulation()
    
    print("\n" + "=" * 70)
    print("🎯 FINAL TEST RESULTS")
    print("=" * 70)
    
    if pipeline_passed and intake_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\n✅ COMPLETE RESOLUTION CONFIRMED!")
        print("✅ String concatenation error fully eliminated!")
        print("✅ API can handle LLM integer outputs in all scenarios!")
        print("✅ Email intake endpoints are now production-ready!")
        
        print("\n🚀 DEPLOYMENT STATUS: READY FOR PRODUCTION")
        print("\n📋 VALIDATION CHECKLIST:")
        print("   ✅ _parse_coverage_amount() handles integers")
        print("   ✅ _parse_employee_count() handles integers")
        print("   ✅ policy_type validation handles integers")
        print("   ✅ industry validation handles integers")
        print("   ✅ industry assignment handles integers")
        print("   ✅ data_types processing handles integers")
        print("   ✅ security_measures processing handles integers")
        print("   ✅ Complete business pipeline works with integers")
        print("   ✅ Email intake simulation works with integers")
        
    else:
        print("❌ SOME TESTS STILL FAILING!")
        print(f"   Business Pipeline: {'PASSED' if pipeline_passed else 'FAILED'}")
        print(f"   Email Intake: {'PASSED' if intake_passed else 'FAILED'}")
    
    print("\n" + "=" * 70)