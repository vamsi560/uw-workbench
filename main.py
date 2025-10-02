from pydantic import BaseModel
# Duplicate-free polling endpoint for submissions
class SubmissionOut(BaseModel):
    id: int
    subject: str
    from_email: str | None = None
    created_at: datetime
    status: str

@app.get("/api/workitems", response_model=List[SubmissionOut])
def get_workitems(
    since_id: int = None,
    since: datetime = None,
    db: Session = Depends(get_db)
):
    query = db.query(Submission)

    if since_id is not None:
        query = query.filter(Submission.id > since_id)
    elif since is not None:
        query = query.filter(Submission.created_at > since)
    else:
        # No filters, return 20 most recent
        query = query.order_by(Submission.created_at.desc()).limit(20)

    # Always order by created_at ASC for output
    results = query.order_by(Submission.created_at.asc()).all()

    # Remove duplicates by id (shouldn't be needed if id is PK, but for safety)
    seen = set()
    unique_submissions = []
    for sub in results:
        if sub.id not in seen:
            seen.add(sub.id)
            unique_submissions.append(sub)

    return [
        SubmissionOut(
            id=sub.id,
            subject=sub.subject,
            from_email=getattr(sub, "from_email", None),
            created_at=sub.created_at,
            status=sub.status
        )
        for sub in unique_submissions
    ]
import logging
from typing import List
from fastapi import FastAPI, HTTPException, Depends, status, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime
import uuid
import json

