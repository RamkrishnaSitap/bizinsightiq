package com.bizinsightiq.service;

import com.bizinsightiq.client.PythonMlClient;
import com.bizinsightiq.client.dto.*;
import com.bizinsightiq.domain.model.CustomerCluster;
import com.bizinsightiq.domain.model.Dataset;
import com.bizinsightiq.domain.model.QuoteSimulation;
import com.bizinsightiq.domain.model.SegmentationRun;
import com.bizinsightiq.domain.repository.CustomerClusterRepository;
import com.bizinsightiq.domain.repository.DatasetRepository;
import com.bizinsightiq.domain.repository.QuoteSimulationRepository;
import com.bizinsightiq.domain.repository.SegmentationRunRepository;
import com.bizinsightiq.security.UserPrincipal;
import com.bizinsightiq.web.dto.*;
import jakarta.persistence.EntityNotFoundException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Service
public class AnalyticsOrchestrationService {

    private static final Logger log = LoggerFactory.getLogger(AnalyticsOrchestrationService.class);

    private final DatasetRepository datasetRepository;
    private final FileStorageService fileStorageService;
    private final PythonMlClient pythonMlClient;
    private final SegmentationRunRepository segmentationRunRepository;
    private final CustomerClusterRepository customerClusterRepository;
    private final QuoteSimulationRepository quoteSimulationRepository;

    public AnalyticsOrchestrationService(
            DatasetRepository datasetRepository,
            FileStorageService fileStorageService,
            PythonMlClient pythonMlClient,
            SegmentationRunRepository segmentationRunRepository,
            CustomerClusterRepository customerClusterRepository,
            QuoteSimulationRepository quoteSimulationRepository
    ) {
        this.datasetRepository = datasetRepository;
        this.fileStorageService = fileStorageService;
        this.pythonMlClient = pythonMlClient;
        this.segmentationRunRepository = segmentationRunRepository;
        this.customerClusterRepository = customerClusterRepository;
        this.quoteSimulationRepository = quoteSimulationRepository;
    }

    /**
     * Executes Exploratory Data Analysis (EDA) on an authenticated user's dataset.
     */
    public EdaResponseDto getDatasetEda(UUID datasetId, UserPrincipal principal) {
        log.info("Executing EDA for dataset id '{}' owned by user '{}'", datasetId, principal.getUsername());
        Dataset dataset = resolveDatasetWithOwnership(datasetId, principal.getId());
        byte[] csvBytes = fileStorageService.readFileBytes(dataset.getStorageKey());
        return pythonMlClient.runEda(csvBytes, dataset.getOriginalFilename());
    }

    /**
     * Executes K-Means customer segmentation and persists the run and cluster assignments.
     */
    public SegmentationRunResponse runCustomerSegmentation(
            UUID datasetId,
            RunSegmentationRequest request,
            UserPrincipal principal
    ) {
        log.info("Executing customer segmentation for dataset id '{}' (k={}, user='{}')",
                datasetId, request.nClusters(), principal.getUsername());

        Dataset dataset = resolveDatasetWithOwnership(datasetId, principal.getId());
        byte[] csvBytes = fileStorageService.readFileBytes(dataset.getStorageKey());

        // Invoke FastAPI outside of a database transaction
        SegmentationResponseDto response = pythonMlClient.runSegmentation(
                csvBytes,
                dataset.getOriginalFilename(),
                request.nClusters(),
                request.randomState(),
                request.evaluateCandidates(),
                true
        );

        // Persist run metadata and customer cluster assignments atomically
        return persistSegmentationResults(dataset.getId(), response);
    }

    /**
     * Trains and benchmarks Linear Regression and Random Forest models on the dataset.
     */
    public PredictionTrainingResponseDto trainPredictionModels(
            UUID datasetId,
            TrainPredictionRequest request,
            UserPrincipal principal
    ) {
        log.info("Executing prediction model training on dataset id '{}' (strategy='{}', user='{}')",
                datasetId, request.splitStrategy(), principal.getUsername());

        Dataset dataset = resolveDatasetWithOwnership(datasetId, principal.getId());
        byte[] csvBytes = fileStorageService.readFileBytes(dataset.getStorageKey());

        return pythonMlClient.trainPredictionModels(
                csvBytes,
                dataset.getOriginalFilename(),
                request.splitStrategy(),
                request.testSize(),
                request.randomState()
        );
    }

