package com.bizinsightiq.client.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

/**
 * Data transfer object mapping FastAPI's ScenarioComparisonResponse schema.
 */
public record ScenarioComparisonResponseDto(
        @JsonProperty("scenario_a") PredictionExplanationResponseDto scenarioA,
        @JsonProperty("scenario_b") PredictionExplanationResponseDto scenarioB,
        @JsonProperty("predicted_sales_a") Double predictedSalesA,
        @JsonProperty("predicted_sales_b") Double predictedSalesB,
        @JsonProperty("absolute_difference") Double absoluteDifference,
        @JsonProperty("percentage_difference") Double percentageDifference,
        @JsonProperty("changed_features_count") Integer changedFeaturesCount,
        @JsonProperty("feature_comparisons") List<FeatureComparisonItemDto> featureComparisons,
        @JsonProperty("is_difference_additive_exact") Boolean isDifferenceAdditiveExact,
        @JsonProperty("explainer_type") String explainerType,
        @JsonProperty("base_value") Double baseValue,
        @JsonProperty("model_used") String modelUsed,
        @JsonProperty("dataset_id") String datasetId,
        @JsonProperty("success") Boolean success,
        @JsonProperty("disclaimer") String disclaimer
) {
    public record FeatureComparisonItemDto(
            @JsonProperty("feature") String feature,
            @JsonProperty("scenario_a_value") String scenarioAValue,
            @JsonProperty("scenario_b_value") String scenarioBValue,
            @JsonProperty("is_changed") Boolean isChanged,
            @JsonProperty("scenario_a_contribution") Double scenarioAContribution,
            @JsonProperty("scenario_b_contribution") Double scenarioBContribution,
            @JsonProperty("contribution_difference") Double contributionDifference,
            @JsonProperty("direction") String direction,
            @JsonProperty("interpretation") String interpretation
    ) {}
}
