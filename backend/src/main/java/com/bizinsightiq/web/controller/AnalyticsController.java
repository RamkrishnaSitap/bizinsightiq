package com.bizinsightiq.web.controller;

import com.bizinsightiq.client.dto.*;
import com.bizinsightiq.domain.model.SegmentationRun;
import com.bizinsightiq.security.UserPrincipal;
import com.bizinsightiq.service.AnalyticsOrchestrationService;
import com.bizinsightiq.web.dto.*;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/datasets/{datasetId}/analytics")
public class AnalyticsController {

    private final AnalyticsOrchestrationService analyticsService;

    public AnalyticsController(AnalyticsOrchestrationService analyticsService) {
        this.analyticsService = analyticsService;
    }

    /**
     * Exploratory Data Analysis (EDA) on the dataset.
     */
    @GetMapping("/eda")
    public ResponseEntity<EdaResponseDto> getEda(
            @PathVariable("datasetId") UUID datasetId,
            @AuthenticationPrincipal UserPrincipal principal
    ) {
        EdaResponseDto response = analyticsService.getDatasetEda(datasetId, principal);
        return ResponseEntity.ok(response);
    }

    /**
     * Executes K-Means customer segmentation and persists cluster assignments.
     */
    @PostMapping("/segmentation")
    public ResponseEntity<SegmentationRunResponse> runSegmentation(
            @PathVariable("datasetId") UUID datasetId,
            @Valid @RequestBody(required = false) RunSegmentationRequest request,
            @AuthenticationPrincipal UserPrincipal principal
    ) {
        RunSegmentationRequest req = request != null ? request : new RunSegmentationRequest(4, 42, true);
        SegmentationRunResponse response = analyticsService.runCustomerSegmentation(datasetId, req, principal);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    /**
     * Lists previous segmentation runs for this dataset.
     */
    @GetMapping("/segmentation/runs")
    public ResponseEntity<List<SegmentationRun>> getSegmentationRuns(
            @PathVariable("datasetId") UUID datasetId,
            @AuthenticationPrincipal UserPrincipal principal
    ) {
        List<SegmentationRun> runs = analyticsService.getDatasetSegmentationRuns(datasetId, principal);
        return ResponseEntity.ok(runs);
    }

    /**
     * Trains and compares Linear Regression and Random Forest models on the dataset.
     */
    @PostMapping("/predictions/train")
    public ResponseEntity<PredictionTrainingResponseDto> trainPredictionModels(
            @PathVariable("datasetId") UUID datasetId,
            @Valid @RequestBody(required = false) TrainPredictionRequest request,
            @AuthenticationPrincipal UserPrincipal principal
    ) {
        TrainPredictionRequest req = request != null ? request : new TrainPredictionRequest("chronological", 0.20, 42);
        PredictionTrainingResponseDto response = analyticsService.trainPredictionModels(datasetId, req, principal);
        return ResponseEntity.ok(response);
    }

    /**
     * Simulates a sales scenario quote and persists the record.
     */
    @PostMapping("/predictions")
    public ResponseEntity<QuoteSimulationResponse> simulateQuote(
            @PathVariable("datasetId") UUID datasetId,
            @Valid @RequestBody SimulateQuoteRequest request,
            @AuthenticationPrincipal UserPrincipal principal
    ) {
        QuoteSimulationResponse response = analyticsService.simulateQuote(datasetId, request, principal);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    /**
     * Explains a What-If quote prediction using SHAP feature attributions.
     */
    @PostMapping("/predictions/explain")
    public ResponseEntity<PredictionExplanationResponseDto> explainQuote(
            @PathVariable("datasetId") UUID datasetId,
            @Valid @RequestBody SimulateQuoteRequest request,
            @AuthenticationPrincipal UserPrincipal principal
    ) {
        PredictionExplanationResponseDto response = analyticsService.explainQuote(datasetId, request, principal);
        return ResponseEntity.ok(response);
    }

    /**
     * Compares two What-If quote scenarios side by side using SHAP feature attributions.
     */
    @PostMapping("/predictions/compare")
    public ResponseEntity<ScenarioComparisonResponseDto> compareScenarios(
            @PathVariable("datasetId") UUID datasetId,
            @Valid @RequestBody CompareScenariosRequest request,
            @AuthenticationPrincipal UserPrincipal principal
    ) {
        ScenarioComparisonResponseDto response = analyticsService.compareScenarios(datasetId, request, principal);
        return ResponseEntity.ok(response);
    }

    /**
     * Generates decision-support business insights across the four analytical pillars.
     */
    @GetMapping("/insights")
    public ResponseEntity<InsightsResponseDto> getInsights(
            @PathVariable("datasetId") UUID datasetId,
            @RequestParam(value = "severity", required = false) String severity,
            @RequestParam(value = "category", required = false) String category,
            @AuthenticationPrincipal UserPrincipal principal
    ) {
        InsightsResponseDto response = analyticsService.generateInsights(datasetId, severity, category, principal);
        return ResponseEntity.ok(response);
    }
}
