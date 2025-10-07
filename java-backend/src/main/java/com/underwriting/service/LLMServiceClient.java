package com.underwriting.service;

import com.underwriting.dto.llm.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;
import reactor.core.publisher.Mono;
import reactor.util.retry.Retry;

import java.time.Duration;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.TimeoutException;

@Service
public class LLMServiceClient {
    
    private static final Logger logger = LoggerFactory.getLogger(LLMServiceClient.class);
    
    @Value("${llm.service.url}")
    private String llmServiceUrl;
    
    @Value("${llm.service.timeout:30s}")
    private Duration timeout;
    
    @Value("${llm.service.retry.max-attempts:3}")
    private int maxRetryAttempts;
    
    private final WebClient webClient;
    
    public LLMServiceClient(WebClient.Builder webClientBuilder) {
        this.webClient = webClientBuilder
            .codecs(configurer -> configurer.defaultCodecs().maxInMemorySize(10 * 1024 * 1024)) // 10MB
            .build();
    }
    
    /**
     * Extract structured data from text using LLM service
     */
    public LLMExtractionResponse extractData(String text, String subject, String senderEmail) {
        logger.info("Calling LLM service for data extraction. Text length: {}", text.length());
        
        try {
            LLMExtractionRequest request = new LLMExtractionRequest(text, subject, senderEmail);
            
            LLMExtractionResponse response = webClient
                .post()
                .uri(llmServiceUrl + "/api/extract")
                .bodyValue(request)
                .retrieve()
                .bodyToMono(LLMExtractionResponse.class)
                .timeout(timeout)
                .retryWhen(createRetrySpec("extraction"))
                .block();
            
            logger.info("LLM extraction completed successfully. Processing time: {}ms", 
                       response != null ? response.getProcessingTimeMs() : "unknown");
            
            return response != null ? response : createFallbackExtractionResponse();
            
        } catch (Exception e) {
            logger.error("LLM extraction failed: {}", e.getMessage(), e);
            return createFallbackExtractionResponse();
        }
    }
    
    /**
     * Perform AI-driven triage and prioritization
     */
    public LLMTriageResponse triageSubmission(Map<String, Object> submissionData, Map<String, Object> extractedFields) {
        logger.info("Calling LLM service for submission triage");
        
        try {
            LLMTriageRequest request = new LLMTriageRequest(submissionData, extractedFields);
            
            LLMTriageResponse response = webClient
                .post()
                .uri(llmServiceUrl + "/api/triage")
                .bodyValue(request)
                .retrieve()
                .bodyToMono(LLMTriageResponse.class)
                .timeout(timeout)
                .retryWhen(createRetrySpec("triage"))
                .block();
            
            logger.info("LLM triage completed successfully. Priority: {}, Risk Score: {}", 
                       response != null ? response.getPriority() : "unknown",
                       response != null ? response.getRiskScore() : "unknown");
            
            return response != null ? response : createFallbackTriageResponse();
            
        } catch (Exception e) {
            logger.error("LLM triage failed: {}", e.getMessage(), e);
            return createFallbackTriageResponse();
        }
    }
    
    /**
     * Perform AI-driven risk assessment
     */
    public LLMRiskAssessmentResponse assessRisk(Map<String, Object> submissionData, Map<String, Object> extractedFields) {
        logger.info("Calling LLM service for risk assessment");
        
        try {
            LLMRiskAssessmentRequest request = new LLMRiskAssessmentRequest(submissionData, extractedFields);
            
            LLMRiskAssessmentResponse response = webClient
                .post()
                .uri(llmServiceUrl + "/api/risk-assessment")
                .bodyValue(request)
                .retrieve()
                .bodyToMono(LLMRiskAssessmentResponse.class)
                .timeout(timeout)
                .retryWhen(createRetrySpec("risk-assessment"))
                .block();
            
            logger.info("LLM risk assessment completed successfully. Overall risk score: {}", 
                       response != null ? response.getOverallRiskScore() : "unknown");
            
            return response != null ? response : createFallbackRiskAssessmentResponse();
            
        } catch (Exception e) {
            logger.error("LLM risk assessment failed: {}", e.getMessage(), e);
            return createFallbackRiskAssessmentResponse();
        }
    }
    
