package com.underwriting.dto.llm;

import java.util.List;

/**
 * Response DTO from LLM triage service
 * Maps from Python FastAPI endpoint: POST /api/triage
 */
public class LLMTriageResponse {
    
    private String priority;
    private Double riskScore;
    private String assignedCategory;
    private String reasoning;
    private List<String> recommendedActions;
    
    // Constructors
    public LLMTriageResponse() {}
    
    public LLMTriageResponse(String priority, Double riskScore, String assignedCategory) {
        this.priority = priority;
        this.riskScore = riskScore;
        this.assignedCategory = assignedCategory;
    }
    
    // Getters and Setters
    public String getPriority() { return priority; }
    public void setPriority(String priority) { this.priority = priority; }
    
    public Double getRiskScore() { return riskScore; }
    public void setRiskScore(Double riskScore) { this.riskScore = riskScore; }
    
    public String getAssignedCategory() { return assignedCategory; }
    public void setAssignedCategory(String assignedCategory) { this.assignedCategory = assignedCategory; }
    
    public String getReasoning() { return reasoning; }
    public void setReasoning(String reasoning) { this.reasoning = reasoning; }
    
    public List<String> getRecommendedActions() { return recommendedActions; }
    public void setRecommendedActions(List<String> recommendedActions) { this.recommendedActions = recommendedActions; }
}