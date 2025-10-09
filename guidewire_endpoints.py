"""
Guidewire Integration Endpoints
Handles pushing work items to Guidewire PolicyCenter
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db, WorkItem, Submission
from guidewire_client import guidewire_client
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class GuidewireSubmissionRequest(BaseModel):
    work_item_id: int
    force_resubmit: bool = False

class GuidewireSubmissionResponse(BaseModel):
    success: bool
    work_item_id: int
    guidewire_account_id: Optional[str] = None
    guidewire_job_id: Optional[str] = None
    guidewire_account_number: Optional[str] = None
    guidewire_job_number: Optional[str] = None
    quote_info: Optional[Dict[str, Any]] = None
    message: str
    error: Optional[str] = None

@router.post("/api/guidewire/submit", response_model=GuidewireSubmissionResponse)
async def submit_to_guidewire(
    request: GuidewireSubmissionRequest,
    db: Session = Depends(get_db)
):
    """
    Submit a work item to Guidewire PolicyCenter
    Creates account, submission, and generates quote
    """
    logger.info(f"Submitting work item {request.work_item_id} to Guidewire")
    
    try:
        # Get work item from database
        work_item = db.query(WorkItem).filter(WorkItem.id == request.work_item_id).first()
        if not work_item:
            raise HTTPException(
                status_code=404,
                detail=f"Work item {request.work_item_id} not found"
            )
        
        # Check if already submitted to Guidewire (unless force resubmit)
        if hasattr(work_item, 'guidewire_job_id') and work_item.guidewire_job_id and not request.force_resubmit:
            return GuidewireSubmissionResponse(
                success=True,
                work_item_id=work_item.id,
                guidewire_job_id=work_item.guidewire_job_id,
                message="Work item already submitted to Guidewire (use force_resubmit=true to resubmit)"
            )
        
        # Get submission data
        submission = db.query(Submission).filter(Submission.id == work_item.submission_id).first()
        if not submission:
            raise HTTPException(
                status_code=400,
                detail="No submission data found for work item"
            )
        
        # Prepare submission data
        submission_data = _prepare_submission_data(work_item, submission)
        
        logger.info(f"Prepared submission data for {submission_data.get('company_name', 'Unknown Company')}")
        
        # Submit to Guidewire
        result = guidewire_client.create_cyber_submission(submission_data)
        
        if result["success"]:
            # Update work item with Guidewire information
            _update_work_item_with_guidewire_data(db, work_item, result)
            
            # Store comprehensive Guidewire response data for UI display
            if "parsed_data" in result:
                try:
                    guidewire_response_id = guidewire_client.store_guidewire_response(
                        db=db,
                        work_item_id=work_item.id,
                        submission_id=work_item.submission_id,
                        parsed_data=result["parsed_data"],
                        raw_response=result.get("raw_response", {})
                    )
                    logger.info(f"Stored Guidewire response data with ID: {guidewire_response_id}")
                except Exception as e:
                    logger.error(f"Failed to store Guidewire response data: {str(e)}")
                    # Don't fail the whole request if storage fails
            
            return GuidewireSubmissionResponse(
                success=True,
                work_item_id=work_item.id,
                guidewire_account_id=result.get("account_id"),
                guidewire_job_id=result.get("job_id"),
                guidewire_account_number=result.get("account_number"),
                guidewire_job_number=result.get("job_number"),
                quote_info=result.get("quote_info"),
                message=result.get("message", "Submission successful")
            )
        else:
            # Log the failure but don't update work item
            logger.error(f"Guidewire submission failed: {result.get('message', 'Unknown error')}")
            
            return GuidewireSubmissionResponse(
                success=False,
                work_item_id=work_item.id,
                message=result.get("message", "Submission failed"),
                error=result.get("error", "Unknown error")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting to Guidewire: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(e)}"
        )

@router.get("/api/guidewire/status/{work_item_id}")
async def get_guidewire_status(
    work_item_id: int,
    db: Session = Depends(get_db)
):
    """
    Get Guidewire submission status for a work item
    """
    work_item = db.query(WorkItem).filter(WorkItem.id == work_item_id).first()
    if not work_item:
        raise HTTPException(
            status_code=404,
            detail=f"Work item {work_item_id} not found"
        )
    
    guidewire_data = {}
    if hasattr(work_item, 'guidewire_job_id') and work_item.guidewire_job_id:
        guidewire_data = {
            "submitted": True,
            "job_id": work_item.guidewire_job_id,
            "account_id": getattr(work_item, 'guidewire_account_id', None),
            "job_number": getattr(work_item, 'guidewire_job_number', None),
            "account_number": getattr(work_item, 'guidewire_account_number', None)
        }
    else:
        guidewire_data = {
            "submitted": False,
            "message": "Work item not yet submitted to Guidewire"
        }
    
    return {
        "work_item_id": work_item_id,
        "work_item_title": work_item.title,
        "work_item_status": work_item.status.value if work_item.status else None,
        "guidewire": guidewire_data
    }

@router.post("/api/guidewire/test-connection")
async def test_guidewire_connection():
    """
    Test connection to Guidewire API
    """
    try:
        result = guidewire_client.test_connection()
        return {
            "connection_test": result,
            "endpoint": guidewire_client.config.full_url,
            "timestamp": "2025-10-09T07:20:00Z"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Connection test failed: {str(e)}"
        )

def _prepare_submission_data(work_item: WorkItem, submission: Submission) -> Dict[str, Any]:
    """Prepare submission data for Guidewire from work item and submission"""
    
    # Start with extracted fields if available
    extracted_data = {}
    if submission.extracted_fields:
        if isinstance(submission.extracted_fields, str):
            try:
                extracted_data = json.loads(submission.extracted_fields)
            except:
                extracted_data = {}
        elif isinstance(submission.extracted_fields, dict):
            extracted_data = submission.extracted_fields
    
    # Enhance with work item data
    submission_data = {
        # Company information
        "company_name": extracted_data.get("company_name") or extracted_data.get("named_insured") or "Unknown Company",
        "company_ein": extracted_data.get("company_ein", "00-0000000"),
        
        # Address information
        "business_address": extracted_data.get("business_address") or extracted_data.get("mailing_address", "Address Not Provided"),
        "business_city": extracted_data.get("business_city") or extracted_data.get("mailing_city", "Unknown"),
        "business_state": extracted_data.get("business_state") or extracted_data.get("mailing_state", "CA"),
        "business_zip": extracted_data.get("business_zip") or extracted_data.get("mailing_zip", "00000"),
        
        # Policy information
        "policy_type": work_item.policy_type or extracted_data.get("policy_type", "Cyber Liability"),
        "coverage_amount": work_item.coverage_amount or extracted_data.get("coverage_amount", "50000"),
        "effective_date": extracted_data.get("effective_date", "2025-01-01"),
        
        # Business information
        "industry": work_item.industry or extracted_data.get("industry", "technology"),
        "employee_count": extracted_data.get("employee_count", "10"),
        "annual_revenue": extracted_data.get("annual_revenue", "1000000"),
        
        # Contact information
        "contact_name": extracted_data.get("contact_name", "Business Owner"),
        "contact_email": extracted_data.get("contact_email") or submission.sender_email,
        "contact_phone": extracted_data.get("contact_phone", "555-0000"),
        
        # Additional fields
        "years_in_business": extracted_data.get("years_in_business", "5"),
        "business_description": extracted_data.get("business_description", "General business operations")
    }
    
    return submission_data

def _update_work_item_with_guidewire_data(db: Session, work_item: WorkItem, guidewire_result: Dict[str, Any]):
    """Update work item with Guidewire submission results"""
    
    try:
        # Add Guidewire fields to work item (you'll need to add these columns to the database schema)
        # For now, we'll add them to the work item's risk_categories field as a workaround
        guidewire_info = {
            "guidewire_account_id": guidewire_result.get("account_id"),
            "guidewire_job_id": guidewire_result.get("job_id"),
            "guidewire_account_number": guidewire_result.get("account_number"),
            "guidewire_job_number": guidewire_result.get("job_number"),
            "guidewire_submitted_at": "2025-10-09T07:20:00Z",
            "quote_info": guidewire_result.get("quote_info")
        }
        
        # Store in risk_categories JSON field for now
        if work_item.risk_categories:
            work_item.risk_categories.update({"guidewire": guidewire_info})
        else:
            work_item.risk_categories = {"guidewire": guidewire_info}
        
        # Update description
        work_item.description += f"\n\nGuidewire Submission: Job #{guidewire_result.get('job_number', 'Unknown')}"
        
        db.commit()
        logger.info(f"Updated work item {work_item.id} with Guidewire data")
        
    except Exception as e:
        logger.error(f"Error updating work item with Guidewire data: {str(e)}")
        db.rollback()
        # Don't raise exception - submission was successful, just logging failed