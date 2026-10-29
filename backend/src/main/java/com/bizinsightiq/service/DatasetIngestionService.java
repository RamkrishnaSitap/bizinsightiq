package com.bizinsightiq.service;

import com.bizinsightiq.client.PythonMlClient;
import com.bizinsightiq.client.dto.ValidationResponseDto;
import com.bizinsightiq.domain.model.Dataset;
import com.bizinsightiq.domain.repository.DatasetRepository;
import com.bizinsightiq.security.UserPrincipal;
import com.bizinsightiq.web.dto.UploadDatasetResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDate;
import java.util.*;

@Service
public class DatasetIngestionService {

    private static final Logger log = LoggerFactory.getLogger(DatasetIngestionService.class);
    private static final int BATCH_SIZE = 500;

    private static final String INSERT_TRANSACTION_SQL = """
            INSERT INTO sales_transactions (
                dataset_id, order_id, customer_id, order_date, category, region,
                quantity, unit_price, discount, sales, profit, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """;

    private final DatasetRepository datasetRepository;
    private final FileStorageService fileStorageService;
    private final PythonMlClient pythonMlClient;
    private final JdbcTemplate jdbcTemplate;

    public DatasetIngestionService(DatasetRepository datasetRepository,
                                   FileStorageService fileStorageService,
                                   PythonMlClient pythonMlClient,
                                   JdbcTemplate jdbcTemplate) {
        this.datasetRepository = datasetRepository;
        this.fileStorageService = fileStorageService;
        this.pythonMlClient = pythonMlClient;
        this.jdbcTemplate = jdbcTemplate;
    }

    @Transactional
    public UploadDatasetResponse ingestCsvDataset(MultipartFile file, String datasetName, UserPrincipal principal) {
        String originalFilename = StringUtils.cleanPath(
                file.getOriginalFilename() != null ? file.getOriginalFilename() : "dataset.csv"
        );
        String displayName = StringUtils.hasText(datasetName) ? datasetName.trim() : originalFilename;

        // 1. Pre-register Dataset in PENDING state to obtain authoritative UUID
        Dataset dataset = new Dataset(principal.getId(), displayName, originalFilename, "pending");
        dataset.setStatus("PENDING");
        dataset = datasetRepository.saveAndFlush(dataset);
        UUID datasetId = dataset.getId();

        log.info("Starting CSV ingestion for dataset '{}' (id: {}) by user '{}'", displayName, datasetId, principal.getUsername());

        // 2. Stage File in Server-Controlled Storage Key
        String storageKey = fileStorageService.storeFile(file, datasetId);
        dataset.setStorageKey(storageKey);

        byte[] fileBytes;
        try {
            fileBytes = file.getBytes();
        } catch (Exception ex) {
            fileStorageService.deleteFile(storageKey);
            throw new IllegalArgumentException("Failed to read uploaded file stream", ex);
        }

        // 3. Validate via FastAPI ML Engine
        ValidationResponseDto validation;
        try {
            validation = pythonMlClient.validateDataset(fileBytes, originalFilename);
        } catch (Exception ex) {
            log.error("Validation service invocation failed: {}", ex.getMessage());
            fileStorageService.deleteFile(storageKey);
            throw ex;
        }

        // 4. Handle Validation Failures
        if (!validation.isValid()) {
            log.warn("Dataset '{}' failed validation with {} error(s): {}", displayName, validation.errors().size(), validation.errors());
            
            // Record failed dataset metadata for audit trail
            dataset.setStatus("FAILED");
            dataset.setIsValid(false);
            dataset.setTotalRows(validation.totalRows());
            dataset.setTotalColumns(validation.totalColumns());
            datasetRepository.saveAndFlush(dataset);

            // Clean up raw file since import did not succeed
            fileStorageService.deleteFile(storageKey);

            return UploadDatasetResponse.failure(
                    datasetId,
                    displayName,
                    originalFilename,
                    validation.totalRows(),
                    validation.errors(),
                    validation.warnings(),
                    "Dataset validation failed: " + String.join("; ", validation.errors())
            );
        }

        // 5. Batch Persist Transactions into PostgreSQL
        Path filePath = fileStorageService.resolveStoragePath(storageKey);
        int insertedCount = 0;
        try {
            insertedCount = persistTransactionsBatch(filePath, datasetId);
        } catch (Exception ex) {
            log.error("Database batch insertion failed for dataset {}: {}", datasetId, ex.getMessage());
            fileStorageService.deleteFile(storageKey);
            throw new RuntimeException("Database error during transactional batch insert: " + ex.getMessage(), ex);
        }

        // 6. Update Dataset Metadata to VALIDATED
        dataset.setStatus("VALIDATED");
        dataset.setIsValid(true);
        dataset.setTotalRows(insertedCount);
        dataset.setTotalColumns(validation.totalColumns());
        datasetRepository.saveAndFlush(dataset);

        log.info("Successfully ingested and persisted dataset '{}' with {} transactions", displayName, insertedCount);

        return UploadDatasetResponse.success(
                datasetId,
                displayName,
                originalFilename,
                insertedCount,
                validation.warnings()
        );
    }

