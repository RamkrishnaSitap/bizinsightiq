package com.bizinsightiq;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Main entry point for BizInsightIQ Enterprise Spring Boot Backend.
 * <p>
 * Authoritative manager for database persistence, Flyway migrations,
 * business orchestration, and secure communication with the Python FastAPI ML microservice.
 */
@SpringBootApplication
public class BizInsightIqApplication {

    public static void main(String[] args) {
        SpringApplication.run(BizInsightIqApplication.class, args);
    }
}
