package com.bizinsightiq.web.dto;

import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Pattern;

public record TrainPredictionRequest(
        @Pattern(regexp = "^(chronological|random)$", message = "Split strategy must be 'chronological' or 'random'")
        String splitStrategy,

        @DecimalMin(value = "0.05", message = "Test size must be at least 0.05")
        @DecimalMax(value = "0.50", message = "Test size cannot exceed 0.50")
        Double testSize,

        Integer randomState
) {
    public TrainPredictionRequest {
        if (splitStrategy == null) splitStrategy = "chronological";
        if (testSize == null) testSize = 0.20;
        if (randomState == null) randomState = 42;
    }
}