from database import get_db, Submission, WorkItem, RiskAssessment, Comment, User, WorkItemHistory, WorkItemStatus, WorkItemPriority, CompanySize, Underwriter, SubmissionMessage, create_tables
from llm_service import llm_service
from models import (
    EmailIntakePayload, EmailIntakeResponse, 
    SubmissionResponse, SubmissionConfirmRequest, 
    SubmissionConfirmResponse, ErrorResponse,
    WorkItemSummary, WorkItemDetail, WorkItemListResponse,
    EnhancedPollingResponse, RiskCategories,
    WorkItemStatusEnum, WorkItemPriorityEnum, CompanySizeEnum
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
    # Extract sender email from either field
    sender_email = request.sender_email or request.from_email or "Unknown sender"
    
    logger.info("Processing email intake", subject=request.subject, sender_email=sender_email)
    
    try:
        # Check for duplicate submissions (same subject and sender within last hour)
        from datetime import timedelta
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        
        existing_submission = db.query(Submission).filter(
            Submission.subject == (request.subject or "No subject"),
            Submission.sender_email == sender_email,
            Submission.created_at > one_hour_ago
        ).first()
        
        if existing_submission:
            logger.warning("Duplicate submission detected", 
                         subject=request.subject, 
                         sender_email=sender_email,
                         existing_ref=existing_submission.submission_ref)
            
            # Return existing submission instead of creating new one
            return EmailIntakeResponse(
                submission_ref=str(existing_submission.submission_ref),
                submission_id=existing_submission.submission_id,
                status="duplicate",
                message="Duplicate submission detected - returning existing submission"
            )
        
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
        combined_text += f"From: {sender_email}\n"
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
            sender_email=sender_email,
            body_text=request.body or "No body content",
            extracted_fields=extracted_data,
            task_status="pending"
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
        
        # Create corresponding work item with enhanced fields
        work_item = WorkItem(
            submission_id=submission.id,
            title=request.subject or "Email Submission",
            description=f"Email from {sender_email}",
            status=WorkItemStatus.PENDING,
            priority=WorkItemPriority.MEDIUM,
            assigned_to=None  # Will be assigned later
        )
        
        # Apply business rules and validation
        from business_rules import CyberInsuranceValidator, WorkflowEngine
        
        # Run comprehensive validation
        validation_status, missing_fields, rejection_reason = CyberInsuranceValidator.validate_submission(extracted_data or {})
        
        # Calculate risk priority
        risk_priority = CyberInsuranceValidator.calculate_risk_priority(extracted_data or {})
        
        # Assign underwriter based on business rules
        assigned_underwriter = None
        if validation_status == "Complete":
            assigned_underwriter = CyberInsuranceValidator.assign_underwriter(extracted_data or {})
        
        # Generate initial risk assessment
        risk_categories = CyberInsuranceValidator.generate_risk_categories(extracted_data or {})
        overall_risk_score = sum(risk_categories.values()) / len(risk_categories)
        
        # Extract cyber insurance specific data from LLM results
        if extracted_data and isinstance(extracted_data, dict):
            work_item.industry = extracted_data.get('industry')
            work_item.policy_type = extracted_data.get('policy_type') or extracted_data.get('coverage_type')
            
            # Use business rules parser for coverage amount
            work_item.coverage_amount = CyberInsuranceValidator._parse_coverage_amount(
                extracted_data.get('coverage_amount') or extracted_data.get('policy_limit') or ''
            )
            
            # Set company size if available
            company_size = extracted_data.get('company_size')
            if company_size:
                try:
                    work_item.company_size = CompanySize(company_size)
                except ValueError:
                    # Try mapping common variations
                    size_mapping = {
                        'small': CompanySize.SMALL,
                        'medium': CompanySize.MEDIUM,
                        'large': CompanySize.LARGE,
                        'enterprise': CompanySize.ENTERPRISE,
                        'startup': CompanySize.SMALL,
                        'sme': CompanySize.MEDIUM,
                        'multinational': CompanySize.ENTERPRISE
                    }
                    work_item.company_size = size_mapping.get(company_size.lower())
        
        # Apply validation results to work item
        if validation_status == "Complete":
            work_item.status = WorkItemStatus.PENDING
        elif validation_status == "Incomplete":
            work_item.status = WorkItemStatus.PENDING
            work_item.description += f"\n\nMissing fields: {', '.join(missing_fields)}"
        elif validation_status == "Rejected":
            work_item.status = WorkItemStatus.REJECTED
            work_item.description += f"\n\nRejection reason: {rejection_reason}"
        
        # Set priority based on risk calculation
        try:
            work_item.priority = WorkItemPriority(risk_priority)
        except ValueError:
            work_item.priority = WorkItemPriority.MEDIUM
        
        # Set assigned underwriter
        work_item.assigned_to = assigned_underwriter
        
        # Set risk data
        work_item.risk_score = overall_risk_score
        work_item.risk_categories = risk_categories
        
        db.add(work_item)
        db.flush()  # Get ID before commit
        
        # Create initial risk assessment if we have risk data
        if risk_categories and overall_risk_score > 0:
            risk_assessment = RiskAssessment(
                work_item_id=work_item.id,
                overall_score=overall_risk_score,
                risk_categories=risk_categories,
                assessment_date=datetime.utcnow(),
                assessed_by="System",
                assessment_notes=f"Initial automated assessment based on submission data. Validation status: {validation_status}"
            )
            db.add(risk_assessment)
        
        # Create history entry for validation results
        history_entry = WorkItemHistory(
            work_item_id=work_item.id,
            action="created",
            changed_by="System",
            timestamp=datetime.utcnow(),
            details={
                "validation_status": validation_status,
                "missing_fields": missing_fields,
                "rejection_reason": rejection_reason,
                "risk_priority": risk_priority,
                "assigned_underwriter": assigned_underwriter
            }
        )
        db.add(history_entry)
        
        db.commit()
        db.refresh(work_item)
        
        logger.info("Submission and work item created", 
                   submission_id=submission.submission_id, 
                   work_item_id=work_item.id,
                   submission_ref=submission_ref,
                   validation_status=validation_status,
                   risk_priority=risk_priority)
        
        # Broadcast new work item to all connected WebSocket clients with enhanced data
        await broadcast_new_workitem(work_item, submission, {
            "validation_status": validation_status,
            "risk_score": overall_risk_score,
            "assigned_underwriter": assigned_underwriter
        })
        
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





@app.post("/api/submissions/confirm/{submission_ref}", response_model=SubmissionConfirmResponse)
async def confirm_submission(
    submission_ref: str,
    request: SubmissionConfirmRequest,
    db: Session = Depends(get_db)
):
    """
    Confirm a submission and assign to underwriter - Updates existing work item instead of creating duplicate
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
        
        # Find existing work item for this submission (should already exist from email_intake)
        work_item = db.query(WorkItem).filter(WorkItem.submission_id == submission.id).first()
        
        if work_item:
            # Update existing work item
            work_item.assigned_to = assigned_underwriter
            work_item.status = WorkItemStatus.IN_REVIEW
            work_item.updated_at = datetime.utcnow()
            logger.info("Updated existing work item", work_item_id=work_item.id, assigned_to=assigned_underwriter)
        else:
            # Create work item only if none exists (fallback scenario)
            work_item = WorkItem(
                submission_id=submission.id,
                title=submission.subject or "Confirmed Submission",
                description=f"Email from {submission.sender_email}",
                assigned_to=assigned_underwriter,
                status=WorkItemStatus.IN_REVIEW,
                priority=WorkItemPriority.MEDIUM
            )
            db.add(work_item)
            logger.info("Created new work item (fallback)", assigned_to=assigned_underwriter)
        
        db.commit()
        db.refresh(work_item)
        
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


def get_or_create_work_item(submission_id: int, db: Session) -> WorkItem:
    """
    Get existing work item for submission or create one if none exists
    Prevents duplicate work item creation
    """
    # Check if work item already exists
    existing_work_item = db.query(WorkItem).filter(WorkItem.submission_id == submission_id).first()
    
    if existing_work_item:
        return existing_work_item
    
    # If no work item exists, this is likely an edge case
    # Log it and return None to let calling code handle appropriately
    logger.warning(f"No work item found for submission_id {submission_id}")
    return None


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


@app.put("/api/work-items/{work_item_id}/status")
async def update_work_item_status(
    work_item_id: int,
    status_update: dict,
    db: Session = Depends(get_db)
):
    """Update work item status with business rule validation"""
    from business_rules import WorkflowEngine, MessageService
    
    try:
        # Get the work item
        work_item = db.query(WorkItem).filter(WorkItem.id == work_item_id).first()
        if not work_item:
            raise HTTPException(status_code=404, detail="Work item not found")
        
        current_status = work_item.status
        new_status = status_update.get("status")
        changed_by = status_update.get("changed_by", "System")
        notes = status_update.get("notes", "")
        
        # Validate status transition using WorkflowEngine
        is_valid, message = WorkflowEngine.validate_status_transition(current_status, new_status)
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid status transition: {message}")
        
        # Update the work item
        old_status = work_item.status
        work_item.status = WorkItemStatus(new_status)
        work_item.updated_at = datetime.utcnow()
        
        # Add history entry
        history_entry = WorkItemHistory(
            work_item_id=work_item.id,
            action=f"status_changed_from_{old_status}_to_{new_status}",
            changed_by=changed_by,
            timestamp=datetime.utcnow(),
            details={
                "old_status": old_status,
                "new_status": new_status,
                "notes": notes
            }
        )
        db.add(history_entry)
        
        # Handle special status transitions
        if new_status == "assigned" and work_item.assigned_to:
            # Send notification to underwriter
            MessageService.send_assignment_notification(work_item.assigned_to, work_item)
        elif new_status == "rejected":
            # Send rejection notification to broker
            submission = db.query(Submission).filter(Submission.submission_id == work_item.submission_id).first()
            if submission:
                MessageService.send_rejection_notification(submission.sender_email, work_item, notes)
        
        db.commit()
        db.refresh(work_item)
        
        # Broadcast status update
        await websocket_manager.broadcast_message({
            "type": "work_item_status_update",
            "data": {
                "id": work_item.id,
                "old_status": old_status,
                "new_status": new_status,
                "changed_by": changed_by,
                "timestamp": datetime.utcnow().isoformat()
            }
        })
        
        return {
            "message": "Status updated successfully",
            "work_item_id": work_item.id,
            "old_status": old_status,
            "new_status": new_status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating work item status", work_item_id=work_item_id, error=str(e))
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")







@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# ===== Polling-based updates for Vercel compatibility =====

@app.get("/api/workitems/poll", response_model=EnhancedPollingResponse)
async def poll_workitems(
    since: str = None,
    limit: int = 50,
    search: str = None,
    priority: str = None,
    status: str = None,
    assigned_to: str = None,
    include_details: bool = False,
    work_item_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Enhanced polling for work items with filtering support and optional detailed data.
    Now includes risk assessment and history data when include_details=true or work_item_id specified.
    
    Args:
        since: ISO timestamp to filter items created after this time
        limit: Maximum number of items to return (default 50, max 100)
        search: Search term to filter across title, description, industry
        priority: Filter by priority (Low, Moderate, Medium, High, Critical)
        status: Filter by status (Pending, In Review, Approved, Rejected)
        assigned_to: Filter by assigned underwriter
        include_details: Include risk assessment and history data
        work_item_id: Get details for specific work item (replaces separate endpoints)
    """
    try:
        # Limit max items to prevent large responses
        limit = min(limit, 100)
        
        # Query work items with their related submission data
        query = db.query(WorkItem, Submission).join(
            Submission, WorkItem.submission_id == Submission.id
        ).order_by(WorkItem.created_at.desc())
        
        # Filter by timestamp if provided
        if since:
            try:
                since_dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
                query = query.filter(WorkItem.created_at > since_dt)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid 'since' timestamp format. Use ISO format (e.g., 2025-09-28T10:00:00Z)"
                )
        
        # Apply filters
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    WorkItem.title.ilike(search_filter),
                    WorkItem.description.ilike(search_filter),
                    WorkItem.industry.ilike(search_filter),
                    Submission.subject.ilike(search_filter),
                    Submission.sender_email.ilike(search_filter)
                )
            )
        
        if priority:
            try:
                priority_enum = WorkItemPriorityEnum(priority)
                query = query.filter(WorkItem.priority == priority_enum.value)
            except ValueError:
                pass  # Invalid priority, ignore filter
        
        if status:
            try:
                status_enum = WorkItemStatusEnum(status)
                query = query.filter(WorkItem.status == status_enum.value)
            except ValueError:
                pass  # Invalid status, ignore filter
        
        if assigned_to:
            query = query.filter(WorkItem.assigned_to.ilike(f"%{assigned_to}%"))
        
        results = query.limit(limit).all()
        
        # If specific work item requested, return detailed data
        if work_item_id:
            work_item_detail = db.query(WorkItem, Submission).join(
                Submission, WorkItem.submission_id == Submission.id
            ).filter(WorkItem.id == work_item_id).first()
            
            if not work_item_detail:
                raise HTTPException(status_code=404, detail="Work item not found")
            
            work_item, submission = work_item_detail
            
            # Get risk assessment
            risk_assessment = db.query(RiskAssessment).filter(
                RiskAssessment.work_item_id == work_item_id
            ).order_by(RiskAssessment.assessment_date.desc()).first()
            
            # Get history
            history = db.query(WorkItemHistory).filter(
                WorkItemHistory.work_item_id == work_item_id
            ).order_by(WorkItemHistory.timestamp.desc()).limit(10).all()
            
            return {
                "work_item": {
                    "id": work_item.id,
                    "submission_id": work_item.submission_id,
                    "submission_ref": str(submission.submission_ref),
                    "title": work_item.title or submission.subject,
                    "description": work_item.description,
                    "status": work_item.status.value if work_item.status else "Pending",
                    "priority": work_item.priority.value if work_item.priority else "Medium",
                    "assigned_to": work_item.assigned_to,
                    "risk_score": work_item.risk_score,
                    "risk_categories": work_item.risk_categories,
                    "industry": work_item.industry,
                    "policy_type": work_item.policy_type,
                    "coverage_amount": work_item.coverage_amount,
                    "created_at": work_item.created_at.isoformat() + "Z",
                    "updated_at": work_item.updated_at.isoformat() + "Z"
                },
                "risk_assessment": {
                    "overall_score": risk_assessment.overall_risk_score if risk_assessment else work_item.risk_score,
                    "risk_categories": risk_assessment.risk_categories if risk_assessment else work_item.risk_categories,
                    "assessed_by": risk_assessment.assessed_by if risk_assessment else "System",
                    "assessment_date": risk_assessment.created_at.isoformat() + "Z" if risk_assessment else None
                } if risk_assessment or work_item.risk_score else None,
                "history": [
                    {
                        "id": h.id,
                        "action": h.action.value if hasattr(h.action, 'value') else str(h.action),
                        "performed_by": h.performed_by,
                        "timestamp": h.timestamp.isoformat() + "Z",
                        "details": h.details
                    } for h in history
                ],
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }

        # Format response with enhanced data structure
        items = []
        for work_item, submission in results:
            # Count comments for this work item
            comments_count = db.query(Comment).filter(Comment.work_item_id == work_item.id).count()
            has_urgent_comments = db.query(Comment).filter(
                Comment.work_item_id == work_item.id,
                Comment.is_urgent == True
            ).first() is not None
            
            # Parse risk categories if available
            risk_categories = None
            if work_item.risk_categories:
                try:
                    risk_categories = RiskCategories(**work_item.risk_categories)
                except Exception:
                    risk_categories = None
            
            item_data = WorkItemSummary(
                id=work_item.id,
                submission_id=work_item.submission_id,
                submission_ref=str(submission.submission_ref),
                title=work_item.title or submission.subject or "No title",
                description=work_item.description,
                status=WorkItemStatusEnum(work_item.status.value) if work_item.status else WorkItemStatusEnum.PENDING,
                priority=WorkItemPriorityEnum(work_item.priority.value) if work_item.priority else WorkItemPriorityEnum.MEDIUM,
                assigned_to=work_item.assigned_to,
                risk_score=work_item.risk_score,
                risk_categories=risk_categories,
                industry=work_item.industry,
                company_size=CompanySizeEnum(work_item.company_size.value) if work_item.company_size else None,
                policy_type=work_item.policy_type,
                coverage_amount=work_item.coverage_amount,
                last_risk_assessment=work_item.last_risk_assessment,
                created_at=work_item.created_at,
                updated_at=work_item.updated_at,
                comments_count=comments_count,
                has_urgent_comments=has_urgent_comments
            )
            
            # Include detailed data if requested
            if include_details:
                # Get risk assessment for this item
                risk_assessment = db.query(RiskAssessment).filter(
                    RiskAssessment.work_item_id == work_item.id
                ).order_by(RiskAssessment.assessment_date.desc()).first()
                
                # Add risk assessment data to item
                if risk_assessment:
                    item_data.__dict__['risk_assessment'] = {
                        "overall_score": risk_assessment.overall_risk_score,
                        "assessed_by": risk_assessment.assessed_by,
                        "assessment_date": risk_assessment.created_at.isoformat() + "Z"
                    }
            
            items.append(item_data)
        
        return EnhancedPollingResponse(
            items=items,
            count=len(items),
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error polling work items", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error polling work items: {str(e)}"
        )





