package com.bizinsightiq.client.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * Data transfer object mapping FastAPI's ScenarioPredictionRequest schema.
 */
public record ScenarioPredictionRequestDto(
        @JsonProperty("category") String category,
        @JsonProperty("region") String region,
        @JsonProperty("quantity") Integer quantity,
        @JsonProperty("discount") Double discount,
        @JsonProperty("month") Integer month,
        @JsonProperty("quarter") Integer quarter,
        @JsonProperty("day_of_week") Integer dayOfWeek,
        @JsonProperty("model_type") String modelType,
        @JsonProperty("dataset_id") String datasetId
) {
    public ScenarioPredictionRequestDto(
            String category,
            String region,
            Integer quantity,
            Double discount,
            Integer month,
            Integer quarter,
            Integer dayOfWeek
    ) {
        this(category, region, quantity, discount, month, quarter, dayOfWeek, "random_forest", null);
    }
}
