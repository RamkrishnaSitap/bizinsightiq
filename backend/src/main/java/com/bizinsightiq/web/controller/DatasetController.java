package com.bizinsightiq.web.controller;

import com.bizinsightiq.security.UserPrincipal;
import com.bizinsightiq.service.DatasetIngestionService;
import com.bizinsightiq.service.DatasetService;
import com.bizinsightiq.web.dto.CreateDatasetRequest;
import com.bizinsightiq.web.dto.DatasetResponse;
import com.bizinsightiq.web.dto.UploadDatasetResponse;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/v1/datasets")
public class DatasetController {

    private final DatasetService datasetService;
    private final DatasetIngestionService ingestionService;

    public DatasetController(DatasetService datasetService, DatasetIngestionService ingestionService) {
        this.datasetService = datasetService;
        this.ingestionService = ingestionService;
    }

    @PostMapping(value = "/upload", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<UploadDatasetResponse> uploadDataset(
            @RequestParam("file") MultipartFile file,
            @RequestParam(value = "name", required = false) String name,
            @AuthenticationPrincipal UserPrincipal principal) {

        UploadDatasetResponse response = ingestionService.ingestCsvDataset(file, name, principal);

        if (response.isValid()) {
            return ResponseEntity.status(HttpStatus.CREATED).body(response);
        } else {
            return ResponseEntity.status(HttpStatus.UNPROCESSABLE_ENTITY).body(response);
        }
    }

    @PostMapping
    public ResponseEntity<DatasetResponse> createDataset(
            @Valid @RequestBody CreateDatasetRequest request,
            @AuthenticationPrincipal UserPrincipal principal) {

        DatasetResponse response = datasetService.createDataset(request, principal);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    @GetMapping
    public ResponseEntity<List<DatasetResponse>> listDatasets(
            @AuthenticationPrincipal UserPrincipal principal) {

        List<DatasetResponse> datasets = datasetService.listUserDatasets(principal);
        return ResponseEntity.ok(datasets);
    }

    @GetMapping("/{id}")
    public ResponseEntity<DatasetResponse> getDataset(
            @PathVariable UUID id,
            @AuthenticationPrincipal UserPrincipal principal) {

        DatasetResponse dataset = datasetService.getDatasetById(id, principal);
        return ResponseEntity.ok(dataset);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteDataset(
            @PathVariable UUID id,
            @AuthenticationPrincipal UserPrincipal principal) {

        datasetService.deleteDataset(id, principal);
        return ResponseEntity.noContent().build();
    }
}
