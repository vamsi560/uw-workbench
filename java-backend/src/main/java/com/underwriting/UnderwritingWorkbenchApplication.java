package com.underwriting;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;

@SpringBootApplication
@EnableConfigurationProperties
public class UnderwritingWorkbenchApplication {

    public static void main(String[] args) {
        SpringApplication.run(UnderwritingWorkbenchApplication.class, args);
    }
}