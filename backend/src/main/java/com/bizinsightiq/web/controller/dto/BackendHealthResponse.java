package com.bizinsightiq.web.controller.dto;

import java.time.Instant;
import java.util.Map;

public record BackendHealthResponse(
    String status,
    String service,
    String version,
    Instant timestamp,
    Map<String, Object> downstream
) {}
