"""
Dashboard API endpoints for displaying Guidewire data in UI
Provides comprehensive data access for dashboard widgets and displays
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta

from database import get_db, WorkItem, GuidewireResponse, Submission
from models import (
    GuidewireResponseData, GuidewireSubmissionSummary, 
    GuidewireAccountInfo, GuidewireJobInfo, GuidewirePricingInfo,
    GuidewireCoverageInfo, GuidewireBusinessData
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/guidewire", tags=["guidewire-dashboard"])


@router.get("/work-item/{work_item_id}/data", response_model=GuidewireResponseData)
async def get_guidewire_data_for_work_item(
    work_item_id: int,
    db: Session = Depends(get_db)
):
    """Get comprehensive Guidewire data for a specific work item"""
    
    # Get the Guidewire response data
    guidewire_data = db.query(GuidewireResponse).filter(
        GuidewireResponse.work_item_id == work_item_id
    ).first()
    
    if not guidewire_data:
        raise HTTPException(
            status_code=404, 
            detail=f"No Guidewire data found for work item {work_item_id}"
        )
    
    # Convert to response model
    return _convert_to_response_model(guidewire_data)


@router.get("/summary", response_model=List[GuidewireSubmissionSummary])
async def get_guidewire_submissions_summary(
    limit: int = Query(50, description="Maximum number of records to return"),
    offset: int = Query(0, description="Number of records to skip"),
    status_filter: Optional[str] = Query(None, description="Filter by job status"),
    db: Session = Depends(get_db)
):
    """Get summary of all Guidewire submissions for dashboard display"""
    
    query = db.query(GuidewireResponse).join(WorkItem)
    
    # Apply status filter if provided
    if status_filter:
        query = query.filter(GuidewireResponse.job_status == status_filter)
    
    # Order by most recent first
    query = query.order_by(GuidewireResponse.created_at.desc())
    
    # Apply pagination
    guidewire_data = query.offset(offset).limit(limit).all()
    
    # Convert to summary models
    summaries = []
    for data in guidewire_data:
        summaries.append(GuidewireSubmissionSummary(
            work_item_id=data.work_item_id,
            account_number=data.account_number,
            job_number=data.job_number,
            organization_name=data.organization_name,
            job_status=data.job_status,
            policy_type=data.policy_type,
            total_cost_amount=data.total_cost_amount,
            total_cost_currency=data.total_cost_currency,
            job_effective_date=data.job_effective_date,
            submission_success=data.submission_success,
            quote_generated=data.quote_generated,
            created_at=data.created_at
        ))
    
    return summaries


@router.get("/dashboard/stats")
async def get_guidewire_dashboard_stats(db: Session = Depends(get_db)):
    """Get statistical data for Guidewire dashboard widgets"""
    
    # Get total submissions
    total_submissions = db.query(GuidewireResponse).count()
    
    # Get successful submissions
    successful_submissions = db.query(GuidewireResponse).filter(
        GuidewireResponse.submission_success == True
    ).count()
    
    # Get quotes generated
    quotes_generated = db.query(GuidewireResponse).filter(
        GuidewireResponse.quote_generated == True
    ).count()
    
    # Get submissions by status
    status_counts = db.query(
        GuidewireResponse.job_status,
        db.func.count(GuidewireResponse.id).label('count')
    ).group_by(GuidewireResponse.job_status).all()
    
    # Get recent submissions (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_submissions = db.query(GuidewireResponse).filter(
        GuidewireResponse.created_at >= thirty_days_ago
    ).count()
    
    # Calculate average premium amount
    avg_premium = db.query(
        db.func.avg(GuidewireResponse.total_premium_amount)
    ).filter(
        GuidewireResponse.total_premium_amount.isnot(None)
    ).scalar()
    
    # Get policy type distribution
    policy_types = db.query(
        GuidewireResponse.policy_type,
        db.func.count(GuidewireResponse.id).label('count')
    ).group_by(GuidewireResponse.policy_type).all()
    
    return {
        "total_submissions": total_submissions,
        "successful_submissions": successful_submissions,
        "quotes_generated": quotes_generated,
        "success_rate": (successful_submissions / total_submissions * 100) if total_submissions > 0 else 0,
        "quote_rate": (quotes_generated / total_submissions * 100) if total_submissions > 0 else 0,
        "recent_submissions_30d": recent_submissions,
        "average_premium": float(avg_premium) if avg_premium else 0,
        "status_distribution": [
            {"status": status, "count": count} for status, count in status_counts
        ],
        "policy_type_distribution": [
            {"policy_type": policy_type, "count": count} for policy_type, count in policy_types
        ]
    }


@router.get("/dashboard/pricing-trends")
async def get_pricing_trends(
    days: int = Query(30, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Get pricing trends for dashboard charts"""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get daily pricing data
    daily_pricing = db.query(
        db.func.date(GuidewireResponse.created_at).label('date'),
        db.func.avg(GuidewireResponse.total_premium_amount).label('avg_premium'),
        db.func.count(GuidewireResponse.id).label('quote_count')
    ).filter(
        GuidewireResponse.created_at >= start_date,
        GuidewireResponse.total_premium_amount.isnot(None)
    ).group_by(
        db.func.date(GuidewireResponse.created_at)
    ).order_by('date').all()
    
    # Get coverage amount distribution
    coverage_distribution = db.query(
        db.case([
            (GuidewireResponse.total_premium_amount < 1000, "Under $1K"),
            (GuidewireResponse.total_premium_amount < 5000, "$1K - $5K"),
            (GuidewireResponse.total_premium_amount < 10000, "$5K - $10K"),
            (GuidewireResponse.total_premium_amount < 25000, "$10K - $25K"),
        ], else_="$25K+").label('range'),
        db.func.count(GuidewireResponse.id).label('count')
    ).filter(
        GuidewireResponse.total_premium_amount.isnot(None)
    ).group_by('range').all()
    
    return {
        "daily_trends": [
            {
                "date": str(date),
                "average_premium": float(avg_premium) if avg_premium else 0,
                "quote_count": quote_count
            }
            for date, avg_premium, quote_count in daily_pricing
        ],
        "coverage_distribution": [
            {"range": range_val, "count": count}
            for range_val, count in coverage_distribution
        ]
    }


