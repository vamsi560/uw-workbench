#!/usr/bin/env python3
"""
Create a minimal PDF to test Logic Apps attachment handling
"""

import base64
from reportlab.pdfgen import canvas
import io

def create_minimal_test_pdf():
    """Create the smallest possible PDF with some text"""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(200, 200))  # Very small page
    c.setFont("Helvetica", 10)
    c.drawString(20, 180, "TEST PDF")
    c.drawString(20, 160, "Company: MedTech Solutions")
    c.drawString(20, 140, "Policy: Cyber Insurance")
    c.drawString(20, 120, "Amount: $1,000,000")
    c.save()
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

# Create minimal PDF
print("🏗️  Creating minimal test PDF for Logic Apps...")
minimal_pdf = create_minimal_test_pdf()
minimal_base64 = base64.b64encode(minimal_pdf).decode('utf-8')

print(f"✅ Minimal PDF created:")
print(f"   Size: {len(minimal_pdf)} bytes")
print(f"   Base64 length: {len(minimal_base64)} characters")

# Save the PDF
with open('minimal_test.pdf', 'wb') as f:
    f.write(minimal_pdf)

print(f"📄 Saved as: minimal_test.pdf")

# Test parsing
try:
    from file_parsers import parse_attachments
    
    test_attachment = [{
        "filename": "minimal_test.pdf",
        "contentBase64": minimal_base64
    }]
    
    result = parse_attachments(test_attachment, "uploads")
    if result:
        print(f"✅ Parsing successful: {result}")
    else:
        print(f"❌ Parsing failed")
        
except Exception as e:
    print(f"❌ Error: {e}")

# Create Logic Apps test payload
from datetime import datetime
import json

minimal_payload = {
    "subject": "TEST: Minimal PDF - MedTech Solutions",
    "from": "test@medtechsolutions.com",
    "body": "This is a test with minimal PDF attachment.",
    "receivedDateTime": datetime.utcnow().isoformat().replace(":", "%3A") + "Z",
    "attachments": [
        {
            "name": "minimal_test.pdf",
            "contentType": "application/pdf",
            "contentBytes": minimal_base64
        }
    ]
}

with open('minimal_logic_apps_test.json', 'w') as f:
    json.dump(minimal_payload, f, indent=2)

print(f"\n🧪 Minimal test payload saved as: minimal_logic_apps_test.json")
print(f"   Try sending this small PDF via email to test Logic Apps")
print(f"   If this works, the issue is with larger PDF handling")
print(f"   If this fails, there's a broader Logic Apps attachment issue")

# Compare with the working comprehensive PDF
print(f"\n📊 Size comparison:")
print(f"   Minimal PDF:       {len(minimal_pdf):,} bytes")
print(f"   Comprehensive PDF: 5,996 bytes") 
print(f"   Logic Apps limit appears to be around 2KB based on truncation")