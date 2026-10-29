package com.bizinsightiq.client;

import com.bizinsightiq.client.dto.*;
import com.bizinsightiq.client.exception.FastApiException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;

import java.util.Map;

@Service
public class FastApiClient implements PythonMlClient {

    private static final Logger log = LoggerFactory.getLogger(FastApiClient.class);
    private final RestClient restClient;

    public FastApiClient(RestClient fastApiRestClient) {
        this.restClient = fastApiRestClient;
    }

    @Override
    public FastApiHealthResponse checkHealth() {
        try {
            log.debug("Checking Python FastAPI microservice health");
            return restClient.get()
                    .uri("/health")
                    .retrieve()
                    .onStatus(HttpStatusCode::isError, (request, response) -> {
                        log.error("FastAPI health check failed with status code {}", response.getStatusCode());
                        throw new FastApiException("FastAPI service responded with error status: " + response.getStatusCode().value(), response.getStatusCode().value());
                    })
                    .body(FastApiHealthResponse.class);
        } catch (RestClientException ex) {
            log.error("Unable to connect to Python FastAPI ML service: {}", ex.getMessage());
            throw new FastApiException("Python FastAPI ML service unavailable at configured endpoint", ex);
        }
    }

    @Override
    @SuppressWarnings("unchecked")
    public boolean isReady() {
        try {
            Map<String, Object> response = restClient.get()
                    .uri("/ready")
                    .retrieve()
                    .body(Map.class);

            return response != null && Boolean.TRUE.equals(response.get("ready"));
        } catch (Exception ex) {
            log.warn("FastAPI readiness check failed: {}", ex.getMessage());
            return false;
        }
    }

    @Override
    public ValidationResponseDto validateDataset(byte[] csvBytes, String filename) {
        try {
            log.debug("Sending CSV dataset '{}' ({} bytes) to FastAPI for validation", filename, csvBytes != null ? csvBytes.length : 0);

            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            if (csvBytes != null) {
                body.add("file", createByteArrayResource(csvBytes, filename));
            }

            return restClient.post()
                    .uri("/datasets/validate")
                    .contentType(MediaType.MULTIPART_FORM_DATA)
                    .body(body)
                    .retrieve()
                    .onStatus(HttpStatusCode::isError, (request, response) -> {
                        log.error("FastAPI dataset validation failed with status code {}", response.getStatusCode());
                        throw new FastApiException("FastAPI validation service error: " + response.getStatusCode().value(), response.getStatusCode().value());
                    })
                    .body(ValidationResponseDto.class);
        } catch (RestClientException ex) {
            log.error("Error communicating with FastAPI validation endpoint: {}", ex.getMessage());
            throw new FastApiException("Failed to communicate with FastAPI validation service: " + ex.getMessage(), ex);
        }
    }

    @Override
    public EdaResponseDto runEda(byte[] csvBytes, String filename) {
        try {
            log.info("Requesting EDA analysis from FastAPI for '{}' ({} bytes)", filename, csvBytes != null ? csvBytes.length : 0);

            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            if (csvBytes != null && csvBytes.length > 0) {
                body.add("file", createByteArrayResource(csvBytes, filename));
            }

            return restClient.post()
                    .uri("/analytics/eda")
                    .contentType(MediaType.MULTIPART_FORM_DATA)
                    .body(body)
                    .retrieve()
                    .onStatus(HttpStatusCode::isError, (request, response) -> {
                        log.error("FastAPI EDA calculation failed with status code {}", response.getStatusCode());
                        throw new FastApiException("FastAPI EDA calculation error: " + response.getStatusCode().value(), response.getStatusCode().value());
                    })
                    .body(EdaResponseDto.class);
        } catch (RestClientException ex) {
            log.error("Error communicating with FastAPI EDA endpoint: {}", ex.getMessage());
            throw new FastApiException("Failed to communicate with FastAPI EDA service: " + ex.getMessage(), ex);
        }
    }

