package com.bizinsightiq.client;

import com.bizinsightiq.client.dto.FastApiHealthResponse;
import com.bizinsightiq.client.exception.FastApiException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.web.client.RestClient;

import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.method;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.*;

class FastApiClientTest {

    private MockRestServiceServer mockServer;
    private FastApiClient fastApiClient;

    @BeforeEach
    void setUp() {
        RestClient.Builder builder = RestClient.builder().baseUrl("http://mock-fastapi:8000/api/v1");
        mockServer = MockRestServiceServer.bindTo(builder).build();
        RestClient restClient = builder.build();
        fastApiClient = new FastApiClient(restClient);
    }

    @Test
    @DisplayName("checkHealth() should parse JSON response when FastAPI returns 200 OK")
    void testCheckHealthSuccess() {
        String json = """
            {
                "status": "ok",
                "app": "BizInsightIQ ML Service",
                "version": "1.0.0",
                "core_modules": ["data_loader", "validator", "eda", "segmentation", "prediction", "insights"]
            }
            """;

        mockServer.expect(requestTo("http://mock-fastapi:8000/api/v1/health"))
                .andExpect(method(HttpMethod.GET))
                .andRespond(withSuccess(json, MediaType.APPLICATION_JSON));

        FastApiHealthResponse response = fastApiClient.checkHealth();

        assertNotNull(response);
        assertEquals("ok", response.status());
        assertEquals("BizInsightIQ ML Service", response.app());
        assertEquals("1.0.0", response.version());
        assertEquals(6, response.coreModules().size());
        assertTrue(response.isHealthy());
        mockServer.verify();
    }

    @Test
    @DisplayName("checkHealth() should throw FastApiException when downstream returns 500 Internal Error")
    void testCheckHealthServerError() {
        mockServer.expect(requestTo("http://mock-fastapi:8000/api/v1/health"))
                .andExpect(method(HttpMethod.GET))
                .andRespond(withServerError());

        FastApiException ex = assertThrows(FastApiException.class, () -> fastApiClient.checkHealth());
        assertTrue(ex.getMessage().contains("500") || ex.getMessage().contains("error"));
        mockServer.verify();
    }

    @Test
    @DisplayName("isReady() should return true when FastAPI ready endpoint returns ready: true")
    void testIsReadySuccess() {
        String json = "{\"ready\": true, \"timestamp\": 1729800000.0}";

        mockServer.expect(requestTo("http://mock-fastapi:8000/api/v1/ready"))
                .andExpect(method(HttpMethod.GET))
                .andRespond(withSuccess(json, MediaType.APPLICATION_JSON));

        boolean ready = fastApiClient.isReady();
        assertTrue(ready);
        mockServer.verify();
    }

    @Test
    @DisplayName("isReady() should return false when FastAPI service is unavailable")
    void testIsReadyFailure() {
        mockServer.expect(requestTo("http://mock-fastapi:8000/api/v1/ready"))
                .andExpect(method(HttpMethod.GET))
                .andRespond(withStatus(HttpStatus.SERVICE_UNAVAILABLE));

        boolean ready = fastApiClient.isReady();
        assertFalse(ready);
        mockServer.verify();
    }

    @Test
    @DisplayName("validateDataset() should return ValidationResponseDto when FastAPI validation endpoint succeeds")
    void testValidateDatasetSuccess() {
        String json = """
            {
                "is_valid": true,
                "total_rows": 1200,
                "total_columns": 8,
                "columns_present": ["CustomerID", "OrderDate", "Category", "Region", "Quantity", "Discount", "Sales", "Profit"],
                "missing_columns": [],
                "missing_values_by_column": {},
                "duplicate_rows_count": 0,
                "invalid_numeric_counts": {},
                "invalid_date_count": 0,
                "errors": [],
                "warnings": []
            }
            """;

        mockServer.expect(requestTo("http://mock-fastapi:8000/api/v1/datasets/validate"))
                .andExpect(method(HttpMethod.POST))
                .andRespond(withSuccess(json, MediaType.APPLICATION_JSON));

        com.bizinsightiq.client.dto.ValidationResponseDto response =
                fastApiClient.validateDataset("CustomerID,OrderDate,Category,Region,Quantity,Discount,Sales,Profit".getBytes(), "sample.csv");

        assertNotNull(response);
        assertTrue(response.isValid());
        assertEquals(1200, response.totalRows());
        assertEquals(8, response.totalColumns());
        assertTrue(response.errors().isEmpty());
        mockServer.verify();
    }

