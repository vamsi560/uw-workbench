# Test Email Content for Underwriting Workbench API

## 📧 **Sample Email Content**

### **Email Subject:**
```
Insurance Policy Submission - General Liability Coverage Request
```

### **Email Body:**
```
Dear Underwriting Team,

I hope this email finds you well. I am writing to submit a new insurance policy application for our client, ABC Manufacturing Corp.

**Policy Details:**
- Insured Company: ABC Manufacturing Corp
- Policy Type: General Liability Insurance
- Coverage Amount: $2,000,000 per occurrence
- Effective Date: March 1, 2024
- Broker: John Smith, Smith Insurance Agency
- Contact: john.smith@smithinsurance.com

**Client Information:**
ABC Manufacturing Corp is a mid-size manufacturing company specializing in automotive parts. They have been in business for 15 years and have a clean claims history. The company operates from a 50,000 sq ft facility in Detroit, Michigan, with 75 employees.

**Coverage Requirements:**
- General Liability: $2,000,000 per occurrence / $4,000,000 aggregate
- Product Liability: $2,000,000 per occurrence
- Completed Operations: $2,000,000 per occurrence
- Personal & Advertising Injury: $2,000,000 per occurrence

**Risk Assessment:**
The client has implemented comprehensive safety protocols and maintains regular equipment maintenance schedules. They have not had any significant claims in the past 5 years.

Please find attached the following documents:
1. Application form (completed)
2. Financial statements (last 3 years)
3. Safety inspection reports
4. Previous policy declarations

I would appreciate your review and a quote within 48 hours. Please let me know if you need any additional information.

Best regards,
John Smith
Senior Insurance Broker
Smith Insurance Agency
Phone: (555) 123-4567
Email: john.smith@smithinsurance.com
```

## 🧪 **JSON Test Payload for API**

### **Direct API Test (POST to /api/email/intake):**

```json
{
  "subject": "Insurance Policy Submission - General Liability Coverage Request",
  "from_email": "john.smith@smithinsurance.com",
  "received_at": "2024-01-15T10:30:00Z",
  "body": "Dear Underwriting Team,\n\nI hope this email finds you well. I am writing to submit a new insurance policy application for our client, ABC Manufacturing Corp.\n\n**Policy Details:**\n- Insured Company: ABC Manufacturing Corp\n- Policy Type: General Liability Insurance\n- Coverage Amount: $2,000,000 per occurrence\n- Effective Date: March 1, 2024\n- Broker: John Smith, Smith Insurance Agency\n- Contact: john.smith@smithinsurance.com\n\n**Client Information:**\nABC Manufacturing Corp is a mid-size manufacturing company specializing in automotive parts. They have been in business for 15 years and have a clean claims history. The company operates from a 50,000 sq ft facility in Detroit, Michigan, with 75 employees.\n\n**Coverage Requirements:**\n- General Liability: $2,000,000 per occurrence / $4,000,000 aggregate\n- Product Liability: $2,000,000 per occurrence\n- Completed Operations: $2,000,000 per occurrence\n- Personal & Advertising Injury: $2,000,000 per occurrence\n\n**Risk Assessment:**\nThe client has implemented comprehensive safety protocols and maintains regular equipment maintenance schedules. They have not had any significant claims in the past 5 years.\n\nPlease find attached the following documents:\n1. Application form (completed)\n2. Financial statements (last 3 years)\n3. Safety inspection reports\n4. Previous policy declarations\n\nI would appreciate your review and a quote within 48 hours. Please let me know if you need any additional information.\n\nBest regards,\nJohn Smith\nSenior Insurance Broker\nSmith Insurance Agency\nPhone: (555) 123-4567\nEmail: john.smith@smithinsurance.com",
  "attachments": []
}
```

## 📎 **Test with Attachments (DOCX/XLSX)**

### **JSON with Sample Attachments:**

