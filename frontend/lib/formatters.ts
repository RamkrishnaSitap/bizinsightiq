/**
 * Utility functions for safely formatting dates, numbers, currencies, and analytical data.
 */

import { EDAResponse, EDATrendItem, EDACategoryItem, EDARegionalItem, EDADiscountItem } from './types';

export function formatDateTime(dateString?: string | null): string {
  if (!dateString) return '—';
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return '—';
  return date.toLocaleString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function formatDate(dateString?: string | null): string {
  if (!dateString) return '—';
  const date = new Date(dateString);
  if (isNaN(date.getTime())) return '—';
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

export function formatNumber(val?: number | null, decimals: number = 0): string {
  if (val === null || val === undefined || isNaN(val)) return '—';
  return val.toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

export function formatCurrency(val?: number | null, decimals: number = 2): string {
  if (val === null || val === undefined || isNaN(val)) return '—';
  return (
    '$' +
    val.toLocaleString(undefined, {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    })
  );
}

export function normalizeEdaData(data: any): EDAResponse {
  if (!data) return data;
  return {
    ...data,
    trends: (data.trends || []).map((t: any): EDATrendItem => {
      const period = String(t.Period || t.period || t.year_month || '');
      const sales = Number(t.Sales ?? t.sales ?? 0);
      const profit = Number(t.Profit ?? t.profit ?? 0);
      const quantity = Number(t.Quantity ?? t.quantity ?? 0);
      const orderCount = Number(t.OrderCount ?? t.order_count ?? t.orders ?? 0);
      const profitMargin = Number(t.ProfitMarginPct ?? t.profit_margin_pct ?? 0);
      return {
        ...t,
        period,
        year_month: period,
        Period: period,
        sales,
        Sales: sales,
        profit,
        Profit: profit,
        quantity,
        Quantity: quantity,
        order_count: orderCount,
        OrderCount: orderCount,
        profit_margin_pct: profitMargin,
        ProfitMarginPct: profitMargin,
      };
    }),
    category_performance: (data.category_performance || []).map((c: any): EDACategoryItem => {
      const category = String(c.Category || c.category || '');
      const sales = Number(c.Sales ?? c.sales ?? 0);
      const profit = Number(c.Profit ?? c.profit ?? 0);
      const quantity = Number(c.Quantity ?? c.quantity ?? 0);
      const orderCount = Number(c.OrderCount ?? c.order_count ?? 0);
      const avgDiscount = Number(c.AvgDiscountPct ?? c.avg_discount_pct ?? 0);
      const profitMargin = Number(c.ProfitMarginPct ?? c.profit_margin_pct ?? 0);
      return {
        ...c,
        category,
        Category: category,
        sales,
        Sales: sales,
        profit,
        Profit: profit,
        quantity,
        Quantity: quantity,
        order_count: orderCount,
        OrderCount: orderCount,
        avg_discount_pct: avgDiscount,
        AvgDiscountPct: avgDiscount,
        profit_margin_pct: profitMargin,
        ProfitMarginPct: profitMargin,
      };
    }),
    regional_performance: (data.regional_performance || []).map((r: any): EDARegionalItem => {
      const region = String(r.Region || r.region || '');
      const sales = Number(r.Sales ?? r.sales ?? 0);
      const profit = Number(r.Profit ?? r.profit ?? 0);
      const quantity = Number(r.Quantity ?? r.quantity ?? 0);
      const customers = Number(r.UniqueCustomers ?? r.customers ?? 0);
      const profitMargin = Number(r.ProfitMarginPct ?? r.profit_margin_pct ?? 0);
      return {
        ...r,
        region,
        Region: region,
        sales,
        Sales: sales,
        profit,
        Profit: profit,
        quantity,
        Quantity: quantity,
        customers,
        UniqueCustomers: customers,
        profit_margin_pct: profitMargin,
        ProfitMarginPct: profitMargin,
      };
    }),
    discount_analysis: (data.discount_analysis || []).map((d: any): EDADiscountItem => {
      const discountBracket = String(d.DiscountBracket || d.discount_bucket || '');
      const sales = Number(d.TotalSales ?? d.sales ?? 0);
      const profit = Number(d.TotalProfit ?? d.profit ?? 0);
      const profitMargin = Number(d.ProfitMarginPct ?? d.profit_margin ?? 0);
      const orderCount = Number(d.OrderCount ?? d.order_count ?? 0);
      return {
        ...d,
        discount_bucket: discountBracket,
        DiscountBracket: discountBracket,
        sales,
        TotalSales: sales,
        profit,
        TotalProfit: profit,
        profit_margin: profitMargin,
        ProfitMarginPct: profitMargin,
        order_count: orderCount,
        OrderCount: orderCount,
      };
    }),
  };
}
