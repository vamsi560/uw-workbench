"""
Dashboard API Endpoints for Underwriter Portal
Extends the main API with comprehensive dashboard functionality
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from database import get_db, WorkItem, User, Submission
from dashboard_models import (
    UnderwriterDashboard, DashboardRequest, WorkQueueRequest, AnalyticsRequest,
    DashboardTimeframe, SubmissionDetailView, PortfolioAnalyticsReport,
    CompanyProfile, CybersecurityPosture, FinancialHealth, PolicyDetails,
    CoverageLimits, CoverageComponents, QuoteInformation, PricingFactors,
    CompetitiveAnalysis, CommunicationSummary, ComplianceChecks,
    AssignmentRecommendation, UnderwriterWorkload, UnderwriterExpertise
)
from dashboard_service import DashboardService, RiskScoringService, RecommendationService
from portfolio_analytics import PortfolioAnalyticsService
from enhanced_risk_scoring import EnhancedRiskScoringEngine, RiskBenchmarkingService
from models import (
    WorkItemSummary, WorkItemDetail, UserDetail, UserRoleEnum,
    CompanySizeEnum, WorkItemStatusEnum, WorkItemPriorityEnum
)
from business_rules import CyberInsuranceValidator, MessageService
from business_config import BusinessConfig

# Create router for dashboard endpoints
dashboard_router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@dashboard_router.get("/underwriter/{underwriter_id}", response_model=UnderwriterDashboard)
async def get_underwriter_dashboard(
    underwriter_id: str,
    timeframe: DashboardTimeframe = DashboardTimeframe.WEEK,
    db: Session = Depends(get_db)
):
    """Get comprehensive dashboard data for an underwriter"""
    
    try:
        dashboard_service = DashboardService(db)
        dashboard = dashboard_service.get_underwriter_dashboard(underwriter_id, timeframe)
        return dashboard
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating dashboard: {str(e)}")

@dashboard_router.get("/work-queue/{underwriter_id}")
async def get_work_queue(
    underwriter_id: str,
    priority_filter: Optional[str] = Query(None),
    status_filter: Optional[List[str]] = Query(None),
    industry_filter: Optional[List[str]] = Query(None),
    risk_score_min: Optional[float] = Query(None, ge=0, le=100),
    risk_score_max: Optional[float] = Query(None, ge=0, le=100),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Get filtered work queue for underwriter"""
    
    try:
        dashboard_service = DashboardService(db)
        
        # Build work queue summary with filters
        work_queue = dashboard_service._get_work_queue_summary(underwriter_id)
        
        # Apply filters if provided
        if priority_filter or status_filter or industry_filter or risk_score_min or risk_score_max:
            work_queue = _apply_work_queue_filters(
                work_queue, priority_filter, status_filter, industry_filter,
                risk_score_min, risk_score_max, limit
            )
        
        return work_queue
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving work queue: {str(e)}")

@dashboard_router.get("/submission/{work_item_id}/detail", response_model=SubmissionDetailView)
async def get_submission_detail_view(
    work_item_id: int,
    db: Session = Depends(get_db)
):
    """Get comprehensive submission detail view for underwriter analysis"""
    
    try:
        # Get work item and submission
        work_item = db.query(WorkItem).filter(WorkItem.id == work_item_id).first()
        if not work_item:
            raise HTTPException(status_code=404, detail="Work item not found")
        
        submission = db.query(Submission).filter(Submission.id == work_item.submission_id).first()
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        # Parse extracted fields
        extracted_fields = submission.extracted_fields or {}
        
        # Build comprehensive view
        detail_view = await _build_submission_detail_view(work_item, submission, extracted_fields, db)
        
        return detail_view
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving submission details: {str(e)}")

