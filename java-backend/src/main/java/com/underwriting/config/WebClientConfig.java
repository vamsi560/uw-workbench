package com.underwriting.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.beans.factory.annotation.Value;

@Configuration
public class WebClientConfig {
    
    @Value("${llm.service.url:http://localhost:8001}")
    private String llmServiceUrl;
    
    @Bean
    public WebClient webClient() {
        return WebClient.builder()
                .baseUrl(llmServiceUrl)
                .defaultHeader("Content-Type", "application/json")
                .codecs(configurer -> configurer.defaultCodecs().maxInMemorySize(10 * 1024 * 1024)) // 10MB
                .build();
    }
}