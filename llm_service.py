import json
import logging
from typing import Dict, Any, Optional
import google.generativeai as genai

from config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with Google Gemini LLM"""
    
    def __init__(self):
        self.google_client = None
        
        # Initialize Google Gemini client with configured model
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.google_client = genai.GenerativeModel(settings.gemini_model)
    
    def extract_insurance_data(self, combined_text: str) -> Dict[str, Any]:
        """Extract structured insurance data from text using Google Gemini"""
        
        prompt = self._create_extraction_prompt(combined_text)
        
        try:
            if self.google_client:
                return self._extract_with_google(prompt)
            else:
                raise Exception("Google Gemini not configured")
                
        except Exception as e:
            logger.error(f"Error extracting data with Gemini: {str(e)}")
            # Return default structure if LLM fails
            return self._get_default_response()
    
    def _create_extraction_prompt(self, text: str) -> str:
        """Create the prompt for data extraction"""
        return f"""
You are an expert cyber insurance underwriter analyzing an insurance submission. 
Extract the following information from the text and return ONLY a valid JSON object.

Text to analyze:
{text}

Extract these fields for cyber insurance submission:
{{
    "company_name": "Name of the company requesting insurance",
    "insured_name": "Primary contact name or insured party name",
    "contact_email": "Contact email address",
    "contact_name": "Primary contact person's name",
    "contact_title": "Primary contact's job title",
    "industry": "Industry sector (healthcare, technology, financial_services, etc.)",
    "company_size": "Company size (small, medium, large, enterprise)",
    "employee_count": "Number of employees",
    "annual_revenue": "Annual revenue amount",
    "coverage_amount": "Requested coverage amount",
    "policy_type": "Type of cyber insurance policy (use: Cyber Liability, Privacy Liability, Data Breach Response, Technology E&O, Cyber Security, First Party Cyber, or Third Party Cyber)",
    "deductible": "Policy deductible amount",
    "effective_date": "Policy effective date",
    "expiry_date": "Policy expiry date",
    "data_types": "Types of data handled (PII, PHI, payment data, etc.)",
    "security_measures": "Security measures in place",
    "compliance_certifications": "Compliance certifications (SOC2, HIPAA, ISO27001, etc.)",
    "previous_incidents": "Previous security incidents or breaches",
    "previous_breach": "Has there been a previous breach (yes/no)",
    "business_type": "Type of business (SaaS, manufacturing, consulting, etc.)",
    "cloud_usage": "Does the company use cloud services (yes/no)",
    "remote_workforce": "Percentage of remote workforce",
    "years_in_operation": "Years the company has been in operation",
    "current_coverage": "Current cyber insurance coverage amount if any"
}}

CRITICAL INSTRUCTIONS:
- Extract company name carefully - look for "Company Name:", organization names, or sender company
- For contact_email: Use the "From:" email address from the email header
- For dates: Use YYYY-MM-DD format when possible
- For amounts: Extract FULL numeric values (convert millions to numbers):
  * "$30 million" → "30000000"
  * "$45 million" → "45000000" 
  * "$15 million" → "15000000"
  * "$5 million" → "5000000"
  * "$5M" → "5000000"
  * "$500,000" → "500000"
  * Remove all $, commas, and convert text to numbers
  * ALWAYS multiply by 1,000,000 when you see "million"
- For coverage_amount: Look for "coverage", "limit", "coverage limit", or "insurance amount"
- For annual_revenue: Look for "revenue", "annual revenue", "sales", or "income"
- For policy_type: If not explicitly stated, use "Cyber Liability" as default for cyber insurance requests
- For industry: Use lowercase (healthcare, technology, financial_services, manufacturing, etc.)
- For company_size: Use lowercase (small, medium, large, enterprise) 
- If information is not found, use "Not specified"
- Return ONLY the JSON object, no additional text
- Ensure all field names match exactly as specified above
"""
    
    def _extract_with_google(self, prompt: str) -> Dict[str, Any]:
        """Extract data using Google Gemini"""
        try:
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=settings.max_tokens,
                temperature=0.1,
            )
            
            response = self.google_client.generate_content(
                prompt, 
                generation_config=generation_config
            )
            content = response.text.strip()
            logger.info(f"Google Gemini response: {content}")
            return self._parse_json_response(content)
            
        except Exception as e:
            logger.error(f"Error with Google Gemini: {str(e)}")
            raise
    
    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON response from LLM"""
        try:
            # Clean up response - remove any markdown formatting
            content = content.replace("```json", "").replace("```", "").strip()
            
            # Parse JSON
            data = json.loads(content)
            
            # Validate required fields for cyber insurance
            required_fields = ["company_name", "insured_name", "contact_email", "industry", "coverage_amount", "policy_type", "effective_date"]
            for field in required_fields:
                if field not in data:
                    data[field] = "Not specified"
                elif not isinstance(data[field], str):
                    data[field] = str(data[field])
            
            logger.info(f"Successfully parsed JSON response: {data}")
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {str(e)}")
            logger.error(f"Raw content: {content}")
            return self._get_default_response()
        except Exception as e:
            logger.error(f"Error processing response: {str(e)}")
            return self._get_default_response()
    
    def _get_default_response(self) -> Dict[str, Any]:
        """Return default response when LLM fails"""
        return {
            "company_name": "Not specified",
            "insured_name": "Not specified",
            "contact_email": "Not specified",
            "contact_name": "Not specified",
            "industry": "Not specified",
            "company_size": "Not specified",
            "coverage_amount": "Not specified",
            "policy_type": "cyber",
            "effective_date": "Not specified",
            "expiry_date": "Not specified",
            "data_types": "Not specified",
            "security_measures": "Not specified",
            "compliance_certifications": "Not specified",
            "previous_incidents": "Not specified",
            "business_type": "Not specified"
        }


# Global instance
llm_service = LLMService()
