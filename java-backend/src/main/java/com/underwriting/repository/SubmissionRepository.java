package com.underwriting.repository;

import com.underwriting.domain.Submission;
import com.underwriting.domain.SubmissionStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface SubmissionRepository extends JpaRepository<Submission, Long> {
    
    // Find by submission reference UUID
    Optional<Submission> findBySubmissionRef(UUID submissionRef);
    
    // Find submissions by status
    List<Submission> findByStatus(SubmissionStatus status);
    Page<Submission> findByStatus(SubmissionStatus status, Pageable pageable);
    
    // Find submissions assigned to a specific user
    List<Submission> findByAssignedTo(String assignedTo);
    Page<Submission> findByAssignedTo(String assignedTo, Pageable pageable);
    
    // Find submissions by sender email
    List<Submission> findBySenderEmail(String senderEmail);
    
    // Find recent submissions
    @Query("SELECT s FROM Submission s WHERE s.createdAt >= :since ORDER BY s.createdAt DESC")
    List<Submission> findRecentSubmissions(@Param("since") LocalDateTime since);
    
    // Find submissions since a specific ID (for polling)
    @Query("SELECT s FROM Submission s WHERE s.id > :sinceId ORDER BY s.createdAt ASC")
    List<Submission> findSinceId(@Param("sinceId") Long sinceId, Pageable pageable);
    
    // Find submissions since a specific timestamp (for polling)
    @Query("SELECT s FROM Submission s WHERE s.createdAt > :since ORDER BY s.createdAt ASC")
    List<Submission> findSince(@Param("since") LocalDateTime since, Pageable pageable);
    
    // Find latest submissions
    List<Submission> findTop20ByOrderByCreatedAtDesc();
    
    // Count submissions by status
    @Query("SELECT COUNT(s) FROM Submission s WHERE s.status = :status")
    long countByStatus(@Param("status") SubmissionStatus status);
    
    // Find submissions that need attention (no work items or unassigned)
    @Query("SELECT s FROM Submission s LEFT JOIN s.workItems wi WHERE wi IS NULL OR s.assignedTo IS NULL")
    List<Submission> findSubmissionsNeedingAttention();
    
    // Search submissions by subject or sender email
    @Query("SELECT s FROM Submission s WHERE " +
           "LOWER(s.subject) LIKE LOWER(CONCAT('%', :searchTerm, '%')) OR " +
           "LOWER(s.senderEmail) LIKE LOWER(CONCAT('%', :searchTerm, '%'))")
    Page<Submission> searchSubmissions(@Param("searchTerm") String searchTerm, Pageable pageable);
    
    // Find duplicate submissions (same subject and sender within timeframe)
    @Query("SELECT s FROM Submission s WHERE s.subject = :subject AND s.senderEmail = :senderEmail " +
           "AND s.createdAt > :since ORDER BY s.createdAt DESC")
    List<Submission> findPotentialDuplicates(@Param("subject") String subject, 
                                           @Param("senderEmail") String senderEmail, 
                                           @Param("since") LocalDateTime since);
}