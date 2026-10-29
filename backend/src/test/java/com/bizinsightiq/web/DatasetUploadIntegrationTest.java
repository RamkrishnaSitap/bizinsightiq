package com.bizinsightiq.web;

import com.bizinsightiq.client.PythonMlClient;
import com.bizinsightiq.client.dto.ValidationResponseDto;
import com.bizinsightiq.domain.model.Dataset;
import com.bizinsightiq.domain.model.User;
import com.bizinsightiq.domain.repository.DatasetRepository;
import com.bizinsightiq.domain.repository.SalesTransactionRepository;
import com.bizinsightiq.domain.repository.UserRepository;
import com.bizinsightiq.security.JwtTokenProvider;
import com.bizinsightiq.security.UserPrincipal;
import com.bizinsightiq.service.FileStorageService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import static org.hamcrest.Matchers.*;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.multipart;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
class DatasetUploadIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private DatasetRepository datasetRepository;

    @Autowired
    private SalesTransactionRepository salesTransactionRepository;

    @Autowired
    private FileStorageService fileStorageService;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Autowired
    private JwtTokenProvider tokenProvider;

    @MockBean
    private PythonMlClient pythonMlClient;

    private User testUser;
    private String jwtToken;

    private static final String VALID_CSV_CONTENT = """
            CustomerID,OrderDate,Category,Region,Quantity,Discount,Sales,Profit
            CUST-1001,2023-01-15,Technology,East,5,0.10,1250.00,250.00
            CUST-1002,2023-01-16,Furniture,West,2,0.05,450.00,80.00
            CUST-1003,2023-01-17,Office Supplies,South,10,0.20,150.00,-15.00
            """;

    @BeforeEach
    void setUp() {
        salesTransactionRepository.deleteAll();
        datasetRepository.deleteAll();
        userRepository.deleteAll();

        testUser = new User("data_analyst", "analyst@bizinsightiq.com", passwordEncoder.encode("Pass123!"), "ROLE_ANALYST");
        testUser = userRepository.saveAndFlush(testUser);
        jwtToken = tokenProvider.generateToken(UserPrincipal.create(testUser));
    }

    @Test
    @DisplayName("POST /api/v1/datasets/upload without JWT should return 401 Unauthorized")
    void testUploadWithoutAuthentication() throws Exception {
        MockMultipartFile file = new MockMultipartFile(
                "file", "sales.csv", "text/csv", VALID_CSV_CONTENT.getBytes()
        );

        mockMvc.perform(multipart("/api/v1/datasets/upload").file(file))
                .andExpect(status().isUnauthorized());
    }

    @Test
    @DisplayName("POST /api/v1/datasets/upload with valid CSV should validate, persist batch and return 201 Created")
    void testUploadValidCsvSuccess() throws Exception {
        MockMultipartFile file = new MockMultipartFile(
                "file", "q1_sales.csv", "text/csv", VALID_CSV_CONTENT.getBytes()
        );

        ValidationResponseDto mockValidation = new ValidationResponseDto(
                true, 3, 8,
                List.of("CustomerID", "OrderDate", "Category", "Region", "Quantity", "Discount", "Sales", "Profit"),
                Collections.emptyList(),
                Collections.emptyMap(),
                0,
                Collections.emptyMap(),
                0,
                Collections.emptyList(),
                Collections.emptyList()
        );
        when(pythonMlClient.validateDataset(any(), anyString())).thenReturn(mockValidation);

        mockMvc.perform(multipart("/api/v1/datasets/upload")
                        .file(file)
                        .param("name", "Q1 Retail Report")
                        .header("Authorization", "Bearer " + jwtToken))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.datasetId", notNullValue()))
                .andExpect(jsonPath("$.name", is("Q1 Retail Report")))
                .andExpect(jsonPath("$.status", is("VALIDATED")))
                .andExpect(jsonPath("$.totalRows", is(3)))
                .andExpect(jsonPath("$.validRows", is(3)))
                .andExpect(jsonPath("$.isValid", is(true)));

        // Verify dataset persisted in PostgreSQL (H2 test mode)
        List<Dataset> userDatasets = datasetRepository.findByUserId(testUser.getId());
        assertEquals(1, userDatasets.size());
        Dataset dataset = userDatasets.get(0);
        assertEquals("Q1 Retail Report", dataset.getName());
        assertEquals("VALIDATED", dataset.getStatus());
        assertTrue(dataset.getIsValid());

        // Verify transactions persisted in batch
        long transactionCount = salesTransactionRepository.countByDatasetId(dataset.getId());
        assertEquals(3, transactionCount);

        // Verify file exists in storage
        Path storedFile = fileStorageService.resolveStoragePath(dataset.getStorageKey());
        assertTrue(Files.exists(storedFile));
    }

    @Test
    @DisplayName("POST /api/v1/datasets/upload with invalid CSV should return 422 and not persist transactions")
    void testUploadValidationFailure() throws Exception {
        String invalidCsv = "CustomerID,OrderDate,Category,Region\nCUST-1,2023-01-01,Tech,East";
        MockMultipartFile file = new MockMultipartFile(
                "file", "bad_schema.csv", "text/csv", invalidCsv.getBytes()
        );

        ValidationResponseDto mockFailure = new ValidationResponseDto(
                false, 1, 4,
                List.of("CustomerID", "OrderDate", "Category", "Region"),
                List.of("Quantity", "Discount", "Sales", "Profit"),
                Collections.emptyMap(),
                0,
                Collections.emptyMap(),
                0,
                List.of("Missing required column(s): Quantity, Discount, Sales, Profit"),
                Collections.emptyList()
        );
        when(pythonMlClient.validateDataset(any(), anyString())).thenReturn(mockFailure);

        mockMvc.perform(multipart("/api/v1/datasets/upload")
                        .file(file)
                        .param("name", "Faulty Dataset")
                        .header("Authorization", "Bearer " + jwtToken))
                .andExpect(status().isUnprocessableEntity())
                .andExpect(jsonPath("$.status", is("FAILED")))
                .andExpect(jsonPath("$.isValid", is(false)))
                .andExpect(jsonPath("$.errors", hasSize(1)))
                .andExpect(jsonPath("$.errors[0]", containsString("Missing required column(s)")));

        // Verify dataset status is FAILED
        List<Dataset> userDatasets = datasetRepository.findByUserId(testUser.getId());
        assertEquals(1, userDatasets.size());
        Dataset dataset = userDatasets.get(0);
        assertEquals("FAILED", dataset.getStatus());
        assertFalse(dataset.getIsValid());

        // Verify zero transactions persisted
        long transactionCount = salesTransactionRepository.countByDatasetId(dataset.getId());
        assertEquals(0, transactionCount);

        // Verify storage file was cleaned up
        Path storedFile = fileStorageService.resolveStoragePath(dataset.getStorageKey());
        assertFalse(Files.exists(storedFile), "Invalid file should be cleaned up from storage!");
    }

    @Test
    @DisplayName("POST /api/v1/datasets/upload with empty file should return 400 Bad Request")
    void testUploadEmptyFile() throws Exception {
        MockMultipartFile emptyFile = new MockMultipartFile(
                "file", "empty.csv", "text/csv", new byte[0]
        );

        mockMvc.perform(multipart("/api/v1/datasets/upload")
                        .file(emptyFile)
                        .header("Authorization", "Bearer " + jwtToken))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.status", is(400)))
                .andExpect(jsonPath("$.message", containsString("empty")));
    }

    @Test
    @DisplayName("POST /api/v1/datasets/upload with non-CSV extension should return 400 Bad Request")
    void testUploadNonCsvFile() throws Exception {
        MockMultipartFile textFile = new MockMultipartFile(
                "file", "payload.txt", "text/plain", "Some random text content".getBytes()
        );

        mockMvc.perform(multipart("/api/v1/datasets/upload")
                        .file(textFile)
                        .header("Authorization", "Bearer " + jwtToken))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.status", is(400)))
                .andExpect(jsonPath("$.message", containsString("CSV files (.csv) are accepted")));
    }

    @Test
    @DisplayName("File storage should confine path traversal attempts into UUID filename")
    void testPathTraversalConfinement() throws Exception {
        MockMultipartFile traversalFile = new MockMultipartFile(
                "file", "../../etc/passwd.csv", "text/csv", VALID_CSV_CONTENT.getBytes()
        );

        ValidationResponseDto mockValidation = new ValidationResponseDto(
                true, 3, 8,
                List.of("CustomerID", "OrderDate", "Category", "Region", "Quantity", "Discount", "Sales", "Profit"),
                Collections.emptyList(), Collections.emptyMap(), 0, Collections.emptyMap(), 0,
                Collections.emptyList(), Collections.emptyList()
        );
        when(pythonMlClient.validateDataset(any(), anyString())).thenReturn(mockValidation);

        mockMvc.perform(multipart("/api/v1/datasets/upload")
                        .file(traversalFile)
                        .header("Authorization", "Bearer " + jwtToken))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.datasetId", notNullValue()));

        // Confirm file is stored strictly inside uploadRoot
        List<Dataset> userDatasets = datasetRepository.findByUserId(testUser.getId());
        Dataset dataset = userDatasets.get(0);
        Path storedFile = fileStorageService.resolveStoragePath(dataset.getStorageKey());
        assertTrue(storedFile.startsWith(fileStorageService.getUploadRoot()));
        assertTrue(storedFile.getFileName().toString().endsWith(".csv"));
    }

    @Test
    @DisplayName("DELETE /api/v1/datasets/{id} should delete dataset and clean up stored file from disk")
    void testDeleteDatasetCleansUpStorage() throws Exception {
        // Upload valid dataset
        MockMultipartFile file = new MockMultipartFile(
                "file", "to_delete.csv", "text/csv", VALID_CSV_CONTENT.getBytes()
        );
        ValidationResponseDto mockValidation = new ValidationResponseDto(
                true, 3, 8,
                List.of("CustomerID", "OrderDate", "Category", "Region", "Quantity", "Discount", "Sales", "Profit"),
                Collections.emptyList(), Collections.emptyMap(), 0, Collections.emptyMap(), 0,
                Collections.emptyList(), Collections.emptyList()
        );
        when(pythonMlClient.validateDataset(any(), anyString())).thenReturn(mockValidation);

        mockMvc.perform(multipart("/api/v1/datasets/upload")
                        .file(file)
                        .header("Authorization", "Bearer " + jwtToken))
                .andExpect(status().isCreated());

        Dataset dataset = datasetRepository.findByUserId(testUser.getId()).get(0);
        UUID datasetId = dataset.getId();
        Path storedFile = fileStorageService.resolveStoragePath(dataset.getStorageKey());
        assertTrue(Files.exists(storedFile), "File must exist before deletion");

        // Delete dataset
        mockMvc.perform(delete("/api/v1/datasets/" + datasetId)
                        .header("Authorization", "Bearer " + jwtToken))
                .andExpect(status().isNoContent());

        // Verify dataset removed from DB
        assertFalse(datasetRepository.findById(datasetId).isPresent());

        // Verify stored file was cleaned up from filesystem
        assertFalse(Files.exists(storedFile), "Stored file must be removed from disk upon dataset deletion");
    }
}
