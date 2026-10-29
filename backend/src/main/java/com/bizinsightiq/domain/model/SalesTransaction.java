package com.bizinsightiq.domain.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import org.hibernate.annotations.CreationTimestamp;

import java.math.BigDecimal;
import java.time.Instant;
import java.time.LocalDate;
import java.util.Objects;
import java.util.UUID;

@Entity
@Table(
    name = "sales_transactions",
    indexes = {
        @Index(name = "idx_sales_transactions_dataset_id", columnList = "dataset_id"),
        @Index(name = "idx_sales_transactions_dataset_date", columnList = "dataset_id, order_date"),
        @Index(name = "idx_sales_transactions_dataset_category", columnList = "dataset_id, category"),
        @Index(name = "idx_sales_transactions_dataset_region", columnList = "dataset_id, region"),
        @Index(name = "idx_sales_transactions_customer", columnList = "dataset_id, customer_id")
    }
)
public class SalesTransaction {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id", updatable = false, nullable = false)
    private Long id;

    @NotNull
    @Column(name = "dataset_id", nullable = false)
    private UUID datasetId;

    @Size(max = 50)
    @Column(name = "order_id", length = 50)
    private String orderId;

    @NotBlank
    @Size(max = 50)
    @Column(name = "customer_id", length = 50, nullable = false)
    private String customerId;

    @NotNull
    @Column(name = "order_date", nullable = false)
    private LocalDate orderDate;

    @NotBlank
    @Size(max = 50)
    @Column(name = "category", length = 50, nullable = false)
    private String category;

    @NotBlank
    @Size(max = 50)
    @Column(name = "region", length = 50, nullable = false)
    private String region;

    @NotNull
    @Min(0)
    @Column(name = "quantity", nullable = false)
    private Integer quantity;

    @Digits(integer = 10, fraction = 2)
    @Column(name = "unit_price", precision = 12, scale = 2)
    private BigDecimal unitPrice;

    @NotNull
    @DecimalMin("0.0000")
    @DecimalMax("1.0000")
    @Digits(integer = 1, fraction = 4)
    @Column(name = "discount", precision = 5, scale = 4, nullable = false)
    private BigDecimal discount;

    @NotNull
    @DecimalMin("0.00")
    @Digits(integer = 10, fraction = 2)
    @Column(name = "sales", precision = 12, scale = 2, nullable = false)
    private BigDecimal sales;

    @NotNull
    @Digits(integer = 10, fraction = 2)
    @Column(name = "profit", precision = 12, scale = 2, nullable = false)
    private BigDecimal profit;

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt;

    public SalesTransaction() {
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public UUID getDatasetId() {
        return datasetId;
    }

    public void setDatasetId(UUID datasetId) {
        this.datasetId = datasetId;
    }

    public String getOrderId() {
        return orderId;
    }

    public void setOrderId(String orderId) {
        this.orderId = orderId;
    }

    public String getCustomerId() {
        return customerId;
    }

    public void setCustomerId(String customerId) {
        this.customerId = customerId;
    }

    public LocalDate getOrderDate() {
        return orderDate;
    }

    public void setOrderDate(LocalDate orderDate) {
        this.orderDate = orderDate;
    }

    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
    }

    public String getRegion() {
        return region;
    }

    public void setRegion(String region) {
        this.region = region;
    }

    public Integer getQuantity() {
        return quantity;
    }

    public void setQuantity(Integer quantity) {
        this.quantity = quantity;
    }

    public BigDecimal getUnitPrice() {
        return unitPrice;
    }

    public void setUnitPrice(BigDecimal unitPrice) {
        this.unitPrice = unitPrice;
    }

    public BigDecimal getDiscount() {
        return discount;
    }

    public void setDiscount(BigDecimal discount) {
        this.discount = discount;
    }

    public BigDecimal getSales() {
        return sales;
    }

    public void setSales(BigDecimal sales) {
        this.sales = sales;
    }

    public BigDecimal getProfit() {
        return profit;
    }

    public void setProfit(BigDecimal profit) {
        this.profit = profit;
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
        if (!(o instanceof SalesTransaction that)) return false;
        return Objects.equals(id, that.id);
    }

    @Override
    public int hashCode() {
        return Objects.hashCode(id);
    }
}
