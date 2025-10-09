#!/usr/bin/env python3
"""
Create a complete test PDF with realistic cyber insurance submission data
"""

import base64
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import os

def create_comprehensive_cyber_insurance_pdf():
    """Create a PDF with comprehensive cyber insurance submission data"""
    
    # Create a BytesIO buffer to hold the PDF
    buffer = io.BytesIO()
    
    # Create PDF
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "CYBER INSURANCE SUBMISSION FORM")
    
    # Company Information
    y = height - 100
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "COMPANY INFORMATION")
    
    y -= 30
    c.setFont("Helvetica", 10)
    company_info = [
        "Company Name: Orion Data Technologies Inc.",
        "Named Insured: Orion Data Technologies Incorporated",
        "DBA Name: Orion Tech Solutions",
        "Entity Type: Corporation", 
        "Company EIN: 12-3456789",
        "Company DUNS: 123456789",
        "NAIC Code: 12345",
        "",
        "Mailing Address: 123 Tech Park Drive, Suite 200",
        "Mailing City: San Francisco", 
        "Mailing State: CA",
        "Mailing ZIP: 94105",
        "",
        "Business Address: 456 Innovation Blvd, Floor 5",
        "Business City: Palo Alto",
        "Business State: CA", 
        "Business ZIP: 94301",
        "",
        "Industry: Technology",
        "Industry Code: 541511",
        "Business Description: Cloud-based software solutions and data analytics",
        "Company Size: Medium",
        "Employee Count: 285",
        "Annual Revenue: $45,000,000",
        "Years in Business: 12"
    ]
    
    for line in company_info:
        c.drawString(50, y, line)
        y -= 15
        if y < 100:  # Start new page if needed
            c.showPage()
            y = height - 50
    
    # Contact Information
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "PRIMARY CONTACT")
    y -= 20
    
    c.setFont("Helvetica", 10)
    contact_info = [
        "Contact Name: Sarah Johnson",
        "Contact Title: Chief Information Security Officer",
        "Contact Email: s.johnson@oriondatatech.com",
        "Contact Phone: (555) 123-4567",
        ""
    ]
    
    for line in contact_info:
        c.drawString(50, y, line)
        y -= 15
    
    # Insurance Agency Information
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "INSURANCE AGENCY/BROKER")
    y -= 20
    
    c.setFont("Helvetica", 10)
    agency_info = [
        "Agency Name: TechRisk Insurance Partners",
        "Agency ID: TR-12345",
        "Agency Contact: Michael Chen",
        "Agency Email: m.chen@techriskpartners.com",
        "Agency Phone: (555) 987-6543",
        "Producer Name: Jennifer Martinez",
        "Producer Code: JM-789",
        ""
    ]
    
    for line in agency_info:
        c.drawString(50, y, line)
        y -= 15
    
    # Current Policy Information
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "CURRENT POLICY INFORMATION") 
    y -= 20
    
    c.setFont("Helvetica", 10)
    policy_info = [
        "Current Policy Number: CYB-2024-567890",
        "Current Carrier: CyberGuard Insurance Company",
        "Current Expiration: 2024-12-31",
        "Renewal Indicator: Yes",
        "Policy Type: Comprehensive Cyber Liability",
        ""
    ]
    
    for line in policy_info:
        c.drawString(50, y, line)
        y -= 15
    
    # Coverage Requirements
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "COVERAGE REQUIREMENTS")
    y -= 20
    
    c.setFont("Helvetica", 10)
    coverage_info = [
        "Coverage Amount: $10,000,000",
        "Aggregate Limit: $10,000,000", 
        "Per Occurrence Limit: $5,000,000",
        "Deductible: $25,000",
        "Self Insured Retention: $10,000",
        "Effective Date: 2025-01-01",
        "Expiry Date: 2026-01-01",
        "Policy Term: 1 year",
        "",
        "SUBLIMITS:",
        "Privacy Liability Limit: $5,000,000",
        "Network Security Limit: $5,000,000",
        "Data Breach Response Limit: $2,000,000",
        "Business Interruption Limit: $3,000,000",
        "Cyber Extortion Limit: $1,000,000",
        "Regulatory Fines Limit: $2,000,000",
        "Forensic Costs Limit: $500,000",
        "Notification Costs Limit: $1,000,000",
        "Credit Monitoring Limit: $500,000",
        "Crisis Management Limit: $250,000",
        ""
    ]
    
    for line in coverage_info:
        c.drawString(50, y, line)
        y -= 15
        if y < 100:
            c.showPage()
            y = height - 50
    
    # Data and Compliance
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "DATA AND COMPLIANCE")
    y -= 20
    
    c.setFont("Helvetica", 10)
    data_compliance = [
        "Data Types: PII, Payment Data, Proprietary Business Data",
        "Records Count: 2,500,000",
        "PCI Compliance: Yes",
        "HIPAA Compliance: Not applicable",
        "SOX Compliance: Yes", 
        "GDPR Compliance: Yes",
        "CCPA Compliance: Yes",
        "ISO 27001 Certified: Yes",
        "SOC 2 Certified: Yes - Type II",
        "Other Certifications: FedRAMP Moderate, NIST Cybersecurity Framework",
        ""
    ]
    
    for line in data_compliance:
        c.drawString(50, y, line)
        y -= 15
    
    # Security Measures
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "SECURITY MEASURES")
    y -= 20
    
    c.setFont("Helvetica", 10)
    security_measures = [
        "Incident Response Plan: Yes - Tested annually",
        "Business Continuity Plan: Yes - Tested quarterly", 
        "Disaster Recovery Plan: Yes - RTO: 4 hours, RPO: 1 hour",
        "Employee Training: Yes - Monthly security awareness training",
        "Penetration Testing: Quarterly external, annual internal",
        "Vulnerability Scanning: Daily automated scanning",
        "Multi-Factor Authentication: Yes - All systems",
        "Encryption at Rest: Yes - AES-256",
        "Encryption in Transit: Yes - TLS 1.3",
        "Endpoint Protection: CrowdStrike Falcon",
        "Email Security: Microsoft Advanced Threat Protection",
        "Network Monitoring: 24/7 SOC with SIEM",
        "Access Controls: Role-based access control (RBAC)",
        "Patch Management: Automated patching within 72 hours",
        ""
    ]
    
    for line in security_measures:
        c.drawString(50, y, line)
        y -= 15
        if y < 100:
            c.showPage()
            y = height - 50
    
    # Technology Environment
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "TECHNOLOGY ENVIRONMENT")
    y -= 20
    
    c.setFont("Helvetica", 10)
    tech_environment = [
        "Cloud Services: Yes - Hybrid cloud architecture",
        "Cloud Providers: AWS (primary), Microsoft Azure (secondary)",
        "Remote Workforce Percentage: 65%",
        "Third Party Vendors: 47 active technology vendors",
        "Vendor Risk Management: Yes - Annual assessments",
        "Website URL: www.oriondatatech.com",
        "Annual Website Revenue: $12,000,000",
        "Mobile Apps: 3 customer-facing applications",
        "API Endpoints: 127 active endpoints",
        "Databases: 15 production databases (PostgreSQL, MongoDB)",
        "Payment Processing: Stripe, PayPal integration",
        ""
    ]
    
    for line in tech_environment:
        c.drawString(50, y, line)
        y -= 15
    
    # Claims History
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "CLAIMS AND INCIDENT HISTORY")
    y -= 20
    
    c.setFont("Helvetica", 10)
    claims_history = [
        "Previous Breach: No significant data breaches",
        "Breach Details: Minor phishing incident in 2022 - no data compromise",
        "Breach Costs: $15,000 (investigation and employee training)",
        "Litigation History: None",
        "Regulatory Actions: None",
        ""
    ]
    
    for line in claims_history:
        c.drawString(50, y, line)
        y -= 15
    
    # Submission Details
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "SUBMISSION DETAILS")
    y -= 20
    
    c.setFont("Helvetica", 10)
    submission_details = [
        "Submission Date: 2024-10-09",
        "Quote Deadline: 2024-10-23",
        "Bind Date: 2024-12-15",
        "Underwriter Name: David Kim",
        "Underwriter Email: d.kim@cyberguard.com",
        "",
        "Special Terms: 24-hour breach notification requirement",
        "Additional Coverages: Social Engineering coverage requested",
        "Remarks: Company expanding internationally - need global coverage",
        "",
        "Authorized Signature: Sarah Johnson, CISO",
        "Date: October 9, 2024"
    ]
    
    for line in submission_details:
        c.drawString(50, y, line)
        y -= 15
    
    # Save PDF
    c.save()
    
    # Get PDF bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes

