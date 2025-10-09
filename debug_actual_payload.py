#!/usr/bin/env python3
"""
Test the actual Logic Apps payload that's causing null attachment_content
"""

import json
import base64

# Your actual Logic Apps payload
actual_payload = {
  "from": "Vamsi.Sapireddy@valuemomentum.com",
  "subject": "MedTech Solutions Inc.",
  "body": "<html><head>\r\n<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\"><style type=\"text/css\" style=\"display:none\">\r\n<!--\r\np\r\n\t{margin-top:0;\r\n\tmargin-bottom:0}\r\n-->\r\n</style></head><body dir=\"ltr\"><div class=\"elementToProof\" style=\"font-family:Aptos,Aptos_EmbeddedFont,Aptos_MSFontService,Calibri,Helvetica,sans-serif; font-size:11pt; color:rgb(0,0,0)\">Cyber based new submission</div></body></html>",
  "receivedDateTime": "2025-10-09T04:40:15+00:00",
  "attachments": [
    {
      "@odata.type": "#microsoft.graph.fileAttachment",
      "id": "AAMkADFlMTAxZjNhLTI4OWUtNDJiZC1iNDcyLWU0MTIwOWMzMTFhOQBGAAAAAABC3NI54pfDQpLU352Xoqg2BwAD00Z11N_DQazsGJul-GYsAAR8X-vUAAAD00Z11N_DQazsGJul-GYsAASDGRizAAABEgAQAF6nYLvQ8uJHrd735A_KPyc=",
      "lastModifiedDateTime": "2025-10-09T04:40:15+00:00",
      "name": "comprehensive_cyber_insurance_submission.pdf",
      "contentType": "application/pdf",
      "size": 6316,
      "isInline": False,
      "contentId": None,
      "contentBytes": "JVBERi0xLjMKJZOMi54gUmVwb3J0TGFiIEdlbmVyYXRlZCBQREYgZG9jdW1lbnQgaHR0cDovL3d3dy5yZXBvcnRsYWIuY29tCjEgMCBvYmoKPDwKL0YxIDIgMCBSIC9GMiAzIDAgUgo+PgplbmRvYmoKMiAwIG9iago8PAovQmFzZUZvbnQgL0hlbHZldGljYSAvRW5jb2RpbmcgL1dpbkFuc2lFbmNvZGluZyAvTmFtZSAvRjEgL1N1YnR5cGUgL1R5cGUxIC9UeXBlIC9Gb250Cj4+CmVuZG9iagozIDAgb2JqCjw8Ci9CYXNlRm9udCAvSGVsdmV0aWNhLUJvbGQgL0VuY29kaW5nIC9XaW5BbnNpRW5jb2RpbmcgL05hbWUgL0YyIC9TdWJ0eXBlIC9UeXBlMSAvVHlwZSAvRm9udAo+PgplbmRvYmoKNCAwIG9iago8PAovQ29udGVudHMgMTAgMCBSIC9NZWRpYUJveCBbIDAgMCA2MTIgNzkyIF0gL1BhcmVudCA5IDAgUiAvUmVzb3VyY2VzIDw8Ci9Gb250IDEgMCBSIC9Qcm9jU2V0IFsgL1BERiAvVGV4dCAvSW1hZ2VCIC9JbWFnZUMgL0ltYWdlSSBdCj4+IC9Sb3RhdGUgMCAvVHJhbnMgPDwKCj4+IAogIC9UeXBlIC9QYWdlCj4+CmVuZG9iago1IDAgb2JqCjw8Ci9Db250ZW50cyAxMSAwIFIgL01lZGlhQm94IFsgMCAwIDYxMiA3OTIgXSAvUGFyZW50IDkgMCBSIC9SZXNvdXJjZXMgPDwKL0ZvbnQgMSAwIFIgL1Byb2NTZXQgWyAvUERGIC9UZXh0IC9JbWFnZUIgL0ltYWdlQyAvSW1hZ2VJIF0KPj4gL1JvdGF0ZSAwIC9UcmFucyA8PAoKPj4gCiAgL1R5cGUgL1BhZ2UKPj4KZW5kb2JqCjYgMCBvYmoKPDwKL0NvbnRlbnRzIDEyIDAgUiAvTWVkaWFCb3ggWyAwIDAgNjEyIDc5MiBdIC9QYXJlbnQgOSAwIFIgL1Jlc291cmNlcyA8PAovRm9udCAxIDAgUiAvUHJvY1NldCBbIC9QREYgL1RleHQgL0ltYWdlQiAvSW1hZ2VJIF0KPj4gL1JvdGF0ZSAwIC9UcmFucyA8PAoKPj4gCiAgL1R5cGUgL1BhZ2UKPj4KZW5kb2JqCjcgMCBvYmoKPDwKL1BhZ2VNb2RlIC9Vc2VOb25lIC9QYWdlcyA5IDAgUiAvVHlwZSAvQ2F0YWxvZwo+PgplbmRvYmoKOCAwIG9iago8PAovQXV0aG9yIChhbm9ueW1vdXMpIC9DcmVhdGlvbkRhdGUgKEQ6MjAyNTEwMDkwNDM2NTcrMDAnMDAnKSAvQ3JlYXRvciAoUmVwb3J0TGFiIFBERiBMaWJyYXJ5IC0gd3d3LnJlcG9ydGxhYi5jb20pIC9LZXl3b3JkcyAoKSAvTW9kRGF0ZSAoRDoyMDI1MTAwOTA0MzY1NyswMCcwMCcpIC9Qcm9kdWNlciAoUmVwb3J0TGFiIFBERiBMaWJyYXJ5IC0gd3d3LnJlcG9ydGxhYi5jb20pIAogIC9TdWJqZWN0ICh1bnNwZWNpZmllZCkgL1RpdGxlICh1bnRpdGxlZCkgL1RyYXBwZWQgL0ZhbHNlCj4+CmVuZG9iago5IDAgb2JqCjw8Ci9Db3VudCAzIC9LaWRzIFsgNCAwIFIgNSAwIFIgNiAwIFIgXSAvVHlwZSAvUGFnZXMKPj4KZW5kb2JqCjEwIDAgb2JqCjw8Ci9GaWx0ZXIgWyAvQVNDSUk4NURlY29kZSAvRmxhdGVEZWNvZGUgXSAvTGVuZ3RoIDEzMTcKPj4Kc3RyZWFtCkdhdFUyYkFRJl0nXSZMNm1cNVZfJkBtLGBbQW4kbkwiYztWT3RxT21oKFRIXlpeIig2UDEiP2JdZWFzLU0yXWVbQHBtNjJQYWxlKm4pSVlWQCxmNEFeWEU2bFFHQThbJFMzNlorRV9hRkwjYF9xcUEjTy4jJkRsKlQrKClMcFFoUUM5R2s+OF40OkchaeTQzNDQ2NTM1IGYgCjAwMDAwMDAwNzMgMDAwMDAgbiAKMDAwMDAwMDExNCAwMDAwMCBuIAowMDAwMDAwMjIxIDAwMDAwIG4gCjAwMDAwMDAzMzMgMDAwMDAgbiAKMDAwMDAwMDUyNyAwMDAwMCBuIAowMDAwMDAwNzIxIDAwMDAwIG4gCjAwMDAwMDA5MTUgMDAwMDAgbiAKMDAwMDAwMDk4MyAwMDAwMCBuIAowMDAwMDAxMjc5IDAwMDAwIG4gCjAwMDAwMDEzNTAgMDAwMDAgbiAKMDAwMDAwMjc1OSAwMDAwMCBuIAowMDAwMDA0MDM1IDAwMDAwIG4gCnRyYWlsZXIKPDwKL0lEIApbPDJhYzU3NjE2OWE1NzM3ZDRlNzAxZTExNTk4NWYyNmU5PjwyYWM1NzYxNjlhNTczN2Q0ZTcwMWUxMTU5ODVmMjZlOT5dCiUgUmVwb3J0TGFiIGdlbmVyYXRlZCBQREYgZG9jdW1lbnQgLS0gZGlnZXN0IChodHRwOi8vd3d3LnJlcG9ydGxhYi5jb20pCgovSW5mbyA4IDAgUgovUm9vdCA3IDAgUgovU2l6ZSAxMwo+PgpzdGFydHhyZWYKNTUwOQolJUVPRgo="
    },
    {
      "name": "comprehensive_cyber_insurance_submission.pdf",
      "contentType": "application/pdf",
      "contentBytes": "JVBERi0xLjMKJZOMi54gUmVwb3J0TGFiIEdlbmVyYXRlZCBQREYgZG9jdW1lbnQgaHR0cDovL3d3dy5yZXBvcnRsYWIuY29tCjEgMCBvYmoKPDwKL0YxIDIgMCBSIC9GMiAzIDAgUgo+PgplbmRvYmoKMiAwIG9iago8PAovQmFzZUZvbnQgL0hlbHZldGljYSAvRW5jb2RpbmcgL1dpbkFuc2lFbmNvZGluZyAvTmFtZSAvRjEgL1N1YnR5cGUgL1R5cGUxIC9UeXBlIC9Gb250Cj4+CmVuZG9iagozIDAgb2JqCjw8Ci9CYXNlRm9udCAvSGVsdmV0aWNhLUJvbGQgL0VuY29kaW5nIC9XaW5BbnNpRW5jb2RpbmcgL05hbWUgL0YyIC9TdWJ0eXBlIC9UeXBlMSAvVHlwZSAvRm9udAo+PgplbmRvYmoKNCAwIG9iago8PAovQ29udGVudHMgMTAgMCBSIC9NZWRpYUJveCBbIDAgMCA2MTIgNzkyIF0gL1BhcmVudCA5IDAgUiAvUmVzb3VyY2VzIDw8Ci9Gb250IDEgMCBSIC9Qcm9jU2V0IFsgL1BERiAvVGV4dCAvSW1hZ2VCIC9JbWFnZUMgL0ltYWdlSSBdCj4+IC9Sb3RhdGUgMCAvVHJhbnMgPDwKCj4+IAogIC9UeXBlIC9QYWdlCj4+CmVuZG9iago1IDAgb2JqCjw8Ci9Db250ZW50cyAxMSAwIFIgL01lZGlhQm94IFsgMCAwIDYxMiA3OTIgXSAvUGFyZW50IDkgMCBSIC9SZXNvdXJjZXMgPDwKL0ZvbnQgMSAwIFIgL1Byb2NTZXQgWyAvUERGIC9UZXh0IC9JbWFnZUIgL0ltYWdlQyAvSW1hZ2VJIF0KPj4gL1JvdGF0ZSAwIC9UcmFucyA8PAoKPj4gCiAgL1R5cGUgL1BhZ2UKPj4KZW5kb2JqCjYgMCBvYmoKPDwKL0NvbnRlbnRzIDEyIDAgUiAvTWVkaWFCb3ggWyAwIDAgNjEyIDc5MiBdIC9QYXJlbnQgOSAwIFIgL1Jlc291cmNlcyA8PAovRm9udCAxIDAgUiAvUHJvY1NldCBbIC9QREYgL1RleHQgL0ltYWdlQiAvSW1hZ2VJIF0KPj4gL1JvdGF0ZSAwIC9UcmFucyA8PAoKPj4gCiAgL1R5cGUgL1BhZ2UKPj4KZW5kb2JqCjcgMCBvYmoKPDwKL1BhZ2VNb2RlIC9Vc2VOb25lIC9QYWdlcyA5IDAgUiAvVHlwZSAvQ2F0YWxvZwo+PgplbmRvYmoKOCAwIG9iago8PAovQXV0aG9yIChhbm9ueW1vdXMpIC9DcmVhdGlvbkRhdGUgKEQ6MjAyNTEwMDkwNDM2NTcrMDAnMDAnKSAvQ3JlYXRvciAoUmVwb3J0TGFiIFBERiBMaWJyYXJ5IC0gd3d3LnJlcG9ydGxhYi5jb20pIC9LZXl3b3JkcyAoKSAvTW9kRGF0ZSAoRDoyMDI1MTAwOTA0MzY1NyswMCcwMCcpIC9Qcm9kdWNlciAoUmVwb3J0TGFiIFBERiBMaWJyYXJ5IC0gd3d3LnJlcG9ydGxhYi5jb20pIAogIC9TdWJqZWN0ICh1bnNwZWNpZmllZCkgL1RpdGxlICh1bnRpdGxlZCkgL1RyYXBwZWQgL0ZhbHNlCj4+CmVuZG9iago5IDAgb2JqCjw8Ci9Db3VudCAzIC9LaWRzIFsgNCAwIFIgNSAwIFIgNiAwIFIgXSAvVHlwZSAvUGFnZXMKPj4KZW5kb2JqCjEwIDAgb2JqCjw8Ci9GaWx0ZXIgWyAvQVNDSUk4NURlY29kZSAvRmxhdGVEZWNvZGUgXSAvTGVuZ3RoIDEzMTcKPj4Kc3RyZWFtCkdhdFUyYkFRJl0nXSZMNm1cNVZfJkBtLGBbQW4kbkwiYztWT3RxT21oKFRIXlpeIig2UDEiP2JdZWFzLU0yXWVbQHBtNjJQYWxlKm4pSVlWQCxmNEFeWEU2bFFHQThbJFMzNlorRV9hRkwjYF9xcUEjTy4jJkRsKlQrKClMcFFoUUM5R2s+OF40OkchaWnAyOTM1IGYgCjAwMDAwMDAwNzMgMDAwMDAgbiAKMDAwMDAwMDExNCAwMDAwMCBuIAowMDAwMDAwMjIxIDAwMDAwIG4gCjAwMDAwMDAzMzMgMDAwMDAgbiAKMDAwMDAwMDUyNyAwMDAwMCBuIAowMDAwMDAwNzIxIDAwMDAwIG4gCjAwMDAwMDA5MTUgMDAwMDAgbiAKMDAwMDAwMDk4MyAwMDAwMCBuIAowMDAwMDAxMjc5IDAwMDAwIG4gCjAwMDAwMDEzNTAgMDAwMDAgbiAKMDAwMDAwMjc1OSAwMDAwMCBuIAowMDAwMDA0MDM1IDAwMDAwIG4gCnRyYWlsZXIKPDwKL0lEIApbPDJhYzU3NjE2OWE1NzM3ZDRlNzAxZTExNTk4NWYyNmU5PjwyYWM1NzYxNjlhNTczN2Q0ZTcwMWUxMTU5ODVmMjZlOT5dCiUgUmVwb3J0TGFiIGdlbmVyYXRlZCBQREYgZG9jdW1lbnQgLS0gZGlnZXN0IChodHRwOi8vd3d3LnJlcG9ydGxhYi5jb20pCgovSW5mbyA4IDAgUgovUm9vdCA3IDAgUgovU2l6ZSAxMwo+PgpzdGFydHhyZWYKNTUwOQolJUVPRgo="
    }
  ]
}

