package com.bizinsightiq.domain.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import org.hibernate.annotations.CreationTimestamp;

import java.time.Instant;
import java.util.Objects;
import java.util.UUID;

@Entity
@Table(
    name = "datasets",
    indexes = {
        @Index(name = "idx_datasets_user_id", columnList = "user_id")
    }
)
public class Dataset {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(name = "id", updatable = false, nullable = false)
    private UUID id;

    @NotNull
    @Column(name = "user_id", nullable = false)
    private UUID userId;

    @NotBlank
    @Size(max = 150)
    @Column(name = "name", length = 150, nullable = false)
    private String name;

    @NotBlank
    @Size(max = 255)
    @Column(name = "original_filename", length = 255, nullable = false)
    private String originalFilename;

    @NotBlank
    @Size(max = 500)
    @Column(name = "storage_key", length = 500, nullable = false)
    private String storageKey;

    @NotBlank
    @Size(max = 30)
    @Column(name = "status", length = 30, nullable = false)
    private String status = "PENDING";

    @Min(0)
    @Column(name = "total_rows", nullable = false)
    private Integer totalRows = 0;

    @Min(0)
    @Column(name = "total_columns", nullable = false)
    private Integer totalColumns = 0;

    @NotNull
    @Column(name = "is_valid", nullable = false)
    private Boolean isValid = false;

    @CreationTimestamp
    @Column(name = "uploaded_at", nullable = false, updatable = false)
    private Instant uploadedAt;

    public Dataset() {
    }

    public Dataset(UUID userId, String name, String originalFilename, String storageKey) {
        this.userId = userId;
        this.name = name;
        this.originalFilename = originalFilename;
        this.storageKey = storageKey;
        this.status = "PENDING";
        this.totalRows = 0;
        this.totalColumns = 0;
        this.isValid = false;
    }

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public UUID getUserId() {
        return userId;
    }

    public void setUserId(UUID userId) {
        this.userId = userId;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getOriginalFilename() {
        return originalFilename;
    }

    public void setOriginalFilename(String originalFilename) {
        this.originalFilename = originalFilename;
    }

    public String getStorageKey() {
        return storageKey;
    }

    public void setStorageKey(String storageKey) {
        this.storageKey = storageKey;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public Integer getTotalRows() {
        return totalRows;
    }

    public void setTotalRows(Integer totalRows) {
        this.totalRows = totalRows;
    }

    public Integer getTotalColumns() {
        return totalColumns;
    }

    public void setTotalColumns(Integer totalColumns) {
        this.totalColumns = totalColumns;
    }

    public Boolean getIsValid() {
        return isValid;
    }

    public void setIsValid(Boolean isValid) {
        this.isValid = isValid;
    }

    public Instant getUploadedAt() {
        return uploadedAt;
    }

    public void setUploadedAt(Instant uploadedAt) {
        this.uploadedAt = uploadedAt;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Dataset dataset)) return false;
        return Objects.equals(id, dataset.id);
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(id);
    }
}
