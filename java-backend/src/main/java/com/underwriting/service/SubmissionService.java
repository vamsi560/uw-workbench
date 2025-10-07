package com.underwriting.service;

import com.underwriting.domain.Submission;
import com.underwriting.domain.SubmissionStatus;
import com.underwriting.dto.SubmissionDto;
import com.underwriting.dto.EmailIntakeRequest;
import com.underwriting.repository.SubmissionRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@Transactional
public class SubmissionService {
    
    @Autowired
    private SubmissionRepository submissionRepository;
    
    @Autowired
    private LLMServiceClient llmServiceClient;
    
    /**
     * Create a new submission from email intake
     */
    public SubmissionDto createSubmission(EmailIntakeRequest request) {
        // Check for potential duplicates
        List<Submission> duplicates = submissionRepository.findPotentialDuplicates(
            request.getSubject(),
            request.getSenderEmail(),
            LocalDateTime.now().minusHours(1)
        );
        
        if (!duplicates.isEmpty()) {
            // Return existing submission if duplicate found
            return convertToDto(duplicates.get(0));
        }
        
        // Create new submission
        Submission submission = new Submission(
            request.getSubject(),
            request.getSenderEmail(),
            request.getEmailBody()
        );
        
        submission = submissionRepository.save(submission);
        
        // Process with LLM service asynchronously if needed
        // This could be done in a separate thread or message queue
        processSubmissionWithLLM(submission, request);
        
        return convertToDto(submission);
    }
    
    /**
     * Get submission by ID
     */
    @Transactional(readOnly = true)
    public Optional<SubmissionDto> getSubmissionById(Long id) {
        return submissionRepository.findById(id)
            .map(this::convertToDto);
    }
    
    /**
     * Get submission by reference UUID
     */
    @Transactional(readOnly = true)
    public Optional<SubmissionDto> getSubmissionByRef(UUID submissionRef) {
        return submissionRepository.findBySubmissionRef(submissionRef)
            .map(this::convertToDto);
    }
    
    /**
     * Get submissions by status
     */
    @Transactional(readOnly = true)
    public Page<SubmissionDto> getSubmissionsByStatus(SubmissionStatus status, Pageable pageable) {
        return submissionRepository.findByStatus(status, pageable)
            .map(this::convertToDto);
    }
    
    /**
     * Get submissions assigned to user
     */
    @Transactional(readOnly = true)
    public Page<SubmissionDto> getSubmissionsByAssignedTo(String assignedTo, Pageable pageable) {
        return submissionRepository.findByAssignedTo(assignedTo, pageable)
            .map(this::convertToDto);
    }
    
    /**
     * Get recent submissions for polling
     */
    @Transactional(readOnly = true)
    public List<SubmissionDto> getRecentSubmissions(Optional<Long> sinceId, Optional<LocalDateTime> since, int limit) {
        Pageable pageable = PageRequest.of(0, limit, Sort.by("createdAt").descending());
        
        List<Submission> submissions;
        if (sinceId.isPresent()) {
            submissions = submissionRepository.findSinceId(sinceId.get(), pageable);
        } else if (since.isPresent()) {
            submissions = submissionRepository.findSince(since.get(), pageable);
        } else {
            submissions = submissionRepository.findTop20ByOrderByCreatedAtDesc();
        }
        
        return submissions.stream()
            .map(this::convertToDto)
            .collect(Collectors.toList());
    }
    
    /**
     * Update submission status
     */
    public SubmissionDto updateSubmissionStatus(Long id, SubmissionStatus newStatus, String changedBy, String reason) {
        Submission submission = submissionRepository.findById(id)
            .orElseThrow(() -> new RuntimeException("Submission not found"));
        
        SubmissionStatus oldStatus = submission.getStatus();
        submission.setStatus(newStatus);
        
        submission = submissionRepository.save(submission);
        
        // TODO: Create audit trail entry
        // auditService.createStatusChangeAudit(submission, oldStatus, newStatus, changedBy, reason);
        
        return convertToDto(submission);
    }
    
    /**
     * Assign submission to user
     */
    public SubmissionDto assignSubmission(Long id, String assignedTo) {
        Submission submission = submissionRepository.findById(id)
            .orElseThrow(() -> new RuntimeException("Submission not found"));
        
        submission.setAssignedTo(assignedTo);
        submission = submissionRepository.save(submission);
        
        return convertToDto(submission);
    }
    
    /**
     * Search submissions
     */
    @Transactional(readOnly = true)
    public Page<SubmissionDto> searchSubmissions(String searchTerm, Pageable pageable) {
        return submissionRepository.searchSubmissions(searchTerm, pageable)
            .map(this::convertToDto);
    }
    
    /**
     * Get submissions needing attention
     */
    @Transactional(readOnly = true)
    public List<SubmissionDto> getSubmissionsNeedingAttention() {
        return submissionRepository.findSubmissionsNeedingAttention()
            .stream()
            .map(this::convertToDto)
            .collect(Collectors.toList());
    }
    
    /**
     * Process submission with LLM service
     */
    private void processSubmissionWithLLM(Submission submission, EmailIntakeRequest request) {
        try {
            // Prepare text for LLM processing
            String combinedText = request.getCombinedText() != null ? 
                request.getCombinedText() : request.getEmailBody();
            
            // Call LLM service for data extraction
            var extractionResponse = llmServiceClient.extractData(
                combinedText, 
                request.getSubject(), 
                request.getSenderEmail()
            );
            
            if (extractionResponse != null && extractionResponse.getExtractedFields() != null) {
                submission.setExtractedFields(extractionResponse.getExtractedFields());
                submissionRepository.save(submission);
                
                // Log successful processing
                System.out.println("Successfully processed submission " + submission.getId() + 
                                 " with LLM. Processing time: " + extractionResponse.getProcessingTimeMs() + "ms");
            }
            
        } catch (Exception e) {
            // Log error and continue - don't fail submission creation
            System.err.println("Failed to process submission " + submission.getId() + 
                             " with LLM: " + e.getMessage());
            
            // Set fallback extracted fields to indicate manual review needed
            Map<String, Object> fallbackFields = new HashMap<>();
            fallbackFields.put("status", "llm_processing_failed");
            fallbackFields.put("manual_review_required", true);
            fallbackFields.put("error_message", e.getMessage());
            
            submission.setExtractedFields(fallbackFields);
            submissionRepository.save(submission);
        }
    }
    
    /**
     * Convert entity to DTO
     */
    private SubmissionDto convertToDto(Submission submission) {
        SubmissionDto dto = new SubmissionDto();
        dto.setId(submission.getId());
        dto.setSubmissionId(submission.getSubmissionId());
        dto.setSubmissionRef(submission.getSubmissionRef());
        dto.setSubject(submission.getSubject());
        dto.setSenderEmail(submission.getSenderEmail());
        dto.setBodyText(submission.getBodyText());
        dto.setExtractedFields(submission.getExtractedFields());
        dto.setAssignedTo(submission.getAssignedTo());
        dto.setStatus(submission.getStatus());
        dto.setCreatedAt(submission.getCreatedAt());
        dto.setUpdatedAt(submission.getUpdatedAt());
        return dto;
    }
}