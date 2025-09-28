import logging
from typing import List
from fastapi import FastAPI, HTTPException, Depends, status, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import json

from database import get_db, Submission, WorkItem, create_tables
from llm_service import llm_service
from models import (
    EmailIntakePayload, EmailIntakeResponse, 
    SubmissionResponse, SubmissionConfirmRequest, 
    SubmissionConfirmResponse, ErrorResponse
)
from config import settings
from logging_config import configure_logging, get_logger
from websocket_manager import websocket_manager
import asyncio

# Configure logging first
configure_logging()
logger = get_logger(__name__)

# Use minimal file parser for Vercel deployment
try:
    from file_parsers_minimal import parse_attachments
    logger.info("Using minimal file parser for Vercel deployment")
except ImportError:
    from file_parsers import parse_attachments
    logger.info("Using full file parser")

# Create FastAPI app
app = FastAPI(
    title="Underwriting Workbench API",
    description="Backend API for insurance submission processing",
    version="1.0.0"
)

# Configure CORS for Vercel deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.cors_origins == "*" else settings.cors_origins.split(","),
    allow_credentials=settings.cors_credentials,
    allow_methods=["*"] if settings.cors_methods == "*" else settings.cors_methods.split(","),
    allow_headers=["*"] if settings.cors_headers == "*" else settings.cors_headers.split(","),
)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Underwriting Workbench API")
    create_tables()
    logger.info("Database tables created successfully")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error("Unhandled exception", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


@app.post("/api/email/intake", response_model=EmailIntakeResponse)
async def email_intake(
    request: EmailIntakePayload,
    db: Session = Depends(get_db)
):
    """
    Process incoming email with attachments and extract insurance data
    """
    logger.info("Processing email intake", subject=request.subject, from_email=request.from_email)
    
    try:
        # Generate unique submission reference
        submission_ref = str(uuid.uuid4())
        
        # Parse attachments if any
        attachment_text = ""
        if request.attachments:
            logger.info("Processing attachments", count=len(request.attachments))
            # Filter out attachments with missing data
            valid_attachments = [
                {"filename": att.filename, "contentBase64": att.contentBase64} 
                for att in request.attachments 
                if att.filename and att.contentBase64
            ]
            if valid_attachments:
                attachment_text = parse_attachments(valid_attachments, settings.upload_dir)
        
        # Combine email body and attachment text with null safety
        combined_text = f"Email Subject: {request.subject or 'No subject'}\n"
        combined_text += f"From: {request.from_email or 'Unknown sender'}\n"
        combined_text += f"Email Body:\n{request.body or 'No body content'}\n\n"
        
        if attachment_text:
            combined_text += f"Attachment Content:\n{attachment_text}"
        
        logger.info("Extracting structured data with LLM")
        
        # Extract structured data using LLM
        extracted_data = llm_service.extract_insurance_data(combined_text)
        
        # Get next submission ID
        last_submission = db.query(Submission).order_by(Submission.submission_id.desc()).first()
        next_submission_id = (last_submission.submission_id + 1) if last_submission else 1
        
        # Create submission record directly with null safety
        submission = Submission(
            submission_id=next_submission_id,
            submission_ref=submission_ref,
            subject=request.subject or "No subject",
            sender_email=request.from_email or "Unknown sender",
            body_text=request.body or "No body content",
            extracted_fields=extracted_data,
            task_status="pending"
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
        
        logger.info("Submission created", submission_id=submission.submission_id, submission_ref=submission_ref)
        
        # Broadcast new work item to all connected WebSocket clients
        await broadcast_new_workitem(submission)
        
        return EmailIntakeResponse(
            submission_ref=str(submission_ref),
            submission_id=submission.submission_id,
            status="success",
            message="Email processed successfully and submission created"
        )
        
    except Exception as e:
        logger.error("Error processing email intake", error=str(e), exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error processing email: {str(e)}"
        )


@app.get("/api/submissions/{submission_ref}", response_model=SubmissionResponse)
async def get_submission(
    submission_ref: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve a submission by submission reference UUID
    """
    logger.info("Retrieving submission", submission_ref=submission_ref)
    
    try:
        submission = db.query(Submission).filter(Submission.submission_ref == submission_ref).first()
        
        if not submission:
            raise HTTPException(
                status_code=404,
                detail="Submission not found"
            )
        
        logger.info("Submission retrieved successfully", submission_ref=submission_ref)
        
        return SubmissionResponse(
            id=submission.id,
            submission_id=submission.submission_id,
            submission_ref=str(submission.submission_ref),
            subject=submission.subject,
            sender_email=submission.sender_email,
            body_text=submission.body_text,
            extracted_fields=submission.extracted_fields,
            assigned_to=submission.assigned_to,
            task_status=submission.task_status,
            created_at=submission.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving submission", submission_ref=submission_ref, error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving submission: {str(e)}"
        )


@app.post("/api/submissions/confirm/{submission_ref}", response_model=SubmissionConfirmResponse)
async def confirm_submission(
    submission_ref: str,
    request: SubmissionConfirmRequest,
    db: Session = Depends(get_db)
):
    """
    Confirm a submission and assign to underwriter
    """
    logger.info("Confirming submission", submission_ref=submission_ref)
    
    try:
        # Get the submission
        submission = db.query(Submission).filter(Submission.submission_ref == submission_ref).first()
        
        if not submission:
            raise HTTPException(
                status_code=404,
                detail="Submission not found"
            )
        
        # Assign underwriter
        assigned_underwriter = assign_underwriter(request.underwriter_email)
        
        # Update submission with assignment
        submission.assigned_to = assigned_underwriter
        submission.task_status = "in_progress"
        db.commit()
        
        logger.info("Submission updated with assignment", submission_ref=submission_ref, assigned_to=assigned_underwriter)
        
        # Create work item
        work_item = WorkItem(
            submission_id=submission.id,
            assigned_to=assigned_underwriter,
            status="pending"
        )
        db.add(work_item)
        db.commit()
        db.refresh(work_item)
        
        logger.info("Work item created", work_item_id=work_item.id, assigned_to=assigned_underwriter)
        
        return SubmissionConfirmResponse(
            submission_id=submission.submission_id,
            submission_ref=str(submission.submission_ref),
            work_item_id=work_item.id,
            assigned_to=assigned_underwriter,
            task_status="in_progress"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error confirming submission", submission_ref=submission_ref, error=str(e))
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error confirming submission: {str(e)}"
        )


def assign_underwriter(preferred_email: str = None) -> str:
    """
    Simple round-robin underwriter assignment
    In a real system, this would query a database of available underwriters
    """
    if preferred_email:
        return preferred_email
    
    # Simple list of underwriters for round-robin assignment
    underwriters = [
        "underwriter1@company.com",
        "underwriter2@company.com", 
        "underwriter3@company.com"
    ]
    
    # For now, just return the first one
    # In production, you'd implement proper round-robin logic
    return underwriters[0]


@app.get("/api/submissions", response_model=List[SubmissionResponse])
async def get_all_submissions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all submissions with pagination
    """
    logger.info("Retrieving all submissions", skip=skip, limit=limit)
    
    try:
        submissions = db.query(Submission).offset(skip).limit(limit).all()
        
        result = []
        for submission in submissions:
            result.append(SubmissionResponse(
                id=submission.id,
                submission_id=submission.submission_id,
                submission_ref=str(submission.submission_ref),
                subject=submission.subject,
                sender_email=submission.sender_email,
                body_text=submission.body_text,
                extracted_fields=submission.extracted_fields,
                assigned_to=submission.assigned_to,
                task_status=submission.task_status,
                created_at=submission.created_at
            ))
        
        logger.info("Retrieved submissions", count=len(result))
        return result
        
    except Exception as e:
        logger.error("Error retrieving submissions", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving submissions: {str(e)}"
        )


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Underwriting Workbench API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "email_intake": "/api/email/intake",
            "submissions": "/api/submissions",
            "submission_detail": "/api/submissions/{submission_ref}",
            "confirm_submission": "/api/submissions/confirm/{submission_ref}"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# ===== Polling-based updates for Vercel compatibility =====

@app.get("/api/workitems/poll")
async def poll_workitems(
    since: str = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Poll for recent work items. Optimized for frontend polling instead of SSE.
    
    Args:
        since: ISO timestamp to filter items created after this time
        limit: Maximum number of items to return (default 50, max 100)
    """
    try:
        # Limit max items to prevent large responses
        limit = min(limit, 100)
        
        query = db.query(Submission).order_by(Submission.created_at.desc())
        
        # Filter by timestamp if provided
        if since:
            try:
                since_dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
                query = query.filter(Submission.created_at > since_dt)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid 'since' timestamp format. Use ISO format (e.g., 2025-09-28T10:00:00Z)"
                )
        
        submissions = query.limit(limit).all()
        
        # Format response similar to SSE format for consistency
        items = []
        for submission in submissions:
            items.append({
                "id": submission.id,
                "submission_id": submission.submission_id,
                "submission_ref": str(submission.submission_ref),
                "subject": submission.subject or "No subject",
                "from_email": submission.sender_email or "Unknown sender",
                "created_at": submission.created_at.isoformat() + "Z" if submission.created_at else None,
                "status": submission.task_status or "pending",
                "extracted_fields": submission.extracted_fields or {}
            })
        
        return {
            "items": items,
            "count": len(items),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error polling work items", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error polling work items: {str(e)}"
        )


@app.websocket("/ws/workitems")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time work item updates"""
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive and handle any incoming messages
            data = await websocket.receive_text()
            # Echo back any messages (optional)
            await websocket_manager.send_personal_message(f"Echo: {data}", websocket)
    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket_manager.disconnect(websocket)


@app.post("/api/test/workitem")
async def test_workitem(db: Session = Depends(get_db)):
    """Test endpoint to create a fake work item and broadcast it"""
    try:
        # Create a test submission
        submission_ref = str(uuid.uuid4())
        last_submission = db.query(Submission).order_by(Submission.submission_id.desc()).first()
        next_submission_id = (last_submission.submission_id + 1) if last_submission else 1
        
        test_submission = Submission(
            submission_id=next_submission_id,
            submission_ref=submission_ref,
            subject="Test Insurance Policy Submission",
            sender_email="test@example.com",
            body_text="This is a test work item created for WebSocket testing.",
            extracted_fields={
                "insured_name": "Test Company Inc",
                "policy_type": "General Liability",
                "coverage_amount": "$1,000,000",
                "effective_date": "2024-01-01",
                "broker": "Test Insurance Agency"
            },
            task_status="pending"
        )
        
        db.add(test_submission)
        db.commit()
        db.refresh(test_submission)
        
        # Broadcast the test work item (WebSocket)
        await broadcast_new_workitem(test_submission)
        
        return {
            "message": "Test work item created and broadcasted",
            "submission_id": test_submission.submission_id,
            "submission_ref": str(submission_ref),
            "websocket_connections": websocket_manager.get_connection_count()
        }
        
    except Exception as e:
        logger.error(f"Error creating test work item: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating test work item: {str(e)}"
        )


async def broadcast_new_workitem(submission: Submission):
    """Broadcast a new work item to all connected WebSocket clients"""
    try:
        workitem_data = {
            "id": submission.id,
            "submission_id": submission.submission_id,
            "submission_ref": str(submission.submission_ref),
            "subject": submission.subject or "No subject",
            "from_email": submission.sender_email or "Unknown sender",
            "created_at": submission.created_at.isoformat() + "Z" if submission.created_at else None,
            "status": submission.task_status or "pending",
            "extracted_fields": submission.extracted_fields or {}
        }
        
        await websocket_manager.broadcast_workitem(workitem_data)
        logger.info(f"Broadcasted new work item: {submission.submission_id}")
        
    except Exception as e:
        logger.error(f"Error broadcasting work item: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
