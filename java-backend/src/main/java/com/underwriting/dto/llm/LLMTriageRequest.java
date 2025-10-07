package com.underwriting.dto.llm;

import java.util.Map;

/**
 * Request DTO for LLM triage service
 * Maps to Python FastAPI endpoint: POST /api/triage
 */
public class LLMTriageRequest {
    
    private Map<String, Object> submissionData;
    private Map<String, Object> extractedFields;
    
    // Constructors
    public LLMTriageRequest() {}
    
    public LLMTriageRequest(Map<String, Object> submissionData, Map<String, Object> extractedFields) {
        this.submissionData = submissionData;
        this.extractedFields = extractedFields;
    }
    
    // Getters and Setters
    public Map<String, Object> getSubmissionData() { return submissionData; }
    public void setSubmissionData(Map<String, Object> submissionData) { this.submissionData = submissionData; }
    
    public Map<String, Object> getExtractedFields() { return extractedFields; }
    public void setExtractedFields(Map<String, Object> extractedFields) { this.extractedFields = extractedFields; }
}