    @Test
    @DisplayName("validateDataset() should return invalid response when dataset has validation errors")
    void testValidateDatasetWithErrors() {
        String json = """
            {
                "is_valid": false,
                "total_rows": 10,
                "total_columns": 7,
                "columns_present": ["CustomerID", "OrderDate", "Category", "Region", "Quantity", "Discount", "Profit"],
                "missing_columns": ["Sales"],
                "missing_values_by_column": {},
                "duplicate_rows_count": 0,
                "invalid_numeric_counts": {},
                "invalid_date_count": 0,
                "errors": ["Missing required column(s): Sales"],
                "warnings": []
            }
            """;

        mockServer.expect(requestTo("http://mock-fastapi:8000/api/v1/datasets/validate"))
                .andExpect(method(HttpMethod.POST))
                .andRespond(withSuccess(json, MediaType.APPLICATION_JSON));

        com.bizinsightiq.client.dto.ValidationResponseDto response =
                fastApiClient.validateDataset("CustomerID,OrderDate,Category,Region,Quantity,Discount,Profit".getBytes(), "invalid.csv");

        assertNotNull(response);
        assertFalse(response.isValid());
        assertEquals(1, response.missingColumns().size());
        assertEquals("Sales", response.missingColumns().get(0));
        assertEquals(1, response.errors().size());
        mockServer.verify();
    }

    @Test
    @DisplayName("runEda() should return EdaResponseDto when FastAPI EDA succeeds")
    void testRunEdaSuccess() {
        String json = """
            {
                "kpis": {
                    "total_sales": 2297200.86,
                    "total_profit": 286397.02,
                    "total_units": 37873,
                    "unique_customers": 793,
                    "total_orders": 5009,
                    "profit_margin_pct": 12.47,
                    "avg_order_value": 458.61,
                    "avg_discount_pct": 15.62
                },
                "trends": [{"year_month": "2023-01", "sales": 45000.0, "profit": 5500.0}],
                "category_performance": [{"category": "Technology", "sales": 836154.03}],
                "regional_performance": [{"region": "West", "sales": 725457.82}],
                "discount_analysis": [{"discount_bucket": "0-10%", "profit_margin": 25.4}],
                "correlation_matrix": {"Sales": {"Profit": 0.48}}
            }
            """;

        mockServer.expect(requestTo("http://mock-fastapi:8000/api/v1/analytics/eda"))
                .andExpect(method(HttpMethod.POST))
                .andRespond(withSuccess(json, MediaType.APPLICATION_JSON));

        com.bizinsightiq.client.dto.EdaResponseDto response = fastApiClient.runEda("dummy,csv".getBytes(), "sales.csv");

        assertNotNull(response);
        assertNotNull(response.kpis());
        assertEquals(2297200.86, response.kpis().totalSales());
        assertEquals(5009, response.kpis().totalOrders());
        assertEquals(1, response.trends().size());
        assertEquals(1, response.categoryPerformance().size());
        mockServer.verify();
    }

