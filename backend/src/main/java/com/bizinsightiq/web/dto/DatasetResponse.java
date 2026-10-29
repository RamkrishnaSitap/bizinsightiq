package com.bizinsightiq.web.dto;

import com.bizinsightiq.domain.model.Dataset;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.time.Instant;
import java.util.UUID;

public record DatasetResponse(
    UUID id,
    UUID userId,
    String name,
    String originalFilename,
    String storageKey,
    String status,
    int totalRows,
    int totalColumns,
    boolean isValid,
    Instant uploadedAt
) {
    @JsonProperty("createdAt")
    public Instant createdAt() {
        return uploadedAt;
    }

    public static DatasetResponse fromEntity(Dataset entity) {
        return new DatasetResponse(
                entity.getId(),
                entity.getUserId(),
                entity.getName(),
                entity.getOriginalFilename(),
                entity.getStorageKey(),
                entity.getStatus(),
                entity.getTotalRows(),
                entity.getTotalColumns(),
                entity.getIsValid(),
                entity.getUploadedAt()
        );
    }
}
