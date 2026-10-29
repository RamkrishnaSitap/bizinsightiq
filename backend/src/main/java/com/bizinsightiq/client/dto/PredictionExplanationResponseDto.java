package com.bizinsightiq.client.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

/**
 * Data transfer object mapping FastAPI's PredictionExplanationResponse schema.
 */
public record PredictionExplanationResponseDto(
        @JsonProperty("predicted_sales") Double predictedSales,
        @JsonProperty("base_value") Double baseValue,
        @JsonProperty("model_used") String modelUsed,
        @JsonProperty("dataset_id") String datasetId,
        @JsonProperty("success") Boolean success,
        @JsonProperty("feature_contributions") List<FeatureContributionDto> featureContributions,
        @JsonProperty("additive_sum") Double additiveSum,
        @JsonProperty("is_additive_exact") Boolean isAdditiveExact,
        @JsonProperty("explainer_type") String explainerType,
        @JsonProperty("disclaimer") String disclaimer
) {
    public record FeatureContributionDto(
            @JsonProperty("feature") String feature,
            @JsonProperty("input_value") String inputValue,
            @JsonProperty("contribution") Double contribution,
            @JsonProperty("direction") String direction,
            @JsonProperty("interpretation") String interpretation,
            @JsonProperty("percentage_impact") Double percentageImpact
    ) {}
}