# Generate the comprehensive PDF
print("🏗️  Creating comprehensive cyber insurance submission PDF...")
pdf_content = create_comprehensive_cyber_insurance_pdf()

# Convert to base64
pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')

print(f"✅ PDF created successfully!")
print(f"   PDF size: {len(pdf_content)} bytes")
print(f"   Base64 size: {len(pdf_base64)} characters")

# Save the PDF file for inspection
with open('comprehensive_cyber_insurance_submission.pdf', 'wb') as f:
    f.write(pdf_content)

print(f"📄 PDF saved as: comprehensive_cyber_insurance_submission.pdf")

# Test the attachment parsing
try:
    from file_parsers import parse_attachments
    
    test_attachment = [{
        "filename": "comprehensive_cyber_insurance_submission.pdf",
        "contentBase64": pdf_base64
    }]
    
    print(f"\n🧪 Testing attachment parsing...")
    result = parse_attachments(test_attachment, "uploads")
    
    if result and len(result) > 100:
        print(f"✅ SUCCESS: PDF parsed successfully!")
        print(f"   Extracted text length: {len(result)} characters")
        print(f"   First 500 characters:")
        print(f"   {result[:500]}...")
    else:
        print(f"❌ Failed to parse PDF: {result}")
        
except Exception as e:
    print(f"❌ Error testing PDF parsing: {e}")

