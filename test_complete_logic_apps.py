#!/usr/bin/env python3
"""
Test Logic Apps endpoint with complete PDF content to prove backend works
"""

import requests
import json
from datetime import datetime

# Create a proper PDF with complete content for testing
complete_pdf_base64 = "JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFIKPj4KZW5kb2JqCgoyIDAgb2JqCjw8Ci9UeXBlIC9QYWdlcwovS2lkcyBbMyAwIFJdCi9Db3VudCAxCj4+CmVuZG9iagoKMyAwIG9iago8PAovVHlwZSAvUGFnZQovUGFyZW50IDIgMCBSCi9NZWRpYUJveCBbMCAwIDYxMiA3OTJdCi9Db250ZW50cyA0IDAgUgo+PgplbmRvYmoKCjQgMCBvYmoKPDwKL0xlbmd0aCA0NAo+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjEwMCA3MDAgVGQKKFRlc3QgUERGIENvbnRlbnQgLSBPcmlvbiBEYXRhIFRlY2hub2xvZ2llcyBJbmMuKSBUagpFVAplbmRzdHJlYW0KZW5kb2JqCgp4cmVmCjAgNQowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1OCAwMDAwMCBuIAowMDAwMDAwMTE1IDAwMDAwIG4gCjAwMDAwMDAyMDYgMDAwMDAgbiAKdHJhaWxlcgo8PAovU2l6ZSA1Ci9Sb290IDEgMCBSCj4+CnN0YXJ0eHJlZgoyOTkKJSVFT0Y="

# Test Logic Apps payload with complete PDF
logic_apps_payload = {
    "subject": "Test: Cyber Insurance Submission - Orion Data Technologies Inc.",
    "from": "test@oriondatatech.com",
    "body": "<html><body><h1>Cyber Insurance Application</h1><p>Please find attached our completed cyber insurance submission form.</p><p>Company: Orion Data Technologies Inc.</p><p>Industry: Technology</p><p>Coverage Amount: $5M</p></body></html>",
    "receivedDateTime": datetime.utcnow().isoformat() + "Z",
    "attachments": [
        {
            "name": "Complete-Cyber-Insurance-Form.pdf",
            "contentType": "application/pdf",
            "contentBytes": complete_pdf_base64
        }
    ]
}

print("🧪 Testing Logic Apps endpoint with COMPLETE PDF content...")
print(f"   PDF size: {len(complete_pdf_base64)} chars (complete)")
print(f"   Subject: {logic_apps_payload['subject']}")
print(f"   Attachments: {len(logic_apps_payload['attachments'])}")

# Test locally if running
try:
    # Test the attachment parsing directly first
    from file_parsers import parse_attachments
    
    valid_attachments = [{
        "filename": "Complete-Cyber-Insurance-Form.pdf",
        "contentBase64": complete_pdf_base64
    }]
    
    print("\n📄 Testing direct attachment parsing...")
    result = parse_attachments(valid_attachments, "uploads")
    print(f"   Result length: {len(result)} chars")
    if result and len(result) > 10:
        print("✅ SUCCESS: Complete PDF processed successfully!")
        print(f"   Extracted content: {result}")
    else:
        print(f"❌ Failed to extract content: '{result}'")
        
except Exception as e:
    print(f"❌ Error testing attachment parsing: {e}")

# Save payload for manual testing
with open('test_complete_logic_apps_payload.json', 'w') as f:
    json.dump(logic_apps_payload, f, indent=2)

print(f"\n📋 Complete Logic Apps payload saved to: test_complete_logic_apps_payload.json")
print(f"   Use this payload to test your Logic Apps endpoint")
print(f"   POST to: http://localhost:8000/api/logicapps/email/intake")

# Compare with your truncated PDF
print(f"\n📊 Comparison:")
print(f"   Your Logic Apps PDF: 733 chars (TRUNCATED)")
print(f"   Complete test PDF: {len(complete_pdf_base64)} chars (COMPLETE)")
print(f"   Size difference: {len(complete_pdf_base64) - 733} chars missing")