"""
LLM Processing Microservice
Standalone FastAPI service for AI/ML processing using Google Gemini
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import json
import logging
import asyncio
from datetime import datetime

from llm_service import LLMService
from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="LLM Processing Microservice",
    description="AI/ML processing service for insurance underwriting",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM service
llm_service = LLMService()

# Pydantic models for API
class ExtractionRequest(BaseModel):
    text: str = Field(..., description="Combined text from email and attachments")
    email_subject: Optional[str] = Field(None, description="Email subject line")
    sender_email: Optional[str] = Field(None, description="Sender's email address")
    attachment_info: Optional[List[str]] = Field(None, description="List of attachment filenames")

class ExtractionResponse(BaseModel):
    extracted_fields: Dict[str, Any] = Field(..., description="Structured data extracted from text")
    summary: Dict[str, Any] = Field(..., description="Summary of the submission")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    model_used: str = Field(..., description="AI model used for processing")

class SummarizationRequest(BaseModel):
    subject: Optional[str] = Field(None, description="Email subject")
    body_text: Optional[str] = Field(None, description="Email body text")
    extracted_fields: Optional[Dict[str, Any]] = Field(None, description="Previously extracted structured data")

class TriageRequest(BaseModel):
    submission_data: Dict[str, Any] = Field(..., description="Complete submission data for triage")
    extracted_fields: Dict[str, Any] = Field(..., description="Extracted fields from LLM")

class TriageResponse(BaseModel):
    priority: str = Field(..., description="Assigned priority (LOW, MEDIUM, HIGH, CRITICAL)")
    risk_score: float = Field(..., description="Risk score from 0.0 to 10.0")
    assigned_category: str = Field(..., description="Suggested category for routing")
    reasoning: str = Field(..., description="AI reasoning for the triage decision")
    recommended_actions: List[str] = Field(..., description="Suggested next steps")

class RiskAssessmentRequest(BaseModel):
    submission_data: Dict[str, Any] = Field(..., description="Complete submission data")
    extracted_fields: Dict[str, Any] = Field(..., description="Structured extracted data")
    company_profile: Optional[Dict[str, Any]] = Field(None, description="Company profile information")

class RiskAssessmentResponse(BaseModel):
    overall_risk_score: float = Field(..., description="Overall risk score (0.0-10.0)")
    risk_categories: Dict[str, float] = Field(..., description="Breakdown by risk category")
    risk_factors: List[Dict[str, Any]] = Field(..., description="Identified risk factors")
    recommendations: List[str] = Field(..., description="Risk mitigation recommendations")
    confidence_score: float = Field(..., description="Confidence in the assessment (0.0-1.0)")

@app.post("/api/extract", response_model=ExtractionResponse)
async def extract_data(request: ExtractionRequest):
    """Extract structured insurance data from text using AI"""
    start_time = datetime.now()
    
    try:
        logger.info(f"Processing extraction request for {len(request.text)} characters")
        
        # Extract structured data using LLM
        extracted_fields = llm_service.extract_insurance_data(request.text)
        
        # Generate summary
        summary = llm_service.summarize_submission(
            request.email_subject,
            request.text,
            extracted_fields
        )
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        logger.info(f"Extraction completed in {processing_time:.2f}ms")
        
        return ExtractionResponse(
            extracted_fields=extracted_fields,
            summary=summary,
            processing_time_ms=processing_time,
            model_used=settings.gemini_model
        )
        
    except Exception as e:
        logger.error(f"Extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

@app.post("/api/summarize", response_model=Dict[str, Any])
async def summarize_submission(request: SummarizationRequest):
    """Generate summary of submission data"""
    try:
        summary = llm_service.summarize_submission(
            request.subject,
            request.body_text,
            request.extracted_fields
        )
        return summary
        
    except Exception as e:
        logger.error(f"Summarization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")

@app.post("/api/triage", response_model=TriageResponse)
async def triage_submission(request: TriageRequest):
    """AI-driven submission triage and prioritization"""
    try:
        # TODO: Implement AI triage logic
        # For now, return a placeholder response
        return TriageResponse(
            priority="MEDIUM",
            risk_score=5.0,
            assigned_category="Cyber Insurance",
            reasoning="Automatic triage based on submission content and extracted fields",
            recommended_actions=["Review company size", "Assess technical controls", "Verify compliance status"]
        )
        
    except Exception as e:
        logger.error(f"Triage failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Triage failed: {str(e)}")

@app.post("/api/risk-assessment", response_model=RiskAssessmentResponse)
async def assess_risk(request: RiskAssessmentRequest):
    """AI-driven risk assessment of submissions"""
    try:
        # TODO: Implement AI risk assessment logic
        # For now, return a placeholder response
        return RiskAssessmentResponse(
            overall_risk_score=6.5,
            risk_categories={
                "technical": 7.0,
                "operational": 6.0,
                "financial": 6.5,
                "compliance": 7.5
            },
            risk_factors=[
                {
                    "category": "technical",
                    "factor": "Insufficient endpoint protection",
                    "severity": "high",
                    "impact": 8.0
                }
            ],
            recommendations=[
                "Implement comprehensive endpoint detection and response (EDR)",
                "Establish incident response procedures",
                "Conduct regular security awareness training"
            ],
            confidence_score=0.85
        )
        
    except Exception as e:
        logger.error(f"Risk assessment failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Risk assessment failed: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test LLM service connectivity
        test_response = llm_service._get_default_response()
        
        return {
            "status": "healthy",
            "service": "llm-processing-microservice",
            "timestamp": datetime.now().isoformat(),
            "model": settings.gemini_model,
            "llm_service_available": True
        }
    except Exception as e:
        return {
            "status": "degraded",
            "service": "llm-processing-microservice",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "llm_service_available": False
        }

@app.get("/api/models")
async def get_available_models():
    """Get information about available AI models"""
    return {
        "current_model": settings.gemini_model,
        "capabilities": [
            "text_extraction",
            "data_structuring", 
            "summarization",
            "risk_assessment",
            "triage_classification"
        ],
        "supported_formats": [
            "email_text",
            "pdf_text",
            "document_text"
        ]
    }

# Background task for batch processing
@app.post("/api/batch-process")
async def batch_process(background_tasks: BackgroundTasks, requests: List[ExtractionRequest]):
    """Process multiple extraction requests in background"""
    
    def process_batch(requests_batch: List[ExtractionRequest]):
        results = []
        for req in requests_batch:
            try:
                extracted_fields = llm_service.extract_insurance_data(req.text)
                summary = llm_service.summarize_submission(req.email_subject, req.text, extracted_fields)
                results.append({
                    "status": "success",
                    "extracted_fields": extracted_fields,
                    "summary": summary
                })
            except Exception as e:
                results.append({
                    "status": "error",
                    "error": str(e)
                })
        
        # Store results or send to callback URL
        logger.info(f"Batch processing completed for {len(results)} requests")
        return results
    
    background_tasks.add_task(process_batch, requests)
    
    return {
        "message": f"Batch processing started for {len(requests)} requests",
        "status": "accepted"
    }

# Remove auto-start when imported - use start_llm_service.py instead
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8001)