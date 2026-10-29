package com.bizinsightiq.web.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotNull;

/**
 * Request payload for side-by-side What-If scenario comparison.
 */
public record CompareScenariosRequest(
        @NotNull(message = "Scenario A is required")
        @Valid
        SimulateQuoteRequest scenarioA,

        @NotNull(message = "Scenario B is required")
        @Valid
        SimulateQuoteRequest scenarioB,

        String modelType
) {}