# ===== Frontend Integration API Endpoints =====

@app.put("/api/submissions/{submission_id}")
async def update_submission(
    submission_id: int,
    updates: dict,
    db: Session = Depends(get_db)
):
    """Update submission fields (for inline editing) - Also updates related work item"""
    
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Update allowed fields
    allowed_fields = ['subject', 'sender_email', 'assigned_to', 'task_status']
    
    for field, value in updates.items():
        if field in allowed_fields and hasattr(submission, field):
            setattr(submission, field, value)
    
    # Also update related work item if exists
    work_item = db.query(WorkItem).filter(WorkItem.submission_id == submission.id).first()
    if work_item:
        if 'assigned_to' in updates:
            work_item.assigned_to = updates['assigned_to']
        if 'subject' in updates:
            work_item.title = updates['subject']
        work_item.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(submission)
    
    return {
        "message": f"Submission {submission_id} updated successfully",
        "updated_fields": list(updates.keys())
    }


@app.put("/api/workitems/{workitem_id}")
async def update_workitem(
    workitem_id: int,
    updates: dict,
    db: Session = Depends(get_db)
):
    """Update work item fields (for inline editing)"""
    
    work_item = db.query(WorkItem).filter(WorkItem.id == workitem_id).first()
    if not work_item:
        raise HTTPException(status_code=404, detail="Work item not found")
    
    # Update allowed fields
    allowed_fields = ['title', 'description', 'status', 'priority', 'assigned_to', 'industry', 'policy_type', 'coverage_amount']
    
    for field, value in updates.items():
        if field in allowed_fields and hasattr(work_item, field):
            # Handle enum fields
            if field == 'status' and value:
                try:
                    setattr(work_item, field, WorkItemStatus(value))
                except ValueError:
                    continue
            elif field == 'priority' and value:
                try:
                    setattr(work_item, field, WorkItemPriority(value))
                except ValueError:
                    continue
            else:
                setattr(work_item, field, value)
    
    work_item.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(work_item)
    
    return {
        "message": f"Work item {workitem_id} updated successfully",
        "updated_fields": list(updates.keys())
    }


