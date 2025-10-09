#!/usr/bin/env python3
"""
Test Guidewire Policy Center with Comprehensive Data
Test with submission that has rich extracted fields
"""

import sys
sys.path.append('.')

import json
from guidewire_client import GuidewireClient
from database import get_db, Submission, WorkItem

def test_with_comprehensive_data():
    """Test with a submission that has comprehensive extracted fields"""
    
    print("🎯 GUIDEWIRE POLICY CENTER - COMPREHENSIVE DATA TEST")
    print("=" * 65)
    
    client = GuidewireClient()
    db = next(get_db())
    
    try:
        # Get a submission with lots of data (from our earlier analysis)
        result = db.query(WorkItem, Submission).join(
            Submission, WorkItem.submission_id == Submission.id
        ).filter(Submission.extracted_fields.isnot(None)).order_by(WorkItem.id.desc()).first()
        
        if not result:
            print("❌ No comprehensive submissions found")
            return
        
        work_item, submission = result
        
        # Parse extracted fields
        if isinstance(submission.extracted_fields, str):
            extracted_data = json.loads(submission.extracted_fields)
        else:
            extracted_data = submission.extracted_fields or {}
        
        print(f"📋 Testing with: {submission.subject}")
        print(f"📊 Fields available: {len(extracted_data)}")
        
        # Show key data
        key_fields = ['company_name', 'industry', 'annual_revenue', 'employee_count', 
                     'policy_type', 'coverage_amount', 'contact_email', 'contact_name']
        
        print(f"\n🏢 KEY BUSINESS DATA:")
        data_quality_score = 0
        for field in key_fields:
            value = extracted_data.get(field, 'Not specified')
            has_value = value and str(value).strip() not in ['', 'Not specified']
            if has_value:
                data_quality_score += 1
            status = "✅" if has_value else "⚪"
            print(f"   {status} {field}: {value}")
        
        print(f"\n📈 Data Quality Score: {data_quality_score}/{len(key_fields)} ({data_quality_score/len(key_fields)*100:.1f}%)")
        
        # Test Guidewire mapping
        print(f"\n🗺️ GUIDEWIRE MAPPING TEST:")
        try:
            guidewire_data = client._map_to_guidewire_format(extracted_data)
            
            print(f"   ✅ Mapping successful!")
            print(f"   📊 Generated sections: {len(guidewire_data)}")
            
            # Show each section
            for section_name, section_data in guidewire_data.items():
                if isinstance(section_data, dict):
                    non_empty = sum(1 for v in section_data.values() if v is not None and str(v).strip())
                    print(f"      {section_name}: {len(section_data)} fields, {non_empty} with data")
                    
                    # Show sample fields for each section
                    sample_count = 0
                    for key, value in section_data.items():
                        if sample_count >= 3:  # Show first 3 fields
                            break
                        if value is not None and str(value).strip():
                            print(f"         ✅ {key}: {value}")
                            sample_count += 1
            
            # Test the business data mapping specifically
            print(f"\n🏭 BUSINESS DATA MAPPING:")
            business_data = client._map_business_data(extracted_data)
            print(f"   Industry Code: {business_data.get('industryCode', 'Not mapped')}")
            print(f"   Entity Type: {business_data.get('entityType', 'Not mapped')}")
            print(f"   Revenue Band: {business_data.get('revenueBand', 'Not mapped')}")
            
            # Test coverage calculations
            print(f"\n💰 COVERAGE CALCULATIONS:")
            coverage_data = client._calculate_coverage_limits(extracted_data)
            for limit_type, amount in coverage_data.items():
                if isinstance(amount, (int, float)):
                    print(f"   {limit_type}: ${amount:,}")
                else:
                    print(f"   {limit_type}: {amount}")
            
            print(f"\n🎯 POLICY CENTER READINESS:")
            readiness_score = 0
            readiness_total = 4
            
            # Check account data
            if guidewire_data.get('account', {}).get('organizationName'):
                print(f"   ✅ Account data ready")
                readiness_score += 1
            else:
                print(f"   ⚠️  Account data incomplete")
            
            # Check job data
            if extracted_data.get('policy_type'):
                print(f"   ✅ Job/Policy data ready")
                readiness_score += 1
            else:
                print(f"   ⚠️  Job/Policy data incomplete")
            
            # Check coverage data
            if any(coverage_data.values()):
                print(f"   ✅ Coverage data ready")
                readiness_score += 1
            else:
                print(f"   ⚠️  Coverage data incomplete")
            
            # Check business data
            if business_data.get('industryCode') != 'OTHER':
                print(f"   ✅ Business classification ready")
                readiness_score += 1
            else:
                print(f"   ⚠️  Business classification needs review")
            
            print(f"\n📊 Policy Center Readiness: {readiness_score}/{readiness_total} ({readiness_score/readiness_total*100:.1f}%)")
            
            if readiness_score >= 3:
                print(f"🎉 READY FOR POLICY CENTER SUBMISSION!")
            else:
                print(f"⚠️  Needs more data for optimal submission")
            
        except Exception as e:
            print(f"❌ Mapping error: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # Test composite request generation
        print(f"\n📋 COMPOSITE REQUEST PREVIEW:")
        try:
            # This would be the actual submission call (simulated)
            print(f"   Would create composite request with:")
            print(f"   1. Account: {extracted_data.get('company_name', 'Unknown Company')}")
            print(f"   2. Policy: {extracted_data.get('policy_type', 'Cyber Insurance')}")
            print(f"   3. Limits: ${extracted_data.get('coverage_amount', 'TBD')}")
            print(f"   4. Premium: To be calculated by Guidewire")
            
        except Exception as e:
            print(f"❌ Request generation error: {str(e)}")
            
    except Exception as e:
        print(f"❌ Test error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_with_comprehensive_data()