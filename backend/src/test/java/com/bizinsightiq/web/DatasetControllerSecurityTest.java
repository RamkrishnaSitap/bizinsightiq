package com.bizinsightiq.web;

import com.bizinsightiq.client.PythonMlClient;
import com.bizinsightiq.domain.model.Dataset;
import com.bizinsightiq.domain.model.User;
import com.bizinsightiq.domain.repository.DatasetRepository;
import com.bizinsightiq.domain.repository.UserRepository;
import com.bizinsightiq.security.JwtTokenProvider;
import com.bizinsightiq.security.UserPrincipal;
import com.bizinsightiq.web.dto.CreateDatasetRequest;
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

import java.util.UUID;

import static org.hamcrest.Matchers.*;
import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class DatasetControllerSecurityTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private DatasetRepository datasetRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Autowired
    private JwtTokenProvider tokenProvider;

    @MockBean
    private PythonMlClient pythonMlClient;

    private User userAlice;
    private User userBob;
    private String tokenAlice;
    private String tokenBob;

    @BeforeEach
    void setUp() {
        datasetRepository.deleteAll();
        userRepository.deleteAll();

        userAlice = new User("alice", "alice@bizinsightiq.com", passwordEncoder.encode("PassAlice123"), "ROLE_ANALYST");
        userAlice = userRepository.saveAndFlush(userAlice);
        tokenAlice = tokenProvider.generateToken(UserPrincipal.create(userAlice));

        userBob = new User("bob", "bob@bizinsightiq.com", passwordEncoder.encode("PassBob123"), "ROLE_ANALYST");
        userBob = userRepository.saveAndFlush(userBob);
        tokenBob = tokenProvider.generateToken(UserPrincipal.create(userBob));
    }

    @Test
    @DisplayName("POST /api/v1/datasets without token should return 401 Unauthorized")
    void testCreateDatasetUnauthenticated() throws Exception {
        CreateDatasetRequest request = new CreateDatasetRequest(
                "Q1 Sales", "sales_q1.csv", "uploads/q1.csv", 100, 8
        );

        mockMvc.perform(post("/api/v1/datasets")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isUnauthorized());
    }

    @Test
    @DisplayName("POST /api/v1/datasets with token should create dataset bound to authenticated user")
    void testCreateDatasetAuthenticated() throws Exception {
        CreateDatasetRequest request = new CreateDatasetRequest(
                "Alice Retail Data", "alice_sales.csv", "uploads/alice.csv", 500, 8
        );

        mockMvc.perform(post("/api/v1/datasets")
                        .header("Authorization", "Bearer " + tokenAlice)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id", notNullValue()))
                .andExpect(jsonPath("$.userId", is(userAlice.getId().toString())))
                .andExpect(jsonPath("$.name", is("Alice Retail Data")))
                .andExpect(jsonPath("$.status", is("PENDING")))
                .andExpect(jsonPath("$.totalRows", is(500)));
    }

    @Test
    @DisplayName("GET /api/v1/datasets should return only datasets owned by authenticated user")
    void testListDatasetsTenantIsolation() throws Exception {
        // Alice creates 2 datasets
        Dataset dAlice1 = new Dataset(userAlice.getId(), "Alice DS 1", "f1.csv", "k1");
        Dataset dAlice2 = new Dataset(userAlice.getId(), "Alice DS 2", "f2.csv", "k2");
        datasetRepository.saveAndFlush(dAlice1);
        datasetRepository.saveAndFlush(dAlice2);

        // Bob creates 1 dataset
        Dataset dBob1 = new Dataset(userBob.getId(), "Bob DS 1", "b1.csv", "bk1");
        datasetRepository.saveAndFlush(dBob1);

        // Alice lists datasets: should only see Alice's 2 datasets
        mockMvc.perform(get("/api/v1/datasets")
                        .header("Authorization", "Bearer " + tokenAlice))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(2)))
                .andExpect(jsonPath("$[*].name", containsInAnyOrder("Alice DS 1", "Alice DS 2")))
                .andExpect(jsonPath("$[*].userId", everyItem(is(userAlice.getId().toString()))));

        // Bob lists datasets: should only see Bob's 1 dataset
        mockMvc.perform(get("/api/v1/datasets")
                        .header("Authorization", "Bearer " + tokenBob))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)))
                .andExpect(jsonPath("$[0].name", is("Bob DS 1")))
                .andExpect(jsonPath("$[0].userId", is(userBob.getId().toString())));
    }

    @Test
    @DisplayName("GET /api/v1/datasets/{id} for another user's dataset should return 404 Not Found")
    void testCrossUserDatasetAccessRejected() throws Exception {
        // Alice owns dataset
        Dataset datasetAlice = new Dataset(userAlice.getId(), "Alice Confidential", "conf.csv", "k_conf");
        datasetAlice = datasetRepository.saveAndFlush(datasetAlice);

        // Bob attempts to read Alice's dataset
        mockMvc.perform(get("/api/v1/datasets/" + datasetAlice.getId())
                        .header("Authorization", "Bearer " + tokenBob))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.status", is(404)))
                .andExpect(jsonPath("$.error", is("Not Found")));
    }

    @Test
    @DisplayName("DELETE /api/v1/datasets/{id} for another user's dataset should return 404 and not delete")
    void testCrossUserDatasetDeleteRejected() throws Exception {
        // Alice owns dataset
        Dataset datasetAlice = new Dataset(userAlice.getId(), "Alice Protected", "prot.csv", "k_prot");
        datasetAlice = datasetRepository.saveAndFlush(datasetAlice);
        UUID datasetId = datasetAlice.getId();

        // Bob attempts to delete Alice's dataset
        mockMvc.perform(delete("/api/v1/datasets/" + datasetId)
                        .header("Authorization", "Bearer " + tokenBob))
                .andExpect(status().isNotFound());

        // Verify dataset still exists in database
        assertTrue(datasetRepository.findById(datasetId).isPresent(), "Alice's dataset must remain in the database!");
    }

    @Test
    @DisplayName("DELETE /api/v1/datasets/{id} for owned dataset should return 204 No Content")
    void testDeleteOwnedDatasetSuccess() throws Exception {
        // Alice owns dataset
        Dataset datasetAlice = new Dataset(userAlice.getId(), "Alice Deletable", "del.csv", "k_del");
        datasetAlice = datasetRepository.saveAndFlush(datasetAlice);
        UUID datasetId = datasetAlice.getId();

        // Alice deletes her own dataset
        mockMvc.perform(delete("/api/v1/datasets/" + datasetId)
                        .header("Authorization", "Bearer " + tokenAlice))
                .andExpect(status().isNoContent());

        // Verify dataset was removed from database
        assertFalse(datasetRepository.findById(datasetId).isPresent(), "Dataset should be deleted from database");
    }

    @Test
    @DisplayName("Non-admin user requesting admin endpoint should receive 403 Forbidden")
    void testRoleEnforcementForNonAdmin() throws Exception {
        // Alice has ROLE_ANALYST, attempts to access /api/v1/users/**
        mockMvc.perform(get("/api/v1/users/admin-panel")
                        .header("Authorization", "Bearer " + tokenAlice))
                .andExpect(status().isForbidden())
                .andExpect(jsonPath("$.status", is(403)));
    }
}