# Create the Logic Apps test payload
from datetime import datetime
import json

logic_apps_payload = {
    "subject": "Cyber Insurance Renewal - Orion Data Technologies Inc. - Policy CYB-2024-567890",
    "from": "s.johnson@oriondatatech.com", 
    "body": """<html><body>
<h2>Cyber Insurance Renewal Submission</h2>
<p>Dear Underwriting Team,</p>
<p>Please find attached our completed cyber insurance renewal submission for Orion Data Technologies Inc.</p>
<p><strong>Key Details:</strong></p>
<ul>
<li>Current Policy: CYB-2024-567890</li>
<li>Requested Coverage: $10M aggregate</li>  
<li>Industry: Technology/Software</li>
<li>Employees: 285</li>
<li>Annual Revenue: $45M</li>
<li>Quote Deadline: October 23, 2024</li>
</ul>
<p>We are seeking comprehensive cyber liability coverage including data breach response, business interruption, and regulatory defense costs.</p>
<p>Please let me know if you need any additional information.</p>
<p>Best regards,<br>
Sarah Johnson<br>
Chief Information Security Officer<br>
Orion Data Technologies Inc.<br>
s.johnson@oriondatatech.com<br>
(555) 123-4567</p>
</body></html>""",
    "receivedDateTime": datetime.utcnow().isoformat() + "Z",
    "attachments": [
        {
            "name": "comprehensive_cyber_insurance_submission.pdf",
            "contentType": "application/pdf",
            "contentBytes": pdf_base64
        }
    ]
}

# Save the complete test payload
with open('comprehensive_logic_apps_payload.json', 'w') as f:
    json.dump(logic_apps_payload, f, indent=2)

print(f"\n📋 Complete Logic Apps test payload saved as: comprehensive_logic_apps_payload.json")
print(f"   This payload contains:")
print(f"   - Comprehensive HTML email body with key details")
print(f"   - Complete PDF with all cyber insurance fields")
print(f"   - Realistic sender email and subject line")
print(f"   - Ready to test full end-to-end Logic Apps flow")

print(f"\n🎯 Use this to test:")
print(f"   1. POST to: http://localhost:8000/api/logicapps/email/intake")
print(f"   2. Verify attachment_content is populated in database")
print(f"   3. Check that LLM extracts all the comprehensive field data")