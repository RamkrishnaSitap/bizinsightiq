package com.bizinsightiq.domain.repository;

import com.bizinsightiq.domain.model.Dataset;
import com.bizinsightiq.domain.model.QuoteSimulation;
import com.bizinsightiq.domain.model.User;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.test.context.ActiveProfiles;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

@DataJpaTest
@ActiveProfiles("test")
class EntityRepositoryTest {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private DatasetRepository datasetRepository;

    @Autowired
    private QuoteSimulationRepository quoteSimulationRepository;

    @Test
    @DisplayName("UserRepository should save and find users by username and email")
    void testUserSaveAndLookup() {
        User user = new User("analyst_test", "test@bizinsightiq.com", "$2a$10$hashedpwstringhere1234567890", "ROLE_ANALYST");
        User saved = userRepository.saveAndFlush(user);

        assertNotNull(saved.getId());
        assertEquals("analyst_test", saved.getUsername());
        assertNotNull(saved.getCreatedAt());

        Optional<User> found = userRepository.findByUsername("analyst_test");
        assertTrue(found.isPresent());
        assertEquals("test@bizinsightiq.com", found.get().getEmail());
        assertTrue(userRepository.existsByUsername("analyst_test"));
    }

    @Test
    @DisplayName("DatasetRepository should enforce tenant isolation by userId")
    void testDatasetTenantIsolation() {
        UUID ownerA = UUID.randomUUID();
        UUID ownerB = UUID.randomUUID();

        Dataset datasetA = new Dataset(ownerA, "Sales Data A", "data_a.csv", "uploads/a.csv");
        datasetA.setTotalRows(500);
        datasetA.setTotalColumns(8);
        datasetA.setIsValid(true);
        Dataset savedA = datasetRepository.save(datasetA);

        Dataset datasetB = new Dataset(ownerB, "Sales Data B", "data_b.csv", "uploads/b.csv");
        datasetRepository.save(datasetB);

        // Owner A should only see dataset A
        List<Dataset> ownerADatasets = datasetRepository.findByUserId(ownerA);
        assertEquals(1, ownerADatasets.size());
        assertEquals("Sales Data A", ownerADatasets.get(0).getName());

        // Cross-tenant lookup should return empty
        Optional<Dataset> crossTenantLookup = datasetRepository.findByIdAndUserId(savedA.getId(), ownerB);
        assertTrue(crossTenantLookup.isEmpty());

        // Legitimate owner lookup should succeed
        Optional<Dataset> legitimateLookup = datasetRepository.findByIdAndUserId(savedA.getId(), ownerA);
        assertTrue(legitimateLookup.isPresent());
    }

    @Test
    @DisplayName("QuoteSimulationRepository should persist and retrieve quotes by userId")
    void testQuoteSimulationSaveAndRetrieve() {
        UUID userId = UUID.randomUUID();
        QuoteSimulation quote = new QuoteSimulation();
        quote.setUserId(userId);
        quote.setCategory("Technology");
        quote.setRegion("East");
        quote.setQuantity(5);
        quote.setDiscount(new BigDecimal("0.1000"));
        quote.setPredictedSales(new BigDecimal("1250.50"));
        quote.setModelVersion("RandomForestRegressor-v1.0");

        QuoteSimulation saved = quoteSimulationRepository.save(quote);
        assertNotNull(saved.getId());

        List<QuoteSimulation> userQuotes = quoteSimulationRepository.findByUserIdOrderByCreatedAtDesc(userId);
        assertEquals(1, userQuotes.size());
        assertEquals(new BigDecimal("1250.50"), userQuotes.get(0).getPredictedSales());
    }
}
