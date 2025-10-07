package com.underwriting.controller;

import com.underwriting.dto.EmailIntakeRequest;
import com.underwriting.dto.SubmissionDto;
import com.underwriting.dto.WorkItemDto;
import com.underwriting.domain.WorkItemStatus;
import com.underwriting.domain.WorkItemPriority;
import com.underwriting.service.SubmissionService;
import com.underwriting.service.WorkItemService;
import com.underwriting.service.LLMServiceClient;
import jakarta.validation.Valid;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = {"https://uw-workbench-portal.vercel.app", "https://uw-workbench-jade.vercel.app"})
public class WorkItemController {
    
    private static final Logger logger = LoggerFactory.getLogger(WorkItemController.class);
    
    @Autowired
    private WorkItemService workItemService;
    
    @Autowired
    private SubmissionService submissionService;
    
    @Autowired
    private LLMServiceClient llmServiceClient;
    
    /**
     * Health check endpoint
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, Object>> health() {
        Map<String, Object> health = new HashMap<>();
        health.put("status", "healthy");
        health.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
        health.put("service", "java-backend");
        health.put("llm_service_available", llmServiceClient.isServiceAvailable());
        
        return ResponseEntity.ok(health);
    }
    
    /**
     * Poll work items endpoint - matches Python API
     */
    @GetMapping("/workitems/poll")
    public ResponseEntity<List<WorkItemDto>> pollWorkItems(
            @RequestParam(required = false) Long sinceId,
            @RequestParam(required = false) String since,
            @RequestParam(defaultValue = "50") int limit) {
        
        logger.info("Polling work items. SinceId: {}, Since: {}, Limit: {}", sinceId, since, limit);
        
        try {
            Optional<Long> sinceIdOpt = Optional.ofNullable(sinceId);
            Optional<LocalDateTime> sinceTimeOpt = Optional.empty();
            
            if (since != null && !since.isEmpty()) {
                try {
                    sinceTimeOpt = Optional.of(LocalDateTime.parse(since, DateTimeFormatter.ISO_LOCAL_DATE_TIME));
                } catch (Exception e) {
                    logger.warn("Invalid 'since' parameter format: {}", since);
                }
            }
            
            List<WorkItemDto> workItems = workItemService.getWorkItemsForPolling(sinceIdOpt, sinceTimeOpt, limit);
            
            logger.info("Retrieved {} work items", workItems.size());
            return ResponseEntity.ok(workItems);
            
        } catch (Exception e) {
            logger.error("Error polling work items: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(List.of());
        }
    }
    
    /**
     * Email intake endpoint - matches Python API
     */
    @PostMapping("/email/intake")
    public ResponseEntity<Map<String, Object>> emailIntake(@Valid @RequestBody EmailIntakeRequest request) {
        logger.info("Processing email intake from: {}", request.getSenderEmail());
        
        try {
            // Create submission
            SubmissionDto submission = submissionService.createSubmission(request);
            
            // Create initial work item
            WorkItemDto workItem = new WorkItemDto(
                submission.getId(),
                "Review submission: " + request.getSubject(),
                "New submission requires review and processing"
            );
            
            WorkItemDto createdWorkItem = workItemService.createWorkItem(workItem);
            
            Map<String, Object> response = new HashMap<>();
            response.put("message", "Email processed successfully");
            response.put("submission_id", submission.getId());
            response.put("submission_ref", submission.getSubmissionRef());
            response.put("work_item_id", createdWorkItem.getId());
            response.put("status", submission.getStatus());
            response.put("extracted_fields", submission.getExtractedFields());
            response.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
            
            logger.info("Email intake processed successfully. Submission ID: {}", submission.getId());
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            logger.error("Error processing email intake: {}", e.getMessage(), e);
            
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("error", "Failed to process email intake");
            errorResponse.put("message", e.getMessage());
            errorResponse.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
            
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }
    
    /**
     * Get work item by ID
     */
    @GetMapping("/workitems/{id}")
    public ResponseEntity<WorkItemDto> getWorkItem(@PathVariable Long id) {
        logger.debug("Getting work item: {}", id);
        
        Optional<WorkItemDto> workItem = workItemService.getWorkItemById(id);
        
        return workItem.map(ResponseEntity::ok)
                      .orElse(ResponseEntity.notFound().build());
    }
    
    /**
     * Update work item status
     */
    @PutMapping("/workitems/{id}/status")
    public ResponseEntity<WorkItemDto> updateWorkItemStatus(
            @PathVariable Long id, 
            @RequestBody Map<String, String> request) {
        
        try {
            String statusStr = request.get("status");
            WorkItemStatus status = WorkItemStatus.valueOf(statusStr.toUpperCase());
            
            WorkItemDto updatedWorkItem = workItemService.updateWorkItemStatus(id, status);
            
            logger.info("Updated work item {} status to {}", id, status);
            return ResponseEntity.ok(updatedWorkItem);
            
        } catch (IllegalArgumentException e) {
            logger.error("Invalid status for work item {}: {}", id, request.get("status"));
            return ResponseEntity.badRequest().build();
        } catch (Exception e) {
            logger.error("Error updating work item {} status: {}", id, e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    /**
     * Assign work item to user
     */
    @PutMapping("/workitems/{id}/assign")
    public ResponseEntity<WorkItemDto> assignWorkItem(
            @PathVariable Long id, 
            @RequestBody Map<String, String> request) {
        
        try {
            String assignedTo = request.get("assigned_to");
            
            WorkItemDto updatedWorkItem = workItemService.assignWorkItem(id, assignedTo);
            
            logger.info("Assigned work item {} to {}", id, assignedTo);
            return ResponseEntity.ok(updatedWorkItem);
            
        } catch (Exception e) {
            logger.error("Error assigning work item {}: {}", id, e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    /**
     * Update work item priority
     */
    @PutMapping("/workitems/{id}/priority")
    public ResponseEntity<WorkItemDto> updateWorkItemPriority(
            @PathVariable Long id, 
            @RequestBody Map<String, String> request) {
        
        try {
            String priorityStr = request.get("priority");
            WorkItemPriority priority = WorkItemPriority.valueOf(priorityStr.toUpperCase());
            
            WorkItemDto updatedWorkItem = workItemService.updateWorkItemPriority(id, priority);
            
            logger.info("Updated work item {} priority to {}", id, priority);
            return ResponseEntity.ok(updatedWorkItem);
            
        } catch (IllegalArgumentException e) {
            logger.error("Invalid priority for work item {}: {}", id, request.get("priority"));
            return ResponseEntity.badRequest().build();
        } catch (Exception e) {
            logger.error("Error updating work item {} priority: {}", id, e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    /**
     * Create a new work item
     */
    @PostMapping("/workitems")
    public ResponseEntity<WorkItemDto> createWorkItem(@Valid @RequestBody WorkItemDto workItemDto) {
        logger.info("Creating new work item for submission: {}", workItemDto.getSubmissionId());
        
        try {
            WorkItemDto createdWorkItem = workItemService.createWorkItem(workItemDto);
            return ResponseEntity.status(HttpStatus.CREATED).body(createdWorkItem);
            
        } catch (Exception e) {
            logger.error("Error creating work item: {}", e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    /**
     * Update work item
     */
    @PutMapping("/workitems/{id}")
    public ResponseEntity<WorkItemDto> updateWorkItem(
            @PathVariable Long id, 
            @Valid @RequestBody WorkItemDto workItemDto) {
        
        logger.info("Updating work item: {}", id);
        
        try {
            workItemDto.setId(id);
            
            Optional<WorkItemDto> existingWorkItem = workItemService.getWorkItemById(id);
            if (existingWorkItem.isEmpty()) {
                return ResponseEntity.notFound().build();
            }
            
            WorkItemDto updated = existingWorkItem.get();
            
            if (workItemDto.getTitle() != null) updated.setTitle(workItemDto.getTitle());
            if (workItemDto.getDescription() != null) updated.setDescription(workItemDto.getDescription());
            if (workItemDto.getStatus() != null) updated.setStatus(workItemDto.getStatus());
            if (workItemDto.getPriority() != null) updated.setPriority(workItemDto.getPriority());
            if (workItemDto.getAssignedTo() != null) updated.setAssignedTo(workItemDto.getAssignedTo());
            if (workItemDto.getRiskScore() != null) updated.setRiskScore(workItemDto.getRiskScore());
            
            // This is a simplified update - in practice you'd implement a proper update service method
            return ResponseEntity.ok(updated);
            
        } catch (Exception e) {
            logger.error("Error updating work item {}: {}", id, e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
    
    /**
     * Get work items for a submission
     */
    @GetMapping("/submissions/{submissionId}/workitems")
    public ResponseEntity<List<WorkItemDto>> getWorkItemsForSubmission(@PathVariable Long submissionId) {
        logger.debug("Getting work items for submission: {}", submissionId);
        
        try {
            List<WorkItemDto> workItems = workItemService.getWorkItemsBySubmissionId(submissionId);
            return ResponseEntity.ok(workItems);
            
        } catch (Exception e) {
            logger.error("Error getting work items for submission {}: {}", submissionId, e.getMessage(), e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(List.of());
        }
    }
    
    /**
     * Get LLM service status and models
     */
    @GetMapping("/llm/status")
    public ResponseEntity<Map<String, Object>> getLLMStatus() {
        Map<String, Object> status = new HashMap<>();
        status.put("available", llmServiceClient.isServiceAvailable());
        status.put("models", llmServiceClient.getAvailableModels());
        status.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
        
        return ResponseEntity.ok(status);
    }
    
    /**
     * Get work items needing attention
     */
    @GetMapping("/workitems/attention")
    public ResponseEntity<List<WorkItemDto>> getWorkItemsNeedingAttention() {
        List<WorkItemDto> workItems = workItemService.getWorkItemsNeedingAttention();
        return ResponseEntity.ok(workItems);
    }
    
    /**
     * Search work items
     */
    @GetMapping("/workitems/search")
    public ResponseEntity<Page<WorkItemDto>> searchWorkItems(
            @RequestParam String q,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        
        Pageable pageable = PageRequest.of(page, size);
        Page<WorkItemDto> results = workItemService.searchWorkItems(q, pageable);
        return ResponseEntity.ok(results);
    }
}