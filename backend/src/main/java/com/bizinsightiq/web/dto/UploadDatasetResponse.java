package com.bizinsightiq.web.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.Collections;
import java.util.List;
import java.util.UUID;

public record UploadDatasetResponse(
    UUID datasetId,
    String name,
    String originalFilename,
    String status,
    int totalRows,
    int validRows,
    int invalidRows,
    boolean isValid,
    List<String> errors,
    List<String> warnings,
    String message
) {
    @JsonProperty("id")
    public UUID id() {
        return datasetId;
    }

    public static UploadDatasetResponse success(
            UUID datasetId,
            String name,
            String originalFilename,
            int totalRows,
            List<String> warnings) {

        return new UploadDatasetResponse(
                datasetId,
                name,
                originalFilename,
                "VALIDATED",
                totalRows,
                totalRows,
                0,
                true,
                Collections.emptyList(),
                warnings != null ? warnings : Collections.emptyList(),
                "Dataset uploaded, validated, and persisted successfully."
        );
    }

    public static UploadDatasetResponse failure(
            UUID datasetId,
            String name,
            String originalFilename,
            int totalRows,
            List<String> errors,
            List<String> warnings,
            String message) {

        return new UploadDatasetResponse(
                datasetId,
                name,
                originalFilename,
                "FAILED",
                totalRows,
                0,
                totalRows,
                false,
                errors != null ? errors : Collections.emptyList(),
                warnings != null ? warnings : Collections.emptyList(),
                message
        );
    }
}
