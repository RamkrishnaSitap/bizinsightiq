package com.bizinsightiq.web.controller;

import com.bizinsightiq.security.UserPrincipal;
import com.bizinsightiq.service.AnalyticsOrchestrationService;
import com.bizinsightiq.web.dto.QuoteSimulationResponse;
import com.bizinsightiq.web.dto.SimulateQuoteRequest;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/v1/analytics/quotes")
public class QuoteSimulationController {

    private final AnalyticsOrchestrationService analyticsService;

    public QuoteSimulationController(AnalyticsOrchestrationService analyticsService) {
        this.analyticsService = analyticsService;
    }

    /**
     * Lists all saved quote simulations for the authenticated user.
     */
    @GetMapping
    public ResponseEntity<List<QuoteSimulationResponse>> getUserQuotes(
            @AuthenticationPrincipal UserPrincipal principal
    ) {
        List<QuoteSimulationResponse> quotes = analyticsService.getUserQuoteSimulations(principal);
        return ResponseEntity.ok(quotes);
    }

    /**
     * Simulates a general quote scenario without tying to a specific dataset.
     */
    @PostMapping
    public ResponseEntity<QuoteSimulationResponse> simulateGeneralQuote(
            @Valid @RequestBody SimulateQuoteRequest request,
            @AuthenticationPrincipal UserPrincipal principal
    ) {
        QuoteSimulationResponse response = analyticsService.simulateQuote(null, request, principal);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }
}
