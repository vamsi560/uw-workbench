"""
Portfolio Analytics and Benchmarking Service
Advanced analytics for underwriter performance tracking and portfolio management
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case, text, desc
from collections import defaultdict
import statistics
import json

from database import (
    WorkItem, User, RiskAssessment, Submission, WorkItemHistory, 
    Comment, WorkItemStatus, WorkItemPriority, CompanySize
)
from dashboard_models import (
    PortfolioAnalyticsReport, DashboardTimeframe, KPIMetric, MetricTrend,
    AnalyticsTimeSeries, AnalyticsTimeSeriesPoint, BenchmarkComparison,
    IndustryRiskMetrics, CoverageTypeMetrics, RiskDistribution
)
from enhanced_risk_scoring import RiskBenchmarkingService

logger = logging.getLogger(__name__)

class PortfolioAnalyticsService:
    """Advanced portfolio analytics and performance tracking"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_portfolio_report(
        self,
        underwriter_id: str,
        timeframe: DashboardTimeframe,
        include_benchmarks: bool = True,
        include_trends: bool = True
    ) -> PortfolioAnalyticsReport:
        """Generate comprehensive portfolio analytics report"""
        
        start_date, end_date = self._get_timeframe_bounds(timeframe)
        
        # Get work items for analysis
        work_items = self._get_work_items_for_analysis(underwriter_id, start_date, end_date)
        
        # Calculate key metrics
        key_metrics = self._calculate_key_metrics(work_items, start_date, end_date)
        
        # Generate time series data
        time_series = []
        if include_trends:
            time_series = self._generate_time_series_analytics(underwriter_id, timeframe)
        
        # Generate benchmarks
        benchmarks = []
        if include_benchmarks:
            benchmarks = self._generate_benchmark_comparisons(underwriter_id, work_items)
        
        # Generate insights and recommendations
        insights = self._generate_portfolio_insights(work_items, key_metrics, benchmarks)
        recommendations = self._generate_portfolio_recommendations(work_items, key_metrics, benchmarks)
        
        return PortfolioAnalyticsReport(
            timeframe=timeframe,
            generated_at=datetime.utcnow(),
            key_metrics=key_metrics,
            time_series=time_series,
            benchmarks=benchmarks,
            insights=insights,
            recommendations=recommendations
        )
    
    def get_industry_performance_comparison(
        self,
        underwriter_id: str,
        timeframe: DashboardTimeframe
    ) -> Dict[str, Any]:
        """Compare underwriter performance against industry benchmarks"""
        
        start_date, end_date = self._get_timeframe_bounds(timeframe)
        work_items = self._get_work_items_for_analysis(underwriter_id, start_date, end_date)
        
        # Group by industry
        industry_performance = defaultdict(lambda: {
            "count": 0,
            "total_premium": 0,
            "risk_scores": [],
            "processing_times": [],
            "approval_rate": 0
        })
        
        for item in work_items:
            if item.industry:
                industry_data = industry_performance[item.industry]
                industry_data["count"] += 1
                
                if item.coverage_amount:
                    industry_data["total_premium"] += item.coverage_amount * 0.05  # Mock premium rate
                
                if item.risk_score:
                    industry_data["risk_scores"].append(item.risk_score)
                
                processing_time = (item.updated_at - item.created_at).days
                industry_data["processing_times"].append(processing_time)
                
                if item.status == WorkItemStatus.APPROVED:
                    industry_data["approval_rate"] += 1
        
        # Calculate metrics and compare to benchmarks
        comparison_results = {}
        
        for industry, data in industry_performance.items():
            if data["count"] > 0:
                # Calculate metrics
                avg_risk_score = statistics.mean(data["risk_scores"]) if data["risk_scores"] else 0
                avg_processing_time = statistics.mean(data["processing_times"]) if data["processing_times"] else 0
                approval_rate = (data["approval_rate"] / data["count"]) * 100
                avg_premium = data["total_premium"] / data["count"] if data["count"] > 0 else 0
                
                # Get industry benchmarks
                benchmarks = RiskBenchmarkingService.get_industry_benchmarks(industry)
                
                comparison_results[industry] = {
                    "metrics": {
                        "count": data["count"],
                        "avg_risk_score": avg_risk_score,
                        "avg_processing_time": avg_processing_time,
                        "approval_rate": approval_rate,
                        "avg_premium": avg_premium,
                        "total_premium": data["total_premium"]
                    },
                    "benchmarks": benchmarks,
                    "performance": {
                        "risk_score_vs_benchmark": avg_risk_score - benchmarks["industry_average"],
                        "processing_efficiency": "Above Average" if avg_processing_time < 5 else "Below Average",
                        "market_position": self._determine_market_position(avg_premium, industry)
                    }
                }
        
        return comparison_results
    
    def get_risk_distribution_analysis(
        self,
        underwriter_id: Optional[str] = None,
        timeframe: DashboardTimeframe = DashboardTimeframe.MONTH
    ) -> Dict[str, Any]:
        """Analyze risk distribution across portfolio"""
        
        start_date, end_date = self._get_timeframe_bounds(timeframe)
        
        query = self.db.query(WorkItem).filter(
            WorkItem.created_at.between(start_date, end_date),
            WorkItem.risk_score.isnot(None)
        )
        
        if underwriter_id:
            query = query.filter(WorkItem.assigned_to == underwriter_id)
        
        work_items = query.all()
        
        # Risk score distribution
        risk_buckets = {
            "0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0
        }
        
        industry_risk_dist = defaultdict(lambda: defaultdict(int))
        coverage_risk_dist = defaultdict(lambda: defaultdict(int))
        
        for item in work_items:
            score = item.risk_score
            
            # Overall distribution
            if score <= 20:
                risk_buckets["0-20"] += 1
            elif score <= 40:
                risk_buckets["21-40"] += 1
            elif score <= 60:
                risk_buckets["41-60"] += 1
            elif score <= 80:
                risk_buckets["61-80"] += 1
            else:
                risk_buckets["81-100"] += 1
            
            # Industry distribution
            if item.industry:
                bucket = self._get_risk_bucket(score)
                industry_risk_dist[item.industry][bucket] += 1
            
            # Coverage amount distribution
            if item.coverage_amount:
                coverage_range = self._get_coverage_range(item.coverage_amount)
                bucket = self._get_risk_bucket(score)
                coverage_risk_dist[coverage_range][bucket] += 1
        
        total_items = len(work_items)
        
        return {
            "overall_distribution": {
                bucket: {"count": count, "percentage": (count / total_items) * 100 if total_items > 0 else 0}
                for bucket, count in risk_buckets.items()
            },
            "industry_distribution": dict(industry_risk_dist),
            "coverage_distribution": dict(coverage_risk_dist),
            "statistics": {
                "total_items": total_items,
                "avg_risk_score": statistics.mean([item.risk_score for item in work_items]) if work_items else 0,
                "median_risk_score": statistics.median([item.risk_score for item in work_items]) if work_items else 0,
                "risk_score_std": statistics.stdev([item.risk_score for item in work_items]) if len(work_items) > 1 else 0
            }
        }
    
    def get_performance_trends(
        self,
        underwriter_id: str,
        metrics: List[str],
        timeframe: DashboardTimeframe
    ) -> Dict[str, AnalyticsTimeSeries]:
        """Get performance trends for specific metrics"""
        
        trends = {}
        
        for metric in metrics:
            if metric == "risk_score":
                trends[metric] = self._get_risk_score_trend(underwriter_id, timeframe)
            elif metric == "processing_time":
                trends[metric] = self._get_processing_time_trend(underwriter_id, timeframe)
            elif metric == "approval_rate":
                trends[metric] = self._get_approval_rate_trend(underwriter_id, timeframe)
            elif metric == "premium_volume":
                trends[metric] = self._get_premium_volume_trend(underwriter_id, timeframe)
            elif metric == "submission_count":
                trends[metric] = self._get_submission_count_trend(underwriter_id, timeframe)
        
        return trends
    
    def get_competitive_analysis(
        self,
        underwriter_id: str,
        timeframe: DashboardTimeframe
    ) -> Dict[str, Any]:
        """Compare underwriter performance against team averages"""
        
        start_date, end_date = self._get_timeframe_bounds(timeframe)
        
        # Get underwriter metrics
        underwriter_metrics = self._calculate_underwriter_metrics(underwriter_id, start_date, end_date)
        
        # Get team averages (excluding current underwriter)
        team_metrics = self._calculate_team_averages(underwriter_id, start_date, end_date)
        
        # Calculate percentile rankings
        percentiles = self._calculate_percentile_rankings(underwriter_id, start_date, end_date)
        
        return {
            "underwriter_metrics": underwriter_metrics,
            "team_averages": team_metrics,
            "percentile_rankings": percentiles,
            "performance_gaps": {
                metric: underwriter_metrics[metric] - team_metrics[metric]
                for metric in underwriter_metrics.keys()
                if metric in team_metrics
            },
            "strengths": self._identify_performance_strengths(underwriter_metrics, team_metrics),
            "improvement_areas": self._identify_improvement_areas(underwriter_metrics, team_metrics)
        }
    
    def _get_work_items_for_analysis(
        self, 
        underwriter_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[WorkItem]:
        """Get work items for analysis"""
        
        return self.db.query(WorkItem).filter(
            WorkItem.assigned_to == underwriter_id,
            WorkItem.created_at.between(start_date, end_date)
        ).all()
    
    def _calculate_key_metrics(
        self, 
        work_items: List[WorkItem],
        start_date: datetime,
        end_date: datetime
    ) -> List[KPIMetric]:
        """Calculate key portfolio metrics"""
        
        total_items = len(work_items)
        
        if total_items == 0:
            return []
        
        # Calculate metrics
        approved_count = sum(1 for item in work_items if item.status == WorkItemStatus.APPROVED)
        declined_count = sum(1 for item in work_items if item.status == WorkItemStatus.REJECTED)
        avg_risk_score = statistics.mean([item.risk_score for item in work_items if item.risk_score])
        total_premium = sum(item.coverage_amount * 0.05 for item in work_items if item.coverage_amount)
        
        processing_times = [
            (item.updated_at - item.created_at).days 
            for item in work_items 
            if item.status in [WorkItemStatus.APPROVED, WorkItemStatus.REJECTED]
        ]
        avg_processing_time = statistics.mean(processing_times) if processing_times else 0
        
        return [
            KPIMetric(
                name="Total Submissions",
                value=total_items,
                unit="count"
            ),
            KPIMetric(
                name="Approval Rate",
                value=(approved_count / total_items) * 100,
                unit="percentage"
            ),
            KPIMetric(
                name="Decline Rate", 
                value=(declined_count / total_items) * 100,
                unit="percentage"
            ),
            KPIMetric(
                name="Average Risk Score",
                value=avg_risk_score,
                unit="score"
            ),
            KPIMetric(
                name="Total Premium Volume",
                value=total_premium,
                unit="currency"
            ),
            KPIMetric(
                name="Average Processing Time",
                value=avg_processing_time,
                unit="days"
            )
        ]
    
    def _generate_time_series_analytics(
        self,
        underwriter_id: str,
        timeframe: DashboardTimeframe
    ) -> List[AnalyticsTimeSeries]:
        """Generate time series analytics"""
        
        # For now, return empty list - would implement actual time series queries
        return []
    
    def _generate_benchmark_comparisons(
        self,
        underwriter_id: str,
        work_items: List[WorkItem]
    ) -> List[BenchmarkComparison]:
        """Generate benchmark comparisons"""
        
        if not work_items:
            return []
        
        # Calculate underwriter metrics
        avg_risk_score = statistics.mean([item.risk_score for item in work_items if item.risk_score])
        approval_rate = (sum(1 for item in work_items if item.status == WorkItemStatus.APPROVED) / len(work_items)) * 100
        
        # Mock industry benchmarks (would come from actual data)
        benchmarks = [
            BenchmarkComparison(
                metric="Average Risk Score",
                our_value=avg_risk_score,
                industry_average=55.0,
                top_quartile=45.0,
                bottom_quartile=65.0,
                percentile_rank=self._calculate_percentile(avg_risk_score, 55.0, 10.0)
            ),
            BenchmarkComparison(
                metric="Approval Rate",
                our_value=approval_rate,
                industry_average=75.0,
                top_quartile=85.0,
                bottom_quartile=65.0,
                percentile_rank=self._calculate_percentile(approval_rate, 75.0, 8.0)
            )
        ]
        
        return benchmarks
    
    def _generate_portfolio_insights(
        self,
        work_items: List[WorkItem],
        key_metrics: List[KPIMetric],
        benchmarks: List[BenchmarkComparison]
    ) -> List[str]:
        """Generate portfolio insights"""
        
        insights = []
        
        if not work_items:
            return ["No data available for analysis"]
        
        # Risk concentration analysis
        high_risk_count = sum(1 for item in work_items if item.risk_score and item.risk_score > 70)
        if high_risk_count / len(work_items) > 0.3:
            insights.append(f"High concentration of high-risk submissions ({high_risk_count}/{len(work_items)})")
        
        # Industry concentration
        industry_counts = defaultdict(int)
        for item in work_items:
            if item.industry:
                industry_counts[item.industry] += 1
        
        if industry_counts:
            top_industry = max(industry_counts, key=industry_counts.get)
            concentration = industry_counts[top_industry] / len(work_items)
            if concentration > 0.4:
                insights.append(f"Heavy concentration in {top_industry} industry ({concentration:.1%})")
        
        # Processing efficiency
        processing_times = [
            (item.updated_at - item.created_at).days 
            for item in work_items 
            if item.status in [WorkItemStatus.APPROVED, WorkItemStatus.REJECTED]
        ]
        
        if processing_times:
            avg_time = statistics.mean(processing_times)
            if avg_time > 7:
                insights.append(f"Processing time above target (avg: {avg_time:.1f} days)")
            elif avg_time < 3:
                insights.append(f"Excellent processing efficiency (avg: {avg_time:.1f} days)")
        
        # Coverage amount analysis
        coverage_amounts = [item.coverage_amount for item in work_items if item.coverage_amount]
        if coverage_amounts:
            avg_coverage = statistics.mean(coverage_amounts)
            if avg_coverage > 5_000_000:
                insights.append(f"Portfolio focused on large accounts (avg coverage: ${avg_coverage:,.0f})")
        
        return insights
    
    def _generate_portfolio_recommendations(
        self,
        work_items: List[WorkItem],
        key_metrics: List[KPIMetric],
        benchmarks: List[BenchmarkComparison]
    ) -> List[str]:
        """Generate portfolio recommendations"""
        
        recommendations = []
        
        if not work_items:
            return ["No recommendations available"]
        
        # Risk management recommendations
        high_risk_ratio = sum(1 for item in work_items if item.risk_score and item.risk_score > 70) / len(work_items)
        if high_risk_ratio > 0.3:
            recommendations.append("Consider tightening underwriting guidelines for high-risk submissions")
        
        # Processing efficiency recommendations
        processing_times = [
            (item.updated_at - item.created_at).days 
            for item in work_items 
            if item.status in [WorkItemStatus.APPROVED, WorkItemStatus.REJECTED]
        ]
        
        if processing_times and statistics.mean(processing_times) > 7:
            recommendations.append("Focus on reducing processing time through workflow optimization")
        
        # Diversification recommendations
        industry_counts = defaultdict(int)
        for item in work_items:
            if item.industry:
                industry_counts[item.industry] += 1
        
        if industry_counts:
            top_industry_ratio = max(industry_counts.values()) / len(work_items)
            if top_industry_ratio > 0.5:
                recommendations.append("Consider diversifying industry exposure to reduce concentration risk")
        
        # Benchmark-based recommendations
        for benchmark in benchmarks:
            if benchmark.percentile_rank < 25:
                recommendations.append(f"Improve {benchmark.metric} performance (currently in bottom quartile)")
        
        return recommendations
    
    def _get_risk_score_trend(self, underwriter_id: str, timeframe: DashboardTimeframe) -> AnalyticsTimeSeries:
        """Get risk score trend over time"""
        
        # Mock implementation - would query actual historical data
        data_points = [
            AnalyticsTimeSeriesPoint(date=datetime.utcnow() - timedelta(days=30), value=52.5),
            AnalyticsTimeSeriesPoint(date=datetime.utcnow() - timedelta(days=20), value=48.2),
            AnalyticsTimeSeriesPoint(date=datetime.utcnow() - timedelta(days=10), value=51.8),
            AnalyticsTimeSeriesPoint(date=datetime.utcnow(), value=49.3)
        ]
        
        return AnalyticsTimeSeries(
            metric_name="Average Risk Score",
            data_points=data_points,
            trend=MetricTrend.DOWN,
            growth_rate=-2.1
        )
    
    def _get_processing_time_trend(self, underwriter_id: str, timeframe: DashboardTimeframe) -> AnalyticsTimeSeries:
        """Get processing time trend over time"""
        
        # Mock implementation
        data_points = [
            AnalyticsTimeSeriesPoint(date=datetime.utcnow() - timedelta(days=30), value=5.2),
            AnalyticsTimeSeriesPoint(date=datetime.utcnow() - timedelta(days=20), value=4.8),
            AnalyticsTimeSeriesPoint(date=datetime.utcnow() - timedelta(days=10), value=4.1),
            AnalyticsTimeSeriesPoint(date=datetime.utcnow(), value=3.9)
        ]
        
        return AnalyticsTimeSeries(
            metric_name="Average Processing Time",
            data_points=data_points,
            trend=MetricTrend.DOWN,
            growth_rate=-8.5
        )
    
    def _get_approval_rate_trend(self, underwriter_id: str, timeframe: DashboardTimeframe) -> AnalyticsTimeSeries:
        """Get approval rate trend over time"""
        
        # Mock implementation
        data_points = [
            AnalyticsTimeSeriesPoint(date=datetime.utcnow() - timedelta(days=30), value=72.0),
            AnalyticsTimeSeriesPoint(date=datetime.utcnow() - timedelta(days=20), value=75.5),
            AnalyticsTimeSeriesPoint(date=datetime.utcnow() - timedelta(days=10), value=78.2),
            AnalyticsTimeSeriesPoint(date=datetime.utcnow(), value=76.8)
        ]
        
        return AnalyticsTimeSeries(
            metric_name="Approval Rate",
            data_points=data_points,
            trend=MetricTrend.UP,
            growth_rate=3.2
        )
    
    def _get_premium_volume_trend(self, underwriter_id: str, timeframe: DashboardTimeframe) -> AnalyticsTimeSeries:
        """Get premium volume trend over time"""
        
        # Mock implementation
        data_points = [
            AnalyticsTimeSeriesPoint(date=datetime.utcnow() - timedelta(days=30), value=125000),
            AnalyticsTimeSeriesPoint(date=datetime.utcnow() - timedelta(days=20), value=142000),
            AnalyticsTimeSeriesPoint(date=datetime.utcnow() - timedelta(days=10), value=138000),
            AnalyticsTimeSeriesPoint(date=datetime.utcnow(), value=156000)
        ]
        
        return AnalyticsTimeSeries(
            metric_name="Premium Volume",
            data_points=data_points,
            trend=MetricTrend.UP,
            growth_rate=12.8
        )
    
    def _get_submission_count_trend(self, underwriter_id: str, timeframe: DashboardTimeframe) -> AnalyticsTimeSeries:
        """Get submission count trend over time"""
        
        # Mock implementation
        data_points = [
            AnalyticsTimeSeriesPoint(date=datetime.utcnow() - timedelta(days=30), value=25),
            AnalyticsTimeSeriesPoint(date=datetime.utcnow() - timedelta(days=20), value=32),
            AnalyticsTimeSeriesPoint(date=datetime.utcnow() - timedelta(days=10), value=28),
            AnalyticsTimeSeriesPoint(date=datetime.utcnow(), value=35)
        ]
        
        return AnalyticsTimeSeries(
            metric_name="Submission Count",
            data_points=data_points,
            trend=MetricTrend.UP,
            growth_rate=18.5
        )
    
    def _calculate_underwriter_metrics(
        self, 
        underwriter_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, float]:
        """Calculate comprehensive metrics for an underwriter"""
        
        work_items = self.db.query(WorkItem).filter(
            WorkItem.assigned_to == underwriter_id,
            WorkItem.created_at.between(start_date, end_date)
        ).all()
        
        if not work_items:
            return {}
        
        completed_items = [item for item in work_items if item.status in [WorkItemStatus.APPROVED, WorkItemStatus.REJECTED]]
        
        metrics = {
            "submission_count": len(work_items),
            "approval_rate": (sum(1 for item in work_items if item.status == WorkItemStatus.APPROVED) / len(work_items)) * 100,
            "decline_rate": (sum(1 for item in work_items if item.status == WorkItemStatus.REJECTED) / len(work_items)) * 100,
            "avg_risk_score": statistics.mean([item.risk_score for item in work_items if item.risk_score]) if any(item.risk_score for item in work_items) else 0,
            "avg_processing_time": statistics.mean([(item.updated_at - item.created_at).days for item in completed_items]) if completed_items else 0,
            "total_premium": sum(item.coverage_amount * 0.05 for item in work_items if item.coverage_amount),
            "avg_coverage_amount": statistics.mean([item.coverage_amount for item in work_items if item.coverage_amount]) if any(item.coverage_amount for item in work_items) else 0
        }
        
        return metrics
    
    def _calculate_team_averages(
        self, 
        exclude_underwriter_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, float]:
        """Calculate team average metrics excluding specific underwriter"""
        
        work_items = self.db.query(WorkItem).filter(
            WorkItem.assigned_to != exclude_underwriter_id,
            WorkItem.assigned_to.isnot(None),
            WorkItem.created_at.between(start_date, end_date)
        ).all()
        
        if not work_items:
            return {}
        
        completed_items = [item for item in work_items if item.status in [WorkItemStatus.APPROVED, WorkItemStatus.REJECTED]]
        
        # Group by underwriter
        underwriter_metrics = defaultdict(list)
        for item in work_items:
            underwriter_metrics[item.assigned_to].append(item)
        
        # Calculate averages across underwriters
        team_submission_counts = [len(items) for items in underwriter_metrics.values()]
        team_approval_rates = [
            (sum(1 for item in items if item.status == WorkItemStatus.APPROVED) / len(items)) * 100
            for items in underwriter_metrics.values()
        ]
        
        return {
            "avg_submission_count": statistics.mean(team_submission_counts) if team_submission_counts else 0,
            "avg_approval_rate": statistics.mean(team_approval_rates) if team_approval_rates else 0,
            "avg_risk_score": statistics.mean([item.risk_score for item in work_items if item.risk_score]) if any(item.risk_score for item in work_items) else 0,
            "avg_processing_time": statistics.mean([(item.updated_at - item.created_at).days for item in completed_items]) if completed_items else 0
        }
    
    def _calculate_percentile_rankings(
        self, 
        underwriter_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, float]:
        """Calculate percentile rankings for underwriter performance"""
        
        # Get all underwriters' metrics
        underwriter_performance = {}
        
        underwriters = self.db.query(WorkItem.assigned_to).filter(
            WorkItem.assigned_to.isnot(None),
            WorkItem.created_at.between(start_date, end_date)
        ).distinct().all()
        
        for (uw_id,) in underwriters:
            metrics = self._calculate_underwriter_metrics(uw_id, start_date, end_date)
            underwriter_performance[uw_id] = metrics
        
        # Calculate percentiles
        percentiles = {}
        
        if underwriter_id in underwriter_performance:
            user_metrics = underwriter_performance[underwriter_id]
            
            for metric, value in user_metrics.items():
                all_values = [metrics.get(metric, 0) for metrics in underwriter_performance.values() if metric in metrics]
                if all_values:
                    sorted_values = sorted(all_values)
                    rank = sorted_values.index(value) + 1
                    percentile = (rank / len(sorted_values)) * 100
                    percentiles[metric] = percentile
        
        return percentiles
    
    def _identify_performance_strengths(
        self, 
        underwriter_metrics: Dict[str, float], 
        team_metrics: Dict[str, float]
    ) -> List[str]:
        """Identify performance strengths"""
        
        strengths = []
        
        for metric, value in underwriter_metrics.items():
            if metric in team_metrics:
                if metric in ["approval_rate", "total_premium", "avg_coverage_amount"] and value > team_metrics[metric] * 1.1:
                    strengths.append(f"Above average {metric.replace('_', ' ')}")
                elif metric in ["avg_processing_time", "decline_rate"] and value < team_metrics[metric] * 0.9:
                    strengths.append(f"Below average {metric.replace('_', ' ')}")
        
        return strengths
    
    def _identify_improvement_areas(
        self, 
        underwriter_metrics: Dict[str, float], 
        team_metrics: Dict[str, float]
    ) -> List[str]:
        """Identify areas for improvement"""
        
        improvements = []
        
        for metric, value in underwriter_metrics.items():
            if metric in team_metrics:
                if metric in ["approval_rate", "total_premium", "avg_coverage_amount"] and value < team_metrics[metric] * 0.9:
                    improvements.append(f"Below average {metric.replace('_', ' ')}")
                elif metric in ["avg_processing_time", "decline_rate"] and value > team_metrics[metric] * 1.1:
                    improvements.append(f"Above average {metric.replace('_', ' ')}")
        
        return improvements
    
    def _determine_market_position(self, avg_premium: float, industry: str) -> str:
        """Determine market position based on premium levels"""
        
        # Mock industry premium benchmarks
        industry_benchmarks = {
            "Healthcare": 15000,
            "Financial Services": 20000,
            "Technology": 12000,
            "Manufacturing": 8000,
            "Retail": 10000
        }
        
        benchmark = industry_benchmarks.get(industry, 12000)
        
        if avg_premium > benchmark * 1.2:
            return "Premium Market"
        elif avg_premium > benchmark * 0.8:
            return "Market Rate"
        else:
            return "Competitive Market"
    
    def _get_risk_bucket(self, score: float) -> str:
        """Get risk bucket for score"""
        if score <= 40:
            return "Low"
        elif score <= 70:
            return "Medium"
        else:
            return "High"
    
    def _get_coverage_range(self, amount: float) -> str:
        """Get coverage range for amount"""
        if amount <= 1_000_000:
            return "$0-1M"
        elif amount <= 5_000_000:
            return "$1-5M"
        elif amount <= 10_000_000:
            return "$5-10M"
        else:
            return "$10M+"
    
    def _calculate_percentile(self, value: float, mean: float, std: float) -> float:
        """Calculate percentile rank (mock implementation)"""
        # Simplified percentile calculation
        z_score = (value - mean) / std if std > 0 else 0
        
        # Convert z-score to approximate percentile
        if z_score <= -2:
            return 2.5
        elif z_score <= -1:
            return 16
        elif z_score <= 0:
            return 50
        elif z_score <= 1:
            return 84
        elif z_score <= 2:
            return 97.5
        else:
            return 99
    
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