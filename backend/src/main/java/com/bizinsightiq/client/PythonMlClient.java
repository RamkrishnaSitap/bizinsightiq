package com.bizinsightiq.client;

import com.bizinsightiq.client.dto.*;

/**
 * Contract for interacting with the Python AI/ML microservice (FastAPI).
 */
public interface PythonMlClient {

    /**
     * Pings the FastAPI health endpoint to verify microservice status and core ML modules.
     *
     * @return FastApiHealthResponse with service version and active modules
     */
    FastApiHealthResponse checkHealth();

    /**
     * Checks if the FastAPI microservice is ready to process incoming analysis requests.
     *
     * @return true if ready, false otherwise
     */
    boolean isReady();

    /**
     * Validates an uploaded CSV dataset using the FastAPI validation endpoint.
     *
     * @param csvBytes raw CSV content bytes
     * @param filename source filename
     * @return ValidationResponseDto with structured errors and warnings
     */
    ValidationResponseDto validateDataset(byte[] csvBytes, String filename);

    /**
     * Executes exploratory data analysis (EDA) and calculates business KPIs, trends,
     * category performance, regional breakdown, discount elasticity, and correlation matrix.
     *
     * @param csvBytes raw CSV content bytes (or null to analyze default bundled dataset)
     * @param filename source filename
     * @return EdaResponseDto containing all computed business metrics
     */
    EdaResponseDto runEda(byte[] csvBytes, String filename);

    /**
     * Executes customer RFM aggregation and unsupervised K-Means clustering.
     *
     * @param csvBytes raw CSV content bytes
     * @param filename source filename
     * @param nClusters number of clusters to form (2 to 7)
     * @param randomState seed for reproducible centroid initialization
     * @param evaluateCandidates whether to perform candidate k evaluation sweep
     * @param includeAssignments whether to include customer-level cluster assignments
     * @return SegmentationResponseDto containing profiles, metrics, and assignments
     */
    SegmentationResponseDto runSegmentation(
            byte[] csvBytes,
            String filename,
            int nClusters,
            int randomState,
            boolean evaluateCandidates,
            boolean includeAssignments
    );

    /**
     * Trains and compares Linear Regression baseline and Random Forest models.
     *
     * @param csvBytes raw CSV content bytes
     * @param filename source filename
     * @param splitStrategy chronological or random
     * @param testSize evaluation test split fraction
     * @param randomState random seed
     * @return PredictionTrainingResponseDto with benchmark metrics and model comparison
     */
    PredictionTrainingResponseDto trainPredictionModels(
            byte[] csvBytes,
            String filename,
            String splitStrategy,
            double testSize,
            int randomState
    );

    /**
     * Overloaded method including datasetId to bind trained models to a dataset.
     */
    default PredictionTrainingResponseDto trainPredictionModels(
            byte[] csvBytes,
            String filename,
            String splitStrategy,
            double testSize,
            int randomState,
            String datasetId
    ) {
        return trainPredictionModels(csvBytes, filename, splitStrategy, testSize, randomState);
    }

    /**
     * Predicts gross sales for a What-If order scenario using the trained model.
     *
     * @param request scenario parameters (category, region, quantity, discount, date features)
     * @return ScenarioPredictionResponseDto with predicted sales and metadata
     */
    ScenarioPredictionResponseDto predictScenario(ScenarioPredictionRequestDto request);

    /**
     * Deconstructs a sales prediction using SHAP (SHapley Additive exPlanations) values.
     *
     * @param request scenario parameters (category, region, quantity, discount, date features, modelType, datasetId)
     * @return PredictionExplanationResponseDto with baseline expectation, feature contributions, and interpretations
     */
    PredictionExplanationResponseDto explainScenario(ScenarioPredictionRequestDto request);

    /**
     * Compares two What-If order scenarios side by side using the same fitted model and SHAP explainer.
     *
     * @param request comparison payload with Scenario A, Scenario B, modelType, and datasetId
     * @return ScenarioComparisonResponseDto with predictions, differences, and feature SHAP shifts
     */
    ScenarioComparisonResponseDto compareScenarios(ScenarioComparisonRequestDto request);

    /**
     * Evaluates heuristic business decision rules across the four analytical pillars.
     *
     * @param csvBytes raw CSV content bytes
     * @param filename source filename
     * @param severity optional filter (CRITICAL, WARNING, INFO)
     * @param category optional pillar category filter
     * @return InsightsResponseDto containing structured insights and summary counts
     */
    InsightsResponseDto generateInsights(byte[] csvBytes, String filename, String severity, String category);
}
