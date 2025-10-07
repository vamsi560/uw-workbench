package com.underwriting.domain;

import jakarta.persistence.*;
import com.fasterxml.jackson.annotation.JsonManagedReference;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Entity
@Table(name = "submissions")
public class Submission {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "submission_id")
    private Integer submissionId;
    
    @Column(name = "submission_ref", unique = true)
    private UUID submissionRef;
    
    @Column(name = "subject", nullable = false, columnDefinition = "TEXT")
    private String subject;
    
    @Column(name = "sender_email", nullable = false, columnDefinition = "TEXT")
    private String senderEmail;
    
    @Column(name = "body_text", columnDefinition = "TEXT")
    private String bodyText;
    
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "extracted_fields", columnDefinition = "jsonb")
    private Map<String, Object> extractedFields;
    
    @Column(name = "assigned_to")
    private String assignedTo;
    
    @Enumerated(EnumType.STRING)
    @Column(name = "status")
    private SubmissionStatus status = SubmissionStatus.NEW;
    
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    // Relationships
    @OneToMany(mappedBy = "submission", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    @JsonManagedReference
    private List<WorkItem> workItems;
    
    @PrePersist
    protected void onCreate() {
        if (submissionRef == null) {
            submissionRef = UUID.randomUUID();
        }
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }
    
    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
    
    // Constructors
    public Submission() {}
    
    public Submission(String subject, String senderEmail, String bodyText) {
        this.subject = subject;
        this.senderEmail = senderEmail;
        this.bodyText = bodyText;
        this.submissionRef = UUID.randomUUID();
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
    
    public List<WorkItem> getWorkItems() { return workItems; }
    public void setWorkItems(List<WorkItem> workItems) { this.workItems = workItems; }
}