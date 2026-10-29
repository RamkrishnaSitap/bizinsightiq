package com.bizinsightiq.client.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.Collections;
import java.util.List;
import java.util.Map;

@JsonIgnoreProperties(ignoreUnknown = true)
public record ValidationResponseDto(
    @JsonProperty("is_valid")
    boolean isValid,

    @JsonProperty("total_rows")
    int totalRows,

    @JsonProperty("total_columns")
    int totalColumns,

    @JsonProperty("columns_present")
    List<String> columnsPresent,

    @JsonProperty("missing_columns")
    List<String> missingColumns,

    @JsonProperty("missing_values_by_column")
    Map<String, Integer> missingValuesByColumn,

    @JsonProperty("duplicate_rows_count")
    int duplicateRowsCount,

    @JsonProperty("invalid_numeric_counts")
    Map<String, Integer> invalidNumericCounts,

    @JsonProperty("invalid_date_count")
    int invalidDateCount,

    List<String> errors,
    List<String> warnings
) {
    public List<String> errors() {
        return errors != null ? errors : Collections.emptyList();
    }

    public List<String> warnings() {
        return warnings != null ? warnings : Collections.emptyList();
    }
}
