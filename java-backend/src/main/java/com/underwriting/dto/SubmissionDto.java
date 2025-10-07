package com.underwriting.dto;

import com.underwriting.domain.SubmissionStatus;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.UUID;

public class SubmissionDto {
    
    private Long id;
    private Integer submissionId;
    private UUID submissionRef;
    
    @NotBlank(message = "Subject is required")
    @Size(max = 1000, message = "Subject must not exceed 1000 characters")
    private String subject;
    
    @NotBlank(message = "Sender email is required")
    @Email(message = "Invalid email format")
    private String senderEmail;
    
    private String bodyText;
    private Map<String, Object> extractedFields;
    private String assignedTo;
    private SubmissionStatus status;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    
    // Constructors
    public SubmissionDto() {}
    
    public SubmissionDto(String subject, String senderEmail, String bodyText) {
        this.subject = subject;
        this.senderEmail = senderEmail;
        this.bodyText = bodyText;
        this.status = SubmissionStatus.NEW;
    }
    
    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    
    public Integer getSubmissionId() { return submissionId; }
    public void setSubmissionId(Integer submissionId) { this.submissionId = submissionId; }
    
    public UUID getSubmissionRef() { return submissionRef; }
    public void setSubmissionRef(UUID submissionRef) { this.submissionRef = submissionRef; }
    
    public String getSubject() { return subject; }
    public void setSubject(String subject) { this.subject = subject; }
    
    public String getSenderEmail() { return senderEmail; }
    public void setSenderEmail(String senderEmail) { this.senderEmail = senderEmail; }
    
    public String getBodyText() { return bodyText; }
    public void setBodyText(String bodyText) { this.bodyText = bodyText; }
    
    public Map<String, Object> getExtractedFields() { return extractedFields; }
    public void setExtractedFields(Map<String, Object> extractedFields) { this.extractedFields = extractedFields; }
    
    public String getAssignedTo() { return assignedTo; }
    public void setAssignedTo(String assignedTo) { this.assignedTo = assignedTo; }
    
    public SubmissionStatus getStatus() { return status; }
    public void setStatus(SubmissionStatus status) { this.status = status; }
    
    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
    
    public LocalDateTime getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(LocalDateTime updatedAt) { this.updatedAt = updatedAt; }
}