package com.bizinsightiq.config;

import com.bizinsightiq.client.PythonMlClient;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class SecurityConfigTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private PythonMlClient pythonMlClient;

    @Test
    @DisplayName("Public health endpoint should be accessible without authentication")
    void testPublicHealthAccessible() throws Exception {
        mockMvc.perform(get("/api/v1/health"))
                .andExpect(status().isOk());
    }

    @Test
    @DisplayName("Public actuator health endpoint should be accessible without authentication")
    void testPublicActuatorHealthAccessible() throws Exception {
        mockMvc.perform(get("/actuator/health"))
                .andExpect(status().isOk());
    }

    @Test
    @DisplayName("Public auth login endpoint should be accessible without token")
    void testPublicLoginAccessible() throws Exception {
        mockMvc.perform(post("/api/v1/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"username\":\"admin\",\"password\":\"wrongpass\"}"))
                .andExpect(status().isUnauthorized()); // 401 Bad Credentials, not 401 Filter Rejection
    }

    @Test
    @DisplayName("Protected datasets endpoint should reject unauthenticated request with 401 Unauthorized")
    void testProtectedDatasetsRequiresAuthentication() throws Exception {
        mockMvc.perform(get("/api/v1/datasets"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    @DisplayName("Protected quotes endpoint should reject unauthenticated request with 401 Unauthorized")
    void testProtectedQuotesRequiresAuthentication() throws Exception {
        mockMvc.perform(get("/api/v1/quotes"))
                .andExpect(status().isUnauthorized());
    }
}