    /**
     * Simulates a sales scenario quote and persists the resulting simulation record.
     */
    public QuoteSimulationResponse simulateQuote(
            UUID datasetId,
            SimulateQuoteRequest request,
            UserPrincipal principal
    ) {
        log.info("Simulating quote scenario for dataset id '{}', category='{}', region='{}', user='{}'",
                datasetId, request.category(), request.region(), principal.getUsername());

        // Verify dataset ownership if datasetId provided
        Dataset dataset = null;
        if (datasetId != null) {
            dataset = resolveDatasetWithOwnership(datasetId, principal.getId());
        }

        String selectedModel = request.modelType() != null && !request.modelType().isBlank()
                ? request.modelType().trim().toLowerCase()
                : "random_forest";

        ScenarioPredictionRequestDto requestDto = new ScenarioPredictionRequestDto(
                request.category(),
                request.region(),
                request.quantity(),
                request.discount().doubleValue(),
                request.month(),
                request.quarter(),
                request.dayOfWeek(),
                selectedModel,
                dataset != null ? dataset.getId().toString() : null
        );

        // Invoke FastAPI inference outside of database transaction
        ScenarioPredictionResponseDto response = pythonMlClient.predictScenario(requestDto);

        // Persist simulation result
        return persistQuoteSimulation(principal.getId(), dataset != null ? dataset.getId() : null, request, response);
    }

    /**
     * Explains a What-If quote prediction using SHAP feature attributions.
     */
    public PredictionExplanationResponseDto explainQuote(
            UUID datasetId,
            SimulateQuoteRequest request,
            UserPrincipal principal
    ) {
        log.info("Generating SHAP explanation for dataset id '{}', category='{}', region='{}', user='{}'",
                datasetId, request.category(), request.region(), principal.getUsername());

        Dataset dataset = null;
        if (datasetId != null) {
            dataset = resolveDatasetWithOwnership(datasetId, principal.getId());
        }

        String selectedModel = request.modelType() != null && !request.modelType().isBlank()
                ? request.modelType().trim().toLowerCase()
                : "random_forest";

        ScenarioPredictionRequestDto requestDto = new ScenarioPredictionRequestDto(
                request.category(),
                request.region(),
                request.quantity(),
                request.discount().doubleValue(),
                request.month(),
                request.quarter(),
                request.dayOfWeek(),
                selectedModel,
                dataset != null ? dataset.getId().toString() : null
        );

        return pythonMlClient.explainScenario(requestDto);
    }

    /**
     * Compares two What-If quote scenarios side by side using the same fitted model and SHAP explainer.
     */
    public ScenarioComparisonResponseDto compareScenarios(
            UUID datasetId,
            CompareScenariosRequest request,
            UserPrincipal principal
    ) {
        log.info("Comparing scenarios for dataset id '{}', model='{}', user='{}'",
                datasetId, request.modelType(), principal.getUsername());

        Dataset dataset = null;
        if (datasetId != null) {
            dataset = resolveDatasetWithOwnership(datasetId, principal.getId());
        }

        String selectedModel = request.modelType() != null && !request.modelType().isBlank()
                ? request.modelType().trim().toLowerCase()
                : (request.scenarioA().modelType() != null && !request.scenarioA().modelType().isBlank()
                    ? request.scenarioA().modelType().trim().toLowerCase()
                    : "random_forest");

        ScenarioComparisonRequestDto.SingleScenarioInputDto aDto = new ScenarioComparisonRequestDto.SingleScenarioInputDto(
                request.scenarioA().category(),
                request.scenarioA().region(),
                request.scenarioA().quantity(),
                request.scenarioA().discount().doubleValue(),
                request.scenarioA().month(),
                request.scenarioA().quarter(),
                request.scenarioA().dayOfWeek()
        );

        ScenarioComparisonRequestDto.SingleScenarioInputDto bDto = new ScenarioComparisonRequestDto.SingleScenarioInputDto(
                request.scenarioB().category(),
                request.scenarioB().region(),
                request.scenarioB().quantity(),
                request.scenarioB().discount().doubleValue(),
                request.scenarioB().month(),
                request.scenarioB().quarter(),
                request.scenarioB().dayOfWeek()
        );

        ScenarioComparisonRequestDto requestDto = new ScenarioComparisonRequestDto(
                aDto,
                bDto,
                selectedModel,
                dataset != null ? dataset.getId().toString() : null
        );

        return pythonMlClient.compareScenarios(requestDto);
    }

    /**
     * Generates decision-support business insights across the four analytical pillars.
     */
    public InsightsResponseDto generateInsights(
            UUID datasetId,
            String severity,
            String category,
            UserPrincipal principal
    ) {
        log.info("Generating business insights for dataset id '{}', severity='{}', category='{}', user='{}'",
                datasetId, severity, category, principal.getUsername());

        Dataset dataset = resolveDatasetWithOwnership(datasetId, principal.getId());
        byte[] csvBytes = fileStorageService.readFileBytes(dataset.getStorageKey());

        return pythonMlClient.generateInsights(csvBytes, dataset.getOriginalFilename(), severity, category);
    }

