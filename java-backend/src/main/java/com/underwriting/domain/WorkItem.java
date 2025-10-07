package com.underwriting.domain;

import jakarta.persistence.*;
import com.fasterxml.jackson.annotation.JsonBackReference;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.LocalDateTime;
import java.util.Map;

@Entity
@Table(name = "work_items")
public class WorkItem {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "submission_id", nullable = false)
    private Long submissionId;
    
    @Column(name = "title", length = 500)
    private String title;
    
    @Column(name = "description", columnDefinition = "TEXT")
    private String description;
    
    @Column(name = "assigned_to")
    private String assignedTo;
    
    @Enumerated(EnumType.STRING)
    @Column(name = "status")
    private WorkItemStatus status = WorkItemStatus.PENDING;
    
    @Enumerated(EnumType.STRING)
    @Column(name = "priority")
    private WorkItemPriority priority = WorkItemPriority.MEDIUM;
    
    @Column(name = "risk_score")
    private Double riskScore;
    
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "risk_categories", columnDefinition = "jsonb")
    private Map<String, Object> riskCategories;
    
    @Column(name = "industry", length = 100)
    private String industry;
    
    @Enumerated(EnumType.STRING)
    @Column(name = "company_size")
    private CompanySize companySize;
    
    @Column(name = "policy_type", length = 100)
    private String policyType;
    
    @Column(name = "coverage_amount")
    private Double coverageAmount;
    
    @Column(name = "last_risk_assessment")
    private LocalDateTime lastRiskAssessment;
    
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    // Relationships
    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "submission_id", insertable = false, updatable = false)
    @JsonBackReference
    private Submission submission;
    
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }
    
    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
    
    // Constructors
    public WorkItem() {}
    
    public WorkItem(Long submissionId, String title, String description) {
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
    
    public Submission getSubmission() { return submission; }
    public void setSubmission(Submission submission) { this.submission = submission; }
}