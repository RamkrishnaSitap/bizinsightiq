package com.bizinsightiq.client.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * Data transfer object mapping FastAPI's ScenarioComparisonRequest schema.
 */
public record ScenarioComparisonRequestDto(
        @JsonProperty("scenario_a") SingleScenarioInputDto scenarioA,
        @JsonProperty("scenario_b") SingleScenarioInputDto scenarioB,
        @JsonProperty("model_type") String modelType,
        @JsonProperty("dataset_id") String datasetId
) {
    public record SingleScenarioInputDto(
            @JsonProperty("category") String category,
            @JsonProperty("region") String region,
            @JsonProperty("quantity") Integer quantity,
            @JsonProperty("discount") Double discount,
            @JsonProperty("month") Integer month,
            @JsonProperty("quarter") Integer quarter,
            @JsonProperty("day_of_week") Integer dayOfWeek
    ) {}
}