    /**
     * Retrieves saved quote simulations for the authenticated user.
     */
    @Transactional(readOnly = true)
    public List<QuoteSimulationResponse> getUserQuoteSimulations(UserPrincipal principal) {
        return quoteSimulationRepository.findByUserIdOrderByCreatedAtDesc(principal.getId())
                .stream()
                .map(QuoteSimulationResponse::fromEntity)
                .toList();
    }

    /**
     * Retrieves previous segmentation runs for a dataset owned by the user.
     */
    @Transactional(readOnly = true)
    public List<SegmentationRun> getDatasetSegmentationRuns(UUID datasetId, UserPrincipal principal) {
        resolveDatasetWithOwnership(datasetId, principal.getId());
        return segmentationRunRepository.findByDatasetId(datasetId);
    }

    @Transactional
    protected SegmentationRunResponse persistSegmentationResults(UUID datasetId, SegmentationResponseDto response) {
        SegmentationRun run = new SegmentationRun();
        run.setDatasetId(datasetId);
        run.setkClusters(response.nClusters());
        run.setSilhouetteScore(BigDecimal.valueOf(response.silhouetteScore()).setScale(4, RoundingMode.HALF_UP));
        run.setInertia(BigDecimal.valueOf(response.inertia()).setScale(4, RoundingMode.HALF_UP));
        run.setAlgorithmVersion("KMeans-v1.0");

        SegmentationRun savedRun = segmentationRunRepository.save(run);

        int assignedCount = 0;
        if (response.customerAssignments() != null && !response.customerAssignments().isEmpty()) {
            List<CustomerCluster> clusters = new ArrayList<>(response.customerAssignments().size());
            for (SegmentationResponseDto.CustomerAssignmentDto assignment : response.customerAssignments()) {
                CustomerCluster cluster = new CustomerCluster();
                cluster.setSegmentationRunId(savedRun.getId());
                cluster.setCustomerId(assignment.customerId());
                cluster.setClusterId(assignment.clusterId());
                cluster.setRecency(assignment.recency());
                cluster.setFrequency(assignment.frequency());
                cluster.setMonetaryValue(BigDecimal.valueOf(assignment.monetaryValue()).setScale(2, RoundingMode.HALF_UP));
                cluster.setTotalProfit(BigDecimal.valueOf(assignment.totalProfit()).setScale(2, RoundingMode.HALF_UP));
                clusters.add(cluster);
            }
            customerClusterRepository.saveAll(clusters);
            assignedCount = clusters.size();
        }

        return new SegmentationRunResponse(
                savedRun.getId(),
                savedRun.getDatasetId(),
                savedRun.getkClusters(),
                savedRun.getSilhouetteScore().doubleValue(),
                savedRun.getInertia().doubleValue(),
                response.pcaVarianceRatio(),
                response.clusterProfiles(),
                response.candidatesEvaluation(),
                assignedCount,
                savedRun.getCreatedAt()
        );
    }

    @Transactional
    protected QuoteSimulationResponse persistQuoteSimulation(
            UUID userId,
            UUID datasetId,
            SimulateQuoteRequest request,
            ScenarioPredictionResponseDto response
    ) {
        QuoteSimulation simulation = new QuoteSimulation();
        simulation.setUserId(userId);
        simulation.setDatasetId(datasetId);
        simulation.setCategory(request.category());
        simulation.setRegion(request.region());
        simulation.setQuantity(request.quantity());
        simulation.setDiscount(request.discount().setScale(4, RoundingMode.HALF_UP));
        simulation.setPredictedSales(BigDecimal.valueOf(response.predictedSales()).setScale(2, RoundingMode.HALF_UP));
        String rawModel = response.modelUsed() != null ? response.modelUsed() : "RandomForestRegressor-v1.0";
        simulation.setModelVersion(rawModel.length() > 100 ? rawModel.substring(0, 100) : rawModel);

        QuoteSimulation saved = quoteSimulationRepository.save(simulation);
        return QuoteSimulationResponse.fromEntity(saved);
    }

    private Dataset resolveDatasetWithOwnership(UUID datasetId, UUID userId) {
        return datasetRepository.findByIdAndUserId(datasetId, userId)
                .orElseThrow(() -> new EntityNotFoundException("Dataset not found with id: " + datasetId));
    }
}
