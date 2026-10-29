package com.bizinsightiq.web.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

public record CreateDatasetRequest(
    @NotBlank(message = "Dataset name cannot be blank")
    @Size(max = 150, message = "Dataset name cannot exceed 150 characters")
    String name,

    @NotBlank(message = "Original filename cannot be blank")
    @Size(max = 255, message = "Original filename cannot exceed 255 characters")
    String originalFilename,

    @NotBlank(message = "Storage key cannot be blank")
    @Size(max = 500, message = "Storage key cannot exceed 500 characters")
    String storageKey,

    Integer totalRows,
    Integer totalColumns
) {}
