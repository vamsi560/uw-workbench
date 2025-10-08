#!/usr/bin/env python3
"""
Test script to verify Logic Apps HTML processing
"""

import json
import base64
from bs4 import BeautifulSoup

# Test HTML content from your payload
html_content = """<html><head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"><style type="text/css" style="display:none">
<!--
p
	{margin-top:0;
	margin-bottom:0}
-->
</style></head><body dir="ltr"><div class="elementToProof" style="font-family:Aptos,Aptos_EmbeddedFont,Aptos_MSFontService,Calibri,Helvetica,sans-serif; font-size:11pt; color:rgb(0,0,0)">New Submission</div><div class="elementToProof" style="font-family:Aptos,Aptos_EmbeddedFont,Aptos_MSFontService,Calibri,Helvetica,sans-serif; font-size:11pt; color:rgb(0,0,0)"><br></div></body></html>"""

print("Original HTML content:")
print(html_content)
print("\n" + "="*50 + "\n")

# Test HTML processing
if '<html>' in html_content.lower() or '<body>' in html_content.lower():
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        text_content = soup.get_text(strip=True, separator=' ')
        print("Extracted text content:")
        print(f"'{text_content}'")
        print(f"\nText length: {len(text_content)}")
        print(f"HTML length: {len(html_content)}")
    except Exception as html_error:
        print(f"HTML processing failed: {html_error}")

print("\n" + "="*60 + "\n")

# Test base64 detection (should NOT decode HTML as base64)
import re
print("Base64 detection test:")
print(f"Length > 100: {len(html_content) > 100}")
print(f"Only base64 chars: {bool(re.match(r'^[A-Za-z0-9+/=]+$', html_content))}")
print(f"No HTML tags: {'<' not in html_content}")
print("Should decode as base64:", len(html_content) > 100 and re.match(r'^[A-Za-z0-9+/=]+$', html_content) and '<' not in html_content)

# Test actual base64 content from attachment
print("\n" + "="*60 + "\n")
print("Testing actual base64 PDF content:")
pdf_base64 = "JVBERi0xLjcNCiW1tbW1DQoxIDAgb2JqDQo8PC9UeXBlL0NhdGFsb2cvUGFnZXMgMiAwIFIvTGFuZyhlbikgL1N0cnVjdFRyZWVSb290IDMyIDAgUi9NYXJrSW5mbzw8L01hcmtlZCB0cnVlPj4vTWV0YWRhdGEgNzE2IDAgUi9WaWV3ZXJQcmVmZXJlbmNlcyA3MTcgMCBSPj4="

print(f"PDF base64 length: {len(pdf_base64)}")
print(f"Only base64 chars: {bool(re.match(r'^[A-Za-z0-9+/=]+$', pdf_base64))}")
print(f"No HTML tags: {'<' not in pdf_base64}")
print("Should decode as base64:", len(pdf_base64) > 100 and re.match(r'^[A-Za-z0-9+/=]+$', pdf_base64) and '<' not in pdf_base64)

try:
    decoded_pdf = base64.b64decode(pdf_base64)
    print(f"Successfully decoded PDF, first 50 bytes: {decoded_pdf[:50]}")
except Exception as e:
    print(f"PDF decode failed: {e}")