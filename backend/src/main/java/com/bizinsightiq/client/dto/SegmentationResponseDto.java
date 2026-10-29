package com.bizinsightiq.client.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;
import java.util.Map;

/**
 * Data transfer object mapping FastAPI's SegmentationResponse schema.
 */
public record SegmentationResponseDto(
        @JsonProperty("n_clusters") Integer nClusters,
        @JsonProperty("silhouette_score") Double silhouetteScore,
        @JsonProperty("inertia") Double inertia,
        @JsonProperty("pca_variance_ratio") List<Double> pcaVarianceRatio,
        @JsonProperty("cluster_profiles") List<Map<String, Object>> clusterProfiles,
        @JsonProperty("candidates_evaluation") List<Map<String, Object>> candidatesEvaluation,
        @JsonProperty("customer_assignments") List<CustomerAssignmentDto> customerAssignments
) {
    public record CustomerAssignmentDto(
            @JsonProperty("customer_id") String customerId,
            @JsonProperty("cluster_id") Integer clusterId,
            @JsonProperty("recency") Integer recency,
            @JsonProperty("frequency") Integer frequency,
            @JsonProperty("monetary_value") Double monetaryValue,
            @JsonProperty("total_profit") Double totalProfit
    ) {}
}
