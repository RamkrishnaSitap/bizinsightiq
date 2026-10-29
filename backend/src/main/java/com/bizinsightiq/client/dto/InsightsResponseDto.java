package com.bizinsightiq.client.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;
import java.util.Map;

/**
 * Data transfer object mapping FastAPI's InsightsResponse schema.
 */
public record InsightsResponseDto(
        @JsonProperty("summary") InsightsSummaryDto summary,
        @JsonProperty("insights") List<InsightItemDto> insights
) {
    public record InsightsSummaryDto(
            @JsonProperty("total_insights") Integer totalInsights,
            @JsonProperty("critical_count") Integer criticalCount,
            @JsonProperty("warning_count") Integer warningCount,
            @JsonProperty("info_count") Integer infoCount
    ) {}

    public record InsightItemDto(
            @JsonProperty("insight_id") String insightId,
            @JsonProperty("category") String category,
            @JsonProperty("severity") String severity,
            @JsonProperty("title") String title,
            @JsonProperty("evidence") Map<String, Object> evidence,
            @JsonProperty("recommendation") String recommendation,
            @JsonProperty("limitations") String limitations
    ) {}
}