@dashboard_router.get("/analytics/portfolio", response_model=PortfolioAnalyticsReport)
async def get_portfolio_analytics(
    underwriter_id: str,
    timeframe: DashboardTimeframe = DashboardTimeframe.MONTH,
    include_benchmarks: bool = True,
    include_trends: bool = True,
    db: Session = Depends(get_db)
):
    """Get comprehensive portfolio analytics report"""
    
    try:
        dashboard_service = DashboardService(db)
        
        # Generate portfolio analytics
        start_date, end_date = dashboard_service._get_timeframe_bounds(timeframe)
        portfolio_summary = dashboard_service._get_portfolio_summary(underwriter_id, start_date, end_date)
        kpis = dashboard_service._calculate_kpis(underwriter_id, start_date, end_date)
        
        # Build analytics report
        report = PortfolioAnalyticsReport(
            timeframe=timeframe,
            generated_at=datetime.utcnow(),
            key_metrics=[
                kpis.active_submissions,
                kpis.quotes_issued,
                kpis.portfolio_premium,
                kpis.risk_score_average
            ],
            time_series=[] if not include_trends else _generate_time_series_data(underwriter_id, timeframe, db),
            benchmarks=[] if not include_benchmarks else _generate_benchmark_data(underwriter_id, db),
            insights=_generate_portfolio_insights(portfolio_summary),
            recommendations=_generate_portfolio_recommendations(portfolio_summary)
        )
        
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating analytics report: {str(e)}")

