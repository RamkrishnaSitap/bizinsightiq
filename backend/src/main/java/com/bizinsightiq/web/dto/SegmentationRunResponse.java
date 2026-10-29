package com.bizinsightiq.web.dto;

import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.UUID;

public record SegmentationRunResponse(
        UUID runId,
        UUID datasetId,
        Integer nClusters,
        Double silhouetteScore,
        Double inertia,
        List<Double> pcaVarianceRatio,
        List<Map<String, Object>> clusterProfiles,
        List<Map<String, Object>> candidatesEvaluation,
        Integer assignedCustomerCount,
        Instant createdAt
) {}
