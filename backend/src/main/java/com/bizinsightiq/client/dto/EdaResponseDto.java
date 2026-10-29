package com.bizinsightiq.client.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;
import java.util.Map;

/**
 * Data transfer object mapping FastAPI's EDAResponse schema.
 */
public record EdaResponseDto(
        @JsonProperty("kpis") BusinessKpisDto kpis,
        @JsonProperty("trends") List<Map<String, Object>> trends,
        @JsonProperty("category_performance") List<Map<String, Object>> categoryPerformance,
        @JsonProperty("regional_performance") List<Map<String, Object>> regionalPerformance,
        @JsonProperty("discount_analysis") List<Map<String, Object>> discountAnalysis,
        @JsonProperty("correlation_matrix") Map<String, Map<String, Double>> correlationMatrix
) {
    public record BusinessKpisDto(
            @JsonProperty("total_sales") Double totalSales,
            @JsonProperty("total_profit") Double totalProfit,
            @JsonProperty("total_units") Integer totalUnits,
            @JsonProperty("unique_customers") Integer uniqueCustomers,
            @JsonProperty("total_orders") Integer totalOrders,
            @JsonProperty("profit_margin_pct") Double profitMarginPct,
            @JsonProperty("avg_order_value") Double avgOrderValue,
            @JsonProperty("avg_discount_pct") Double avgDiscountPct
    ) {}
}