@dashboard_router.post("/work-item/{work_item_id}/risk-assessment")
async def generate_risk_assessment(
    work_item_id: int,
    db: Session = Depends(get_db)
):
    """Generate or update risk assessment for work item"""
    
    try:
        # Get work item and submission
        work_item = db.query(WorkItem).filter(WorkItem.id == work_item_id).first()
        if not work_item:
            raise HTTPException(status_code=404, detail="Work item not found")
        
        submission = db.query(Submission).filter(Submission.id == work_item.submission_id).first()
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        extracted_fields = submission.extracted_fields or {}
        
        # Generate comprehensive risk assessment
        risk_service = RiskScoringService(db)
        risk_assessment = risk_service.calculate_comprehensive_risk_assessment(extracted_fields)
        
        # Update work item with risk score
        work_item.risk_score = risk_assessment.overall_score
        db.commit()
        
        return {
            "work_item_id": work_item_id,
            "risk_assessment": risk_assessment,
            "updated_at": datetime.utcnow()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating risk assessment: {str(e)}")

@dashboard_router.post("/work-item/{work_item_id}/recommendation")
async def generate_underwriting_recommendation(
    work_item_id: int,
    db: Session = Depends(get_db)
):
    """Generate automated underwriting recommendation"""
    
    try:
        # Get work item and submission
        work_item = db.query(WorkItem).filter(WorkItem.id == work_item_id).first()
        if not work_item:
            raise HTTPException(status_code=404, detail="Work item not found")
        
        submission = db.query(Submission).filter(Submission.id == work_item.submission_id).first()
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        extracted_fields = submission.extracted_fields or {}
        
        # Generate risk assessment if not available
        if not work_item.risk_score:
            risk_service = RiskScoringService(db)
            risk_assessment = risk_service.calculate_comprehensive_risk_assessment(extracted_fields)
            work_item.risk_score = risk_assessment.overall_score
            db.commit()
        else:
            risk_service = RiskScoringService(db)
            risk_assessment = risk_service.calculate_comprehensive_risk_assessment(extracted_fields)
        
        # Generate recommendation
        recommendation_service = RecommendationService(db)
        recommendation = recommendation_service.generate_automated_recommendation(
            work_item, risk_assessment, extracted_fields
        )
        
        return {
            "work_item_id": work_item_id,
            "recommendation": recommendation,
            "risk_assessment": risk_assessment,
            "generated_at": datetime.utcnow()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendation: {str(e)}")

@dashboard_router.get("/assignment/recommendations/{work_item_id}")
async def get_assignment_recommendations(
    work_item_id: int,
    db: Session = Depends(get_db)
):
    """Get underwriter assignment recommendations for work item"""
    
    try:
        # Get work item details
        work_item = db.query(WorkItem).filter(WorkItem.id == work_item_id).first()
        if not work_item:
            raise HTTPException(status_code=404, detail="Work item not found")
        
        submission = db.query(Submission).filter(Submission.id == work_item.submission_id).first()
        extracted_fields = submission.extracted_fields if submission else {}
        
        # Get available underwriters
        underwriters = db.query(User).filter(
            User.role.in_([UserRoleEnum.UNDERWRITER, UserRoleEnum.SENIOR_UNDERWRITER]),
            User.is_available == True
        ).all()
        
        # Generate recommendations
        recommendations = []
        for underwriter in underwriters:
            recommendation = _generate_assignment_recommendation(
                underwriter, work_item, extracted_fields, db
            )
            recommendations.append(recommendation)
        
        # Sort by recommendation score
        recommendations.sort(key=lambda x: x.recommendation_score, reverse=True)
        
        return {
            "work_item_id": work_item_id,
            "recommendations": recommendations[:5],  # Top 5 recommendations
            "generated_at": datetime.utcnow()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating assignment recommendations: {str(e)}")

@dashboard_router.get("/team/metrics")
async def get_team_metrics(
    timeframe: DashboardTimeframe = DashboardTimeframe.WEEK,
    db: Session = Depends(get_db)
):
    """Get team-wide performance metrics"""
    
    try:
        dashboard_service = DashboardService(db)
        start_date, end_date = dashboard_service._get_timeframe_bounds(timeframe)
        team_metrics = dashboard_service._calculate_team_metrics(start_date, end_date)
        
        return {
            "timeframe": timeframe,
            "metrics": team_metrics,
            "generated_at": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving team metrics: {str(e)}")

@dashboard_router.get("/underwriters")
async def get_underwriter_list(
    include_workload: bool = True,
    db: Session = Depends(get_db)
):
    """Get list of underwriters with optional workload information"""
    
    try:
        underwriters = db.query(User).filter(
            User.role.in_([UserRoleEnum.UNDERWRITER, UserRoleEnum.SENIOR_UNDERWRITER])
        ).all()
        
        result = []
        for underwriter in underwriters:
            user_detail = UserDetail(
                id=underwriter.id,
                name=underwriter.name,
                email=underwriter.email,
                role=underwriter.role,
                specializations=underwriter.specializations or [],
                max_capacity=underwriter.max_capacity or 25,
                current_workload=underwriter.current_workload or 0,
                is_available=underwriter.is_available,
                avg_processing_time_days=underwriter.avg_processing_time_days,
                success_rate=underwriter.success_rate,
                last_assignment=underwriter.last_assignment
            )
            
            if include_workload:
                workload = _calculate_underwriter_workload(underwriter.id, db)
                result.append({
                    "user": user_detail,
                    "workload": workload
                })
            else:
                result.append({"user": user_detail})
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving underwriters: {str(e)}")

@dashboard_router.post("/message/info-request")
async def send_information_request(
    work_item_id: int,
    underwriter_id: str,
    requested_info: str,
    db: Session = Depends(get_db)
):
    """Send information request to broker"""
    
    try:
        # Get work item and submission
        work_item = db.query(WorkItem).filter(WorkItem.id == work_item_id).first()
        if not work_item:
            raise HTTPException(status_code=404, detail="Work item not found")
        
        submission = db.query(Submission).filter(Submission.id == work_item.submission_id).first()
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        # Get underwriter
        underwriter = db.query(User).filter(User.id == underwriter_id).first()
        if not underwriter:
            raise HTTPException(status_code=404, detail="Underwriter not found")
        
        # Send information request
        result = MessageService.create_info_request(
            work_item_id=work_item_id,
            underwriter_name=underwriter.name,
            broker_email=submission.sender_email,
            requested_info=requested_info,
            db_session=db
        )
        
        return {
            "message": "Information request sent successfully",
            "result": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending information request: {str(e)}")

@dashboard_router.get("/analytics/industry-performance/{underwriter_id}")
async def get_industry_performance_comparison(
    underwriter_id: str,
    timeframe: DashboardTimeframe = DashboardTimeframe.MONTH,
    db: Session = Depends(get_db)
):
    """Get industry performance comparison for underwriter"""
    
    try:
        analytics_service = PortfolioAnalyticsService(db)
        comparison = analytics_service.get_industry_performance_comparison(underwriter_id, timeframe)
        
        return {
            "underwriter_id": underwriter_id,
            "timeframe": timeframe,
            "industry_comparison": comparison,
            "generated_at": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating industry comparison: {str(e)}")

@dashboard_router.get("/analytics/risk-distribution")
async def get_risk_distribution_analysis(
    underwriter_id: Optional[str] = Query(None),
    timeframe: DashboardTimeframe = DashboardTimeframe.MONTH,
    db: Session = Depends(get_db)
):
    """Get risk distribution analysis across portfolio"""
    
    try:
        analytics_service = PortfolioAnalyticsService(db)
        analysis = analytics_service.get_risk_distribution_analysis(underwriter_id, timeframe)
        
        return {
            "underwriter_id": underwriter_id,
            "timeframe": timeframe,
            "risk_analysis": analysis,
            "generated_at": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating risk distribution analysis: {str(e)}")

@dashboard_router.get("/analytics/performance-trends/{underwriter_id}")
async def get_performance_trends(
    underwriter_id: str,
    metrics: List[str] = Query(["risk_score", "processing_time", "approval_rate"]),
    timeframe: DashboardTimeframe = DashboardTimeframe.QUARTER,
    db: Session = Depends(get_db)
):
    """Get performance trends for specific metrics"""
    
    try:
        analytics_service = PortfolioAnalyticsService(db)
        trends = analytics_service.get_performance_trends(underwriter_id, metrics, timeframe)
        
        return {
            "underwriter_id": underwriter_id,
            "timeframe": timeframe,
            "metrics": metrics,
            "trends": trends,
            "generated_at": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating performance trends: {str(e)}")

@dashboard_router.get("/analytics/competitive-analysis/{underwriter_id}")
async def get_competitive_analysis(
    underwriter_id: str,
    timeframe: DashboardTimeframe = DashboardTimeframe.QUARTER,
    db: Session = Depends(get_db)
):
    """Get competitive analysis comparing underwriter to team"""
    
    try:
        analytics_service = PortfolioAnalyticsService(db)
        analysis = analytics_service.get_competitive_analysis(underwriter_id, timeframe)
        
        return {
            "underwriter_id": underwriter_id,
            "timeframe": timeframe,
            "competitive_analysis": analysis,
            "generated_at": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating competitive analysis: {str(e)}")

@dashboard_router.get("/risk/industry-benchmarks/{industry}")
async def get_industry_risk_benchmarks(
    industry: str,
    db: Session = Depends(get_db)
):
    """Get risk benchmarks for specific industry"""
    
    try:
        benchmarks = RiskBenchmarkingService.get_industry_benchmarks(industry)
        
        return {
            "industry": industry,
            "benchmarks": benchmarks,
            "generated_at": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving industry benchmarks: {str(e)}")

@dashboard_router.post("/risk/enhanced-assessment")
async def generate_enhanced_risk_assessment(
    work_item_id: int,
    include_historical: bool = False,
    db: Session = Depends(get_db)
):
    """Generate enhanced risk assessment using advanced scoring engine"""
    
    try:
        # Get work item and submission
        work_item = db.query(WorkItem).filter(WorkItem.id == work_item_id).first()
        if not work_item:
            raise HTTPException(status_code=404, detail="Work item not found")
        
        submission = db.query(Submission).filter(Submission.id == work_item.submission_id).first()
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        extracted_fields = submission.extracted_fields or {}
        
        # Get historical data if requested
        historical_data = None
        if include_historical:
            # Mock historical data - would query actual historical records
            historical_data = {
                "claims_count": 0,
                "incident_count": 1
            }
        
        # Generate enhanced risk assessment
        risk_assessment = EnhancedRiskScoringEngine.calculate_enhanced_risk_score(
            extracted_fields, historical_data
        )
        
        # Update work item with new risk score
        work_item.risk_score = risk_assessment.overall_score
        db.commit()
        
        return {
            "work_item_id": work_item_id,
            "enhanced_risk_assessment": risk_assessment,
            "historical_data_included": include_historical,
            "generated_at": datetime.utcnow()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating enhanced risk assessment: {str(e)}")

# Helper functions

def _apply_work_queue_filters(work_queue, priority_filter, status_filter, industry_filter, 
                             risk_score_min, risk_score_max, limit):
    """Apply filters to work queue items"""
    # This would implement filtering logic for work queue items
    # For now, return original work queue (filtering would be done in the service layer)
    return work_queue

async def _build_submission_detail_view(work_item, submission, extracted_fields, db):
    """Build comprehensive submission detail view"""
    
    # Convert work item to summary
    work_item_summary = WorkItemSummary(
        id=work_item.id,
        submission_id=work_item.submission_id,
        submission_ref=submission.submission_ref,
        title=work_item.title,
        description=work_item.description,
        status=WorkItemStatusEnum(work_item.status.value),
        priority=WorkItemPriorityEnum(work_item.priority.value),
        assigned_to=work_item.assigned_to,
        risk_score=work_item.risk_score,
        industry=work_item.industry,
        company_size=CompanySizeEnum(work_item.company_size.value) if work_item.company_size else None,
        policy_type=work_item.policy_type,
        coverage_amount=work_item.coverage_amount,
        created_at=work_item.created_at,
        updated_at=work_item.updated_at,
        comments_count=0,
        has_urgent_comments=False
    )
    
    # Build company profile
    company_profile = CompanyProfile(
        name=extracted_fields.get("insured_name", "Unknown Company"),
        industry=extracted_fields.get("industry", "Unknown"),
        company_size=CompanySizeEnum.SMALL,  # Would parse from extracted fields
        employee_count=_parse_employee_count(extracted_fields.get("employee_count")),
        annual_revenue=_parse_revenue(extracted_fields.get("revenue")),
        years_in_business=extracted_fields.get("years_in_business"),
        credit_rating=extracted_fields.get("credit_rating"),
        previous_claims=False  # Would parse from extracted fields
    )
    
    # Build cybersecurity posture - handle both string and integer inputs
    security_measures_raw = extracted_fields.get("security_measures", "")
    security_measures_str = str(security_measures_raw) if security_measures_raw else ""
    data_types_raw = extracted_fields.get("data_types", "")
    data_types_str = str(data_types_raw) if data_types_raw else ""
    
    cybersecurity_posture = CybersecurityPosture(
        security_measures=security_measures_str.split(",") if security_measures_str else [],
        data_types_handled=data_types_str.split(",") if data_types_str else [],
        compliance_certifications=[],
        previous_incidents=False,
        incident_count_last_year=0
    )
    
    # Build financial health
    financial_health = FinancialHealth(
        credit_rating=extracted_fields.get("credit_rating"),
        revenue_trend="stable"  # Would analyze from historical data
    )
    
    # Generate risk assessment
    risk_service = RiskScoringService(db)
    risk_assessment = risk_service.calculate_comprehensive_risk_assessment(extracted_fields)
    
    # Build policy details
    coverage_amount = _parse_coverage_amount(extracted_fields.get("coverage_amount"))
    policy_details = PolicyDetails(
        coverage_type=extracted_fields.get("policy_type", "Cyber Liability"),
        limits=CoverageLimits(
            per_claim_limit=coverage_amount or 1_000_000,
            aggregate_limit=(coverage_amount or 1_000_000) * 2,
            retention_deductible=10_000,
            sub_limits={}
        ),
        components=CoverageComponents(),
        exclusions=[],
        endorsements=[]
    )
    
    # Generate automated recommendation
    recommendation_service = RecommendationService(db)
    automated_recommendation = recommendation_service.generate_automated_recommendation(
        work_item, risk_assessment, extracted_fields
    )
    
    # Build communication summary (mock)
    communication_summary = CommunicationSummary()
    
    # Build compliance checks (mock)
    compliance_checks = ComplianceChecks(
        compliance_score=75.0
    )
    
    return SubmissionDetailView(
        work_item=work_item_summary,
        company_profile=company_profile,
        cybersecurity_posture=cybersecurity_posture,
        financial_health=financial_health,
        risk_assessment=risk_assessment,
        policy_details=policy_details,
        quote_information=None,  # Would be generated based on pricing rules
        assignment_recommendation=None,  # Would be generated if unassigned
        communication_summary=communication_summary,
        automated_recommendation=automated_recommendation,
        compliance_checks=compliance_checks
    )

def _generate_assignment_recommendation(underwriter, work_item, extracted_fields, db):
    """Generate assignment recommendation for underwriter"""
    
    # Calculate recommendation score based on expertise, workload, etc.
    score = 50  # Base score
    reasons = []
    
    # Industry expertise
    industry = extracted_fields.get("industry", "")
    if industry in (underwriter.specializations or []):
        score += 30
        reasons.append(f"Industry expertise: {industry}")
    
    # Workload factor
    current_workload = underwriter.current_workload or 0
    max_capacity = underwriter.max_capacity or 25
    utilization = current_workload / max_capacity
    
    if utilization < 0.7:
        score += 20
        reasons.append("Low workload utilization")
    elif utilization < 0.9:
        score += 10
        reasons.append("Moderate workload utilization")
    else:
        score -= 10
        reasons.append("High workload utilization")
    
    # Risk level match
    risk_score = work_item.risk_score or 50
    if risk_score > 75 and underwriter.role == UserRoleEnum.SENIOR_UNDERWRITER:
        score += 25
        reasons.append("Senior underwriter for high-risk case")
    
    return AssignmentRecommendation(
        underwriter=UserDetail(
            id=underwriter.id,
            name=underwriter.name,
            email=underwriter.email,
            role=underwriter.role,
            specializations=underwriter.specializations or [],
            max_capacity=underwriter.max_capacity or 25,
            current_workload=underwriter.current_workload or 0,
            is_available=underwriter.is_available
        ),
        recommendation_score=min(score, 100),
        expertise_match=underwriter.specializations or [],
        workload_factor=utilization,
        reasons=reasons,
        estimated_processing_time=underwriter.avg_processing_time_days or 3.5
    )

def _calculate_underwriter_workload(underwriter_id: str, db: Session) -> UnderwriterWorkload:
    """Calculate current workload for underwriter"""
    
    current_assignments = db.query(WorkItem).filter(
        WorkItem.assigned_to == underwriter_id,
        WorkItem.status.in_([WorkItemStatus.PENDING, WorkItemStatus.IN_REVIEW])
    ).count()
    
    pending_urgent = db.query(WorkItem).filter(
        WorkItem.assigned_to == underwriter_id,
        WorkItem.priority.in_([WorkItemPriority.HIGH, WorkItemPriority.CRITICAL]),
        WorkItem.status.in_([WorkItemStatus.PENDING, WorkItemStatus.IN_REVIEW])
    ).count()
    
    user = db.query(User).filter(User.id == underwriter_id).first()
    capacity = user.max_capacity if user else 25
    utilization = (current_assignments / capacity) * 100
    
    return UnderwriterWorkload(
        current_assignments=current_assignments,
        capacity=capacity,
        utilization_percentage=min(utilization, 100),
        average_processing_time_days=user.avg_processing_time_days if user else 3.5,
        pending_urgent_items=pending_urgent
    )

def _generate_time_series_data(underwriter_id: str, timeframe: DashboardTimeframe, db: Session):
    """Generate time series data for analytics"""
    # Mock implementation - would query historical data
    return []

def _generate_benchmark_data(underwriter_id: str, db: Session):
    """Generate benchmark comparison data"""
    # Mock implementation - would compare against industry/team averages
    return []

def _generate_portfolio_insights(portfolio_summary):
    """Generate portfolio insights"""
    insights = []
    
    if portfolio_summary.risk_distribution.high_risk > portfolio_summary.risk_distribution.low_risk:
        insights.append("Portfolio skews toward higher risk submissions")
    
    if len(portfolio_summary.industry_breakdown) > 0:
        top_industry = portfolio_summary.industry_breakdown[0]
        if top_industry.percentage_of_portfolio > 40:
            insights.append(f"Heavy concentration in {top_industry.industry} industry ({top_industry.percentage_of_portfolio:.1f}%)")
    
    return insights

def _generate_portfolio_recommendations(portfolio_summary):
    """Generate portfolio recommendations"""
    recommendations = []
    
    if portfolio_summary.risk_distribution.high_risk > portfolio_summary.total_policies * 0.3:
        recommendations.append("Consider tightening underwriting guidelines for high-risk submissions")
    
    return recommendations

def _parse_employee_count(employee_str):
    """Parse employee count from string"""
    if not employee_str:
        return None
    try:
        return int(str(employee_str).replace(",", ""))
    except:
        return None

def _parse_revenue(revenue_str):
    """Parse revenue from string"""
    return CyberInsuranceValidator._parse_coverage_amount(revenue_str)

def _parse_coverage_amount(coverage_str):
    """Parse coverage amount from string"""
    return CyberInsuranceValidator._parse_coverage_amount(coverage_str)