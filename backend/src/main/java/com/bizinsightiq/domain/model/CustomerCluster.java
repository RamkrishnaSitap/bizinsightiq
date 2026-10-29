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
    name = "customer_clusters",
    uniqueConstraints = {
        @UniqueConstraint(name = "uq_run_customer", columnNames = {"segmentation_run_id", "customer_id"})
    },
    indexes = {
        @Index(name = "idx_customer_clusters_run_id", columnList = "segmentation_run_id"),
        @Index(name = "idx_customer_clusters_customer", columnList = "segmentation_run_id, customer_id")
    }
)
public class CustomerCluster {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id", updatable = false, nullable = false)
    private Long id;

    @NotNull
    @Column(name = "segmentation_run_id", nullable = false)
    private UUID segmentationRunId;

    @NotBlank
    @Size(max = 50)
    @Column(name = "customer_id", length = 50, nullable = false)
    private String customerId;

    @NotNull
    @Column(name = "cluster_id", nullable = false)
    private Integer clusterId;

    @NotNull
    @Min(0)
    @Column(name = "recency", nullable = false)
    private Integer recency;

    @NotNull
    @Min(1)
    @Column(name = "frequency", nullable = false)
    private Integer frequency;

    @NotNull
    @DecimalMin("0.00")
    @Digits(integer = 10, fraction = 2)
    @Column(name = "monetary_value", precision = 12, scale = 2, nullable = false)
    private BigDecimal monetaryValue;

    @NotNull
    @Digits(integer = 10, fraction = 2)
    @Column(name = "total_profit", precision = 12, scale = 2, nullable = false)
    private BigDecimal totalProfit;

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt;

    public CustomerCluster() {
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public UUID getSegmentationRunId() {
        return segmentationRunId;
    }

    public void setSegmentationRunId(UUID segmentationRunId) {
        this.segmentationRunId = segmentationRunId;
    }

    public String getCustomerId() {
        return customerId;
    }

    public void setCustomerId(String customerId) {
        this.customerId = customerId;
    }

    public Integer getClusterId() {
        return clusterId;
    }

    public void setClusterId(Integer clusterId) {
        this.clusterId = clusterId;
    }

    public Integer getRecency() {
        return recency;
    }

    public void setRecency(Integer recency) {
        this.recency = recency;
    }

    public Integer getFrequency() {
        return frequency;
    }

    public void setFrequency(Integer frequency) {
        this.frequency = frequency;
    }

    public BigDecimal getMonetaryValue() {
        return monetaryValue;
    }

    public void setMonetaryValue(BigDecimal monetaryValue) {
        this.monetaryValue = monetaryValue;
    }

    public BigDecimal getTotalProfit() {
        return totalProfit;
    }

    public void setTotalProfit(BigDecimal totalProfit) {
        this.totalProfit = totalProfit;
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
        if (!(o instanceof CustomerCluster that)) return false;
        return Objects.equals(id, that.id);
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(id);
    }
}
