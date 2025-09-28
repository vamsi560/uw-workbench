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

from database import get_db, Submission, WorkItem, RiskAssessment, Comment, User, WorkItemHistory, WorkItemStatus, WorkItemPriority, CompanySize, create_tables
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

@app.get("/api/work-items/{work_item_id}/risk-assessment")
async def get_risk_assessment(work_item_id: int, db: Session = Depends(get_db)):
    """Get risk assessment for a work item"""
    try:
        work_item = db.query(WorkItem).filter(WorkItem.id == work_item_id).first()
        if not work_item:
            raise HTTPException(status_code=404, detail="Work item not found")
        
        # Get latest risk assessment
        risk_assessment = db.query(RiskAssessment).filter(
            RiskAssessment.work_item_id == work_item_id
        ).order_by(RiskAssessment.assessment_date.desc()).first()
        
        if not risk_assessment:
            return {"message": "No risk assessment found", "work_item_id": work_item_id}
        
        return {
            "work_item_id": work_item_id,
            "assessment_id": risk_assessment.id,
            "overall_score": risk_assessment.overall_score,
            "risk_categories": risk_assessment.risk_categories,
            "assessment_date": risk_assessment.assessment_date.isoformat(),
            "assessed_by": risk_assessment.assessed_by,
            "assessment_notes": risk_assessment.assessment_notes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting risk assessment", work_item_id=work_item_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/validate-submission")
