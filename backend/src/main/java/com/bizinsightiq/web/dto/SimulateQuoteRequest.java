package com.bizinsightiq.web.dto;

import jakarta.validation.constraints.*;

import java.math.BigDecimal;

public record SimulateQuoteRequest(
        @NotBlank(message = "Category is required")
        @Size(max = 50, message = "Category cannot exceed 50 characters")
        String category,

        @NotBlank(message = "Region is required")
        @Size(max = 50, message = "Region cannot exceed 50 characters")
        String region,

        @NotNull(message = "Quantity is required")
        @Min(value = 1, message = "Quantity must be at least 1")
        @Max(value = 1000, message = "Quantity cannot exceed 1000")
        Integer quantity,

        @NotNull(message = "Discount is required")
        @DecimalMin(value = "0.0000", message = "Discount cannot be negative")
        @DecimalMax(value = "1.0000", message = "Discount cannot exceed 1.0 (100%)")
        BigDecimal discount,

        @Min(value = 1, message = "Month must be between 1 and 12")
        @Max(value = 12, message = "Month must be between 1 and 12")
        Integer month,

        @Min(value = 1, message = "Quarter must be between 1 and 4")
        @Max(value = 4, message = "Quarter must be between 1 and 4")
        Integer quarter,

        @Min(value = 0, message = "Day of week must be between 0 and 6")
        @Max(value = 6, message = "Day of week must be between 0 and 6")
        Integer dayOfWeek,

        String modelType
) {
    public SimulateQuoteRequest(
            String category,
            String region,
            Integer quantity,
            BigDecimal discount,
            Integer month,
            Integer quarter,
            Integer dayOfWeek
    ) {
        this(category, region, quantity, discount, month, quarter, dayOfWeek, "random_forest");
    }
}
