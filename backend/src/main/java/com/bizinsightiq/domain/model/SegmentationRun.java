package com.bizinsightiq.domain.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import org.hibernate.annotations.CreationTimestamp;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.Objects;
import java.util.UUID;

@Entity
@Table(
    name = "segmentation_runs",
    indexes = {
        @Index(name = "idx_segmentation_runs_dataset_id", columnList = "dataset_id")
    }
)
public class SegmentationRun {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    @Column(name = "id", updatable = false, nullable = false)
    private UUID id;

    @NotNull
    @Column(name = "dataset_id", nullable = false)
    private UUID datasetId;

    @NotNull
    @Min(2)
    @Max(10)
    @Column(name = "k_clusters", nullable = false)
    private Integer kClusters;

    @NotNull
    @Digits(integer = 2, fraction = 4)
    @Column(name = "silhouette_score", precision = 6, scale = 4, nullable = false)
    private BigDecimal silhouetteScore;

    @NotNull
    @Digits(integer = 10, fraction = 4)
    @Column(name = "inertia", precision = 14, scale = 4, nullable = false)
    private BigDecimal inertia;

    @NotBlank
    @Size(max = 50)
    @Column(name = "algorithm_version", length = 50, nullable = false)
    private String algorithmVersion = "KMeans-v1.0";

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt;

    public SegmentationRun() {
    }

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public UUID getDatasetId() {
        return datasetId;
    }

    public void setDatasetId(UUID datasetId) {
        this.datasetId = datasetId;
    }

    public Integer getkClusters() {
        return kClusters;
    }

    public void setkClusters(Integer kClusters) {
        this.kClusters = kClusters;
    }

    public BigDecimal getSilhouetteScore() {
        return silhouetteScore;
    }

    public void setSilhouetteScore(BigDecimal silhouetteScore) {
        this.silhouetteScore = silhouetteScore;
    }

    public BigDecimal getInertia() {
        return inertia;
    }

    public void setInertia(BigDecimal inertia) {
        this.inertia = inertia;
    }

    public String getAlgorithmVersion() {
        return algorithmVersion;
    }

    public void setAlgorithmVersion(String algorithmVersion) {
        this.algorithmVersion = algorithmVersion;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(Instant createdAt) {
        this.createdAt = createdAt;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof SegmentationRun that)) return false;
        return Objects.equals(id, that.id);
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(id);
    }
}
