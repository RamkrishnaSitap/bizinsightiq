package com.bizinsightiq.web.dto;

import com.bizinsightiq.domain.model.QuoteSimulation;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;

public record QuoteSimulationResponse(
        UUID id,
        UUID userId,
        UUID datasetId,
        String category,
        String region,
        Integer quantity,
        BigDecimal discount,
        BigDecimal predictedSales,
        String modelVersion,
        Instant createdAt
) {
    public static QuoteSimulationResponse fromEntity(QuoteSimulation entity) {
        return new QuoteSimulationResponse(
                entity.getId(),
                entity.getUserId(),
                entity.getDatasetId(),
                entity.getCategory(),
                entity.getRegion(),
                entity.getQuantity(),
                entity.getDiscount(),
                entity.getPredictedSales(),
                entity.getModelVersion(),
                entity.getCreatedAt()
        );
    }
}