    /**
     * Check if LLM service is available
     */
    public boolean isServiceAvailable() {
        try {
            Map<String, Object> healthResponse = webClient
                .get()
                .uri(llmServiceUrl + "/api/health")
                .retrieve()
                .bodyToMono(Map.class)
                .timeout(Duration.ofSeconds(5))
                .block();
            
            boolean isHealthy = healthResponse != null && 
                               "healthy".equals(healthResponse.get("status"));
            
            logger.debug("LLM service health check: {}", isHealthy ? "healthy" : "unhealthy");
            return isHealthy;
            
        } catch (Exception e) {
            logger.warn("LLM service health check failed: {}", e.getMessage());
            return false;
        }
    }
    
    /**
     * Get available AI models from LLM service
     */
    public Map<String, Object> getAvailableModels() {
        try {
            Map<String, Object> modelsResponse = webClient
                .get()
                .uri(llmServiceUrl + "/api/models")
                .retrieve()
                .bodyToMono(Map.class)
                .timeout(Duration.ofSeconds(10))
                .block();
            
            logger.debug("Retrieved available models from LLM service");
            return modelsResponse != null ? modelsResponse : new HashMap<>();
            
        } catch (Exception e) {
            logger.error("Failed to get available models: {}", e.getMessage());
            return new HashMap<>();
        }
    }
    
    /**
     * Create retry specification for different operations
     */
    private Retry createRetrySpec(String operation) {
        return Retry.backoff(maxRetryAttempts, Duration.ofSeconds(1))
            .maxBackoff(Duration.ofSeconds(10))
            .filter(this::isRetryableException)
            .doBeforeRetry(retrySignal -> 
                logger.warn("Retrying {} operation. Attempt: {}, Error: {}", 
                          operation, retrySignal.totalRetries() + 1, retrySignal.failure().getMessage()))
            .onRetryExhaustedThrow((retryBackoffSpec, retrySignal) -> 
                new RuntimeException("LLM service " + operation + " failed after " + maxRetryAttempts + " attempts", 
                                   retrySignal.failure()));
    }
    
    /**
     * Determine if an exception is retryable
     */
    private boolean isRetryableException(Throwable throwable) {
        if (throwable instanceof WebClientResponseException) {
            WebClientResponseException webClientException = (WebClientResponseException) throwable;
            HttpStatus status = HttpStatus.resolve(webClientException.getStatusCode().value());
            // Retry on server errors (5xx) but not client errors (4xx)
            return status != null && status.is5xxServerError();
        }
        // Retry on timeout and connection issues
        return throwable instanceof TimeoutException || 
               throwable.getCause() instanceof java.net.ConnectException;
    }
    
    /**
     * Create fallback response when extraction fails
     */
    private LLMExtractionResponse createFallbackExtractionResponse() {
        Map<String, Object> fallbackFields = new HashMap<>();
        fallbackFields.put("status", "extraction_failed");
        fallbackFields.put("fallback", true);
        fallbackFields.put("company_name", "Unknown");
        fallbackFields.put("industry", "Unknown");
        
        Map<String, Object> fallbackSummary = new HashMap<>();
        fallbackSummary.put("summary", "LLM service unavailable - manual review required");
        fallbackSummary.put("confidence", 0.0);
        
        LLMExtractionResponse response = new LLMExtractionResponse(fallbackFields, fallbackSummary);
        response.setModelUsed("fallback");
        response.setProcessingTimeMs(0.0);
        
        return response;
    }
    
    /**
     * Create fallback response when triage fails
     */
    private LLMTriageResponse createFallbackTriageResponse() {
        LLMTriageResponse response = new LLMTriageResponse("MEDIUM", 5.0, "Manual Review");
        response.setReasoning("LLM service unavailable - assigned default priority");
        response.setRecommendedActions(java.util.Arrays.asList("Manual review required", "Assign to underwriter"));
        return response;
    }
    
    /**
     * Create fallback response when risk assessment fails
     */
    private LLMRiskAssessmentResponse createFallbackRiskAssessmentResponse() {
        LLMRiskAssessmentResponse response = new LLMRiskAssessmentResponse();
        response.setOverallRiskScore(5.0);
        
        Map<String, Double> fallbackCategories = new HashMap<>();
        fallbackCategories.put("technical", 5.0);
        fallbackCategories.put("operational", 5.0);
        fallbackCategories.put("financial", 5.0);
        fallbackCategories.put("compliance", 5.0);
        response.setRiskCategories(fallbackCategories);
        
        response.setRecommendations(java.util.Arrays.asList("Manual risk assessment required"));
        response.setConfidenceScore(0.0);
        
        return response;
    }
}