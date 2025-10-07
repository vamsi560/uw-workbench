package com.underwriting.repository;

import com.underwriting.domain.WorkItem;
import com.underwriting.domain.WorkItemStatus;
import com.underwriting.domain.WorkItemPriority;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface WorkItemRepository extends JpaRepository<WorkItem, Long> {
    
    // Find work items by submission ID
    List<WorkItem> findBySubmissionId(Long submissionId);
    
    // Find work items by status
    List<WorkItem> findByStatus(WorkItemStatus status);
    Page<WorkItem> findByStatus(WorkItemStatus status, Pageable pageable);
    
    // Find work items by priority
    List<WorkItem> findByPriority(WorkItemPriority priority);
    Page<WorkItem> findByPriority(WorkItemPriority priority, Pageable pageable);
    
    // Find work items assigned to a specific user
    List<WorkItem> findByAssignedTo(String assignedTo);
    Page<WorkItem> findByAssignedTo(String assignedTo, Pageable pageable);
    
    // Find work items that need attention (high priority, unassigned, or overdue)
    @Query("SELECT wi FROM WorkItem wi WHERE " +
           "(wi.priority IN ('HIGH', 'CRITICAL')) OR " +
           "(wi.assignedTo IS NULL) OR " +
           "(wi.status = 'PENDING' AND wi.createdAt < :overdueThreshold)")
    List<WorkItem> findWorkItemsNeedingAttention(@Param("overdueThreshold") LocalDateTime overdueThreshold);
    
    // Find work items for polling (recent updates)
    @Query("SELECT wi FROM WorkItem wi WHERE wi.id > :sinceId ORDER BY wi.createdAt DESC")
    List<WorkItem> findWorkItemsSinceId(@Param("sinceId") Long sinceId, Pageable pageable);
    
    // Find work items updated since timestamp (for polling)
    @Query("SELECT wi FROM WorkItem wi WHERE wi.updatedAt > :since ORDER BY wi.createdAt DESC")
    List<WorkItem> findWorkItemsSince(@Param("since") LocalDateTime since, Pageable pageable);
    
    // Get latest work items (for polling without parameters)
    @Query("SELECT wi FROM WorkItem wi ORDER BY wi.createdAt DESC")
    List<WorkItem> findLatestWorkItems(Pageable pageable);
    
    // Find work items by risk score range
    @Query("SELECT wi FROM WorkItem wi WHERE wi.riskScore >= :minScore AND wi.riskScore <= :maxScore")
    List<WorkItem> findByRiskScoreRange(@Param("minScore") Double minScore, @Param("maxScore") Double maxScore);
    
    // Count work items by status
    @Query("SELECT COUNT(wi) FROM WorkItem wi WHERE wi.status = :status")
    long countByStatus(@Param("status") WorkItemStatus status);
    
    // Count work items by assigned user
    @Query("SELECT COUNT(wi) FROM WorkItem wi WHERE wi.assignedTo = :assignedTo")
    long countByAssignedTo(@Param("assignedTo") String assignedTo);
    
    // Find work items with high risk scores
    @Query("SELECT wi FROM WorkItem wi WHERE wi.riskScore > :threshold ORDER BY wi.riskScore DESC")
    List<WorkItem> findHighRiskWorkItems(@Param("threshold") Double threshold);
    
    // Find work items by industry
    List<WorkItem> findByIndustry(String industry);
    
    // Search work items by title or description
    @Query("SELECT wi FROM WorkItem wi WHERE " +
           "LOWER(wi.title) LIKE LOWER(CONCAT('%', :searchTerm, '%')) OR " +
           "LOWER(wi.description) LIKE LOWER(CONCAT('%', :searchTerm, '%'))")
    Page<WorkItem> searchWorkItems(@Param("searchTerm") String searchTerm, Pageable pageable);
}