@router.get("/account/{account_number}")
async def get_account_details(
    account_number: str,
    db: Session = Depends(get_db)
):
    """Get detailed account information from Guidewire"""
    
    guidewire_data = db.query(GuidewireResponse).filter(
        GuidewireResponse.account_number == account_number
    ).first()
    
    if not guidewire_data:
        raise HTTPException(
            status_code=404,
            detail=f"Account {account_number} not found in Guidewire data"
        )
    
    # Get all submissions for this account
    all_submissions = db.query(GuidewireResponse).filter(
        GuidewireResponse.account_number == account_number
    ).order_by(GuidewireResponse.created_at.desc()).all()
    
    return {
        "account_info": {
            "account_number": guidewire_data.account_number,
            "organization_name": guidewire_data.organization_name,
            "account_status": guidewire_data.account_status,
            "number_of_contacts": guidewire_data.number_of_contacts,
            "total_employees": guidewire_data.total_employees,
            "total_revenues": guidewire_data.total_revenues,
            "industry_type": guidewire_data.industry_type
        },
        "submissions": [
            {
                "job_number": sub.job_number,
                "job_status": sub.job_status,
                "policy_type": sub.policy_type,
                "total_premium": sub.total_premium_amount,
                "effective_date": sub.job_effective_date,
                "created_at": sub.created_at
            }
            for sub in all_submissions
        ],
        "total_submissions": len(all_submissions)
    }


def _convert_to_response_model(guidewire_data: GuidewireResponse) -> GuidewireResponseData:
    """Convert database model to response model"""
    
    return GuidewireResponseData(
        id=guidewire_data.id,
        work_item_id=guidewire_data.work_item_id,
        submission_id=guidewire_data.submission_id,
        
        account_info=GuidewireAccountInfo(
            guidewire_account_id=guidewire_data.guidewire_account_id,
            account_number=guidewire_data.account_number,
            account_status=guidewire_data.account_status,
            organization_name=guidewire_data.organization_name,
            number_of_contacts=guidewire_data.number_of_contacts
        ),
        
        job_info=GuidewireJobInfo(
            guidewire_job_id=guidewire_data.guidewire_job_id,
            job_number=guidewire_data.job_number,
            job_status=guidewire_data.job_status,
            job_effective_date=guidewire_data.job_effective_date,
            base_state=guidewire_data.base_state,
            policy_number=guidewire_data.policy_number,
            policy_type=guidewire_data.policy_type,
            underwriting_company=guidewire_data.underwriting_company,
            producer_code=guidewire_data.producer_code
        ),
        
        pricing_info=GuidewirePricingInfo(
            total_cost_amount=guidewire_data.total_cost_amount,
            total_cost_currency=guidewire_data.total_cost_currency,
            total_premium_amount=guidewire_data.total_premium_amount,
            total_premium_currency=guidewire_data.total_premium_currency,
            rate_as_of_date=guidewire_data.rate_as_of_date
        ),
        
        coverage_info=GuidewireCoverageInfo(
            coverage_terms=guidewire_data.coverage_terms,
            coverage_display_values=guidewire_data.coverage_display_values
        ),
        
        business_data=GuidewireBusinessData(
            business_started_date=guidewire_data.business_started_date,
            total_employees=guidewire_data.total_employees,
            total_revenues=guidewire_data.total_revenues,
            total_assets=guidewire_data.total_assets,
            total_liabilities=guidewire_data.total_liabilities,
            industry_type=guidewire_data.industry_type
        ),
        
        response_checksum=guidewire_data.response_checksum,
        submission_success=guidewire_data.submission_success,
        quote_generated=guidewire_data.quote_generated,
        api_links=guidewire_data.api_links,
        created_at=guidewire_data.created_at,
        updated_at=guidewire_data.updated_at
    )