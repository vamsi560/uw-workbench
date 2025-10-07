package com.underwriting.service;

import com.underwriting.domain.WorkItem;
import com.underwriting.domain.WorkItemStatus;
import com.underwriting.domain.WorkItemPriority;
import com.underwriting.dto.WorkItemDto;
import com.underwriting.dto.SubmissionDto;
import com.underwriting.repository.WorkItemRepository;
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
import java.util.stream.Collectors;

@Service
@Transactional
public class WorkItemService {
    
    @Autowired
    private WorkItemRepository workItemRepository;
    
    @Autowired
    private SubmissionRepository submissionRepository;
    
    @Autowired
    private SubmissionService submissionService;
    
    /**
     * Create a new work item
     */
    public WorkItemDto createWorkItem(WorkItemDto workItemDto) {
        // Verify submission exists
        submissionRepository.findById(workItemDto.getSubmissionId())
            .orElseThrow(() -> new RuntimeException("Submission not found"));
        
        WorkItem workItem = convertToEntity(workItemDto);
        workItem = workItemRepository.save(workItem);
        
        return convertToDto(workItem);
    }
    
    /**
     * Get work item by ID
     */
    @Transactional(readOnly = true)
    public Optional<WorkItemDto> getWorkItemById(Long id) {
        return workItemRepository.findById(id)
            .map(this::convertToDto);
    }
    
    /**
     * Get work items by submission ID
     */
    @Transactional(readOnly = true)
    public List<WorkItemDto> getWorkItemsBySubmissionId(Long submissionId) {
        return workItemRepository.findBySubmissionId(submissionId)
            .stream()
            .map(this::convertToDto)
            .collect(Collectors.toList());
    }
    
    /**
     * Get work items for polling
     */
    @Transactional(readOnly = true)
    public List<WorkItemDto> getWorkItemsForPolling(Optional<Long> sinceId, Optional<LocalDateTime> since, int limit) {
        Pageable pageable = PageRequest.of(0, limit, Sort.by("createdAt").descending());
        
        List<WorkItem> workItems;
        if (sinceId.isPresent()) {
            workItems = workItemRepository.findWorkItemsSinceId(sinceId.get(), pageable);
        } else if (since.isPresent()) {
            workItems = workItemRepository.findWorkItemsSince(since.get(), pageable);
        } else {
            workItems = workItemRepository.findLatestWorkItems(pageable);
        }
        
        return workItems.stream()
            .map(this::convertToDto)
            .collect(Collectors.toList());
    }
    
    /**
     * Get work items by status
     */
    @Transactional(readOnly = true)
    public Page<WorkItemDto> getWorkItemsByStatus(WorkItemStatus status, Pageable pageable) {
        return workItemRepository.findByStatus(status, pageable)
            .map(this::convertToDto);
    }
    
    /**
     * Get work items by assigned user
     */
    @Transactional(readOnly = true)
    public Page<WorkItemDto> getWorkItemsByAssignedTo(String assignedTo, Pageable pageable) {
        return workItemRepository.findByAssignedTo(assignedTo, pageable)
            .map(this::convertToDto);
    }
    
    /**
     * Get work items needing attention
     */
    @Transactional(readOnly = true)
    public List<WorkItemDto> getWorkItemsNeedingAttention() {
        LocalDateTime overdueThreshold = LocalDateTime.now().minusDays(2);
        return workItemRepository.findWorkItemsNeedingAttention(overdueThreshold)
            .stream()
            .map(this::convertToDto)
            .collect(Collectors.toList());
    }
    
    /**
     * Update work item status
     */
    public WorkItemDto updateWorkItemStatus(Long id, WorkItemStatus newStatus) {
        WorkItem workItem = workItemRepository.findById(id)
            .orElseThrow(() -> new RuntimeException("Work item not found"));
        
        workItem.setStatus(newStatus);
        workItem = workItemRepository.save(workItem);
        
        return convertToDto(workItem);
    }
    