    @Override
    public SegmentationResponseDto runSegmentation(
            byte[] csvBytes,
            String filename,
            int nClusters,
            int randomState,
            boolean evaluateCandidates,
            boolean includeAssignments
    ) {
        try {
            log.info("Requesting customer segmentation from FastAPI (k={}, random_state={}, eval_candidates={}, assignments={})",
                    nClusters, randomState, evaluateCandidates, includeAssignments);

            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            if (csvBytes != null && csvBytes.length > 0) {
                body.add("file", createByteArrayResource(csvBytes, filename));
            }
            body.add("n_clusters", String.valueOf(nClusters));
            body.add("random_state", String.valueOf(randomState));
            body.add("evaluate_candidates", String.valueOf(evaluateCandidates));
            body.add("include_assignments", String.valueOf(includeAssignments));

            return restClient.post()
                    .uri("/segmentation")
                    .contentType(MediaType.MULTIPART_FORM_DATA)
                    .body(body)
                    .retrieve()
                    .onStatus(HttpStatusCode::isError, (request, response) -> {
                        log.error("FastAPI customer segmentation failed with status code {}", response.getStatusCode());
                        throw new FastApiException("FastAPI segmentation service error: " + response.getStatusCode().value(), response.getStatusCode().value());
                    })
                    .body(SegmentationResponseDto.class);
        } catch (RestClientException ex) {
            log.error("Error communicating with FastAPI segmentation endpoint: {}", ex.getMessage());
            throw new FastApiException("Failed to communicate with FastAPI segmentation service: " + ex.getMessage(), ex);
        }
    }

    @Override
    public PredictionTrainingResponseDto trainPredictionModels(
            byte[] csvBytes,
            String filename,
            String splitStrategy,
            double testSize,
            int randomState
    ) {
        return trainPredictionModels(csvBytes, filename, splitStrategy, testSize, randomState, null);
    }

    @Override
    public PredictionTrainingResponseDto trainPredictionModels(
            byte[] csvBytes,
            String filename,
            String splitStrategy,
            double testSize,
            int randomState,
            String datasetId
    ) {
        try {
            log.info("Requesting regression model training from FastAPI (datasetId={}, strategy={}, test_size={}, random_state={})",
                    datasetId, splitStrategy, testSize, randomState);

            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            if (csvBytes != null && csvBytes.length > 0) {
                body.add("file", createByteArrayResource(csvBytes, filename));
            }
            if (datasetId != null && !datasetId.isBlank()) {
                body.add("dataset_id", datasetId);
            }
            body.add("split_strategy", splitStrategy != null ? splitStrategy : "chronological");
            body.add("test_size", String.valueOf(testSize));
            body.add("random_state", String.valueOf(randomState));

            return restClient.post()
                    .uri("/predictions/train")
                    .contentType(MediaType.MULTIPART_FORM_DATA)
                    .body(body)
                    .retrieve()
                    .onStatus(HttpStatusCode::isError, (request, response) -> {
                        log.error("FastAPI prediction training failed with status code {}", response.getStatusCode());
                        throw new FastApiException("FastAPI prediction training error: " + response.getStatusCode().value(), response.getStatusCode().value());
                    })
                    .body(PredictionTrainingResponseDto.class);
        } catch (RestClientException ex) {
            log.error("Error communicating with FastAPI prediction training endpoint: {}", ex.getMessage());
            throw new FastApiException("Failed to communicate with FastAPI prediction training service: " + ex.getMessage(), ex);
        }
    }

    @Override
    public ScenarioPredictionResponseDto predictScenario(ScenarioPredictionRequestDto request) {
        try {
            log.info("Requesting scenario sales prediction from FastAPI for category='{}', region='{}', qty={}, disc={}",
                    request.category(), request.region(), request.quantity(), request.discount());

            return restClient.post()
                    .uri("/predictions/predict")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(request)
                    .retrieve()
                    .onStatus(HttpStatusCode::isError, (req, response) -> {
                        log.error("FastAPI scenario prediction failed with status code {}", response.getStatusCode());
                        throw new FastApiException("FastAPI prediction inference error: " + response.getStatusCode().value(), response.getStatusCode().value());
                    })
                    .body(ScenarioPredictionResponseDto.class);
        } catch (RestClientException ex) {
            log.error("Error communicating with FastAPI prediction endpoint: {}", ex.getMessage());
            throw new FastApiException("Failed to communicate with FastAPI prediction service: " + ex.getMessage(), ex);
        }
    }