```json
{
  "subject": "Insurance Policy Submission - General Liability Coverage Request",
  "from_email": "john.smith@smithinsurance.com",
  "received_at": "2024-01-15T10:30:00Z",
  "body": "Dear Underwriting Team,\n\nPlease find attached the insurance application and supporting documents for ABC Manufacturing Corp.\n\n**Key Details:**\n- Insured: ABC Manufacturing Corp\n- Policy Type: General Liability\n- Coverage: $2,000,000 per occurrence\n- Effective: March 1, 2024\n- Broker: John Smith, Smith Insurance Agency\n\nBest regards,\nJohn Smith",
  "attachments": [
    {
      "filename": "insurance_application.docx",
      "contentBase64": "UEsDBBQAAAAIAA..." // Base64 encoded DOCX content
    },
    {
      "filename": "financial_statements.xlsx", 
      "contentBase64": "UEsDBBQAAAAIAA..." // Base64 encoded XLSX content
    }
  ]
}
```

## 🔍 **Expected API Response**

### **Successful Response:**
```json
{
  "submission_ref": "123e4567-e89b-12d3-a456-426614174000",
  "submission_id": 1,
  "status": "success",
  "message": "Email processed successfully and submission created"
}
```

### **Extracted Data (from LLM):**
```json
{
  "insured_name": "ABC Manufacturing Corp",
  "policy_type": "General Liability Insurance",
  "coverage_amount": "$2,000,000 per occurrence",
  "effective_date": "March 1, 2024",
  "broker": "John Smith, Smith Insurance Agency"
}
```

## 🧪 **Testing Scenarios**

### **1. Basic Email Test**
- Use the JSON payload above
- Test without attachments
- Verify LLM extraction works

### **2. Email with Attachments**
- Create sample DOCX/XLSX files
- Encode them to Base64
- Test file parsing functionality

### **3. Edge Cases**
- Empty subject/body
- Very long email content
- Special characters in email
- Multiple attachments

### **4. Error Testing**
- Invalid JSON format
- Missing required fields
- Invalid email format
- Large file attachments

## 📝 **Sample DOCX Content for Testing**

Create a simple Word document with this content:

```
INSURANCE APPLICATION FORM

Company Name: ABC Manufacturing Corp
Contact Person: John Smith
Email: john.smith@smithinsurance.com
Phone: (555) 123-4567

Policy Type: General Liability
Coverage Amount: $2,000,000
Effective Date: March 1, 2024
Expiration Date: March 1, 2025

Business Description:
Mid-size manufacturing company specializing in automotive parts.
50,000 sq ft facility in Detroit, Michigan.
75 employees.

Previous Claims: None in past 5 years
Safety Rating: Excellent
```

## 📊 **Sample XLSX Content for Testing**

Create an Excel file with this data:

| Field | Value |
|-------|-------|
| Company Name | ABC Manufacturing Corp |
| Policy Type | General Liability |
| Coverage Amount | $2,000,000 |
| Effective Date | 2024-03-01 |
| Broker | John Smith |
| Agency | Smith Insurance Agency |
| Contact Email | john.smith@smithinsurance.com |
| Phone | (555) 123-4567 |
| Business Type | Manufacturing |
| Years in Business | 15 |
| Number of Employees | 75 |
| Facility Size | 50,000 sq ft |
| Location | Detroit, MI |
| Previous Claims | 0 |
| Safety Rating | Excellent |

## 🚀 **Quick Test Commands**

### **Using curl:**
```bash
curl -X POST https://your-app-name.vercel.app/api/email/intake \
  -H "Content-Type: application/json" \
  -d @test_email.json
```

### **Using PowerShell:**
```powershell
$body = @{
    subject = "Insurance Policy Submission - General Liability Coverage Request"
    from_email = "john.smith@smithinsurance.com"
    received_at = "2024-01-15T10:30:00Z"
    body = "Dear Underwriting Team..."
    attachments = @()
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://your-app-name.vercel.app/api/email/intake" -Method Post -Body $body -ContentType "application/json"
```

This test content should help you verify that your API is working correctly and that the LLM is properly extracting the insurance data!
