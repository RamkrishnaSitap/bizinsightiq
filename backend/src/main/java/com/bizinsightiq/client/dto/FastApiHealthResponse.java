package com.bizinsightiq.client.dto;

import com.fasterxml.jackson.annotation.JsonAlias;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public record FastApiHealthResponse(
    String status,
    @JsonAlias({"service", "app"})
    String app,
    String version,
    @JsonProperty("core_modules")
    List<String> coreModules
) {
    public boolean isHealthy() {
        return "ok".equalsIgnoreCase(status);
    }
}