@app.post("/api/workitems/{workitem_id}/assign")
async def assign_workitem(
    workitem_id: int,
    assignment_data: dict,
    db: Session = Depends(get_db)
):
    """Assign work item to underwriter and create submission"""
    
    underwriter = assignment_data.get('underwriter')
    if not underwriter:
        raise HTTPException(status_code=400, detail="Underwriter is required")
    
    # Get the work item
    work_item = db.query(WorkItem).filter(WorkItem.id == workitem_id).first()
    if not work_item:
        raise HTTPException(status_code=404, detail="Work item not found")
    
    # Get related submission
    submission = db.query(Submission).filter(Submission.id == work_item.submission_id).first()
    if not submission:
        raise HTTPException(status_code=404, detail="Related submission not found")
    
    # Update assignment
    work_item.assigned_to = underwriter
    work_item.status = WorkItemStatus.IN_REVIEW
    work_item.updated_at = datetime.utcnow()
    
    submission.assigned_to = underwriter
    submission.task_status = "assigned"
    
    # Create assignment notification message
    message = SubmissionMessage(
        submission_id=submission.id,
        message_type="assignment_notification",
        sender="system",
        recipient=underwriter,
        subject=f"New Assignment - Work Item #{workitem_id}",
        message=f"You have been assigned work item #{workitem_id} for {submission.subject}",
        is_read=False
    )
    
    db.add(message)
    db.commit()
    
    return {
        "message": f"Work item {workitem_id} assigned to {underwriter}",
        "submission_id": submission.submission_id,
        "assigned_to": underwriter,
        "status": "Assigned"
    }