    private int persistTransactionsBatch(Path csvPath, UUID datasetId) throws Exception {
        int inserted = 0;
        List<Object[]> batch = new ArrayList<>(BATCH_SIZE);

        try (BufferedReader reader = Files.newBufferedReader(csvPath, StandardCharsets.UTF_8)) {
            String headerLine = reader.readLine();
            if (headerLine == null) {
                return 0;
            }

            List<String> headers = parseCsvLine(headerLine);
            int custIdx = findHeaderIndex(headers, "CustomerID", "customer_id");
            int dateIdx = findHeaderIndex(headers, "OrderDate", "order_date");
            int catIdx = findHeaderIndex(headers, "Category", "category");
            int regIdx = findHeaderIndex(headers, "Region", "region");
            int qtyIdx = findHeaderIndex(headers, "Quantity", "quantity");
            int discIdx = findHeaderIndex(headers, "Discount", "discount");
            int salesIdx = findHeaderIndex(headers, "Sales", "sales");
            int profitIdx = findHeaderIndex(headers, "Profit", "profit");
            int orderIdIdx = findHeaderIndex(headers, "OrderID", "order_id");
            int priceIdx = findHeaderIndex(headers, "UnitPrice", "unit_price");

            String line;
            while ((line = reader.readLine()) != null) {
                if (line.isBlank()) continue;

                List<String> tokens = parseCsvLine(line);
                if (tokens.size() <= Math.max(custIdx, profitIdx)) {
                    continue;
                }

                String customerId = tokens.get(custIdx);
                LocalDate orderDate = LocalDate.parse(tokens.get(dateIdx));
                String category = tokens.get(catIdx);
                String region = tokens.get(regIdx);
                int quantity = Integer.parseInt(tokens.get(qtyIdx));
                BigDecimal discount = new BigDecimal(tokens.get(discIdx));
                BigDecimal sales = new BigDecimal(tokens.get(salesIdx));
                BigDecimal profit = new BigDecimal(tokens.get(profitIdx));

                String orderId = (orderIdIdx >= 0 && orderIdIdx < tokens.size()) ? tokens.get(orderIdIdx) : null;
                BigDecimal unitPrice = (priceIdx >= 0 && priceIdx < tokens.size() && !tokens.get(priceIdx).isBlank())
                        ? new BigDecimal(tokens.get(priceIdx)) : null;

                batch.add(new Object[]{
                        datasetId,
                        orderId,
                        customerId,
                        java.sql.Date.valueOf(orderDate),
                        category,
                        region,
                        quantity,
                        unitPrice,
                        discount,
                        sales,
                        profit,
                        java.sql.Timestamp.from(java.time.Instant.now())
                });

                if (batch.size() >= BATCH_SIZE) {
                    jdbcTemplate.batchUpdate(INSERT_TRANSACTION_SQL, batch);
                    inserted += batch.size();
                    batch.clear();
                }
            }

            if (!batch.isEmpty()) {
                jdbcTemplate.batchUpdate(INSERT_TRANSACTION_SQL, batch);
                inserted += batch.size();
                batch.clear();
            }
        }

        return inserted;
    }

    private int findHeaderIndex(List<String> headers, String... candidates) {
        for (int i = 0; i < headers.size(); i++) {
            String h = headers.get(i).trim();
            for (String candidate : candidates) {
                if (h.equalsIgnoreCase(candidate)) {
                    return i;
                }
            }
        }
        return -1;
    }

    public static List<String> parseCsvLine(String line) {
        List<String> tokens = new ArrayList<>();
        StringBuilder sb = new StringBuilder();
        boolean inQuotes = false;
        for (int i = 0; i < line.length(); i++) {
            char c = line.charAt(i);
            if (c == '"') {
                inQuotes = !inQuotes;
            } else if (c == ',' && !inQuotes) {
                tokens.add(sb.toString().trim());
                sb.setLength(0);
            } else {
                sb.append(c);
            }
        }
        tokens.add(sb.toString().trim());
        return tokens;
    }
}
