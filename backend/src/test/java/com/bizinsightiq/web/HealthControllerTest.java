package com.bizinsightiq.web;

import com.bizinsightiq.client.PythonMlClient;
import com.bizinsightiq.client.dto.FastApiHealthResponse;
import com.bizinsightiq.client.exception.FastApiException;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class HealthControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private PythonMlClient pythonMlClient;

    @Test
    @DisplayName("GET /api/v1/health should return UP and downstream details when FastAPI is healthy")
    void testHealthEndpointSuccess() throws Exception {
        FastApiHealthResponse fastApiMock = new FastApiHealthResponse(
                "ok", "BizInsightIQ ML Service", "1.0.0", List.of("eda", "segmentation", "prediction")
        );
        when(pythonMlClient.checkHealth()).thenReturn(fastApiMock);

        mockMvc.perform(get("/api/v1/health")
                        .accept(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("UP"))
                .andExpect(jsonPath("$.service").value("BizInsightIQ Spring Boot Enterprise Core"))
                .andExpect(jsonPath("$.downstream.fastapi.status").value("ok"));
    }

    @Test
    @DisplayName("GET /api/v1/health should return UP with UNAVAILABLE downstream when FastAPI is down")
    void testHealthEndpointWhenDownstreamFails() throws Exception {
        when(pythonMlClient.checkHealth()).thenThrow(new FastApiException("Service unavailable"));

        mockMvc.perform(get("/api/v1/health")
                        .accept(MediaType.APPLICATION_JSON))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("UP"))
                .andExpect(jsonPath("$.downstream.fastapi.status").value("UNAVAILABLE"));
    }
}
