"""
Dashboard-specific models for underwriter portal
Extends the base models with dashboard metrics, analytics, and KPI tracking
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from models import WorkItemSummary, UserDetail, WorkItemStatusEnum, CompanySizeEnum

class DashboardTimeframe(str, Enum):
    TODAY = "today"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    YEAR = "year"

class MetricTrend(str, Enum):
    UP = "up"
    DOWN = "down"
    STABLE = "stable"

# Dashboard KPI Models
class KPIMetric(BaseModel):
    name: str
    value: float
    previous_value: Optional[float] = None
    trend: Optional[MetricTrend] = None
    percentage_change: Optional[float] = None
    target: Optional[float] = None
    unit: str = "count"  # count, percentage, currency, days

class DashboardKPIs(BaseModel):
    active_submissions: KPIMetric
    pending_reviews: KPIMetric
    quotes_issued: KPIMetric
    policies_bound: KPIMetric
    average_processing_time: KPIMetric
    sla_performance: KPIMetric
    portfolio_premium: KPIMetric
    risk_score_average: KPIMetric

# Work Queue Models
class WorkQueueSummary(BaseModel):
    urgent: List[WorkItemSummary] = Field(default_factory=list)
    pending_review: List[WorkItemSummary] = Field(default_factory=list)
    awaiting_info: List[WorkItemSummary] = Field(default_factory=list)
    ready_to_quote: List[WorkItemSummary] = Field(default_factory=list)
    total_count: int = 0

class TeamMetrics(BaseModel):
    average_risk_score: float
    completed_this_week: int
    pending_assignment: int
    team_capacity_utilization: float
    average_cycle_time_days: float

# Risk Distribution Models
class RiskDistribution(BaseModel):
    low_risk: int = Field(..., description="0-40 risk score")
    medium_risk: int = Field(..., description="41-70 risk score")
    high_risk: int = Field(..., description="71-100 risk score")
    total: int

class IndustryRiskMetrics(BaseModel):
    industry: str
    count: int
    average_risk_score: float
    premium_volume: float
    percentage_of_portfolio: float

class CoverageTypeMetrics(BaseModel):
    coverage_type: str
    count: int
    total_limit: float
    average_premium: float
    percentage_of_portfolio: float

# Portfolio Analytics
class PortfolioSummary(BaseModel):
    total_policies: int
    total_premium: float
    average_policy_size: float
    risk_distribution: RiskDistribution
    industry_breakdown: List[IndustryRiskMetrics]
    coverage_breakdown: List[CoverageTypeMetrics]

# Processing Performance
class ProcessingMetrics(BaseModel):
    average_time_to_quote_days: float
    average_time_to_bind_days: float
    sla_compliance_rate: float
    quote_to_bind_ratio: float
    decline_rate: float
    info_request_rate: float

# Company Intelligence Models
class CompanyProfile(BaseModel):
    name: str
    industry: str
    company_size: CompanySizeEnum
    employee_count: Optional[int] = None
    annual_revenue: Optional[float] = None
    years_in_business: Optional[int] = None
    credit_rating: Optional[str] = None
    previous_claims: bool = False

class CybersecurityPosture(BaseModel):
    security_measures: List[str] = Field(default_factory=list)
    data_types_handled: List[str] = Field(default_factory=list)
    compliance_certifications: List[str] = Field(default_factory=list)
    previous_incidents: bool = False
    incident_count_last_year: int = 0

class FinancialHealth(BaseModel):
    credit_rating: Optional[str] = None
    debt_to_equity_ratio: Optional[float] = None
    current_ratio: Optional[float] = None
    revenue_trend: Optional[str] = None  # "improving", "stable", "declining"
    profitability_trend: Optional[str] = None

# Enhanced Risk Assessment
class RiskFactorDetail(BaseModel):
    category: str
    factor: str
    impact_level: str  # "Low", "Medium", "High", "Critical"
    score_impact: float
    description: str
    mitigation_recommendation: Optional[str] = None

class ComprehensiveRiskAssessment(BaseModel):
    overall_score: float = Field(..., ge=0, le=100)
    technical_score: float = Field(..., ge=0, le=100)
    operational_score: float = Field(..., ge=0, le=100)
    financial_score: float = Field(..., ge=0, le=100)
    compliance_score: float = Field(..., ge=0, le=100)
    risk_factors: List[RiskFactorDetail] = Field(default_factory=list)
    industry_benchmark: Optional[float] = None
    risk_level: str  # "Low", "Medium", "High", "Critical"
    confidence_score: float = Field(..., ge=0, le=100)

# Policy and Coverage Models
class CoverageLimits(BaseModel):
    per_claim_limit: float
    aggregate_limit: float
    retention_deductible: float
    sub_limits: Dict[str, float] = Field(default_factory=dict)

class CoverageComponents(BaseModel):
    first_party_coverage: bool = True
    third_party_coverage: bool = True
    regulatory_fines: bool = False
    media_liability: bool = False
    business_interruption: bool = False
    cyber_extortion: bool = False

class PolicyDetails(BaseModel):
    coverage_type: str
    limits: CoverageLimits
    components: CoverageComponents
    exclusions: List[str] = Field(default_factory=list)
    endorsements: List[str] = Field(default_factory=list)
    policy_term_months: int = 12
    territory: str = "USA"

# Pricing Intelligence
class PricingFactors(BaseModel):
    base_premium: float
    risk_adjustment: float
    industry_multiplier: float
    experience_modifier: float
    final_premium: float

class CompetitiveAnalysis(BaseModel):
    market_min: float
    market_max: float
    market_average: float
    our_position: str  # "competitive", "high", "low"
    win_probability: float = Field(..., ge=0, le=100)

class QuoteInformation(BaseModel):
    recommended_premium: float
    pricing_factors: PricingFactors
    competitive_analysis: CompetitiveAnalysis
    margin_analysis: Dict[str, float] = Field(default_factory=dict)
    quote_validity_days: int = 30

# Assignment and Workflow Models
class UnderwriterExpertise(BaseModel):
    industries: List[str] = Field(default_factory=list)
    coverage_types: List[str] = Field(default_factory=list)
    max_authority_limit: float
    specializations: List[str] = Field(default_factory=list)

class UnderwriterWorkload(BaseModel):
    current_assignments: int
    capacity: int
    utilization_percentage: float
    average_processing_time_days: float
    pending_urgent_items: int

class AssignmentRecommendation(BaseModel):
    underwriter: UserDetail
    recommendation_score: int = Field(..., ge=0, le=100)
    expertise_match: List[str] = Field(default_factory=list)
    workload_factor: float
    reasons: List[str] = Field(default_factory=list)
    estimated_processing_time: float

# Communication and Messaging
class MessageThread(BaseModel):
    thread_id: str
    subject: str
    participants: List[str] = Field(default_factory=list)
    message_count: int
    last_message_at: datetime
    is_urgent: bool = False
    status: str = "active"  # active, closed, escalated

class CommunicationSummary(BaseModel):
    broker_correspondence: List[MessageThread] = Field(default_factory=list)
    internal_discussions: List[MessageThread] = Field(default_factory=list)
    information_requests: int = 0
    responses_pending: int = 0
    escalated_items: int = 0

# Decision Support Models
class AutomatedRecommendation(BaseModel):
    action: str  # "approve", "decline", "request_info", "refer_to_senior"
    confidence: float = Field(..., ge=0, le=100)
    reasoning: List[str] = Field(default_factory=list)
    suggested_conditions: List[str] = Field(default_factory=list)
    referral_triggers: Optional[List[str]] = None
    estimated_premium_range: Optional[Dict[str, float]] = None

class ComplianceChecks(BaseModel):
    required_filings: List[str] = Field(default_factory=list)
    jurisdiction_requirements: List[str] = Field(default_factory=list)
    regulatory_alerts: List[str] = Field(default_factory=list)
    compliance_score: float = Field(..., ge=0, le=100)
    outstanding_requirements: List[str] = Field(default_factory=list)

# Main Dashboard Response Models
class UnderwriterDashboard(BaseModel):
    underwriter_id: str
    underwriter_name: str
    last_updated: datetime
    kpis: DashboardKPIs
    work_queue: WorkQueueSummary
    team_metrics: TeamMetrics
    portfolio_summary: PortfolioSummary
    processing_metrics: ProcessingMetrics

class SubmissionDetailView(BaseModel):
    work_item: WorkItemSummary
    company_profile: CompanyProfile
    cybersecurity_posture: CybersecurityPosture
    financial_health: FinancialHealth
    risk_assessment: ComprehensiveRiskAssessment
    policy_details: PolicyDetails
    quote_information: Optional[QuoteInformation] = None
    assignment_recommendation: Optional[AssignmentRecommendation] = None
    communication_summary: CommunicationSummary
    automated_recommendation: AutomatedRecommendation
    compliance_checks: ComplianceChecks

# Analytics and Reporting Models
class AnalyticsTimeSeriesPoint(BaseModel):
    date: datetime
    value: float
    label: Optional[str] = None

class AnalyticsTimeSeries(BaseModel):
    metric_name: str
    data_points: List[AnalyticsTimeSeriesPoint]
    trend: MetricTrend
    growth_rate: Optional[float] = None

class BenchmarkComparison(BaseModel):
    metric: str
    our_value: float
    industry_average: float
    top_quartile: float
    bottom_quartile: float
    percentile_rank: float

class PortfolioAnalyticsReport(BaseModel):
    timeframe: DashboardTimeframe
    generated_at: datetime
    key_metrics: List[KPIMetric]
    time_series: List[AnalyticsTimeSeries]
    benchmarks: List[BenchmarkComparison]
    insights: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)

# API Request Models
class DashboardRequest(BaseModel):
    underwriter_id: Optional[str] = None
    timeframe: DashboardTimeframe = DashboardTimeframe.WEEK
    include_team_metrics: bool = True
    include_portfolio_analytics: bool = True

class WorkQueueRequest(BaseModel):
    underwriter_id: Optional[str] = None
    priority_filter: Optional[str] = None
    status_filter: Optional[List[WorkItemStatusEnum]] = None
    industry_filter: Optional[List[str]] = None
    risk_score_range: Optional[Dict[str, float]] = None  # {"min": 0, "max": 100}
    limit: int = 50

class AnalyticsRequest(BaseModel):
    timeframe: DashboardTimeframe
    metrics: List[str] = Field(default_factory=list)
    include_benchmarks: bool = True
    include_trends: bool = True
    group_by: Optional[str] = None  # "industry", "coverage_type", "underwriter"