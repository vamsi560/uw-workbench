#!/usr/bin/env python3
"""
Analyze the PDF base64 content to understand the issue
"""

import base64

# Your PDF content from Logic Apps
pdf_base64 = "JVBERi0xLjcNCiW1tbW1DQoxIDAgb2JqDQo8PC9UeXBlL0NhdGFsb2cvUGFnZXMgMiAwIFIvTGFuZyhlbikgL1N0cnVjdFRyZWVSb290IDMyIDAgUi9NYXJrSW5mbzw8L01hcmtlZCB0cnVlPj4vTWV0YWRhdGEgNzE2IDAgUi9WaWV3ZXJQcmVmZXJlbmNlcyA3MTcgMCBSPj4NCmVuZG9iag0KMiAwIG9iag0KPDwvVHlwZS9QokTnNtUp7e1Y7y+dWhTZs6bIBWjYFCeSUGoeXLRPLtq82ps5+F/5eNjNhU1kWMOW9Y89TaXplIDcxOS9Sb290IDEgMCBSL0luZm8gMzEgMCBSL0lEWzxGRTk4NjM3NEIzMjM1MjQxOTIyRUVCNTk5OTdFODk4Mz48RkU5ODczNzRCMzIzNTI0MTkyMkVFQjU5OTk3RTg5ODM+XSA+Pg0Kc3RhcnR4cmVmDQo3Mjk3OA0KJTVFT0YNCnhyZWYNCjAgMA0KdHJhaWxlcg0KPDwvU2l6ZSA3MTkvUm9vdCAxIDAgUi9JbmZvIDMxIDAgUi9JRFs8RkU5ODczNzRCMzIzNTI0MTkyMkVFQjU5OTk3RTg5ODM+PEZFOTg3Mzc0QjMyMzUyNDE5MjJFRUI1OTk5N0U4OTgzPl0gL1ByZXYgNzI5NzgvWFJlZlN0bSA3MTM3Nz4+DQpzdGFydHhyZWYNCjg3NTE3DQolJUVPRg=="

print("PDF Base64 Analysis:")
print(f"Base64 length: {len(pdf_base64)} characters")

try:
    # Decode base64
    pdf_bytes = base64.b64decode(pdf_base64)
    print(f"Decoded bytes length: {len(pdf_bytes)} bytes")
    
    # Check if it starts with PDF header
    pdf_header = pdf_bytes[:8]
    print(f"PDF header: {pdf_header}")
    
    # Check if it ends with EOF marker
    pdf_tail = pdf_bytes[-20:]
    print(f"PDF tail (last 20 bytes): {pdf_tail}")
    
    # Look for %%EOF marker
    pdf_content = pdf_bytes.decode('latin-1', errors='ignore')
    if '%%EOF' in pdf_content:
        print("✅ PDF has %%EOF marker")
        eof_pos = pdf_content.rfind('%%EOF')
        print(f"   %%EOF position: {eof_pos}")
        print(f"   Content after %%EOF: '{pdf_content[eof_pos+len('%%EOF'):]}'")
    else:
        print("❌ PDF missing %%EOF marker")
    
    # Check PDF structure
    if pdf_content.startswith('%PDF-'):
        version = pdf_content.split('\n')[0]
        print(f"✅ Valid PDF header: {version}")
    else:
        print("❌ Invalid PDF header")
    
    # Save to file for manual inspection
    with open('debug_pdf_from_logic_apps.pdf', 'wb') as f:
        f.write(pdf_bytes)
    print("📄 Saved PDF to: debug_pdf_from_logic_apps.pdf")
    
    # Try to identify truncation point
    lines = pdf_content.split('\n')
    print(f"\nPDF Structure Analysis:")
    print(f"   Total lines: {len(lines)}")
    print(f"   First line: {lines[0]}")
    print(f"   Last few lines:")
    for i, line in enumerate(lines[-5:]):
        print(f"      {len(lines)-5+i}: '{line}'")
        
except Exception as e:
    print(f"❌ Error analyzing PDF: {e}")
    import traceback
    traceback.print_exc()