    /**
     * Assign work item to user
     */
    public WorkItemDto assignWorkItem(Long id, String assignedTo) {
        WorkItem workItem = workItemRepository.findById(id)
            .orElseThrow(() -> new RuntimeException("Work item not found"));
        
        workItem.setAssignedTo(assignedTo);
        workItem = workItemRepository.save(workItem);
        
        return convertToDto(workItem);
    }
    
    /**
     * Update work item priority
     */
    public WorkItemDto updateWorkItemPriority(Long id, WorkItemPriority priority) {
        WorkItem workItem = workItemRepository.findById(id)
            .orElseThrow(() -> new RuntimeException("Work item not found"));
        
        workItem.setPriority(priority);
        workItem = workItemRepository.save(workItem);
        
        return convertToDto(workItem);
    }
    
    /**
     * Update work item risk score
     */
    public WorkItemDto updateWorkItemRiskScore(Long id, Double riskScore) {
        WorkItem workItem = workItemRepository.findById(id)
            .orElseThrow(() -> new RuntimeException("Work item not found"));
        
        workItem.setRiskScore(riskScore);
        workItem.setLastRiskAssessment(LocalDateTime.now());
        workItem = workItemRepository.save(workItem);
        
        return convertToDto(workItem);
    }
    
    /**
     * Search work items
     */
    @Transactional(readOnly = true)
    public Page<WorkItemDto> searchWorkItems(String searchTerm, Pageable pageable) {
        return workItemRepository.searchWorkItems(searchTerm, pageable)
            .map(this::convertToDto);
    }
    
    /**
     * Convert entity to DTO
     */
    private WorkItemDto convertToDto(WorkItem workItem) {
        WorkItemDto dto = new WorkItemDto();
        dto.setId(workItem.getId());
        dto.setSubmissionId(workItem.getSubmissionId());
        dto.setTitle(workItem.getTitle());
        dto.setDescription(workItem.getDescription());
        dto.setAssignedTo(workItem.getAssignedTo());
        dto.setStatus(workItem.getStatus());
        dto.setPriority(workItem.getPriority());
        dto.setRiskScore(workItem.getRiskScore());
        dto.setRiskCategories(workItem.getRiskCategories());
        dto.setIndustry(workItem.getIndustry());
        dto.setCompanySize(workItem.getCompanySize());
        dto.setPolicyType(workItem.getPolicyType());
        dto.setCoverageAmount(workItem.getCoverageAmount());
        dto.setLastRiskAssessment(workItem.getLastRiskAssessment());
        dto.setCreatedAt(workItem.getCreatedAt());
        dto.setUpdatedAt(workItem.getUpdatedAt());
        
        // Include submission details if needed
        if (workItem.getSubmission() != null) {
            dto.setSubmission(submissionService.getSubmissionById(workItem.getSubmissionId()).orElse(null));
        }
        
        return dto;
    }
    
    /**
     * Convert DTO to entity
     */
    private WorkItem convertToEntity(WorkItemDto dto) {
        WorkItem workItem = new WorkItem();
        workItem.setId(dto.getId());
        workItem.setSubmissionId(dto.getSubmissionId());
        workItem.setTitle(dto.getTitle());
        workItem.setDescription(dto.getDescription());
        workItem.setAssignedTo(dto.getAssignedTo());
        workItem.setStatus(dto.getStatus() != null ? dto.getStatus() : WorkItemStatus.PENDING);
        workItem.setPriority(dto.getPriority() != null ? dto.getPriority() : WorkItemPriority.MEDIUM);
        workItem.setRiskScore(dto.getRiskScore());
        workItem.setRiskCategories(dto.getRiskCategories());
        workItem.setIndustry(dto.getIndustry());
        workItem.setCompanySize(dto.getCompanySize());
        workItem.setPolicyType(dto.getPolicyType());
        workItem.setCoverageAmount(dto.getCoverageAmount());
        workItem.setLastRiskAssessment(dto.getLastRiskAssessment());
        return workItem;
    }
}