"""
Enhanced Risk Scoring Engine for Cyber Insurance
Advanced risk assessment algorithms with machine learning-style scoring
"""

import logging
import json
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from collections import defaultdict
import re

from business_rules import CyberInsuranceValidator
from business_config import BusinessConfig
from dashboard_models import (
    RiskFactorDetail, ComprehensiveRiskAssessment, 
    CompanyProfile, CybersecurityPosture
)

logger = logging.getLogger(__name__)

class EnhancedRiskScoringEngine:
    """
    Advanced risk scoring engine that analyzes multiple dimensions of cyber risk
    """
    
    # Industry risk multipliers (more comprehensive)
    INDUSTRY_RISK_PROFILES = {
        "Healthcare": {
            "base_multiplier": 1.4,
            "data_sensitivity": 0.8,
            "regulatory_burden": 0.9,
            "attack_frequency": 0.7,
            "common_threats": ["ransomware", "phi_theft", "insider_threats"]
        },
        "Financial Services": {
            "base_multiplier": 1.5,
            "data_sensitivity": 0.9,
            "regulatory_burden": 0.8,
            "attack_frequency": 0.8,
            "common_threats": ["account_takeover", "wire_fraud", "data_breach"]
        },
        "Technology": {
            "base_multiplier": 1.2,
            "data_sensitivity": 0.6,
            "regulatory_burden": 0.3,
            "attack_frequency": 0.9,
            "common_threats": ["ip_theft", "ddos", "supply_chain"]
        },
        "Manufacturing": {
            "base_multiplier": 1.1,
            "data_sensitivity": 0.4,
            "regulatory_burden": 0.4,
            "attack_frequency": 0.5,
            "common_threats": ["operational_disruption", "ip_theft", "supply_chain"]
        },
        "Retail": {
            "base_multiplier": 1.3,
            "data_sensitivity": 0.7,
            "regulatory_burden": 0.5,
            "attack_frequency": 0.6,
            "common_threats": ["payment_card_fraud", "customer_data_breach", "pos_malware"]
        },
        "Education": {
            "base_multiplier": 1.0,
            "data_sensitivity": 0.6,
            "regulatory_burden": 0.6,
            "attack_frequency": 0.4,
            "common_threats": ["student_data_breach", "research_theft", "ransomware"]
        },
        "Government": {
            "base_multiplier": 1.6,
            "data_sensitivity": 0.9,
            "regulatory_burden": 0.9,
            "attack_frequency": 0.8,
            "common_threats": ["nation_state", "sensitive_data_breach", "infrastructure_attack"]
        }
    }
    
    # Security control effectiveness scores (0-1, higher is better)
    SECURITY_CONTROLS = {
        "multi_factor_authentication": {"effectiveness": 0.85, "category": "technical"},
        "encryption_at_rest": {"effectiveness": 0.7, "category": "technical"},
        "encryption_in_transit": {"effectiveness": 0.6, "category": "technical"},
        "endpoint_detection": {"effectiveness": 0.8, "category": "technical"},
        "network_segmentation": {"effectiveness": 0.75, "category": "technical"},
        "security_awareness_training": {"effectiveness": 0.6, "category": "operational"},
        "incident_response_plan": {"effectiveness": 0.65, "category": "operational"},
        "vulnerability_management": {"effectiveness": 0.7, "category": "operational"},
        "backup_and_recovery": {"effectiveness": 0.8, "category": "operational"},
        "privileged_access_management": {"effectiveness": 0.85, "category": "technical"},
        "security_information_event_management": {"effectiveness": 0.75, "category": "technical"},
        "data_loss_prevention": {"effectiveness": 0.65, "category": "technical"},
        "web_application_firewall": {"effectiveness": 0.6, "category": "technical"},
        "penetration_testing": {"effectiveness": 0.7, "category": "operational"},
        "security_governance": {"effectiveness": 0.6, "category": "operational"}
    }
    
    # Data type risk weights
    DATA_TYPE_RISKS = {
        "personal_identifiable_information": 0.8,
        "protected_health_information": 0.9,
        "payment_card_information": 0.85,
        "financial_records": 0.8,
        "intellectual_property": 0.75,
        "customer_data": 0.7,
        "employee_data": 0.65,
        "operational_data": 0.4,
        "marketing_data": 0.3,
        "public_data": 0.1
    }
    
    @classmethod
    def calculate_enhanced_risk_score(
        cls, 
        extracted_fields: Dict[str, Any],
        historical_data: Optional[Dict] = None
    ) -> ComprehensiveRiskAssessment:
        """
        Calculate comprehensive risk assessment with advanced scoring
        """
        
        # Initialize risk categories
        risk_categories = {
            "technical": 50.0,
            "operational": 50.0,
            "financial": 50.0,
            "compliance": 50.0
        }
        
        risk_factors = []
        
        # 1. Industry-based risk assessment
        industry_score, industry_factors = cls._assess_industry_risk(extracted_fields)
        risk_factors.extend(industry_factors)
        
        # 2. Company size and complexity assessment
        size_score, size_factors = cls._assess_company_size_risk(extracted_fields)
        risk_factors.extend(size_factors)
        
        # 3. Data type and sensitivity assessment
        data_score, data_factors = cls._assess_data_risk(extracted_fields)
        risk_factors.extend(data_factors)
        
        # 4. Security posture assessment
        security_score, security_factors = cls._assess_security_posture(extracted_fields)
        risk_factors.extend(security_factors)
        
        # 5. Financial stability assessment
        financial_score, financial_factors = cls._assess_financial_risk(extracted_fields)
        risk_factors.extend(financial_factors)
        
        # 6. Compliance and regulatory assessment
        compliance_score, compliance_factors = cls._assess_compliance_risk(extracted_fields)
        risk_factors.extend(compliance_factors)
        
        # 7. Historical performance (if available)
        if historical_data:
            history_score, history_factors = cls._assess_historical_risk(historical_data)
            risk_factors.extend(history_factors)
        else:
            history_score = 0
        
        # Combine scores with weights
        weights = {
            "industry": 0.2,
            "size": 0.15,
            "data": 0.2,
            "security": 0.25,
            "financial": 0.1,
            "compliance": 0.1,
            "history": 0.0 if not historical_data else 0.1
        }
        
        # Calculate category scores
        risk_categories["technical"] = cls._calculate_technical_score(
            industry_score, size_score, data_score, security_score
        )
        risk_categories["operational"] = cls._calculate_operational_score(
            industry_score, size_score, security_score, history_score
        )
        risk_categories["financial"] = financial_score
        risk_categories["compliance"] = compliance_score
        
        # Calculate overall score
        overall_score = (
            weights["industry"] * industry_score +
            weights["size"] * size_score +
            weights["data"] * data_score +
            weights["security"] * security_score +
            weights["financial"] * financial_score +
            weights["compliance"] * compliance_score +
            weights["history"] * history_score
        )
        
        # Ensure scores are within bounds
        overall_score = max(0, min(100, overall_score))
        for category in risk_categories:
            risk_categories[category] = max(0, min(100, risk_categories[category]))
        
        # Determine risk level
        risk_level = cls._determine_risk_level(overall_score)
        
        # Calculate confidence score
        confidence_score = cls._calculate_confidence_score(extracted_fields, historical_data)
        
        # Get industry benchmark
        industry_benchmark = cls._get_industry_benchmark(extracted_fields.get("industry"))
        
        return ComprehensiveRiskAssessment(
            overall_score=overall_score,
            technical_score=risk_categories["technical"],
            operational_score=risk_categories["operational"],
            financial_score=risk_categories["financial"],
            compliance_score=risk_categories["compliance"],
            risk_factors=risk_factors,
            industry_benchmark=industry_benchmark,
            risk_level=risk_level,
            confidence_score=confidence_score
        )
    
    @classmethod
    def _assess_industry_risk(cls, extracted_fields: Dict) -> Tuple[float, List[RiskFactorDetail]]:
        """Assess industry-specific cyber risks"""
        
        industry_raw = extracted_fields.get("industry", "")
        industry = str(industry_raw).strip() if industry_raw else ""
        factors = []
        
        # Default industry risk
        base_score = 50.0
        
        if industry in cls.INDUSTRY_RISK_PROFILES:
            profile = cls.INDUSTRY_RISK_PROFILES[industry]
            
            # Calculate industry risk score
            industry_risk = (
                profile["base_multiplier"] * 20 +
                profile["data_sensitivity"] * 15 +
                profile["regulatory_burden"] * 10 +
                profile["attack_frequency"] * 15
            )
            
            # Add industry-specific risk factors
            factors.append(RiskFactorDetail(
                category="operational",
                factor=f"{industry} Industry Profile",
                impact_level=cls._score_to_impact_level(industry_risk),
                score_impact=industry_risk - 50,
                description=f"Industry-specific risk profile for {industry}",
                mitigation_recommendation=f"Implement {industry}-specific security controls"
            ))
            
            # Add threat-specific factors
            for threat in profile["common_threats"]:
                factors.append(RiskFactorDetail(
                    category="technical",
                    factor=f"Common Threat: {threat.replace('_', ' ').title()}",
                    impact_level="Medium",
                    score_impact=5,
                    description=f"Industry commonly targeted by {threat.replace('_', ' ')} attacks",
                    mitigation_recommendation=f"Implement controls to mitigate {threat.replace('_', ' ')} risks"
                ))
            
            return min(industry_risk, 100), factors
        
        return base_score, factors
    
    @classmethod
    def _assess_company_size_risk(cls, extracted_fields: Dict) -> Tuple[float, List[RiskFactorDetail]]:
        """Assess risk based on company size and complexity"""
        
        factors = []
        base_score = 50.0
        
        # Employee count analysis
        employee_count = cls._parse_employee_count(extracted_fields.get("employee_count"))
        revenue = cls._parse_revenue(extracted_fields.get("revenue"))
        
        if employee_count:
            if employee_count < 50:
                # Small companies - limited resources but smaller attack surface
                size_score = 45.0
                factors.append(RiskFactorDetail(
                    category="operational",
                    factor="Small Organization",
                    impact_level="Low",
                    score_impact=-5,
                    description="Limited resources but smaller attack surface",
                    mitigation_recommendation="Focus on basic security hygiene and cloud security"
                ))
            elif employee_count < 500:
                # Medium companies - growing complexity
                size_score = 55.0
                factors.append(RiskFactorDetail(
                    category="operational",
                    factor="Medium Organization",
                    impact_level="Medium",
                    score_impact=5,
                    description="Growing complexity with moderate resources",
                    mitigation_recommendation="Implement structured security program"
                ))
            else:
                # Large companies - complex attack surface
                size_score = 65.0
                factors.append(RiskFactorDetail(
                    category="operational",
                    factor="Large Organization",
                    impact_level="Medium",
                    score_impact=15,
                    description="Complex attack surface with multiple vectors",
                    mitigation_recommendation="Implement enterprise-grade security controls"
                ))
        else:
            size_score = base_score
        
        # Revenue-based adjustments
        if revenue:
            if revenue > 1_000_000_000:  # $1B+
                factors.append(RiskFactorDetail(
                    category="financial",
                    factor="High-Value Target",
                    impact_level="High",
                    score_impact=10,
                    description="High revenue makes organization attractive target",
                    mitigation_recommendation="Implement advanced threat detection and response"
                ))
                size_score += 10
        
        return min(size_score, 100), factors
    
    @classmethod
    def _assess_data_risk(cls, extracted_fields: Dict) -> Tuple[float, List[RiskFactorDetail]]:
        """Assess risk based on data types and sensitivity"""
        
        factors = []
        base_score = 50.0
        data_score = base_score
        
        data_types_raw = extracted_fields.get("data_types", "")
        data_types_str = str(data_types_raw).lower() if data_types_raw else ""
        
        if not data_types_str:
            return base_score, factors
        
        # Parse data types
        identified_data_types = []
        for data_type, risk_weight in cls.DATA_TYPE_RISKS.items():
            keywords = data_type.replace("_", " ").split()
            if any(keyword in data_types_str for keyword in keywords):
                identified_data_types.append((data_type, risk_weight))
        
        if identified_data_types:
            # Calculate weighted risk score
            total_weight = sum(weight for _, weight in identified_data_types)
            weighted_score = (total_weight / len(identified_data_types)) * 60  # Scale to 0-60 range
            data_score = base_score + weighted_score
            
            # Add specific data type factors
            for data_type, risk_weight in identified_data_types:
                impact_level = "High" if risk_weight > 0.7 else "Medium" if risk_weight > 0.4 else "Low"
                score_impact = risk_weight * 20
                
                factors.append(RiskFactorDetail(
                    category="compliance",
                    factor=f"Data Type: {data_type.replace('_', ' ').title()}",
                    impact_level=impact_level,
                    score_impact=score_impact,
                    description=f"Handling of {data_type.replace('_', ' ')} increases breach impact",
                    mitigation_recommendation=f"Implement data classification and protection for {data_type.replace('_', ' ')}"
                ))
        
        return min(data_score, 100), factors
    
    @classmethod
    def _assess_security_posture(cls, extracted_fields: Dict) -> Tuple[float, List[RiskFactorDetail]]:
        """Assess security posture based on implemented controls"""
        
        factors = []
        base_score = 70.0  # Start with higher base assuming poor security
        security_score = base_score
        
        security_measures_raw = extracted_fields.get("security_measures", "")
        security_measures_str = str(security_measures_raw).lower() if security_measures_raw else ""
        
        if not security_measures_str:
            # No security information provided - assume higher risk
            factors.append(RiskFactorDetail(
                category="technical",
                factor="Unknown Security Posture",
                impact_level="High",
                score_impact=20,
                description="No information provided about security controls",
                mitigation_recommendation="Provide detailed security assessment"
            ))
            return min(security_score + 20, 100), factors
        
        # Check for implemented security controls
        implemented_controls = []
        for control, details in cls.SECURITY_CONTROLS.items():
            keywords = control.replace("_", " ").split()
            if any(keyword in security_measures_str for keyword in keywords):
                implemented_controls.append((control, details))
        
        if implemented_controls:
            # Calculate security benefit
            total_effectiveness = sum(details["effectiveness"] for _, details in implemented_controls)
            avg_effectiveness = total_effectiveness / len(implemented_controls)
            
            # Reduce risk score based on implemented controls
            risk_reduction = avg_effectiveness * 40  # Up to 40 point reduction
            security_score = max(base_score - risk_reduction, 20)  # Minimum score of 20
            
            # Add positive factors for good security
            for control, details in implemented_controls:
                factors.append(RiskFactorDetail(
                    category=details["category"],
                    factor=f"Security Control: {control.replace('_', ' ').title()}",
                    impact_level="Low",
                    score_impact=-(details["effectiveness"] * 10),  # Negative impact = risk reduction
                    description=f"Implementation of {control.replace('_', ' ')} reduces cyber risk",
                    mitigation_recommendation="Maintain and monitor this security control"
                ))
        else:
            # Security measures mentioned but no recognized controls
            factors.append(RiskFactorDetail(
                category="technical",
                factor="Basic Security Measures",
                impact_level="Medium",
                score_impact=10,
                description="Some security measures mentioned but details unclear",
                mitigation_recommendation="Provide detailed inventory of security controls"
            ))
            security_score += 10
        
        return min(security_score, 100), factors
    
    @classmethod
    def _assess_financial_risk(cls, extracted_fields: Dict) -> Tuple[float, List[RiskFactorDetail]]:
        """Assess financial stability and its impact on cyber risk"""
        
        factors = []
        base_score = 50.0
        
        # Revenue stability
        revenue = cls._parse_revenue(extracted_fields.get("revenue"))
        years_in_business = cls._parse_number(extracted_fields.get("years_in_business"))
        credit_rating_raw = extracted_fields.get("credit_rating", "")
        credit_rating = str(credit_rating_raw).upper() if credit_rating_raw else ""
        
        financial_score = base_score
        
        # Years in business factor
        if years_in_business:
            if years_in_business < 2:
                factors.append(RiskFactorDetail(
                    category="financial",
                    factor="New Business",
                    impact_level="Medium",
                    score_impact=15,
                    description="Limited operational history increases uncertainty",
                    mitigation_recommendation="Provide additional financial documentation"
                ))
                financial_score += 15
            elif years_in_business > 10:
                factors.append(RiskFactorDetail(
                    category="financial",
                    factor="Established Business",
                    impact_level="Low",
                    score_impact=-10,
                    description="Long operational history indicates stability",
                    mitigation_recommendation="Continue monitoring financial health"
                ))
                financial_score -= 10
        
        # Credit rating factor
        if credit_rating:
            if credit_rating in ["AAA", "AA", "A"]:
                factors.append(RiskFactorDetail(
                    category="financial",
                    factor="Strong Credit Rating",
                    impact_level="Low",
                    score_impact=-15,
                    description="Strong credit rating indicates financial stability",
                    mitigation_recommendation="Monitor for rating changes"
                ))
                financial_score -= 15
            elif credit_rating in ["BBB", "BB"]:
                factors.append(RiskFactorDetail(
                    category="financial",
                    factor="Moderate Credit Rating",
                    impact_level="Low",
                    score_impact=0,
                    description="Moderate credit rating with stable outlook",
                    mitigation_recommendation="Monitor financial performance"
                ))
            else:
                factors.append(RiskFactorDetail(
                    category="financial",
                    factor="Weak Credit Rating",
                    impact_level="Medium",
                    score_impact=20,
                    description="Weak credit rating may limit security investment",
                    mitigation_recommendation="Request additional financial information"
                ))
                financial_score += 20
        
        return max(min(financial_score, 100), 0), factors
    
    @classmethod
    def _assess_compliance_risk(cls, extracted_fields: Dict) -> Tuple[float, List[RiskFactorDetail]]:
        """Assess compliance and regulatory risk"""
        
        factors = []
        base_score = 50.0
        compliance_score = base_score
        
        industry_raw = extracted_fields.get("industry", "")
        industry = str(industry_raw).strip() if industry_raw else ""
        data_types_raw = extracted_fields.get("data_types", "")
        data_types = str(data_types_raw).lower() if data_types_raw else ""
        
        # Industry-specific compliance requirements
        if "healthcare" in industry.lower():
            factors.append(RiskFactorDetail(
                category="compliance",
                factor="HIPAA Compliance Requirements",
                impact_level="High",
                score_impact=25,
                description="Healthcare industry subject to HIPAA regulations",
                mitigation_recommendation="Ensure HIPAA compliance and regular audits"
            ))
            compliance_score += 25
        
        if "financial" in industry.lower():
            factors.append(RiskFactorDetail(
                category="compliance",
                factor="Financial Services Regulations",
                impact_level="High",
                score_impact=30,
                description="Financial services subject to multiple regulations",
                mitigation_recommendation="Ensure SOX, GLBA, and other financial regulations compliance"
            ))
            compliance_score += 30
        
        # Data-specific compliance
        if "payment" in data_types or "credit card" in data_types:
            factors.append(RiskFactorDetail(
                category="compliance",
                factor="PCI-DSS Requirements",
                impact_level="High",
                score_impact=20,
                description="Payment card data handling requires PCI-DSS compliance",
                mitigation_recommendation="Ensure PCI-DSS compliance and regular validation"
            ))
            compliance_score += 20
        
        if "personal" in data_types or "pii" in data_types:
            factors.append(RiskFactorDetail(
                category="compliance",
                factor="Privacy Regulations",
                impact_level="Medium",
                score_impact=15,
                description="Personal data handling subject to privacy regulations",
                mitigation_recommendation="Ensure GDPR, CCPA, and other privacy law compliance"
            ))
            compliance_score += 15
        
        return min(compliance_score, 100), factors
    
    @classmethod
    def _assess_historical_risk(cls, historical_data: Dict) -> Tuple[float, List[RiskFactorDetail]]:
        """Assess risk based on historical performance"""
        
        factors = []
        base_score = 50.0
        
        # Previous claims history
        claims_count = historical_data.get("claims_count", 0)
        incident_count = historical_data.get("incident_count", 0)
        
        history_score = base_score
        
        if claims_count > 0:
            impact = min(claims_count * 15, 40)  # Cap at 40 points
            factors.append(RiskFactorDetail(
                category="operational",
                factor="Previous Claims History",
                impact_level="High" if claims_count > 2 else "Medium",
                score_impact=impact,
                description=f"{claims_count} previous cyber insurance claims",
                mitigation_recommendation="Review claim root causes and implement additional controls"
            ))
            history_score += impact
        
        if incident_count > 0:
            impact = min(incident_count * 10, 30)  # Cap at 30 points
            factors.append(RiskFactorDetail(
                category="operational",
                factor="Previous Security Incidents",
                impact_level="Medium" if incident_count > 3 else "Low",
                score_impact=impact,
                description=f"{incident_count} reported security incidents",
                mitigation_recommendation="Review incident response and preventive measures"
            ))
            history_score += impact
        
        return min(history_score, 100), factors
    
    @classmethod
    def _calculate_technical_score(cls, industry_score: float, size_score: float, 
                                 data_score: float, security_score: float) -> float:
        """Calculate technical risk category score"""
        
        # Technical risk is heavily influenced by security posture and data sensitivity
        weights = {"industry": 0.2, "size": 0.2, "data": 0.3, "security": 0.3}
        
        return (
            weights["industry"] * industry_score +
            weights["size"] * size_score +
            weights["data"] * data_score +
            weights["security"] * security_score
        )
    
    @classmethod
    def _calculate_operational_score(cls, industry_score: float, size_score: float,
                                   security_score: float, history_score: float) -> float:
        """Calculate operational risk category score"""
        
        # Operational risk focuses on business processes and historical performance
        if history_score > 0:
            weights = {"industry": 0.3, "size": 0.3, "security": 0.2, "history": 0.2}
            return (
                weights["industry"] * industry_score +
                weights["size"] * size_score +
                weights["security"] * security_score +
                weights["history"] * history_score
            )
        else:
            weights = {"industry": 0.4, "size": 0.4, "security": 0.2}
            return (
                weights["industry"] * industry_score +
                weights["size"] * size_score +
                weights["security"] * security_score
            )
    
    @classmethod
    def _determine_risk_level(cls, overall_score: float) -> str:
        """Determine risk level based on score"""
        if overall_score <= 35:
            return "Low"
        elif overall_score <= 55:
            return "Medium"
        elif overall_score <= 75:
            return "High"
        else:
            return "Critical"
    
    @classmethod
    def _calculate_confidence_score(cls, extracted_fields: Dict, historical_data: Optional[Dict] = None) -> float:
        """Calculate confidence in risk assessment"""
        
        confidence = 30.0  # Base confidence
        
        # Data completeness
        key_fields = ["industry", "employee_count", "revenue", "data_types", "security_measures"]
        available_fields = sum(1 for field in key_fields if extracted_fields.get(field))
        confidence += (available_fields / len(key_fields)) * 40
        
        # Security information quality
        if extracted_fields.get("security_measures"):
            security_detail_score = len(extracted_fields["security_measures"]) / 500  # Assume detailed description
            confidence += min(security_detail_score * 20, 20)
        
        # Historical data availability
        if historical_data:
            confidence += 10
        
        return min(confidence, 100)
    
    @classmethod
    def _get_industry_benchmark(cls, industry: str) -> Optional[float]:
        """Get industry benchmark risk score"""
        
        if not industry or industry not in cls.INDUSTRY_RISK_PROFILES:
            return 50.0
        
        profile = cls.INDUSTRY_RISK_PROFILES[industry]
        
        # Calculate benchmark score
        benchmark = (
            profile["base_multiplier"] * 15 +
            profile["data_sensitivity"] * 10 +
            profile["regulatory_burden"] * 10 +
            profile["attack_frequency"] * 15 +
            50  # Base score
        )
        
        return min(benchmark, 100)
    
    @classmethod
    def _score_to_impact_level(cls, score: float) -> str:
        """Convert numeric score to impact level"""
        if score <= 40:
            return "Low"
        elif score <= 70:
            return "Medium"
        else:
            return "High"
    
    @classmethod
    def _parse_employee_count(cls, employee_str) -> Optional[int]:
        """Parse employee count from string"""
        return CyberInsuranceValidator._parse_employee_count(employee_str)
    
    @classmethod
    def _parse_revenue(cls, revenue_str) -> Optional[float]:
        """Parse revenue from string"""
        return CyberInsuranceValidator._parse_revenue(revenue_str)
    
    @classmethod
    def _parse_number(cls, number_str) -> Optional[float]:
        """Parse general number from string"""
        if not number_str:
            return None
        try:
            return float(str(number_str).replace(",", ""))
        except (ValueError, AttributeError):
            return None