    @Test
    @DisplayName("runSegmentation() should return SegmentationResponseDto with cluster profiles and assignments")
    void testRunSegmentationSuccess() {
        String json = """
            {
                "n_clusters": 4,
                "silhouette_score": 0.4521,
                "inertia": 12540.5,
                "pca_variance_ratio": [45.2, 28.6],
                "cluster_profiles": [{"Cluster": 0, "CustomerCount": 200, "DescriptivePersona": "VIP Champions"}],
                "candidates_evaluation": [{"k": 2, "SilhouetteScore": 0.38}],
                "customer_assignments": [
                    {
                        "customer_id": "CUST-001",
                        "cluster_id": 0,
                        "recency": 12,
                        "frequency": 8,
                        "monetary_value": 1420.50,
                        "total_profit": 320.10
                    }
                ]
            }
            """;

        mockServer.expect(requestTo("http://mock-fastapi:8000/api/v1/segmentation"))
                .andExpect(method(HttpMethod.POST))
                .andRespond(withSuccess(json, MediaType.APPLICATION_JSON));

        com.bizinsightiq.client.dto.SegmentationResponseDto response =
                fastApiClient.runSegmentation("dummy,csv".getBytes(), "sales.csv", 4, 42, true, true);

        assertNotNull(response);
        assertEquals(4, response.nClusters());
        assertEquals(0.4521, response.silhouetteScore());
        assertEquals(1, response.clusterProfiles().size());
        assertNotNull(response.customerAssignments());
        assertEquals(1, response.customerAssignments().size());
        assertEquals("CUST-001", response.customerAssignments().get(0).customerId());
        mockServer.verify();
    }

    @Test
    @DisplayName("predictScenario() should send JSON payload and receive predicted sales")
    void testPredictScenarioSuccess() {
        String json = """
            {
                "predicted_sales": 875.42,
                "category": "Technology",
                "region": "East",
                "quantity": 5,
                "discount": 0.10,
                "month": 6,
                "quarter": 2,
                "day_of_week": 2,
                "model_used": "Random Forest Regressor"
            }
            """;

        mockServer.expect(requestTo("http://mock-fastapi:8000/api/v1/predictions/predict"))
                .andExpect(method(HttpMethod.POST))
                .andRespond(withSuccess(json, MediaType.APPLICATION_JSON));

        com.bizinsightiq.client.dto.ScenarioPredictionRequestDto request =
                new com.bizinsightiq.client.dto.ScenarioPredictionRequestDto("Technology", "East", 5, 0.10, 6, 2, 2);

        com.bizinsightiq.client.dto.ScenarioPredictionResponseDto response = fastApiClient.predictScenario(request);

        assertNotNull(response);
        assertEquals(875.42, response.predictedSales());
        assertEquals("Technology", response.category());
        assertEquals("Random Forest Regressor", response.modelUsed());
        mockServer.verify();
    }

    @Test
    @DisplayName("generateInsights() should return structured insights and category counts")
    void testGenerateInsightsSuccess() {
        String json = """
            {
                "summary": {
                    "total_insights": 8,
                    "critical_count": 2,
                    "warning_count": 4,
                    "info_count": 2
                },
                "insights": [
                    {
                        "insight_id": "INS-001",
                        "category": "Sales & Profitability",
                        "severity": "critical",
                        "title": "Severe Margin Erosion in Furniture",
                        "evidence": {"loss_amount": -14200.0},
                        "recommendation": "Review vendor discount structures immediately",
                        "limitations": "Based on historical transactions"
                    }
                ]
            }
            """;

        mockServer.expect(requestTo("http://mock-fastapi:8000/api/v1/insights"))
                .andExpect(method(HttpMethod.POST))
                .andRespond(withSuccess(json, MediaType.APPLICATION_JSON));

        com.bizinsightiq.client.dto.InsightsResponseDto response =
                fastApiClient.generateInsights("dummy,csv".getBytes(), "sales.csv", "CRITICAL", null);

        assertNotNull(response);
        assertEquals(8, response.summary().totalInsights());
        assertEquals(2, response.summary().criticalCount());
        assertEquals(1, response.insights().size());
        assertEquals("INS-001", response.insights().get(0).insightId());
        assertEquals("critical", response.insights().get(0).severity());
        mockServer.verify();
    }
}