    @Override
    public PredictionExplanationResponseDto explainScenario(ScenarioPredictionRequestDto request) {
        try {
            log.info("Requesting SHAP explanation from FastAPI for category='{}', region='{}', model='{}'",
                    request.category(), request.region(), request.modelType());

            return restClient.post()
                    .uri("/predictions/explain")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(request)
                    .retrieve()
                    .onStatus(HttpStatusCode::isError, (req, response) -> {
                        log.error("FastAPI scenario explanation failed with status code {}", response.getStatusCode());
                        throw new FastApiException("FastAPI explanation error: " + response.getStatusCode().value(), response.getStatusCode().value());
                    })
                    .body(PredictionExplanationResponseDto.class);
        } catch (RestClientException ex) {
            log.error("Error communicating with FastAPI explanation endpoint: {}", ex.getMessage());
            throw new FastApiException("Failed to communicate with FastAPI explanation service: " + ex.getMessage(), ex);
        }
    }

    @Override
    public ScenarioComparisonResponseDto compareScenarios(ScenarioComparisonRequestDto request) {
        try {
            log.info("Requesting side-by-side scenario comparison from FastAPI for model='{}', datasetId='{}'",
                    request.modelType(), request.datasetId());

            return restClient.post()
                    .uri("/predictions/compare")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(request)
                    .retrieve()
                    .onStatus(HttpStatusCode::isError, (req, response) -> {
                        log.error("FastAPI scenario comparison failed with status code {}", response.getStatusCode());
                        throw new FastApiException("FastAPI comparison error: " + response.getStatusCode().value(), response.getStatusCode().value());
                    })
                    .body(ScenarioComparisonResponseDto.class);
        } catch (RestClientException ex) {
            log.error("Error communicating with FastAPI comparison endpoint: {}", ex.getMessage());
            throw new FastApiException("Failed to communicate with FastAPI comparison service: " + ex.getMessage(), ex);
        }
    }

    @Override
    public InsightsResponseDto generateInsights(byte[] csvBytes, String filename, String severity, String category) {
        try {
            log.info("Requesting decision support insights from FastAPI (severity={}, category={})", severity, category);

            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            if (csvBytes != null && csvBytes.length > 0) {
                body.add("file", createByteArrayResource(csvBytes, filename));
            }
            if (severity != null && !severity.isBlank()) {
                body.add("severity", severity.trim());
            }
            if (category != null && !category.isBlank()) {
                body.add("category", category.trim());
            }

            return restClient.post()
                    .uri("/insights")
                    .contentType(MediaType.MULTIPART_FORM_DATA)
                    .body(body)
                    .retrieve()
                    .onStatus(HttpStatusCode::isError, (request, response) -> {
                        log.error("FastAPI insights generation failed with status code {}", response.getStatusCode());
                        throw new FastApiException("FastAPI insights service error: " + response.getStatusCode().value(), response.getStatusCode().value());
                    })
                    .body(InsightsResponseDto.class);
        } catch (RestClientException ex) {
            log.error("Error communicating with FastAPI insights endpoint: {}", ex.getMessage());
            throw new FastApiException("Failed to communicate with FastAPI insights service: " + ex.getMessage(), ex);
        }
    }

    private ByteArrayResource createByteArrayResource(byte[] csvBytes, String filename) {
        return new ByteArrayResource(csvBytes) {
            @Override
            public String getFilename() {
                return (filename != null && !filename.isBlank()) ? filename : "dataset.csv";
            }
        };
    }
}
