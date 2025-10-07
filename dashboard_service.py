"""
Dashboard Service Layer for Underwriter Portal
Provides comprehensive analytics, metrics calculation, and business intelligence
"""

import logging
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case, text
from collections import defaultdict
import statistics

from database import (
    WorkItem, User, RiskAssessment, Submission, WorkItemHistory, 
    Comment, WorkItemStatus, WorkItemPriority, CompanySize
)
from dashboard_models import (
    DashboardKPIs, KPIMetric, MetricTrend, WorkQueueSummary, TeamMetrics,
    RiskDistribution, IndustryRiskMetrics, CoverageTypeMetrics, PortfolioSummary,
    ProcessingMetrics, UnderwriterDashboard, ComprehensiveRiskAssessment,
    RiskFactorDetail, AutomatedRecommendation, AssignmentRecommendation,
    UnderwriterWorkload, DashboardTimeframe, AnalyticsTimeSeries,
    AnalyticsTimeSeriesPoint, BenchmarkComparison, PortfolioAnalyticsReport,
    CompanyProfile, CybersecurityPosture, FinancialHealth, PolicyDetails,
    CoverageLimits, CoverageComponents, QuoteInformation, PricingFactors,
    CompetitiveAnalysis
)
from models import (
    WorkItemSummary, UserDetail, WorkItemStatusEnum, WorkItemPriorityEnum,
    CompanySizeEnum, UserRoleEnum
)
from business_rules import CyberInsuranceValidator
from business_config import BusinessConfig

logger = logging.getLogger(__name__)

