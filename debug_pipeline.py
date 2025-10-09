#!/usr/bin/env python3
"""
Test the exact attachment processing with your PDF content
"""

import sys
import os

# Test with the actual import sequence from main.py
print("Testing import sequence from main.py...")

try:
    from file_parsers import parse_attachments
    print("✅ Successfully imported full file parser")
    parser_module = "file_parsers"
except ImportError as e:
    print(f"❌ Full parser import failed: {e}")
    from file_parsers_minimal import parse_attachments
    print("✅ Using minimal file parser")
    parser_module = "file_parsers_minimal"

print(f"Parser module: {parser_module}")
print(f"Parser function: {parse_attachments}")

# Your actual attachment data
your_attachment = [
    {
        "filename": "Sample Data - Cyber Insurance Submission Form.pdf",
        "contentBase64": "JVBERi0xLjcNCiW1tbW1DQoxIDAgb2JqDQo8PC9UeXBlL0NhdGFsb2cvUGFnZXMgMiAwIFIvTGFuZyhlbikgL1N0cnVjdFRyZWVSb290IDMyIDAgUi9NYXJrSW5mbzw8L01hcmtlZCB0cnVlPj4vTWV0YWRhdGEgNzE2IDAgUi9WaWV3ZXJQcmVmZXJlbmNlcyA3MTcgMCBSPj4NCmVuZG9iag0KMiAwIG9iag0KPDwvVHlwZS9QokTnNtUp7e1Y7y+dWhTZs6bIBWjYFCeSUGoeXLRPLtq82ps5+F/5eNjNhU1kWMOW9Y89TaXplIDcxOS9Sb290IDEgMCBSL0luZm8gMzEgMCBSL0lEWzxGRTk4NzM3NEIzMjM1MjQxOTIyRUVCNTk5OTdFODk4Mz48RkU5ODczNzRCMzIzNTI0MTkyMkVFQjU5OTk3RTg5ODM+XSA+Pg0Kc3RhcnR4cmVmDQo3Mjk3OA0KJTVFT0YNCnhyZWYNCjAgMA0KdHJhaWxlcg0KPDwvU2l6ZSA3MTkvUm9vdCAxIDAgUi9JbmZvIDMxIDAgUi9JRFs8RkU5ODczNzRCMzIzNTI0MTkyMkVFQjU5OTk3RTg5ODM+PEZFOTg3Mzc0QjMyMzUyNDE5MjJFRUI1OTk5N0U4OTgzPl0gL1ByZXYgNzI5NzgvWFJlZlN0bSA3MTM3Nz4+DQpzdGFydHhyZWYNCjg3NTE3DQolJUVPRg=="
    }
]

print(f"\n📄 Testing your PDF attachment...")
print(f"   Filename: {your_attachment[0]['filename']}")
print(f"   Content length: {len(your_attachment[0]['contentBase64'])} chars")

# Create uploads directory
upload_dir = "uploads"
os.makedirs(upload_dir, exist_ok=True)
print(f"   Upload directory: {upload_dir}")

try:
    result = parse_attachments(your_attachment, upload_dir)
    print(f"\n📋 Attachment processing result:")
    print(f"   Result type: {type(result)}")
    print(f"   Result length: {len(result) if result else 0} chars")
    
    if "minimal mode" in str(result):
        print("❌ ERROR: Using minimal parser! Attachments not processed")
        print(f"   Full result: {result}")
    elif result and len(result.strip()) > 50:
        print("✅ SUCCESS: Full parser working, content extracted")
        print(f"   First 200 chars: {result[:200]}...")
    elif result and len(result.strip()) > 0:
        print("⚠️  WARNING: Short result, might be an error message")
        print(f"   Full result: {result}")
    else:
        print("❌ ERROR: No content extracted")
        print(f"   Result: '{result}'")
        
except Exception as e:
    print(f"❌ ERROR during processing: {e}")
    import traceback
    traceback.print_exc()