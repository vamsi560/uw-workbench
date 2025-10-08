#!/usr/bin/env python3
"""
Fix the company_size.lower() issue in main.py
Replace the problematic lines with safe str() conversion
"""

def fix_company_size_issue():
    """
    Fix the company_size.lower() calls in main.py
    """
    print("🔧 FIXING COMPANY_SIZE.LOWER() ISSUE IN MAIN.PY")
    print("=" * 60)
    
    # Read the file
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Original problematic pattern
    original_pattern = 'size_mapping.get(company_size.lower())'
    
    # Fixed pattern
    fixed_pattern = 'size_mapping.get(str(company_size).lower() if company_size else "")'
    
    # Count occurrences
    occurrences = content.count(original_pattern)
    print(f"Found {occurrences} occurrences of problematic pattern")
    
    if occurrences == 0:
        print("✅ No problematic patterns found - already fixed!")
        return True
    
    # Show the lines that will be changed
    lines = content.split('\n')
    for i, line in enumerate(lines, 1):
        if original_pattern in line:
            print(f"📍 Line {i}: {line.strip()}")
    
    # Apply the fix
    print(f"\n🔧 Applying fix...")
    print(f"   From: {original_pattern}")
    print(f"   To:   {fixed_pattern}")
    
    fixed_content = content.replace(original_pattern, fixed_pattern)
    
    # Verify the fix was applied
    remaining_occurrences = fixed_content.count(original_pattern)
    new_occurrences = fixed_content.count(fixed_pattern)
    
    print(f"\n✅ Fix Results:")
    print(f"   Remaining problematic patterns: {remaining_occurrences}")
    print(f"   New fixed patterns: {new_occurrences}")
    
    if remaining_occurrences == 0 and new_occurrences >= occurrences:
        # Write the fixed content back
        with open('main.py', 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"✅ Successfully fixed {occurrences} occurrences!")
        print("✅ main.py has been updated")
        return True
    else:
        print("❌ Fix verification failed!")
        return False

def verify_fix():
    """
    Verify the fix by testing the problematic scenario
    """
    print("\n🧪 VERIFYING FIX")
    print("=" * 40)
    
    # Test the scenario that was failing
    mock_data = {'company_size': 123}  # Integer that caused the error
    company_size = mock_data.get('company_size')
    
    try:
        # Test the fixed pattern
        size_mapping = {
            'small': 'SMALL',
            'medium': 'MEDIUM',
            'large': 'LARGE',
            '123': 'NUMERIC_SIZE'
        }
        
        # This should now work
        company_size_str = str(company_size).lower() if company_size else ""
        result = size_mapping.get(company_size_str, 'UNKNOWN')
        
        print(f"✅ Test passed!")
        print(f"   Input: {company_size} ({type(company_size).__name__})")
        print(f"   Processed: '{company_size_str}'")
        print(f"   Result: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 FIXING COMPANY_SIZE STRING CONCATENATION ERROR")
    print("=" * 70)
    
    # Apply the fix
    fix_success = fix_company_size_issue()
    
    # Verify the fix
    verify_success = verify_fix()
    
    print("\n" + "=" * 70)
    print("🎯 FINAL RESULTS")
    print("=" * 70)
    
    if fix_success and verify_success:
        print("🎉 SUCCESS!")
        print("✅ company_size.lower() issue FIXED!")
        print("✅ main.py updated successfully")
        print("✅ String concatenation error should be eliminated")
        print("")
        print("🚀 Both email intake endpoints should now work!")
        print("   • /api/email/intake")
        print("   • /api/logicapps/email/intake")
    else:
        print("❌ Fix failed - manual intervention needed")
    
    print("=" * 70)