package com.bizinsightiq.service;

import com.bizinsightiq.domain.model.Dataset;
import com.bizinsightiq.domain.repository.DatasetRepository;
import com.bizinsightiq.security.UserPrincipal;
import com.bizinsightiq.web.dto.CreateDatasetRequest;
import com.bizinsightiq.web.dto.DatasetResponse;
import jakarta.persistence.EntityNotFoundException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;

@Service
public class DatasetService {

    private static final Logger log = LoggerFactory.getLogger(DatasetService.class);
    private final DatasetRepository datasetRepository;
    private final FileStorageService fileStorageService;

    public DatasetService(DatasetRepository datasetRepository, FileStorageService fileStorageService) {
        this.datasetRepository = datasetRepository;
        this.fileStorageService = fileStorageService;
    }

    @Transactional
    public DatasetResponse createDataset(CreateDatasetRequest request, UserPrincipal principal) {
        log.info("Creating dataset '{}' for authenticated user '{}' (id: {})",
                request.name(), principal.getUsername(), principal.getId());

        Dataset dataset = new Dataset(
                principal.getId(),
                request.name(),
                request.originalFilename(),
                request.storageKey()
        );

        if (request.totalRows() != null) {
            dataset.setTotalRows(request.totalRows());
        }
        if (request.totalColumns() != null) {
            dataset.setTotalColumns(request.totalColumns());
        }

        Dataset saved = datasetRepository.save(dataset);
        return DatasetResponse.fromEntity(saved);
    }

    @Transactional(readOnly = true)
    public List<DatasetResponse> listUserDatasets(UserPrincipal principal) {
        log.debug("Listing datasets for user '{}' (id: {})", principal.getUsername(), principal.getId());
        return datasetRepository.findByUserId(principal.getId())
                .stream()
                .map(DatasetResponse::fromEntity)
                .toList();
    }

    @Transactional(readOnly = true)
    public DatasetResponse getDatasetById(UUID id, UserPrincipal principal) {
        log.debug("Fetching dataset id '{}' for user '{}'", id, principal.getUsername());
        Dataset dataset = datasetRepository.findByIdAndUserId(id, principal.getId())
                .orElseThrow(() -> new EntityNotFoundException("Dataset not found with id: " + id));
        return DatasetResponse.fromEntity(dataset);
    }

    @Transactional
    public void deleteDataset(UUID id, UserPrincipal principal) {
        log.info("Deleting dataset id '{}' owned by user '{}'", id, principal.getUsername());
        Dataset dataset = datasetRepository.findByIdAndUserId(id, principal.getId())
                .orElseThrow(() -> new EntityNotFoundException("Dataset not found with id: " + id));

        // Clean up stored file on disk
        fileStorageService.deleteFile(dataset.getStorageKey());

        // Delete database record (cascading deletes sales_transactions and segmentation_runs)
        datasetRepository.delete(dataset);
    }
}
