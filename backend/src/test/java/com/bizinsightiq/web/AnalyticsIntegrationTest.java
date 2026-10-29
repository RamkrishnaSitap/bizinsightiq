package com.bizinsightiq.web;

import com.bizinsightiq.client.PythonMlClient;
import com.bizinsightiq.client.dto.*;
import com.bizinsightiq.client.exception.FastApiException;
import com.bizinsightiq.domain.model.Dataset;
import com.bizinsightiq.domain.model.User;
import com.bizinsightiq.domain.repository.CustomerClusterRepository;
import com.bizinsightiq.domain.repository.DatasetRepository;
import com.bizinsightiq.domain.repository.QuoteSimulationRepository;
import com.bizinsightiq.domain.repository.SegmentationRunRepository;
import com.bizinsightiq.domain.repository.UserRepository;
import com.bizinsightiq.security.JwtTokenProvider;
import com.bizinsightiq.security.UserPrincipal;
import com.bizinsightiq.service.FileStorageService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import java.math.BigDecimal;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
public class AnalyticsIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private DatasetRepository datasetRepository;

    @Autowired
    private SegmentationRunRepository segmentationRunRepository;

    @Autowired
    private CustomerClusterRepository customerClusterRepository;

    @Autowired
    private QuoteSimulationRepository quoteSimulationRepository;

    @Autowired
    private JwtTokenProvider jwtTokenProvider;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Autowired
    private FileStorageService fileStorageService;

    @MockBean
    private PythonMlClient pythonMlClient;

    private User alice;
    private User bob;
    private String aliceToken;
    private String bobToken;
    private Dataset aliceDataset;

    @BeforeEach
    void setUp() throws Exception {
        quoteSimulationRepository.deleteAll();
        customerClusterRepository.deleteAll();
        segmentationRunRepository.deleteAll();
        datasetRepository.deleteAll();
        userRepository.deleteAll();

        // 1. Seed Alice (owner)
        alice = new User("alice", "alice@bizinsightiq.com", passwordEncoder.encode("SecretPass123!"), "ROLE_ANALYST");
        alice = userRepository.saveAndFlush(alice);
        aliceToken = jwtTokenProvider.generateToken(UserPrincipal.create(alice));

        // 2. Seed Bob (potential attacker / tenant 2)
        bob = new User("bob", "bob@bizinsightiq.com", passwordEncoder.encode("SecretPass123!"), "ROLE_ANALYST");
        bob = userRepository.saveAndFlush(bob);
        bobToken = jwtTokenProvider.generateToken(UserPrincipal.create(bob));

        // 3. Create dataset for Alice
        aliceDataset = new Dataset(alice.getId(), "Alice Sales Data", "sales.csv", "pending");
        aliceDataset.setStatus("VALIDATED");
        aliceDataset.setIsValid(true);
        aliceDataset = datasetRepository.saveAndFlush(aliceDataset);

        // Stage physical CSV file
        String storageKey = "data/uploads/" + aliceDataset.getId() + ".csv";
        aliceDataset.setStorageKey(storageKey);
        aliceDataset = datasetRepository.saveAndFlush(aliceDataset);

        Path physicalPath = fileStorageService.resolveStoragePath(storageKey);
        Files.createDirectories(physicalPath.getParent());
        Files.writeString(physicalPath, "CustomerID,OrderDate,Category,Region,Quantity,Discount,Sales,Profit\nCUST-1,2023-01-01,Tech,East,2,0.1,100,20");
    }

    @Test
    @DisplayName("GET /eda: Should reject unauthenticated requests with 401 Unauthorized")
    void testEdaUnauthenticatedRejection() throws Exception {
        mockMvc.perform(get("/api/v1/datasets/{datasetId}/analytics/eda", aliceDataset.getId()))
                .andExpect(status().isUnauthorized());

        verify(pythonMlClient, never()).runEda(any(), any());
    }

    @Test
    @DisplayName("GET /eda: Cross-tenant isolation - Bob cannot access Alice's dataset (returns 404 Not Found)")
    void testEdaCrossTenantIsolation() throws Exception {
        mockMvc.perform(get("/api/v1/datasets/{datasetId}/analytics/eda", aliceDataset.getId())
                        .header("Authorization", "Bearer " + bobToken))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.status").value(404))
                .andExpect(jsonPath("$.message").value("Dataset not found with id: " + aliceDataset.getId()));

        verify(pythonMlClient, never()).runEda(any(), any());
    }

    @Test
    @DisplayName("GET /eda: Alice can view EDA on her dataset (returns 200 OK with KPIs)")
    void testEdaOwnerSuccess() throws Exception {
        EdaResponseDto mockEda = new EdaResponseDto(
                new EdaResponseDto.BusinessKpisDto(150000.0, 25000.0, 1200, 450, 800, 16.67, 187.5, 12.5),
                List.of(Map.of("year_month", "2023-01", "sales", 150000.0)),
                List.of(Map.of("category", "Technology", "sales", 80000.0)),
                List.of(Map.of("region", "East", "sales", 70000.0)),
                List.of(Map.of("discount_bucket", "0-10%", "profit_margin", 22.0)),
                Map.of("Sales", Map.of("Profit", 0.65))
        );

        when(pythonMlClient.runEda(any(byte[].class), eq("sales.csv"))).thenReturn(mockEda);

        mockMvc.perform(get("/api/v1/datasets/{datasetId}/analytics/eda", aliceDataset.getId())
                        .header("Authorization", "Bearer " + aliceToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.kpis.total_sales").value(150000.0))
                .andExpect(jsonPath("$.kpis.total_profit").value(25000.0))
                .andExpect(jsonPath("$.kpis.unique_customers").value(450))
                .andExpect(jsonPath("$.trends[0].sales").value(150000.0))
                .andExpect(jsonPath("$.category_performance[0].category").value("Technology"));

        verify(pythonMlClient, times(1)).runEda(any(byte[].class), eq("sales.csv"));
    }

    @Test
    @DisplayName("POST /segmentation: Successfully executes K-Means and persists SegmentationRun + CustomerCluster records")
    void testSegmentationPersistsRunAndClusters() throws Exception {
        SegmentationResponseDto mockResponse = new SegmentationResponseDto(
                4,
                0.4850,
                14200.5,
                List.of(48.2, 26.5),
                List.of(Map.of("Cluster", 0, "CustomerCount", 150, "DescriptivePersona", "Loyal High-Value")),
                List.of(Map.of("k", 2, "SilhouetteScore", 0.35)),
                List.of(
                        new SegmentationResponseDto.CustomerAssignmentDto("CUST-101", 0, 15, 6, 1200.50, 310.20),
                        new SegmentationResponseDto.CustomerAssignmentDto("CUST-102", 1, 45, 2, 340.00, 45.00)
                )
        );

        when(pythonMlClient.runSegmentation(any(byte[].class), eq("sales.csv"), eq(4), eq(42), eq(true), eq(true)))
                .thenReturn(mockResponse);

        mockMvc.perform(post("/api/v1/datasets/{datasetId}/analytics/segmentation", aliceDataset.getId())
                        .header("Authorization", "Bearer " + aliceToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"nClusters\": 4, \"randomState\": 42, \"evaluateCandidates\": true}"))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.nClusters").value(4))
                .andExpect(jsonPath("$.silhouetteScore").value(0.485))
                .andExpect(jsonPath("$.assignedCustomerCount").value(2))
                .andExpect(jsonPath("$.clusterProfiles[0].DescriptivePersona").value("Loyal High-Value"));

        // Verify relational persistence in PostgreSQL / H2
        assertEquals(1, segmentationRunRepository.findByDatasetId(aliceDataset.getId()).size());
        var runs = segmentationRunRepository.findByDatasetId(aliceDataset.getId());
        UUID runId = runs.get(0).getId();
        assertEquals(2, customerClusterRepository.findBySegmentationRunId(runId).size());
    }

    @Test
    @DisplayName("POST /segmentation: FastAPI failure returns 502 Bad Gateway and persists 0 runs or clusters")
    void testSegmentationFailureRollsBackCleanly() throws Exception {
        when(pythonMlClient.runSegmentation(any(), any(), anyInt(), anyInt(), anyBoolean(), anyBoolean()))
                .thenThrow(new FastApiException("Downstream FastAPI timed out after 15000ms", 504));

        mockMvc.perform(post("/api/v1/datasets/{datasetId}/analytics/segmentation", aliceDataset.getId())
                        .header("Authorization", "Bearer " + aliceToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"nClusters\": 4}"))
                .andExpect(status().isBadGateway())
                .andExpect(jsonPath("$.status").value(502))
                .andExpect(jsonPath("$.error").value("Bad Gateway"));

        // Verify database contains zero partial records
        assertEquals(0, segmentationRunRepository.findByDatasetId(aliceDataset.getId()).size());
        assertEquals(0, customerClusterRepository.count());
    }

    @Test
    @DisplayName("POST /predictions: Successfully simulates scenario quote and persists QuoteSimulation record")
    void testPredictionSimulateQuoteSuccess() throws Exception {
        ScenarioPredictionResponseDto mockPred = new ScenarioPredictionResponseDto(
                950.40,
                "Technology",
                "East",
                5,
                0.10,
                6,
                2,
                2,
                "Random Forest Regressor"
        );

        when(pythonMlClient.predictScenario(any(ScenarioPredictionRequestDto.class))).thenReturn(mockPred);

        String payload = """
            {
                "category": "Technology",
                "region": "East",
                "quantity": 5,
                "discount": 0.10,
                "month": 6,
                "quarter": 2,
                "dayOfWeek": 2
            }
            """;

        mockMvc.perform(post("/api/v1/datasets/{datasetId}/analytics/predictions", aliceDataset.getId())
                        .header("Authorization", "Bearer " + aliceToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(payload))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.predictedSales").value(950.40))
                .andExpect(jsonPath("$.category").value("Technology"))
                .andExpect(jsonPath("$.quantity").value(5))
                .andExpect(jsonPath("$.modelVersion").value("Random Forest Regressor"));

        // Verify persistence in quote_simulations
        var quotes = quoteSimulationRepository.findByUserIdOrderByCreatedAtDesc(alice.getId());
        assertEquals(1, quotes.size());
        assertEquals(aliceDataset.getId(), quotes.get(0).getDatasetId());
        assertEquals(new BigDecimal("950.40"), quotes.get(0).getPredictedSales());
    }

    @Test
    @DisplayName("POST /predictions/explain: Successfully returns SHAP feature attributions")
    void testPredictionExplainQuoteSuccess() throws Exception {
        var featureContribs = List.of(
                new PredictionExplanationResponseDto.FeatureContributionDto("Category", "Technology", 450.0, "increased", "Pushed prediction $450.00 above baseline", 45.0),
                new PredictionExplanationResponseDto.FeatureContributionDto("Quantity", "5 units", 200.0, "increased", "Pushed prediction $200.00 above baseline", 20.0)
        );
        PredictionExplanationResponseDto mockExplanation = new PredictionExplanationResponseDto(
                950.40,
                300.40,
                "Random Forest Regressor",
                aliceDataset.getId().toString(),
                true,
                featureContribs,
                950.40,
                true,
                "TreeExplainer (RandomForestRegressor)",
                "SHAP statistical attributions"
        );

        when(pythonMlClient.explainScenario(any(ScenarioPredictionRequestDto.class))).thenReturn(mockExplanation);

        String payload = """
            {
                "category": "Technology",
                "region": "East",
                "quantity": 5,
                "discount": 0.10,
                "month": 6,
                "quarter": 2,
                "dayOfWeek": 2
            }
            """;

        mockMvc.perform(post("/api/v1/datasets/{datasetId}/analytics/predictions/explain", aliceDataset.getId())
                        .header("Authorization", "Bearer " + aliceToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(payload))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.predicted_sales").value(950.40))
                .andExpect(jsonPath("$.base_value").value(300.40))
                .andExpect(jsonPath("$.feature_contributions[0].feature").value("Category"))
                .andExpect(jsonPath("$.is_additive_exact").value(true));
    }

    @Test
    @DisplayName("POST /predictions/compare: Successfully compares two scenarios side by side")
    void testPredictionCompareScenariosSuccess() throws Exception {
        var featureContribsA = List.of(
                new PredictionExplanationResponseDto.FeatureContributionDto("Discount", "10%", 87.41, "increased", "Pushed prediction $87.41 above baseline", 10.0)
        );
        var expA = new PredictionExplanationResponseDto(
                950.40, 300.40, "Random Forest Regressor", aliceDataset.getId().toString(), true, featureContribsA, 950.40, true, "TreeExplainer", "Disclaimer"
        );

        var featureContribsB = List.of(
                new PredictionExplanationResponseDto.FeatureContributionDto("Discount", "20%", 45.26, "increased", "Pushed prediction $45.26 above baseline", 5.0)
        );
        var expB = new PredictionExplanationResponseDto(
                908.25, 300.40, "Random Forest Regressor", aliceDataset.getId().toString(), true, featureContribsB, 908.25, true, "TreeExplainer", "Disclaimer"
        );

        var comparisons = List.of(
                new ScenarioComparisonResponseDto.FeatureComparisonItemDto("Discount", "10%", "20%", true, 87.41, 45.26, -42.15, "decreased", "Changing Discount from 10% to 20% reduced sales attribution by -$42.15")
        );

        ScenarioComparisonResponseDto mockComparison = new ScenarioComparisonResponseDto(
                expA, expB, 950.40, 908.25, -42.15, -4.43, 1, comparisons, true, "TreeExplainer", 300.40, "Random Forest Regressor", aliceDataset.getId().toString(), true, "Disclaimer"
        );

        when(pythonMlClient.compareScenarios(any(ScenarioComparisonRequestDto.class))).thenReturn(mockComparison);

        String payload = """
            {
                "scenarioA": {
                    "category": "Technology",
                    "region": "East",
                    "quantity": 5,
                    "discount": 0.10
                },
                "scenarioB": {
                    "category": "Technology",
                    "region": "East",
                    "quantity": 5,
                    "discount": 0.20
                },
                "modelType": "random_forest"
            }
            """;

        mockMvc.perform(post("/api/v1/datasets/{datasetId}/analytics/predictions/compare", aliceDataset.getId())
                        .header("Authorization", "Bearer " + aliceToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(payload))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.predicted_sales_a").value(950.40))
                .andExpect(jsonPath("$.predicted_sales_b").value(908.25))
                .andExpect(jsonPath("$.absolute_difference").value(-42.15))
                .andExpect(jsonPath("$.changed_features_count").value(1))
                .andExpect(jsonPath("$.feature_comparisons[0].feature").value("Discount"))
                .andExpect(jsonPath("$.feature_comparisons[0].is_changed").value(true));
    }

    @Test
    @DisplayName("POST /predictions/compare: Rejects access when dataset is owned by another user (tenant isolation)")
    void testPredictionCompareScenariosOwnershipViolation() throws Exception {
        String payload = """
            {
                "scenarioA": {
                    "category": "Technology",
                    "region": "East",
                    "quantity": 5,
                    "discount": 0.10
                },
                "scenarioB": {
                    "category": "Technology",
                    "region": "East",
                    "quantity": 5,
                    "discount": 0.20
                }
            }
            """;

        mockMvc.perform(post("/api/v1/datasets/{datasetId}/analytics/predictions/compare", aliceDataset.getId())
                        .header("Authorization", "Bearer " + bobToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(payload))
                .andExpect(status().isNotFound());
    }

    @Test
    @DisplayName("POST /predictions: Rejects invalid prediction parameters (quantity < 1, discount > 1.0)")
    void testPredictionInvalidValidation() throws Exception {
        String invalidPayload = """
            {
                "category": "Technology",
                "region": "East",
                "quantity": 0,
                "discount": 1.50
            }
            """;

        mockMvc.perform(post("/api/v1/datasets/{datasetId}/analytics/predictions", aliceDataset.getId())
                        .header("Authorization", "Bearer " + aliceToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(invalidPayload))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.status").value(400))
                .andExpect(jsonPath("$.validationErrors.quantity").exists())
                .andExpect(jsonPath("$.validationErrors.discount").exists());

        verify(pythonMlClient, never()).predictScenario(any());
        assertEquals(0, quoteSimulationRepository.count());
    }

    @Test
    @DisplayName("POST /predictions/train: Trains regression models and returns comparative benchmarks")
    void testTrainPredictionModelsSuccess() throws Exception {
        PredictionTrainingResponseDto mockTraining = new PredictionTrainingResponseDto(
                List.of(
                        Map.of("model", "Linear Regression", "mae", 125.4, "r2", 0.62),
                        Map.of("model", "Random Forest Regressor", "mae", 85.2, "r2", 0.84)
                ),
                Map.of(
                        "linear_regression", new PredictionTrainingResponseDto.RegressionMetricsDto(125.4, 180.2, 0.62, 240, "chronological"),
                        "random_forest", new PredictionTrainingResponseDto.RegressionMetricsDto(85.2, 115.6, 0.84, 240, "chronological")
                ),
                Map.of("total_records", 1200, "train_size", 960, "test_size", 240)
        );

        when(pythonMlClient.trainPredictionModels(any(byte[].class), eq("sales.csv"), eq("chronological"), eq(0.20), eq(42)))
                .thenReturn(mockTraining);

        mockMvc.perform(post("/api/v1/datasets/{datasetId}/analytics/predictions/train", aliceDataset.getId())
                        .header("Authorization", "Bearer " + aliceToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"splitStrategy\": \"chronological\", \"testSize\": 0.20, \"randomState\": 42}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.comparison[0].model").value("Linear Regression"))
                .andExpect(jsonPath("$.comparison[1].model").value("Random Forest Regressor"))
                .andExpect(jsonPath("$.metrics.random_forest.r2").value(0.84));

        verify(pythonMlClient, times(1)).trainPredictionModels(any(), any(), any(), anyDouble(), anyInt());
    }

    @Test
    @DisplayName("GET /insights: Generates structured decision-support insights from Python rules engine")
    void testGenerateInsightsSuccess() throws Exception {
        InsightsResponseDto mockInsights = new InsightsResponseDto(
                new InsightsResponseDto.InsightsSummaryDto(3, 1, 1, 1),
                List.of(
                        new InsightsResponseDto.InsightItemDto(
                                "INS-001",
                                "Sales & Profitability",
                                "critical",
                                "Negative Profit Margin in Tables",
                                Map.of("margin_pct", -12.4),
                                "Re-evaluate discount caps and shipping costs on bulky tables",
                                "Based on historical transaction margin records"
                        )
                )
        );

        when(pythonMlClient.generateInsights(any(byte[].class), eq("sales.csv"), eq("critical"), isNull()))
                .thenReturn(mockInsights);

        mockMvc.perform(get("/api/v1/datasets/{datasetId}/analytics/insights", aliceDataset.getId())
                        .param("severity", "critical")
                        .header("Authorization", "Bearer " + aliceToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.summary.total_insights").value(3))
                .andExpect(jsonPath("$.summary.critical_count").value(1))
                .andExpect(jsonPath("$.insights[0].insight_id").value("INS-001"))
                .andExpect(jsonPath("$.insights[0].severity").value("critical"))
                .andExpect(jsonPath("$.insights[0].recommendation").value(org.hamcrest.Matchers.containsString("Re-evaluate discount caps")));

        verify(pythonMlClient, times(1)).generateInsights(any(), eq("sales.csv"), eq("critical"), isNull());
    }

    @Test
    @DisplayName("GET /api/v1/analytics/quotes: Retrieves saved quote simulations history for the user")
    void testGetUserQuotesList() throws Exception {
        // Pre-seed a quote for Alice
        var quote = new com.bizinsightiq.domain.model.QuoteSimulation();
        quote.setUserId(alice.getId());
        quote.setDatasetId(aliceDataset.getId());
        quote.setCategory("Office Supplies");
        quote.setRegion("West");
        quote.setQuantity(10);
        quote.setDiscount(new BigDecimal("0.0500"));
        quote.setPredictedSales(new BigDecimal("350.00"));
        quote.setModelVersion("RandomForestRegressor-v1.0");
        quoteSimulationRepository.saveAndFlush(quote);

        mockMvc.perform(get("/api/v1/analytics/quotes")
                        .header("Authorization", "Bearer " + aliceToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].category").value("Office Supplies"))
                .andExpect(jsonPath("$[0].quantity").value(10))
                .andExpect(jsonPath("$[0].predictedSales").value(350.00));
    }
}
