package com.bizinsightiq.web.controller;

import com.bizinsightiq.client.PythonMlClient;
import com.bizinsightiq.client.dto.FastApiHealthResponse;
import com.bizinsightiq.web.controller.dto.BackendHealthResponse;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.Instant;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/v1")
public class HealthController {

    private final PythonMlClient pythonMlClient;

    public HealthController(PythonMlClient pythonMlClient) {
        this.pythonMlClient = pythonMlClient;
    }

    @GetMapping("/health")
    public ResponseEntity<BackendHealthResponse> getHealth() {
        Map<String, Object> downstream = new HashMap<>();

        try {
            FastApiHealthResponse fastApiHealth = pythonMlClient.checkHealth();
            Map<String, Object> fastApiDetails = new HashMap<>();
            fastApiDetails.put("status", fastApiHealth.status() != null ? fastApiHealth.status() : "UP");
            fastApiDetails.put("app", fastApiHealth.app() != null ? fastApiHealth.app() : "BizInsightIQ AI/ML REST API");
            fastApiDetails.put("version", fastApiHealth.version() != null ? fastApiHealth.version() : "1.0.0");
            downstream.put("fastapi", fastApiDetails);
        } catch (Exception ex) {
            downstream.put("fastapi", Map.of(
                    "status", "UNAVAILABLE",
                    "detail", "Microservice connection offline"
            ));
        }

        BackendHealthResponse response = new BackendHealthResponse(
                "UP",
                "BizInsightIQ Spring Boot Enterprise Core",
                "1.0.0",
                Instant.now(),
                downstream
        );

        return ResponseEntity.ok(response);
    }
}
