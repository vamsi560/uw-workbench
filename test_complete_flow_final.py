#!/usr/bin/env python3
"""
Final test of Logic Apps endpoint with attachment content storage
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from main import logic_apps_email_intake
from models import LogicAppsEmailPayload, LogicAppsAttachment
from database import SessionLocal, Submission, WorkItem
from unittest.mock import Mock
import asyncio

async def test_complete_flow():
    """Test the complete Logic Apps flow with attachment content"""
    print("Testing complete Logic Apps flow with attachment content...")
    
    # Your actual payload data
    payload_data = {
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
                "name": "Sample Data - Cyber Insurance Submission Form.pdf",
                "contentType": "application/pdf",
                "contentBytes": "JVBERi0xLjcNCiW1tbW1DQoxIDAgb2JqDQo8PC9UeXBlL0NhdGFsb2cvUGFnZXMgMiAwIFIvTGFuZyhlbikgL1N0cnVjdFRyZWVSb290IDMyIDAgUi9NYXJrSW5mbzw8L01hcmtlZCB0cnVlPj4vTWV0YWRhdGEgNzE2IDAgUi9WaWV3ZXJQcmVmZXJlbmNlcyA3MTcgMCBSPj4NCmVuZG9iag0KMiAwIG9iag0KPDwvVHlwZS9QokTnNtUp7e1Y7y+dWhTZs6bIBWjYFCeSUGoeXLRPLtq82ps5+F/5eNjNhU1kWMOW9Y89TaXplIDcxOS9Sb290IDEgMCBSL0luZm8gMzEgMCBSL0lEWzxGRTk4NzM3NEIzMjM1MjQxOTIyRUVCNTk5OTdFODk4Mz48RkU5ODczNzRCMzIzNTI0MTkyMkVFQjU5OTk3RTg5ODM+XSA+Pg0Kc3RhcnR4cmVmDQo3Mjk3OA0KJTVFT0YNCnhyZWYNCjAgMA0KdHJhaWxlcg0KPDwvU2l6ZSA3MTkvUm9vdCAxIDAgUi9JbmZvIDMxIDAgUi9JRFs8RkU5ODczNzRCMzIzNTI0MTkyMkVFQjU5OTk3RTg5ODM+PEZFOTg3Mzc0QjMyMzUyNDE5MjJFRUI1OTk5N0U4OTgzPl0gL1ByZXYgNzI5NzgvWFJlZlN0bSA3MTM3Nz4+DQpzdGFydHhyZWYNCjg3NTE3DQolJUVPRg=="
            }
        ]
    }
    
    # Create the LogicAppsEmailPayload
    request = LogicAppsEmailPayload(**payload_data)
    
    # Mock database session
    db_mock = SessionLocal()
    
    try:
        # Call the Logic Apps endpoint function directly
        print("Calling logic_apps_email_intake...")
        response = await logic_apps_email_intake(request, db_mock)
        
        print(f"✅ Response received:")
        print(f"   - Submission ID: {response.submission_id}")
        print(f"   - Submission Ref: {response.submission_ref}")
        print(f"   - Status: {response.status}")
        print(f"   - Message: {response.message}")
        
        # Verify the submission was created with attachment content
        submission = db_mock.query(Submission).filter(
            Submission.submission_ref == response.submission_ref
        ).first()
        
        if submission:
            print(f"✅ Submission created successfully:")
            print(f"   - Subject: {submission.subject}")
            print(f"   - From: {submission.sender_email}")
            print(f"   - Body text length: {len(submission.body_text) if submission.body_text else 0}")
            print(f"   - Attachment content length: {len(submission.attachment_content) if submission.attachment_content else 0}")
            
            if submission.attachment_content:
                print(f"   - Attachment preview: {submission.attachment_content[:100]}...")
            else:
                print(f"   - Attachment content: None")
            
            # Check extracted fields
            if submission.extracted_fields:
                print(f"   - Company name: {submission.extracted_fields.get('company_name', 'Not found')}")
                print(f"   - Industry: {submission.extracted_fields.get('industry', 'Not found')}")
                print(f"   - Policy type: {submission.extracted_fields.get('policy_type', 'Not found')}")
            
            # Check for work items
            work_items = db_mock.query(WorkItem).filter(WorkItem.submission_id == submission.id).all()
            print(f"   - Work items created: {len(work_items)}")
            
            if work_items:
                wi = work_items[0]
                print(f"     * Status: {wi.status}")
                print(f"     * Priority: {wi.priority}")
                print(f"     * Assigned to: {wi.assigned_to}")
                print(f"     * Risk score: {wi.risk_score}")
        else:
            print("❌ Submission not found in database")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db_mock.close()

if __name__ == "__main__":
    asyncio.run(test_complete_flow())
    print("\n🎉 Complete flow test finished!")