print("🔍 Testing actual Logic Apps payload that's causing null attachment_content...")

# Test both attachments - they should be identical
for i, attachment in enumerate(actual_payload["attachments"]):
    print(f"\n📎 Testing attachment {i+1}:")
    
    # Get the attachment data
    att_name = attachment.get("name", "unknown")
    att_content = attachment.get("contentBytes", "")
    
    print(f"   Name: {att_name}")
    print(f"   Content length: {len(att_content)} chars")
    
    # Test base64 decoding
    try:
        pdf_bytes = base64.b64decode(att_content)
        print(f"   Decoded size: {len(pdf_bytes)} bytes")
        
        # Check PDF structure
        if pdf_bytes.startswith(b'%PDF'):
            print(f"   ✅ Valid PDF header")
            if pdf_bytes.endswith(b'%%EOF\n') or b'%%EOF' in pdf_bytes[-50:]:
                print(f"   ✅ Complete PDF (has %%EOF)")
            else:
                print(f"   ❌ PDF might be truncated (no %%EOF found)")
        else:
            print(f"   ❌ Invalid PDF header")
            
    except Exception as e:
        print(f"   ❌ Base64 decode error: {e}")
        continue
    
    # Test attachment parsing
    try:
        from file_parsers import parse_attachments
        
        valid_attachment = [{
            "filename": att_name,
            "contentBase64": att_content
        }]
        
        print(f"   🧪 Testing attachment parsing...")
        result = parse_attachments(valid_attachment, "uploads")
        
        if result and len(result.strip()) > 50:
            print(f"   ✅ SUCCESS: {len(result)} characters extracted")
            print(f"   First 200 chars: {result[:200]}...")
        elif result and len(result.strip()) > 0:
            print(f"   ⚠️  Short result: '{result}'")
        else:
            print(f"   ❌ No content extracted: '{result}'")
            
    except Exception as e:
        print(f"   ❌ Parser error: {e}")

# Test the Logic Apps format conversion
print(f"\n🔄 Testing Logic Apps format conversion...")

# Simulate what main.py does
valid_attachments = []
for att in actual_payload["attachments"]:
    # This is how main.py processes Logic Apps attachments
    att_name = str(att.get("name")) if att.get("name") else None
    att_content = str(att.get("contentBytes")) if att.get("contentBytes") else None
    
    if att_name and att_content:
        valid_attachments.append({
            "filename": att_name, 
            "contentBase64": att_content
        })

print(f"   Valid attachments found: {len(valid_attachments)}")

if valid_attachments:
    try:
        attachment_text = parse_attachments(valid_attachments, "uploads")
        print(f"   Final result length: {len(attachment_text) if attachment_text else 0}")
        if attachment_text:
            print(f"   Final result type: {type(attachment_text)}")
            if "minimal mode" in str(attachment_text):
                print(f"   ❌ ERROR: Still using minimal parser!")
            else:
                print(f"   ✅ SUCCESS: Full parser working")
        else:
            print(f"   ❌ ERROR: No attachment text returned")
    except Exception as e:
        print(f"   ❌ Processing error: {e}")
        import traceback
        traceback.print_exc()