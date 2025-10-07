package com.underwriting.dto.llm;

import java.util.Map;

/**
 * Request DTO for LLM risk assessment service
 * Maps to Python FastAPI endpoint: POST /api/risk-assessment
 */
public class LLMRiskAssessmentRequest {
    
    private Map<String, Object> submissionData;
    private Map<String, Object> extractedFields;
    private Map<String, Object> companyProfile;
    
    // Constructors
    public LLMRiskAssessmentRequest() {}
    
    public LLMRiskAssessmentRequest(Map<String, Object> submissionData, Map<String, Object> extractedFields) {
        this.submissionData = submissionData;
        this.extractedFields = extractedFields;
    }
    
    // Getters and Setters
    public Map<String, Object> getSubmissionData() { return submissionData; }
    public void setSubmissionData(Map<String, Object> submissionData) { this.submissionData = submissionData; }
    
    public Map<String, Object> getExtractedFields() { return extractedFields; }
    public void setExtractedFields(Map<String, Object> extractedFields) { this.extractedFields = extractedFields; }
    
    public Map<String, Object> getCompanyProfile() { return companyProfile; }
    public void setCompanyProfile(Map<String, Object> companyProfile) { this.companyProfile = companyProfile; }
}