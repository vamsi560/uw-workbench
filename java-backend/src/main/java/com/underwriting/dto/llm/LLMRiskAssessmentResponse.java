package com.underwriting.dto.llm;

import java.util.List;
import java.util.Map;

/**
 * Response DTO from LLM risk assessment service
 * Maps from Python FastAPI endpoint: POST /api/risk-assessment
 */
public class LLMRiskAssessmentResponse {
    
    private Double overallRiskScore;
    private Map<String, Double> riskCategories;
    private List<Map<String, Object>> riskFactors;
    private List<String> recommendations;
    private Double confidenceScore;
    
    // Constructors
    public LLMRiskAssessmentResponse() {}
    
    // Getters and Setters
    public Double getOverallRiskScore() { return overallRiskScore; }
    public void setOverallRiskScore(Double overallRiskScore) { this.overallRiskScore = overallRiskScore; }
    
    public Map<String, Double> getRiskCategories() { return riskCategories; }
    public void setRiskCategories(Map<String, Double> riskCategories) { this.riskCategories = riskCategories; }
    
    public List<Map<String, Object>> getRiskFactors() { return riskFactors; }
    public void setRiskFactors(List<Map<String, Object>> riskFactors) { this.riskFactors = riskFactors; }
    
    public List<String> getRecommendations() { return recommendations; }
    public void setRecommendations(List<String> recommendations) { this.recommendations = recommendations; }
    
    public Double getConfidenceScore() { return confidenceScore; }
    public void setConfidenceScore(Double confidenceScore) { this.confidenceScore = confidenceScore; }
}