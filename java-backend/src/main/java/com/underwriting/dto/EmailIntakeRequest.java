package com.underwriting.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

import java.util.List;

public class EmailIntakeRequest {
    
    @NotBlank(message = "Subject is required")
    @Size(max = 1000, message = "Subject must not exceed 1000 characters")
    private String subject;
    
    @NotBlank(message = "Sender email is required")
    @Email(message = "Invalid email format")
    private String senderEmail;
    
    @NotBlank(message = "Email body is required")
    private String emailBody;
    
    private List<String> attachments;
    private String combinedText; // For LLM processing
    
    // Constructors
    public EmailIntakeRequest() {}
    
    public EmailIntakeRequest(String subject, String senderEmail, String emailBody) {
        this.subject = subject;
        this.senderEmail = senderEmail;
        this.emailBody = emailBody;
    }
    
    // Getters and Setters
    public String getSubject() { return subject; }
    public void setSubject(String subject) { this.subject = subject; }
    
    public String getSenderEmail() { return senderEmail; }
    public void setSenderEmail(String senderEmail) { this.senderEmail = senderEmail; }
    
    public String getEmailBody() { return emailBody; }
    public void setEmailBody(String emailBody) { this.emailBody = emailBody; }
    
    public List<String> getAttachments() { return attachments; }
    public void setAttachments(List<String> attachments) { this.attachments = attachments; }
    
    public String getCombinedText() { return combinedText; }
    public void setCombinedText(String combinedText) { this.combinedText = combinedText; }
}