class DashboardService:
    """Core service for dashboard data aggregation and analytics"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_underwriter_dashboard(
        self, 
        underwriter_id: str, 
        timeframe: DashboardTimeframe = DashboardTimeframe.WEEK
    ) -> UnderwriterDashboard:
        """Get comprehensive dashboard data for an underwriter"""
        
        # Calculate timeframe boundaries
        start_date, end_date = self._get_timeframe_bounds(timeframe)
        
        # Get user details
        user = self.db.query(User).filter(User.id == underwriter_id).first()
        if not user:
            raise ValueError(f"Underwriter {underwriter_id} not found")
        
        # Build dashboard components
        kpis = self._calculate_kpis(underwriter_id, start_date, end_date)
        work_queue = self._get_work_queue_summary(underwriter_id)
        team_metrics = self._calculate_team_metrics(start_date, end_date)
        portfolio_summary = self._get_portfolio_summary(underwriter_id, start_date, end_date)
        processing_metrics = self._calculate_processing_metrics(underwriter_id, start_date, end_date)
        
        return UnderwriterDashboard(
            underwriter_id=underwriter_id,
            underwriter_name=user.name,
            last_updated=datetime.utcnow(),
            kpis=kpis,
            work_queue=work_queue,
            team_metrics=team_metrics,
            portfolio_summary=portfolio_summary,
            processing_metrics=processing_metrics
        )
    
    def _calculate_kpis(
        self, 
        underwriter_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> DashboardKPIs:
        """Calculate key performance indicators"""
        
        # Previous period for comparison
        period_duration = end_date - start_date
        prev_start = start_date - period_duration
        prev_end = start_date
        
        # Active submissions (current period)
        active_current = self.db.query(WorkItem).filter(
            WorkItem.assigned_to == underwriter_id,
            WorkItem.status.in_([WorkItemStatus.PENDING, WorkItemStatus.IN_REVIEW]),
            WorkItem.created_at.between(start_date, end_date)
        ).count()
        
        active_previous = self.db.query(WorkItem).filter(
            WorkItem.assigned_to == underwriter_id,
            WorkItem.status.in_([WorkItemStatus.PENDING, WorkItemStatus.IN_REVIEW]),
            WorkItem.created_at.between(prev_start, prev_end)
        ).count()
        
        # Pending reviews
        pending_current = self.db.query(WorkItem).filter(
            WorkItem.assigned_to == underwriter_id,
            WorkItem.status == WorkItemStatus.IN_REVIEW,
            WorkItem.created_at.between(start_date, end_date)
        ).count()
        
        pending_previous = self.db.query(WorkItem).filter(
            WorkItem.assigned_to == underwriter_id,
            WorkItem.status == WorkItemStatus.IN_REVIEW,
            WorkItem.created_at.between(prev_start, prev_end)
        ).count()
        
        # Quotes issued
        quotes_current = self.db.query(WorkItem).filter(
            WorkItem.assigned_to == underwriter_id,
            WorkItem.status == WorkItemStatus.APPROVED,
            WorkItem.created_at.between(start_date, end_date)
        ).count()
        
        quotes_previous = self.db.query(WorkItem).filter(
            WorkItem.assigned_to == underwriter_id,
            WorkItem.status == WorkItemStatus.APPROVED,
            WorkItem.created_at.between(prev_start, prev_end)
        ).count()
        
        # Calculate average processing time
        avg_processing_time = self._calculate_average_processing_time(underwriter_id, start_date, end_date)
        prev_avg_processing_time = self._calculate_average_processing_time(underwriter_id, prev_start, prev_end)
        
        # Calculate average risk score
        avg_risk_score = self.db.query(func.avg(WorkItem.risk_score)).filter(
            WorkItem.assigned_to == underwriter_id,
            WorkItem.risk_score.isnot(None),
            WorkItem.created_at.between(start_date, end_date)
        ).scalar() or 0
        
        prev_avg_risk_score = self.db.query(func.avg(WorkItem.risk_score)).filter(
            WorkItem.assigned_to == underwriter_id,
            WorkItem.risk_score.isnot(None),
            WorkItem.created_at.between(prev_start, prev_end)
        ).scalar() or 0
        
        # Calculate SLA performance
        sla_performance = self._calculate_sla_performance(underwriter_id, start_date, end_date)
        prev_sla_performance = self._calculate_sla_performance(underwriter_id, prev_start, prev_end)
        
        # Portfolio premium (mock data - would come from policy system)
        portfolio_premium = self._calculate_portfolio_premium(underwriter_id, start_date, end_date)
        prev_portfolio_premium = self._calculate_portfolio_premium(underwriter_id, prev_start, prev_end)
        
        return DashboardKPIs(
            active_submissions=self._create_kpi_metric("Active Submissions", active_current, active_previous),
            pending_reviews=self._create_kpi_metric("Pending Reviews", pending_current, pending_previous),
            quotes_issued=self._create_kpi_metric("Quotes Issued", quotes_current, quotes_previous),
            policies_bound=self._create_kpi_metric("Policies Bound", quotes_current * 0.7, quotes_previous * 0.7),  # Mock conversion rate
            average_processing_time=self._create_kpi_metric("Avg Processing Time", avg_processing_time, prev_avg_processing_time, "days"),
            sla_performance=self._create_kpi_metric("SLA Performance", sla_performance, prev_sla_performance, "percentage"),
            portfolio_premium=self._create_kpi_metric("Portfolio Premium", portfolio_premium, prev_portfolio_premium, "currency"),
            risk_score_average=self._create_kpi_metric("Avg Risk Score", avg_risk_score, prev_avg_risk_score, "score")
        )
    
    def _create_kpi_metric(
        self, 
        name: str, 
        current: float, 
        previous: float, 
        unit: str = "count"
    ) -> KPIMetric:
        """Create a KPI metric with trend analysis"""
        
        if previous == 0:
            trend = MetricTrend.STABLE if current == 0 else MetricTrend.UP
            percentage_change = 0
        else:
            percentage_change = ((current - previous) / previous) * 100
            if percentage_change > 5:
                trend = MetricTrend.UP
            elif percentage_change < -5:
                trend = MetricTrend.DOWN
            else:
                trend = MetricTrend.STABLE
        
        return KPIMetric(
            name=name,
            value=current,
            previous_value=previous,
            trend=trend,
            percentage_change=percentage_change,
            unit=unit
        )
    
    def _get_work_queue_summary(self, underwriter_id: str) -> WorkQueueSummary:
        """Get work queue summary for underwriter"""
        
        # Base query for assigned work items
        base_query = self.db.query(WorkItem).filter(
            WorkItem.assigned_to == underwriter_id
        )
        
        # Urgent items (high priority or overdue)
        urgent_items = base_query.filter(
            or_(
                WorkItem.priority == WorkItemPriority.CRITICAL,
                WorkItem.priority == WorkItemPriority.HIGH,
                and_(
                    WorkItem.created_at < datetime.utcnow() - timedelta(days=3),
                    WorkItem.status == WorkItemStatus.PENDING
                )
            )
        ).limit(20).all()
        
        # Pending review items
        pending_review = base_query.filter(
            WorkItem.status == WorkItemStatus.IN_REVIEW
        ).limit(20).all()
        
        # Awaiting info items (would need additional status tracking)
        awaiting_info = base_query.filter(
            WorkItem.status == WorkItemStatus.PENDING,
            WorkItem.description.like('%information%')  # Mock condition
        ).limit(20).all()
        
        # Ready to quote items
        ready_to_quote = base_query.filter(
            WorkItem.status == WorkItemStatus.PENDING,
            WorkItem.risk_score.isnot(None),
            WorkItem.risk_score < 70  # Low to medium risk
        ).limit(20).all()
        
        return WorkQueueSummary(
            urgent=self._convert_to_summaries(urgent_items),
            pending_review=self._convert_to_summaries(pending_review),
            awaiting_info=self._convert_to_summaries(awaiting_info),
            ready_to_quote=self._convert_to_summaries(ready_to_quote),
            total_count=base_query.count()
        )
    
    def _convert_to_summaries(self, work_items: List[WorkItem]) -> List[WorkItemSummary]:
        """Convert WorkItem objects to WorkItemSummary objects"""
        summaries = []
        for item in work_items:
            # Get submission details
            submission = self.db.query(Submission).filter(
                Submission.id == item.submission_id
            ).first()
            
            # Count comments
            comments_count = self.db.query(Comment).filter(
                Comment.work_item_id == item.id
            ).count()
            
            # Check for urgent comments
            has_urgent_comments = self.db.query(Comment).filter(
                Comment.work_item_id == item.id,
                Comment.is_urgent == True
            ).count() > 0
            
            summary = WorkItemSummary(
                id=item.id,
                submission_id=item.submission_id,
                submission_ref=submission.submission_ref if submission else f"SUB-{item.id}",
                title=item.title,
                description=item.description,
                status=WorkItemStatusEnum(item.status.value),
                priority=WorkItemPriorityEnum(item.priority.value),
                assigned_to=item.assigned_to,
                risk_score=item.risk_score,
                industry=item.industry,
                company_size=CompanySizeEnum(item.company_size.value) if item.company_size else None,
                policy_type=item.policy_type,
                coverage_amount=item.coverage_amount,
                created_at=item.created_at,
                updated_at=item.updated_at,
                comments_count=comments_count,
                has_urgent_comments=has_urgent_comments
            )
            summaries.append(summary)
        
        return summaries
    
    def _calculate_team_metrics(self, start_date: datetime, end_date: datetime) -> TeamMetrics:
        """Calculate team-wide metrics"""
        
        # Average risk score across team
        avg_risk_score = self.db.query(func.avg(WorkItem.risk_score)).filter(
            WorkItem.risk_score.isnot(None),
            WorkItem.created_at.between(start_date, end_date)
        ).scalar() or 0
        
        # Completed work items this week
        completed_count = self.db.query(WorkItem).filter(
            WorkItem.status.in_([WorkItemStatus.APPROVED, WorkItemStatus.REJECTED]),
            WorkItem.updated_at.between(start_date, end_date)
        ).count()
        
        # Pending assignment
        pending_assignment = self.db.query(WorkItem).filter(
            WorkItem.assigned_to.is_(None),
            WorkItem.status == WorkItemStatus.PENDING
        ).count()
        
        # Team capacity utilization
        total_underwriters = self.db.query(User).filter(
            User.role.in_([UserRoleEnum.UNDERWRITER, UserRoleEnum.SENIOR_UNDERWRITER])
        ).count()
        
        active_workload = self.db.query(WorkItem).filter(
            WorkItem.status.in_([WorkItemStatus.PENDING, WorkItemStatus.IN_REVIEW])
        ).count()
        
        capacity_utilization = (active_workload / (total_underwriters * 25)) * 100 if total_underwriters > 0 else 0
        
        # Average cycle time
        avg_cycle_time = self._calculate_average_cycle_time(start_date, end_date)
        
        return TeamMetrics(
            average_risk_score=avg_risk_score,
            completed_this_week=completed_count,
            pending_assignment=pending_assignment,
            team_capacity_utilization=min(capacity_utilization, 100),
            average_cycle_time_days=avg_cycle_time
        )
    
    def _get_portfolio_summary(
        self, 
        underwriter_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> PortfolioSummary:
        """Get portfolio summary for underwriter"""
        
        # Get all work items for this underwriter
        work_items = self.db.query(WorkItem).filter(
            WorkItem.assigned_to == underwriter_id,
            WorkItem.created_at.between(start_date, end_date)
        ).all()
        
        total_policies = len(work_items)
        total_premium = sum(item.coverage_amount or 0 for item in work_items) * 0.05  # Mock premium rate
        avg_policy_size = total_premium / total_policies if total_policies > 0 else 0
        
        # Risk distribution
        risk_distribution = self._calculate_risk_distribution(work_items)
        
        # Industry breakdown
        industry_breakdown = self._calculate_industry_breakdown(work_items)
        
        # Coverage breakdown
        coverage_breakdown = self._calculate_coverage_breakdown(work_items)
        
        return PortfolioSummary(
            total_policies=total_policies,
            total_premium=total_premium,
            average_policy_size=avg_policy_size,
            risk_distribution=risk_distribution,
            industry_breakdown=industry_breakdown,
            coverage_breakdown=coverage_breakdown
        )
    
    def _calculate_risk_distribution(self, work_items: List[WorkItem]) -> RiskDistribution:
        """Calculate risk score distribution"""
        
        low_risk = sum(1 for item in work_items if item.risk_score and item.risk_score <= 40)
        medium_risk = sum(1 for item in work_items if item.risk_score and 40 < item.risk_score <= 70)
        high_risk = sum(1 for item in work_items if item.risk_score and item.risk_score > 70)
        
        return RiskDistribution(
            low_risk=low_risk,
            medium_risk=medium_risk,
            high_risk=high_risk,
            total=len(work_items)
        )
    
    def _calculate_industry_breakdown(self, work_items: List[WorkItem]) -> List[IndustryRiskMetrics]:
        """Calculate industry-specific metrics"""
        
        industry_data = defaultdict(lambda: {"count": 0, "risk_scores": [], "premiums": []})
        
        for item in work_items:
            if item.industry:
                industry_data[item.industry]["count"] += 1
                if item.risk_score:
                    industry_data[item.industry]["risk_scores"].append(item.risk_score)
                if item.coverage_amount:
                    industry_data[item.industry]["premiums"].append(item.coverage_amount * 0.05)
        
        total_policies = len(work_items)
        
        breakdown = []
        for industry, data in industry_data.items():
            avg_risk = statistics.mean(data["risk_scores"]) if data["risk_scores"] else 0
            total_premium = sum(data["premiums"])
            percentage = (data["count"] / total_policies) * 100 if total_policies > 0 else 0
            
            breakdown.append(IndustryRiskMetrics(
                industry=industry,
                count=data["count"],
                average_risk_score=avg_risk,
                premium_volume=total_premium,
                percentage_of_portfolio=percentage
            ))
        
        return sorted(breakdown, key=lambda x: x.count, reverse=True)
    
    def _calculate_coverage_breakdown(self, work_items: List[WorkItem]) -> List[CoverageTypeMetrics]:
        """Calculate coverage type breakdown"""
        
        coverage_data = defaultdict(lambda: {"count": 0, "limits": [], "premiums": []})
        
        for item in work_items:
            coverage_type = item.policy_type or "Unknown"
            coverage_data[coverage_type]["count"] += 1
            if item.coverage_amount:
                coverage_data[coverage_type]["limits"].append(item.coverage_amount)
                coverage_data[coverage_type]["premiums"].append(item.coverage_amount * 0.05)
        
        total_policies = len(work_items)
        
        breakdown = []
        for coverage_type, data in coverage_data.items():
            total_limit = sum(data["limits"])
            avg_premium = statistics.mean(data["premiums"]) if data["premiums"] else 0
            percentage = (data["count"] / total_policies) * 100 if total_policies > 0 else 0
            
            breakdown.append(CoverageTypeMetrics(
                coverage_type=coverage_type,
                count=data["count"],
                total_limit=total_limit,
                average_premium=avg_premium,
                percentage_of_portfolio=percentage
            ))
        
        return sorted(breakdown, key=lambda x: x.count, reverse=True)
    
    def _calculate_processing_metrics(
        self, 
        underwriter_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> ProcessingMetrics:
        """Calculate processing performance metrics"""
        
        # Get completed work items in timeframe
        completed_items = self.db.query(WorkItem).filter(
            WorkItem.assigned_to == underwriter_id,
            WorkItem.status.in_([WorkItemStatus.APPROVED, WorkItemStatus.REJECTED]),
            WorkItem.updated_at.between(start_date, end_date)
        ).all()
        
        if not completed_items:
            return ProcessingMetrics(
                average_time_to_quote_days=0,
                average_time_to_bind_days=0,
                sla_compliance_rate=100,
                quote_to_bind_ratio=0,
                decline_rate=0,
                info_request_rate=0
            )
        
        # Calculate average time to quote
        processing_times = []
        for item in completed_items:
            processing_time = (item.updated_at - item.created_at).days
            processing_times.append(processing_time)
        
        avg_time_to_quote = statistics.mean(processing_times) if processing_times else 0
        avg_time_to_bind = avg_time_to_quote + 2  # Mock additional binding time
        
        # SLA compliance (assuming 5 days SLA)
        sla_compliant = sum(1 for time in processing_times if time <= 5)
        sla_compliance_rate = (sla_compliant / len(completed_items)) * 100
        
        # Quote to bind ratio (mock data)
        approved_count = sum(1 for item in completed_items if item.status == WorkItemStatus.APPROVED)
        quote_to_bind_ratio = (approved_count * 0.7 / approved_count) * 100 if approved_count > 0 else 0
        
        # Decline rate
        rejected_count = sum(1 for item in completed_items if item.status == WorkItemStatus.REJECTED)
        decline_rate = (rejected_count / len(completed_items)) * 100
        
        # Info request rate (mock - would need additional tracking)
        info_request_rate = 25  # Mock value
        
        return ProcessingMetrics(
            average_time_to_quote_days=avg_time_to_quote,
            average_time_to_bind_days=avg_time_to_bind,
            sla_compliance_rate=sla_compliance_rate,
            quote_to_bind_ratio=quote_to_bind_ratio,
            decline_rate=decline_rate,
            info_request_rate=info_request_rate
        )
    
    def _calculate_average_processing_time(
        self, 
        underwriter_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> float:
        """Calculate average processing time for completed items"""
        
        completed_items = self.db.query(WorkItem).filter(
            WorkItem.assigned_to == underwriter_id,
            WorkItem.status.in_([WorkItemStatus.APPROVED, WorkItemStatus.REJECTED]),
            WorkItem.updated_at.between(start_date, end_date)
        ).all()
        
        if not completed_items:
            return 0
        
        processing_times = [
            (item.updated_at - item.created_at).days 
            for item in completed_items
        ]
        
        return statistics.mean(processing_times)
    
    def _calculate_sla_performance(
        self, 
        underwriter_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> float:
        """Calculate SLA performance percentage"""
        
        completed_items = self.db.query(WorkItem).filter(
            WorkItem.assigned_to == underwriter_id,
            WorkItem.status.in_([WorkItemStatus.APPROVED, WorkItemStatus.REJECTED]),
            WorkItem.updated_at.between(start_date, end_date)
        ).all()
        
        if not completed_items:
            return 100
        
        # Assuming 5 days SLA
        sla_compliant = sum(
            1 for item in completed_items 
            if (item.updated_at - item.created_at).days <= 5
        )
        
        return (sla_compliant / len(completed_items)) * 100
    
    def _calculate_portfolio_premium(
        self, 
        underwriter_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> float:
        """Calculate total portfolio premium (mock calculation)"""
        
        total_coverage = self.db.query(func.sum(WorkItem.coverage_amount)).filter(
            WorkItem.assigned_to == underwriter_id,
            WorkItem.coverage_amount.isnot(None),
            WorkItem.created_at.between(start_date, end_date)
        ).scalar() or 0
        
        # Mock premium rate of 5%
        return total_coverage * 0.05
    
    def _calculate_average_cycle_time(self, start_date: datetime, end_date: datetime) -> float:
        """Calculate average cycle time across all underwriters"""
        
        completed_items = self.db.query(WorkItem).filter(
            WorkItem.status.in_([WorkItemStatus.APPROVED, WorkItemStatus.REJECTED]),
            WorkItem.updated_at.between(start_date, end_date)
        ).all()
        
        if not completed_items:
            return 0
        
        cycle_times = [
            (item.updated_at - item.created_at).days 
            for item in completed_items
        ]
        
        return statistics.mean(cycle_times)
    
    def _get_timeframe_bounds(self, timeframe: DashboardTimeframe) -> Tuple[datetime, datetime]:
        """Get start and end dates for timeframe"""
        
        now = datetime.utcnow()
        
        if timeframe == DashboardTimeframe.TODAY:
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now
        elif timeframe == DashboardTimeframe.WEEK:
            start_date = now - timedelta(days=7)
            end_date = now
        elif timeframe == DashboardTimeframe.MONTH:
            start_date = now - timedelta(days=30)
            end_date = now
        elif timeframe == DashboardTimeframe.QUARTER:
            start_date = now - timedelta(days=90)
            end_date = now
        elif timeframe == DashboardTimeframe.YEAR:
            start_date = now - timedelta(days=365)
            end_date = now
        else:
            start_date = now - timedelta(days=7)
            end_date = now
        
        return start_date, end_date


class RiskScoringService:
    """Advanced risk scoring and assessment service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_comprehensive_risk_assessment(
        self, 
        extracted_fields: Dict[str, Any]
    ) -> ComprehensiveRiskAssessment:
        """Calculate comprehensive risk assessment using business rules"""
        
        # Get base risk categories from business rules
        base_categories = CyberInsuranceValidator.generate_risk_categories(extracted_fields)
        
        # Calculate detailed risk factors
        risk_factors = self._identify_risk_factors(extracted_fields, base_categories)
        
        # Calculate overall score
        overall_score = sum(base_categories.values()) / len(base_categories)
        
        # Determine risk level
        risk_level = self._determine_risk_level(overall_score)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(extracted_fields)
        
        # Get industry benchmark
        industry_benchmark = self._get_industry_benchmark(extracted_fields.get("industry"))
        
        return ComprehensiveRiskAssessment(
            overall_score=overall_score,
            technical_score=base_categories.get("technical", 50),
            operational_score=base_categories.get("operational", 50),
            financial_score=base_categories.get("financial", 50),
            compliance_score=base_categories.get("compliance", 50),
            risk_factors=risk_factors,
            industry_benchmark=industry_benchmark,
            risk_level=risk_level,
            confidence_score=confidence_score
        )
    
    def _identify_risk_factors(
        self, 
        extracted_fields: Dict[str, Any], 
        base_categories: Dict[str, float]
    ) -> List[RiskFactorDetail]:
        """Identify specific risk factors and their impacts"""
        
        factors = []
        
        # Industry-specific risks
        industry = extracted_fields.get("industry", "").lower()
        if "healthcare" in industry:
            factors.append(RiskFactorDetail(
                category="compliance",
                factor="HIPAA Compliance Requirements",
                impact_level="High",
                score_impact=15,
                description="Healthcare industry requires strict HIPAA compliance",
                mitigation_recommendation="Implement HIPAA-compliant security controls"
            ))
        
        if "financial" in industry:
            factors.append(RiskFactorDetail(
                category="compliance",
                factor="Financial Regulations",
                impact_level="High",
                score_impact=20,
                description="Financial services subject to extensive regulations",
                mitigation_recommendation="Ensure SOX, PCI-DSS compliance"
            ))
        
        # Data type risks
        data_types = extracted_fields.get("data_types", "").lower()
        if "pii" in data_types or "personal" in data_types:
            factors.append(RiskFactorDetail(
                category="compliance",
                factor="Personal Information Handling",
                impact_level="Medium",
                score_impact=10,
                description="Handling of personally identifiable information",
                mitigation_recommendation="Implement data classification and protection"
            ))
        
        # Company size risks
        employee_count = self._parse_employee_count(extracted_fields.get("employee_count"))
        if employee_count and employee_count > 1000:
            factors.append(RiskFactorDetail(
                category="operational",
                factor="Large Organization Complexity",
                impact_level="Medium",
                score_impact=12,
                description="Large organizations have complex attack surfaces",
                mitigation_recommendation="Implement enterprise security controls"
            ))
        
        # Security measures (positive factors)
        security_measures = extracted_fields.get("security_measures", "").lower()
        if "mfa" in security_measures:
            factors.append(RiskFactorDetail(
                category="technical",
                factor="Multi-Factor Authentication",
                impact_level="Low",
                score_impact=-10,
                description="MFA implementation reduces authentication risks",
                mitigation_recommendation="Maintain and expand MFA coverage"
            ))
        
        return factors
    
    def _determine_risk_level(self, overall_score: float) -> str:
        """Determine risk level based on overall score"""
        if overall_score <= 30:
            return "Low"
        elif overall_score <= 60:
            return "Medium"
        elif overall_score <= 85:
            return "High"
        else:
            return "Critical"
    
    def _calculate_confidence_score(self, extracted_fields: Dict[str, Any]) -> float:
        """Calculate confidence in the risk assessment"""
        
        # Base confidence
        confidence = 50.0
        
        # Increase confidence based on available data
        required_fields = ["industry", "company_size", "employee_count", "revenue", "data_types"]
        available_fields = sum(1 for field in required_fields if extracted_fields.get(field))
        
        confidence += (available_fields / len(required_fields)) * 30
        
        # Additional confidence factors
        if extracted_fields.get("security_measures"):
            confidence += 10
        if extracted_fields.get("previous_claims"):
            confidence += 10
        
        return min(confidence, 100)
    
    def _get_industry_benchmark(self, industry: str) -> Optional[float]:
        """Get industry benchmark risk score"""
        
        # Mock industry benchmarks
        benchmarks = {
            "Healthcare": 65.0,
            "Financial Services": 70.0,
            "Technology": 55.0,
            "Manufacturing": 45.0,
            "Retail": 50.0,
            "Education": 40.0
        }
        
        return benchmarks.get(industry, 50.0)
    
    def _parse_employee_count(self, employee_str: str) -> Optional[int]:
        """Parse employee count from string"""
        if not employee_str:
            return None
        
        try:
            # Remove common formatting
            clean_str = str(employee_str).replace(",", "").replace(" ", "")
            
            # Handle ranges (take upper bound)
            if "-" in clean_str:
                parts = clean_str.split("-")
                clean_str = parts[-1]
            
            return int(float(clean_str))
        except (ValueError, AttributeError):
            return None