@app.get("/api/underwriters")
async def list_underwriters(db: Session = Depends(get_db)):
    """Get list of available underwriters"""
    
    underwriters = db.query(Underwriter).filter(Underwriter.is_active == True).all()
    
    return {
        "underwriters": [
            {
                "id": uw.id,
                "name": uw.name,
                "email": uw.email,
                "specializations": uw.specializations or [],
                "max_coverage_limit": uw.max_coverage_limit,
                "workload": uw.current_workload or 0
            }
            for uw in underwriters
        ]
    }


@app.get("/api/refresh-data")
async def refresh_data(db: Session = Depends(get_db)):
    """Endpoint for frontend refresh functionality"""
    
    # Get fresh counts and summary data
    total_submissions = db.query(Submission).count()
    pending_workitems = db.query(WorkItem).filter(WorkItem.status.in_([WorkItemStatus.PENDING, WorkItemStatus.IN_REVIEW])).count()
    new_workitems = db.query(WorkItem).filter(WorkItem.status == WorkItemStatus.PENDING).count()
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "summary": {
            "total_submissions": total_submissions,
            "pending_submissions": pending_workitems,
            "new_submissions": new_workitems
        },
        "message": "Data refreshed successfully"
    }


@app.post("/api/cleanup-duplicates")
async def cleanup_duplicate_work_items(db: Session = Depends(get_db)):
    """Cleanup duplicate work items - keeps the most recent one per submission"""
    try:
        # Find submissions with multiple work items
        from sqlalchemy import func
        
        duplicates = db.query(WorkItem.submission_id, func.count(WorkItem.id).label('count')).group_by(WorkItem.submission_id).having(func.count(WorkItem.id) > 1).all()
        
        removed_count = 0
        for submission_id, count in duplicates:
            # Get all work items for this submission, ordered by creation date (keep newest)
            work_items = db.query(WorkItem).filter(WorkItem.submission_id == submission_id).order_by(WorkItem.created_at.desc()).all()
            
            # Remove all except the first (most recent)
            for work_item in work_items[1:]:
                db.delete(work_item)
                removed_count += 1
        
        db.commit()
        
        return {
            "message": f"Cleanup completed. Removed {removed_count} duplicate work items.",
            "duplicates_found": len(duplicates),
            "items_removed": removed_count
        }
        
    except Exception as e:
        logger.error("Error during cleanup", error=str(e))
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")


