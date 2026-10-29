package com.bizinsightiq.client.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;
import java.util.Map;

/**
 * Data transfer object mapping FastAPI's PredictionTrainingResponse schema.
 */
public record PredictionTrainingResponseDto(
        @JsonProperty("comparison") List<Map<String, Object>> comparison,
        @JsonProperty("metrics") Map<String, RegressionMetricsDto> metrics,
        @JsonProperty("metadata") Map<String, Object> metadata
) {
    public record RegressionMetricsDto(
            @JsonProperty("mae") Double mae,
            @JsonProperty("rmse") Double rmse,
            @JsonProperty("r2") Double r2,
            @JsonProperty("test_size") Integer testSize,
            @JsonProperty("split_strategy") String splitStrategy
    ) {}
}
