package com.underwriting.dto;

import com.underwriting.domain.WorkItemStatus;
import com.underwriting.domain.WorkItemPriority;
import com.underwriting.domain.CompanySize;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

import java.time.LocalDateTime;
import java.util.Map;

public class WorkItemDto {
    
    private Long id;
    
    @NotNull(message = "Submission ID is required")
    private Long submissionId;
    
    @NotBlank(message = "Title is required")
    @Size(max = 500, message = "Title must not exceed 500 characters")
    private String title;
    
    private String description;
    private String assignedTo;
    private WorkItemStatus status;
    private WorkItemPriority priority;
    private Double riskScore;
    private Map<String, Object> riskCategories;
    private String industry;
    private CompanySize companySize;
    private String policyType;
    private Double coverageAmount;
    private LocalDateTime lastRiskAssessment;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    
    // For API responses, include submission details
    private SubmissionDto submission;
    
    // Constructors
    public WorkItemDto() {}
    
    public WorkItemDto(Long submissionId, String title, String description) {
        this.submissionId = submissionId;
        this.title = title;
        this.description = description;
        this.status = WorkItemStatus.PENDING;
        this.priority = WorkItemPriority.MEDIUM;
    }
    
    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    
    public Long getSubmissionId() { return submissionId; }
    public void setSubmissionId(Long submissionId) { this.submissionId = submissionId; }
    
    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }
    
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    
    public String getAssignedTo() { return assignedTo; }
    public void setAssignedTo(String assignedTo) { this.assignedTo = assignedTo; }
    
    public WorkItemStatus getStatus() { return status; }
    public void setStatus(WorkItemStatus status) { this.status = status; }
    
    public WorkItemPriority getPriority() { return priority; }
    public void setPriority(WorkItemPriority priority) { this.priority = priority; }
    
    public Double getRiskScore() { return riskScore; }
    public void setRiskScore(Double riskScore) { this.riskScore = riskScore; }
    
    public Map<String, Object> getRiskCategories() { return riskCategories; }
    public void setRiskCategories(Map<String, Object> riskCategories) { this.riskCategories = riskCategories; }
    
    public String getIndustry() { return industry; }
    public void setIndustry(String industry) { this.industry = industry; }
    
    public CompanySize getCompanySize() { return companySize; }
    public void setCompanySize(CompanySize companySize) { this.companySize = companySize; }
    
    public String getPolicyType() { return policyType; }
    public void setPolicyType(String policyType) { this.policyType = policyType; }
    
    public Double getCoverageAmount() { return coverageAmount; }
    public void setCoverageAmount(Double coverageAmount) { this.coverageAmount = coverageAmount; }
    
    public LocalDateTime getLastRiskAssessment() { return lastRiskAssessment; }
    public void setLastRiskAssessment(LocalDateTime lastRiskAssessment) { this.lastRiskAssessment = lastRiskAssessment; }
    
    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
    
    public LocalDateTime getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(LocalDateTime updatedAt) { this.updatedAt = updatedAt; }
    
    public SubmissionDto getSubmission() { return submission; }
    public void setSubmission(SubmissionDto submission) { this.submission = submission; }
}