@app.get("/api/debug/duplicates")
async def debug_duplicate_work_items(db: Session = Depends(get_db)):
    """Debug endpoint to identify duplicate work items"""
    from sqlalchemy import func
    
    # Find submissions with multiple work items
    duplicates = db.query(
        WorkItem.submission_id, 
        func.count(WorkItem.id).label('work_item_count'),
        func.array_agg(WorkItem.id).label('work_item_ids')
    ).group_by(WorkItem.submission_id).having(func.count(WorkItem.id) > 1).all()
    
    total_work_items = db.query(WorkItem).count()
    total_submissions = db.query(Submission).count()
    
    duplicate_details = []
    for submission_id, count, work_item_ids in duplicates:
        submission = db.query(Submission).filter(Submission.id == submission_id).first()
        duplicate_details.append({
            "submission_id": submission_id,
            "submission_ref": str(submission.submission_ref) if submission else "Unknown",
            "work_item_count": count,
            "work_item_ids": work_item_ids
        })
    
    return {
        "total_work_items": total_work_items,
        "total_submissions": total_submissions,
        "submissions_with_duplicates": len(duplicates),
        "duplicate_details": duplicate_details,
        "expected_work_items": total_submissions,
        "excess_work_items": total_work_items - total_submissions
    }


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





async def broadcast_new_workitem(work_item: WorkItem, submission: Submission, business_data: dict = None):
    """Broadcast a new work item to all connected WebSocket clients"""
    try:
        # Parse risk categories if available
        risk_categories = None
        if work_item.risk_categories:
            try:
                risk_categories = work_item.risk_categories
            except Exception:
                pass
        
        workitem_data = {
            "id": work_item.id,
            "submission_id": work_item.submission_id,
            "submission_ref": str(submission.submission_ref),
            "title": work_item.title or submission.subject or "No title",
            "description": work_item.description,
            "status": work_item.status.value if work_item.status else "Pending",
            "priority": work_item.priority.value if work_item.priority else "Medium",
            "assigned_to": work_item.assigned_to,
            "risk_score": work_item.risk_score,
            "risk_categories": risk_categories,
            "industry": work_item.industry,
            "company_size": work_item.company_size.value if work_item.company_size else None,
            "policy_type": work_item.policy_type,
            "coverage_amount": work_item.coverage_amount,
            "created_at": work_item.created_at.isoformat() + "Z" if work_item.created_at else None,
            "updated_at": work_item.updated_at.isoformat() + "Z" if work_item.updated_at else None,
            "comments_count": 0,
            "has_urgent_comments": False,
            # Include submission data for backward compatibility
            "subject": submission.subject or "No subject",
            "from_email": submission.sender_email or "Unknown sender",
            "extracted_fields": submission.extracted_fields or {}
        }
        
        # Add business validation data if provided
        if business_data:
            workitem_data.update({
                "validation_status": business_data.get("validation_status"),
                "business_risk_score": business_data.get("risk_score"),
                "assigned_underwriter": business_data.get("assigned_underwriter")
            })
        
        await websocket_manager.broadcast_workitem(workitem_data)
        logger.info(f"Broadcasted new work item: {work_item.id} (submission: {submission.submission_id})")
        
    except Exception as e:
        logger.error(f"Error broadcasting work item: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
