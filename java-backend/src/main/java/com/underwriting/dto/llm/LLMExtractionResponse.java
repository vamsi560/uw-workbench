package com.underwriting.dto.llm;

import java.util.Map;

/**
 * Response DTO from LLM extraction service
 * Maps from Python FastAPI endpoint: POST /api/extract
 */
public class LLMExtractionResponse {
    
    private Map<String, Object> extractedFields;
    private Map<String, Object> summary;
    private Double processingTimeMs;
    private String modelUsed;
    
    // Constructors
    public LLMExtractionResponse() {}
    
    public LLMExtractionResponse(Map<String, Object> extractedFields, Map<String, Object> summary) {
        this.extractedFields = extractedFields;
        this.summary = summary;
    }
    
    // Getters and Setters
    public Map<String, Object> getExtractedFields() { return extractedFields; }
    public void setExtractedFields(Map<String, Object> extractedFields) { this.extractedFields = extractedFields; }
    
    public Map<String, Object> getSummary() { return summary; }
    public void setSummary(Map<String, Object> summary) { this.summary = summary; }
    
    public Double getProcessingTimeMs() { return processingTimeMs; }
    public void setProcessingTimeMs(Double processingTimeMs) { this.processingTimeMs = processingTimeMs; }
    
    public String getModelUsed() { return modelUsed; }
    public void setModelUsed(String modelUsed) { this.modelUsed = modelUsed; }
}