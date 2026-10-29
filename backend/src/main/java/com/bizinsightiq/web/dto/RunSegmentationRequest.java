package com.bizinsightiq.web.dto;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;

public record RunSegmentationRequest(
        @Min(value = 2, message = "Cluster count must be at least 2")
        @Max(value = 7, message = "Cluster count cannot exceed 7")
        Integer nClusters,

        Integer randomState,

        Boolean evaluateCandidates
) {
    public RunSegmentationRequest {
        if (nClusters == null) nClusters = 4;
        if (randomState == null) randomState = 42;
        if (evaluateCandidates == null) evaluateCandidates = true;
    }
}
