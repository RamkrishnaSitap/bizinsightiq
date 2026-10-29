package com.bizinsightiq.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.*;
import java.util.UUID;

@Service
public class FileStorageService {

    private static final Logger log = LoggerFactory.getLogger(FileStorageService.class);

    private final Path uploadRoot;

    public FileStorageService(@Value("${app.storage.upload-dir:data/uploads}") String uploadDir) {
        this.uploadRoot = Paths.get(uploadDir).toAbsolutePath().normalize();
        try {
            Files.createDirectories(this.uploadRoot);
            log.info("Initialized file upload directory at: {}", this.uploadRoot);
        } catch (IOException ex) {
            throw new IllegalStateException("Could not initialize upload storage directory at " + this.uploadRoot, ex);
        }
    }

    public String storeFile(MultipartFile file, UUID datasetId) {
        if (file == null || file.isEmpty()) {
            throw new IllegalArgumentException("Cannot store an empty or missing file");
        }

        String originalFilename = StringUtils.cleanPath(file.getOriginalFilename() != null ? file.getOriginalFilename() : "upload.csv");
        if (!originalFilename.toLowerCase().endsWith(".csv")) {
            throw new IllegalArgumentException("Only CSV files (.csv) are accepted for ingestion");
        }

        // Enforce server-controlled storage filename based on Dataset UUID
        String storageFilename = datasetId.toString() + ".csv";
        Path destination = uploadRoot.resolve(storageFilename).normalize();

        // Enforce path traversal confinement
        if (!destination.startsWith(uploadRoot)) {
            log.error("SECURITY ALERT: Path traversal attempt detected for file: {}", originalFilename);
            throw new SecurityException("Cannot store file outside current storage directory");
        }

        try (InputStream inputStream = file.getInputStream()) {
            Files.copy(inputStream, destination, StandardCopyOption.REPLACE_EXISTING);
            log.debug("Successfully stored dataset file at: {}", destination);
            return "data/uploads/" + storageFilename;
        } catch (IOException ex) {
            throw new RuntimeException("Failed to store uploaded file: " + ex.getMessage(), ex);
        }
    }

    public byte[] readFileBytes(String storageKey) {
        Path filePath = resolveStoragePath(storageKey);
        try {
            return Files.readAllBytes(filePath);
        } catch (IOException ex) {
            throw new RuntimeException("Failed to read stored dataset file: " + ex.getMessage(), ex);
        }
    }

    public boolean deleteFile(String storageKey) {
        if (!StringUtils.hasText(storageKey)) {
            return false;
        }
        try {
            Path filePath = resolveStoragePath(storageKey);
            return Files.deleteIfExists(filePath);
        } catch (Exception ex) {
            log.warn("Could not delete stored file at '{}': {}", storageKey, ex.getMessage());
            return false;
        }
    }

    public Path resolveStoragePath(String storageKey) {
        // Handle both relative key and filename
        String filename = Paths.get(storageKey).getFileName().toString();
        Path resolved = uploadRoot.resolve(filename).normalize();
        if (!resolved.startsWith(uploadRoot)) {
            throw new SecurityException("Security violation: path traversal detected in storage key");
        }
        return resolved;
    }

    public Path getUploadRoot() {
        return uploadRoot;
    }
}
