package com.underwriting.dto.llm;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

import java.util.List;

/**
 * Request DTO for LLM extraction service
 * Maps to Python FastAPI endpoint: POST /api/extract
 */
public class LLMExtractionRequest {
    
    @NotBlank(message = "Text is required for extraction")
    @Size(max = 50000, message = "Text must not exceed 50000 characters")
    private String text;
    
    private String emailSubject;
    private String senderEmail;
    private List<String> attachmentInfo;
    
    // Constructors
    public LLMExtractionRequest() {}
    
    public LLMExtractionRequest(String text, String emailSubject, String senderEmail) {
        this.text = text;
        this.emailSubject = emailSubject;
        this.senderEmail = senderEmail;
    }
    
    // Getters and Setters
    public String getText() { return text; }
    public void setText(String text) { this.text = text; }
    
    public String getEmailSubject() { return emailSubject; }
    public void setEmailSubject(String emailSubject) { this.emailSubject = emailSubject; }
    
    public String getSenderEmail() { return senderEmail; }
    public void setSenderEmail(String senderEmail) { this.senderEmail = senderEmail; }
    
    public List<String> getAttachmentInfo() { return attachmentInfo; }
    public void setAttachmentInfo(List<String> attachmentInfo) { this.attachmentInfo = attachmentInfo; }
}