class RecommendationService:
    """Service for generating automated recommendations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_automated_recommendation(
        self, 
        work_item: WorkItem, 
        risk_assessment: ComprehensiveRiskAssessment,
        extracted_fields: Dict[str, Any]
    ) -> AutomatedRecommendation:
        """Generate automated underwriting recommendation"""
        
        # Determine recommended action
        action, confidence, reasoning = self._determine_action(
            risk_assessment.overall_score, 
            extracted_fields
        )
        
        # Generate suggested conditions
        conditions = self._generate_conditions(risk_assessment, extracted_fields)
        
        # Check for referral triggers
        referral_triggers = self._check_referral_triggers(
            risk_assessment.overall_score, 
            extracted_fields
        )
        
        # Estimate premium range
        premium_range = self._estimate_premium_range(
            extracted_fields, 
            risk_assessment.overall_score
        )
        
        return AutomatedRecommendation(
            action=action,
            confidence=confidence,
            reasoning=reasoning,
            suggested_conditions=conditions,
            referral_triggers=referral_triggers,
            estimated_premium_range=premium_range
        )
    
    def _determine_action(
        self, 
        risk_score: float, 
        extracted_fields: Dict[str, Any]
    ) -> Tuple[str, float, List[str]]:
        """Determine recommended action based on risk score and business rules"""
        
        reasoning = []
        
        # Check business rules first
        validation_result, missing_fields, rejection_reason = CyberInsuranceValidator.validate_submission(extracted_fields)
        
        if validation_result == "Rejected":
            return "decline", 95.0, [rejection_reason]
        
        if validation_result == "Incomplete":
            return "request_info", 90.0, [f"Missing required information: {', '.join(missing_fields)}"]
        
        # Risk-based decisions
        if risk_score <= 40:
            reasoning.append("Low risk profile")
            reasoning.append("Standard underwriting guidelines apply")
            return "approve", 85.0, reasoning
        
        elif risk_score <= 70:
            reasoning.append("Medium risk profile")
            reasoning.append("Additional conditions may be required")
            return "approve", 75.0, reasoning
        
        elif risk_score <= 85:
            reasoning.append("High risk profile")
            reasoning.append("Requires senior underwriter review")
            return "refer_to_senior", 80.0, reasoning
        
        else:
            reasoning.append("Critical risk profile")
            reasoning.append("Outside normal appetite")
            return "decline", 90.0, reasoning
    
    def _generate_conditions(
        self, 
        risk_assessment: ComprehensiveRiskAssessment, 
        extracted_fields: Dict[str, Any]
    ) -> List[str]:
        """Generate suggested policy conditions"""
        
        conditions = []
        
        # High technical risk conditions
        if risk_assessment.technical_score > 70:
            conditions.append("Require implementation of multi-factor authentication")
            conditions.append("Annual security assessment required")
        
        # High compliance risk conditions
        if risk_assessment.compliance_score > 70:
            conditions.append("Provide evidence of regulatory compliance")
            conditions.append("Quarterly compliance reporting required")
        
        # Industry-specific conditions
        industry = extracted_fields.get("industry", "").lower()
        if "healthcare" in industry:
            conditions.append("HIPAA compliance certification required")
        
        if "financial" in industry:
            conditions.append("PCI-DSS compliance required for payment data")
        
        return conditions
    
    def _check_referral_triggers(
        self, 
        risk_score: float, 
        extracted_fields: Dict[str, Any]
    ) -> Optional[List[str]]:
        """Check if submission should be referred to senior underwriter"""
        
        triggers = []
        
        # High risk score
        if risk_score > 75:
            triggers.append(f"High risk score: {risk_score:.1f}")
        
        # Large coverage amounts
        coverage_amount = self._parse_coverage_amount(extracted_fields.get("coverage_amount"))
        if coverage_amount and coverage_amount > 10_000_000:  # $10M+
            triggers.append(f"Large coverage amount: ${coverage_amount:,.0f}")
        
        # High-risk industries
        industry = extracted_fields.get("industry", "")
        high_risk_industries = ["Cryptocurrency", "Cannabis", "Gaming"]
        if any(risk_industry.lower() in industry.lower() for risk_industry in high_risk_industries):
            triggers.append(f"High-risk industry: {industry}")
        
        return triggers if triggers else None
    
    def _estimate_premium_range(
        self, 
        extracted_fields: Dict[str, Any], 
        risk_score: float
    ) -> Optional[Dict[str, float]]:
        """Estimate premium range based on coverage and risk"""
        
        coverage_amount = self._parse_coverage_amount(extracted_fields.get("coverage_amount"))
        if not coverage_amount:
            return None
        
        # Base rate calculation (mock)
        base_rate = 0.02  # 2% of coverage
        
        # Risk adjustment
        if risk_score <= 40:
            risk_multiplier = 0.8
        elif risk_score <= 70:
            risk_multiplier = 1.0
        else:
            risk_multiplier = 1.5
        
        # Industry adjustment
        industry_multiplier = BusinessConfig.get_industry_risk_multiplier(
            extracted_fields.get("industry", "")
        ) if extracted_fields.get("industry") else 1.0
        
        base_premium = coverage_amount * base_rate * risk_multiplier * industry_multiplier
        
        return {
            "minimum": base_premium * 0.8,
            "recommended": base_premium,
            "maximum": base_premium * 1.3
        }
    
    def _parse_coverage_amount(self, coverage_str: str) -> Optional[float]:
        """Parse coverage amount from string"""
        return CyberInsuranceValidator._parse_coverage_amount(coverage_str)