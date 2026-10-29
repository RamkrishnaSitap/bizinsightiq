package com.bizinsightiq.client.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * Data transfer object mapping FastAPI's ScenarioPredictionResponse schema.
 */
public record ScenarioPredictionResponseDto(
        @JsonProperty("predicted_sales") Double predictedSales,
        @JsonProperty("category") String category,
        @JsonProperty("region") String region,
        @JsonProperty("quantity") Integer quantity,
        @JsonProperty("discount") Double discount,
        @JsonProperty("month") Integer month,
        @JsonProperty("quarter") Integer quarter,
        @JsonProperty("day_of_week") Integer dayOfWeek,
        @JsonProperty("model_used") String modelUsed
) {}
