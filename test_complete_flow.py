#!/usr/bin/env python3
"""
Test the complete Logic Apps endpoint with the actual payload
"""

import requests
import json
import sys

# Your actual Logic Apps payload
payload = {
    "from": "Vamsi.Sapireddy@valuemomentum.com",
    "subject": "Submission – Orion Data Technologies Inc.",
    "body": """<html><head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"><style type="text/css" style="display:none">
<!--
p
	{margin-top:0;
	margin-bottom:0}
-->
</style></head><body dir="ltr"><div class="elementToProof" style="font-family:Aptos,Aptos_EmbeddedFont,Aptos_MSFontService,Calibri,Helvetica,sans-serif; font-size:11pt; color:rgb(0,0,0)">New Submission</div><div class="elementToProof" style="font-family:Aptos,Aptos_EmbeddedFont,Aptos_MSFontService,Calibri,Helvetica,sans-serif; font-size:11pt; color:rgb(0,0,0)"><br></div></body></html>""",
    "receivedDateTime": "2025-10-08T17:22:55+00:00",
    "attachments": [
        {
            "@odata.type": "#microsoft.graph.fileAttachment",
            "id": "AAMkADFlMTAxZjNhLTI4OWUtNDJiZC1iNDcyLWU0MTIwOWMzMTFhOQBGAAAAAABC3NI54pfDQpLU352Xoqg2BwAD00Z11N_DQazsGJul-GYsAAR8X-vUAAAD00Z11N_DQazsGJul-GYsAASDGRiwAAABEgAQAFRN0gGFSTFGv7SoEyTQRsk=",
            "lastModifiedDateTime": "2025-10-08T17:22:54+00:00",
            "name": "Sample Data - Cyber Insurance Submission Form.pdf",
            "contentType": "application/pdf",
            "size": 88037,
            "isInline": False,
            "contentId": None,
            "contentBytes": "JVBERi0xLjcNCiW1tbW1DQoxIDAgb2JqDQo8PC9UeXBlL0NhdGFsb2cvUGFnZXMgMiAwIFIvTGFuZyhlbikgL1N0cnVjdFRyZWVSb290IDMyIDAgUi9NYXJrSW5mbzw8L01hcmtlZCB0cnVlPj4vTWV0YWRhdGEgNzE2IDAgUi9WaWV3ZXJQcmVmZXJlbmNlcyA3MTcgMCBSPj4NCmVuZG9iag0KMiAwIG9iag0KPDwvVHlwZS9QokTnNtUp7e1Y7y+dWhTZs6bIBWjYFCeSUGoeXLRPLtq82ps5+F/5eNjNhU1kWMOW9Y89TaXplIDcxOS9Sb290IDEgMCBSL0luZm8gMzEgMCBSL0lEWzxGRTk4NzM3NEIzMjM1MjQxOTIyRUVCNTk5OTdFODk4Mz48RkU5ODczNzRCMzIzNTI0MTkyMkVFQjU5OTk3RTg5ODM+XSA+Pg0Kc3RhcnR4cmVmDQo3Mjk3OA0KJUVFT0YNCnhyZWYNCjAgMA0KdHJhaWxlcg0KPDwvU2l6ZSA3MTkvUm9vdCAxIDAgUi9JbmZvIDMxIDAgUi9JRFs8RkU5ODczNzRCMzIzNTI0MTkyMkVFQjU5OTk3RTg5ODM+PEZFOTg3Mzc0QjMyMzUyNDE5MjJFRUI1OTk5N0U4OTgzPl0gL1ByZXYgNzI5NzgvWFJlZlN0bSA3MTM3Nz4+DQpzdGFydHhyZWYNCjg3NTE3DQolJUVPRg=="
        }
    ]
}

def test_endpoint():
    """Test the Logic Apps endpoint"""
    try:
        url = "http://localhost:8000/api/logicapps/email/intake"
        headers = {"Content-Type": "application/json"}
        
        print("Sending request to Logic Apps endpoint...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print("SUCCESS! Response:")
            print(json.dumps(response_data, indent=2))
            
            # Get the submission reference to check in database
            submission_ref = response_data.get("submission_ref")
            if submission_ref:
                print(f"\nSubmission created with ref: {submission_ref}")
                return True
        else:
            print("ERROR Response:")
            print(f"Status: {response.status_code}")
            print(f"Text: {response.text}")
            try:
                error_data = response.json()
                print("JSON Error:")
                print(json.dumps(error_data, indent=2))
            except:
                pass
            return False
                
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to server on localhost:8000")
        print("Make sure the FastAPI server is running: uvicorn main:app --reload")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def check_database_after_submission():
    """Check if the submission was properly stored"""
    try:
        import subprocess
        print("\nChecking database for new submission...")
        result = subprocess.run(["python", "check_database.py"], 
                              capture_output=True, text=True, timeout=10)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
    except Exception as e:
        print(f"Could not check database: {e}")

if __name__ == "__main__":
    success = test_endpoint()
    if success:
        check_database_after_submission()
    else:
        print("\nEndpoint test failed. Check server status.")
        sys.exit(1)