class RiskBenchmarkingService:
    """Service for risk benchmarking and comparison"""
    
    @classmethod
    def get_industry_benchmarks(cls, industry: str) -> Dict[str, float]:
        """Get industry-specific risk benchmarks"""
        
        if industry in EnhancedRiskScoringEngine.INDUSTRY_RISK_PROFILES:
            profile = EnhancedRiskScoringEngine.INDUSTRY_RISK_PROFILES[industry]
            
            return {
                "industry_average": cls._calculate_industry_average(profile),
                "top_quartile": cls._calculate_industry_average(profile) - 15,
                "bottom_quartile": cls._calculate_industry_average(profile) + 15,
                "data_sensitivity_factor": profile["data_sensitivity"] * 100,
                "regulatory_burden_factor": profile["regulatory_burden"] * 100,
                "attack_frequency_factor": profile["attack_frequency"] * 100
            }
        
        return {
            "industry_average": 50.0,
            "top_quartile": 35.0,
            "bottom_quartile": 65.0,
            "data_sensitivity_factor": 50.0,
            "regulatory_burden_factor": 50.0,
            "attack_frequency_factor": 50.0
        }
    
    @classmethod
    def _calculate_industry_average(cls, profile: Dict) -> float:
        """Calculate industry average risk score"""
        return (
            profile["base_multiplier"] * 15 +
            profile["data_sensitivity"] * 10 +
            profile["regulatory_burden"] * 10 +
            profile["attack_frequency"] * 15 +
            50
        )