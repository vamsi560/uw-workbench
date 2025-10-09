#!/usr/bin/env python3
"""
Test with a complete, valid PDF
"""

import base64

# Create a minimal valid PDF for testing
minimal_pdf_content = """%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test PDF Content - Orion Data Technologies Inc.) Tj
ET
endstream
endobj

xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000206 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
299
%%EOF"""

# Convert to base64
pdf_bytes = minimal_pdf_content.encode('utf-8')
pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

print("Created a minimal valid PDF for testing")
print(f"PDF size: {len(pdf_bytes)} bytes")
print(f"Base64 size: {len(pdf_base64)} chars")
print(f"Base64 content: {pdf_base64}")

# Test the attachment parsing
from file_parsers import parse_attachments
import os

test_attachment = [
    {
        "filename": "Test-Complete-PDF.pdf",
        "contentBase64": pdf_base64
    }
]

os.makedirs("uploads", exist_ok=True)
result = parse_attachments(test_attachment, "uploads")

print(f"\nParsing result:")
print(f"Length: {len(result) if result else 0}")
print(f"Content: {result}")

if "minimal mode" in result:
    print("❌ Still using minimal mode")
else:
    print("✅ Full parser working with complete PDF")