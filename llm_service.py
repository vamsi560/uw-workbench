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
Please analyze the following insurance-related text and extract the structured information. 
Return ONLY a valid JSON object with the exact field names specified.

Text to analyze:
{text}

Extract the following fields and return as JSON:
{{
    "insured_name": "Name of the insured party/company",
    "policy_type": "Type of insurance policy (e.g., General Liability, Property, Auto, etc.)",
    "coverage_amount": "Coverage amount or limit",
    "effective_date": "Policy effective date",
    "broker": "Insurance broker or agent name"
}}

Instructions:
- If a field is not found or unclear, use "Not specified"
- For dates, use YYYY-MM-DD format if possible, otherwise keep original format
- For amounts, include currency if specified
- Return ONLY the JSON object, no additional text or explanation
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
            
            # Validate required fields
            required_fields = ["insured_name", "policy_type", "coverage_amount", "effective_date", "broker"]
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
            "insured_name": "Not specified",
            "policy_type": "Not specified", 
            "coverage_amount": "Not specified",
            "effective_date": "Not specified",
            "broker": "Not specified"
        }


# Global instance
llm_service = LLMService()