async def validate_submission_data(
    validation_request: dict,
    db: Session = Depends(get_db)
):
    """Validate submission data using business rules without creating work item"""
    from business_rules import CyberInsuranceValidator
    
    try:
        extracted_data = validation_request.get("extracted_data", {})
        
        # Run validation
        validation_status, missing_fields, rejection_reason = CyberInsuranceValidator.validate_submission(extracted_data)
        
        # Calculate risk priority
        risk_priority = CyberInsuranceValidator.calculate_risk_priority(extracted_data)
        
        # Generate risk categories
        risk_categories = CyberInsuranceValidator.generate_risk_categories(extracted_data)
        
        # Assign underwriter if complete
        assigned_underwriter = None
        if validation_status == "Complete":
            assigned_underwriter = CyberInsuranceValidator.assign_underwriter(extracted_data)
        
        return {
            "validation_status": validation_status,
            "missing_fields": missing_fields,
            "rejection_reason": rejection_reason,
            "risk_priority": risk_priority,
            "risk_categories": risk_categories,
            "assigned_underwriter": assigned_underwriter,
            "overall_risk_score": sum(risk_categories.values()) / len(risk_categories) if risk_categories else 0
        }
        
    except Exception as e:
        logger.error("Error validating submission data", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/work-items/{work_item_id}/history")
async def get_work_item_history(work_item_id: int, db: Session = Depends(get_db)):
    """Get history for a work item"""
    try:
        work_item = db.query(WorkItem).filter(WorkItem.id == work_item_id).first()
        if not work_item:
            raise HTTPException(status_code=404, detail="Work item not found")
        
        history = db.query(WorkItemHistory).filter(
            WorkItemHistory.work_item_id == work_item_id
        ).order_by(WorkItemHistory.timestamp.desc()).all()
        
        return {
            "work_item_id": work_item_id,
            "history": [
                {
                    "id": h.id,
                    "action": h.action,
                    "changed_by": h.changed_by,
                    "timestamp": h.timestamp.isoformat(),
                    "details": h.details
                } for h in history
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting work item history", work_item_id=work_item_id, error=str(e))
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
    db: Session = Depends(get_db)
):
    """
    Enhanced polling for work items with filtering support.
    
    Args:
        since: ISO timestamp to filter items created after this time
        limit: Maximum number of items to return (default 50, max 100)
        search: Search term to filter across title, description, industry
        priority: Filter by priority (Low, Moderate, Medium, High, Critical)
        status: Filter by status (Pending, In Review, Approved, Rejected)
        assigned_to: Filter by assigned underwriter
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


@app.get("/api/workitems", response_model=WorkItemListResponse)
async def get_work_items(
    search: str = None,
    priority: str = None,
    status: str = None,
    assigned_to: str = None,
    industry: str = None,
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get work items with comprehensive filtering, search, and pagination.
    This is the main endpoint for the frontend data table.
    """
    try:
        # Validate pagination
        page = max(1, page)
        limit = min(max(1, limit), 100)
        offset = (page - 1) * limit
        
        # Base query with submission data
        query = db.query(WorkItem, Submission).join(
            Submission, WorkItem.submission_id == Submission.id
        )
        
        # Apply filters (same logic as polling endpoint)
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
                pass
        
        if status:
            try:
                status_enum = WorkItemStatusEnum(status)
                query = query.filter(WorkItem.status == status_enum.value)
            except ValueError:
                pass
        
        if assigned_to:
            query = query.filter(WorkItem.assigned_to.ilike(f"%{assigned_to}%"))
        
        if industry:
            query = query.filter(WorkItem.industry.ilike(f"%{industry}%"))
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply pagination and ordering
        results = query.order_by(WorkItem.created_at.desc()).offset(offset).limit(limit).all()
        
        # Format response
        work_items = []
        for work_item, submission in results:
            # Count comments
            comments_count = db.query(Comment).filter(Comment.work_item_id == work_item.id).count()
            has_urgent_comments = db.query(Comment).filter(
                Comment.work_item_id == work_item.id,
                Comment.is_urgent == True
            ).first() is not None
            
            # Parse risk categories
            risk_categories = None
            if work_item.risk_categories:
                try:
                    risk_categories = RiskCategories(**work_item.risk_categories)
                except Exception:
                    pass
            
            work_item_summary = WorkItemSummary(
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
            
            work_items.append(work_item_summary)
        
        # Calculate pagination info
        total_pages = (total_count + limit - 1) // limit
        
        return WorkItemListResponse(
            work_items=work_items,
            total=total_count,
            pagination={
                "page": page,
                "limit": limit,
                "total_pages": total_pages,
                "total_items": total_count
            }
        )
        
    except Exception as e:
        logger.error("Error fetching work items", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching work items: {str(e)}"
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
            subject="Test Cyber Insurance Policy Submission",
            sender_email="test@techcorp.com",
            body_text="This is a test work item created for testing the enhanced workbench features.",
            extracted_fields={
                "insured_name": "TechCorp Inc",
                "policy_type": "Cyber Liability",
                "coverage_amount": "5000000",
                "industry": "Technology",
                "company_size": "Medium",
                "effective_date": "2025-01-01",
                "broker": "Cyber Insurance Specialists"
            },
            task_status="pending"
        )
        
        db.add(test_submission)
        db.commit()
        db.refresh(test_submission)
        
        # Create corresponding work item
        test_work_item = WorkItem(
            submission_id=test_submission.id,
            title="Cyber Insurance Application - TechCorp Inc",
            description="Technology company seeking comprehensive cyber liability coverage",
            status=WorkItemStatus.PENDING,
            priority=WorkItemPriority.HIGH,
            industry="Technology",
            company_size=CompanySize.MEDIUM,
            policy_type="Cyber Liability",
            coverage_amount=5000000.0,
            risk_score=75.5,
            risk_categories={
                "technical": 80.0,
                "operational": 65.0,
                "financial": 70.0,
                "compliance": 85.0
            }
        )
        
        db.add(test_work_item)
        db.commit()
        db.refresh(test_work_item)
        
        # Broadcast the test work item (WebSocket)
        await broadcast_new_workitem(test_work_item, test_submission)
        
        return {
            "message": "Test work item created and broadcasted",
            "submission_id": test_submission.submission_id,
            "work_item_id": test_work_item.id,
            "submission_ref": str(submission_ref),
            "websocket_connections": websocket_manager.get_connection_count()
        }
        
    except Exception as e:
        logger.error(f"Error creating test work item: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating test work item: {str(e)}"
        )


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
