'use client';

import React, { useEffect, useState, useCallback } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { useDataset } from '@/lib/dataset-context';
import { useCurrency } from '@/lib/currency-context';
import { analyticsApi } from '@/lib/api';
import { EDAResponse } from '@/lib/types';
import { normalizeEdaData } from '@/lib/formatters';
import AmountDisplay from '@/components/AmountDisplay';
import {
  DollarSign,
  IndianRupee,
  TrendingUp,
  Percent,
  ShoppingBag,
  Users,
  Tag,
  Loader2,
  AlertCircle,
  FileSpreadsheet,
} from 'lucide-react';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  LineChart,
  Line,
  ComposedChart,
  PieChart,
  Pie,
  Cell,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

const CATEGORY_COLORS = ['#4f46e5', '#06b6d4', '#10b981', '#f59e0b', '#ec4899'];
const REGION_COLORS = ['#4f46e5', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b'];

export default function EDAPage() {
  const { selectedDataset, selectedDatasetId } = useDataset();
  const {
    formatCurrency,
    formatCompact,
    symbol,
    currency,
    currencyLabel,
    getHoverDetails,
    rateMode,
    exchangeRate,
  } = useCurrency();
  const [edaData, setEdaData] = useState<EDAResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // User-selectable interactive chart types
  const [trendChartType, setTrendChartType] = useState<'area' | 'line' | 'bar' | 'composed'>('area');
  const [categoryChartType, setCategoryChartType] = useState<'bar' | 'donut' | 'line'>('bar');
  const [regionalChartType, setRegionalChartType] = useState<'bar' | 'stacked' | 'pie' | 'radar'>('bar');

  // Hover states for interactive inspection banner
  const [hoveredTrend, setHoveredTrend] = useState<any>(null);
  const [hoveredCategory, setHoveredCategory] = useState<any>(null);
  const [hoveredRegion, setHoveredRegion] = useState<any>(null);

  // Compute proper Y-axis domain so Sales line and Area are NEVER cut off
  const maxTrendVal = Math.max(
    ...(edaData?.trends || []).map((t) =>
      Math.max(Number(t.sales || t.Sales || 0), Number(t.profit || t.Profit || 0))
    ),
    1000
  );
  const trendYDomain = [0, Math.ceil(maxTrendVal * 1.15)];

  // Live Inspection Info Strip (0% chart obstruction)
  const InspectionBanner = ({
    data,
    defaultSummary,
  }: {
    data: any;
    defaultSummary: React.ReactNode;
  }) => {
    if (!data) {
      return (
        <div className="bg-slate-50 border border-slate-200/80 rounded-xl px-3.5 py-2 text-xs text-slate-600 flex items-center justify-between mb-3 min-h-[42px] transition-colors">
          <div className="flex items-center gap-2">
            <span>{defaultSummary}</span>
          </div>
          <span className="text-[10px] text-slate-400 font-medium hidden sm:inline">
            Hover any data point for in-words detail
          </span>
        </div>
      );
    }

    const title = data.category || data.region || data.period || 'Selected';
    const sales = Number(data.sales || data.Sales || 0);
    const profit = Number(data.profit || data.Profit || 0);
    const margin = data.profit_margin_pct != null
      ? Number(data.profit_margin_pct)
      : (sales > 0 ? (profit / sales) * 100 : null);
    const salesDetails = getHoverDetails(sales);

    return (
      <div className="bg-slate-900 text-white border border-slate-800 rounded-xl px-3.5 py-2 text-xs shadow-xs mb-3 min-h-[42px] flex flex-wrap items-center justify-between gap-2 transition-all animate-in fade-in duration-100">
        <div className="flex flex-wrap items-center gap-2">
          <span className="px-2 py-0.5 rounded-md text-xs font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
            📍 {title}
          </span>
          {margin != null && (
            <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-md ${margin >= 0 ? 'bg-emerald-950/80 text-emerald-400 border border-emerald-800/60' : 'bg-rose-950/80 text-rose-400 border border-rose-800/60'}`}>
              {margin.toFixed(1)}% margin
            </span>
          )}
          <span className="text-slate-200 font-medium">
            Sales: <strong className="text-white font-mono">{formatCurrency(sales)}</strong>
            <span className="text-emerald-400 text-[11px] ml-1.5 font-normal">({salesDetails.inWords})</span>
          </span>
        </div>

        <div className="flex items-center gap-2.5 text-slate-300">
          <span>Profit: <strong className={`font-mono ${profit >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>{formatCurrency(profit)}</strong></span>
          {salesDetails.alternateText && (
            <span className="text-[11px] text-slate-400 border-l border-slate-800 pl-2">
              {salesDetails.alternateText}
            </span>
          )}
        </div>
      </div>
    );
  };

  // Compact, non-blocking chart tooltip (height ~55px, never obstructs adjacent bars)
  const CustomChartTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload || !payload.length) return null;

    const firstItem = payload[0];
    const dataItem = firstItem?.payload;
    const categoryOrRegion = dataItem?.category || dataItem?.region || label;

    return (
      <div className="bg-slate-950/95 backdrop-blur-md text-white px-3 py-2 rounded-xl shadow-xl border border-slate-700/80 text-xs pointer-events-none z-50 text-left min-w-[180px] max-w-[230px]">
        {categoryOrRegion && (
          <div className="font-bold text-slate-200 border-b border-slate-800 pb-1 mb-1.5 flex items-center justify-between gap-2">
            <span className="text-xs font-semibold truncate">{categoryOrRegion}</span>
            {dataItem?.profit_margin_pct != null && (
              <span className={`text-[10px] font-semibold px-1.5 py-0.2 rounded-full shrink-0 ${Number(dataItem.profit_margin_pct) >= 0 ? 'text-emerald-400 bg-emerald-950/80 border border-emerald-800/60' : 'text-rose-400 bg-rose-950/80 border border-rose-800/60'}`}>
                {Number(dataItem.profit_margin_pct).toFixed(1)}%
              </span>
            )}
          </div>
        )}
        <div className="space-y-1">
          {payload.map((item: any, idx: number) => {
            const num = Number(item.value);
            const seriesColor = item.color || item.payload?.fill || item.stroke || '#6366f1';
            const rawName = item.name || item.dataKey;
            const isSelfNamed = rawName === categoryOrRegion || !rawName;
            const seriesName = isSelfNamed
              ? (item.dataKey === 'profit' ? 'Profit' : 'Sales')
              : String(rawName).replace(/ \([^)]*\)/, '');

            return (
              <div key={idx} className="flex items-center justify-between gap-3 text-[11px]">
                <div className="flex items-center gap-1.5 font-medium text-slate-300 truncate">
                  <span
                    className="w-2 h-2 rounded-full shrink-0"
                    style={{ backgroundColor: seriesColor }}
                  />
                  <span className="truncate">{seriesName}:</span>
                </div>
                <span className="font-bold text-white font-mono shrink-0">
                  {formatCurrency(num)}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const fetchEda = useCallback(async (datasetId: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await analyticsApi.getEda(datasetId);
      setEdaData(normalizeEdaData(data));
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to compute EDA');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (selectedDatasetId) {
      fetchEda(selectedDatasetId);
    } else {
      setEdaData(null);
    }
  }, [selectedDatasetId, fetchEda]);

  if (!selectedDatasetId) {
    return (
      <DashboardLayout title="Exploratory Data Analysis (EDA)">
        <div className="bg-white rounded-2xl border border-slate-200/80 p-12 text-center max-w-xl mx-auto mt-12 shadow-xs">
          <FileSpreadsheet className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-800">No Dataset Selected</h3>
          <p className="text-xs text-slate-500 mt-1">
            Please select an active dataset from the sidebar or upload a new CSV on the Datasets page to compute EDA metrics.
          </p>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title={`EDA — ${selectedDataset?.name || 'Dataset Analytics'}`}>
      <div className="space-y-8 max-w-7xl mx-auto">
        {/* Loading Spinner */}
        {isLoading && (
          <div className="bg-white rounded-2xl p-12 text-center border border-slate-200/80 shadow-xs flex flex-col items-center gap-3">
            <Loader2 className="w-8 h-8 text-indigo-600 animate-spin" />
            <p className="text-sm font-semibold text-slate-700">Computing Business KPIs & Trends via FastAPI...</p>
            <p className="text-xs text-slate-400">Aggregating historical order transactions</p>
          </div>
        )}

        {/* Error Alert */}
        {error && !isLoading && (
          <div className="bg-rose-50 border border-rose-200 p-4 rounded-xl flex items-start gap-3 text-xs text-rose-800">
            <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
            <div>
              <p className="font-bold">Failed to load Exploratory Data Analysis</p>
              <p className="mt-0.5">{error}</p>
              <button
                onClick={() => fetchEda(selectedDatasetId)}
                className="mt-2 text-indigo-600 font-semibold hover:underline"
              >
                Retry Calculation
              </button>
            </div>
          </div>
        )}

        {/* Analytics Content */}
        {edaData && !isLoading && (
          <>
            {/* KPI Cards Grid */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs">
                <div className="flex items-center justify-between text-slate-500 mb-2">
                  <span className="text-[11px] font-semibold uppercase tracking-wider">Total Sales</span>
                  {currency === 'INR' ? (
                    <IndianRupee className="w-4 h-4 text-indigo-600" />
                  ) : (
                    <DollarSign className="w-4 h-4 text-indigo-600" />
                  )}
                </div>
                <div className="text-lg font-bold text-slate-900">
                  <AmountDisplay amount={edaData.kpis.total_sales} />
                </div>
              </div>

              <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs">
                <div className="flex items-center justify-between text-slate-500 mb-2">
                  <span className="text-[11px] font-semibold uppercase tracking-wider">Total Profit</span>
                  <TrendingUp className={`w-4 h-4 ${edaData.kpis.total_profit >= 0 ? 'text-emerald-600' : 'text-rose-600'}`} />
                </div>
                <div className={`text-lg font-bold ${edaData.kpis.total_profit >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                  <AmountDisplay amount={edaData.kpis.total_profit} />
                </div>
              </div>

              <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs">
                <div className="flex items-center justify-between text-slate-500 mb-2">
                  <span className="text-[11px] font-semibold uppercase tracking-wider">Profit Margin</span>
                  <Percent className="w-4 h-4 text-blue-600" />
                </div>
                <h4 className="text-lg font-bold text-slate-900">
                  {edaData.kpis.profit_margin_pct != null ? `${Number(edaData.kpis.profit_margin_pct).toFixed(1)}%` : '—'}
                </h4>
              </div>

              <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs">
                <div className="flex items-center justify-between text-slate-500 mb-2">
                  <span className="text-[11px] font-semibold uppercase tracking-wider">Total Orders</span>
                  <ShoppingBag className="w-4 h-4 text-purple-600" />
                </div>
                <h4 className="text-lg font-bold text-slate-900">
                  {edaData.kpis.total_orders?.toLocaleString() ?? '—'}
                </h4>
              </div>

              <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs">
                <div className="flex items-center justify-between text-slate-500 mb-2">
                  <span className="text-[11px] font-semibold uppercase tracking-wider">Unique Customers</span>
                  <Users className="w-4 h-4 text-amber-600" />
                </div>
                <h4 className="text-lg font-bold text-slate-900">
                  {edaData.kpis.unique_customers?.toLocaleString() ?? '—'}
                </h4>
              </div>

              <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs">
                <div className="flex items-center justify-between text-slate-500 mb-2">
                  <span className="text-[11px] font-semibold uppercase tracking-wider">Avg Discount</span>
                  <Tag className="w-4 h-4 text-rose-500" />
                </div>
                <h4 className="text-lg font-bold text-slate-900">
                  {edaData.kpis.avg_discount_pct != null ? `${Number(edaData.kpis.avg_discount_pct).toFixed(1)}%` : '—'}
                </h4>
              </div>
            </div>

            {/* Monthly Trend Chart */}
            <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3">
                <div>
                  <h3 className="text-base font-bold text-slate-900">Monthly Sales & Profit Performance Trend</h3>
                  <p className="text-xs text-slate-500">Chronological trajectory across order dates</p>
                </div>
                {/* User Chart Type Selector */}
                <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200/80 text-xs gap-1 self-start sm:self-auto">
                  <button
                    type="button"
                    onClick={() => setTrendChartType('area')}
                    className={`px-2.5 py-1 rounded-lg font-bold transition-all cursor-pointer flex items-center gap-1 ${
                      trendChartType === 'area'
                        ? 'bg-indigo-600 text-white shadow-xs'
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                    title="Area Chart (Smooth gradient volume)"
                  >
                    <span>📈 Area</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setTrendChartType('line')}
                    className={`px-2.5 py-1 rounded-lg font-bold transition-all cursor-pointer flex items-center gap-1 ${
                      trendChartType === 'line'
                        ? 'bg-indigo-600 text-white shadow-xs'
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                    title="Line Chart (Crisp trajectory multi-lines)"
                  >
                    <span>📉 Line</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setTrendChartType('bar')}
                    className={`px-2.5 py-1 rounded-lg font-bold transition-all cursor-pointer flex items-center gap-1 ${
                      trendChartType === 'bar'
                        ? 'bg-indigo-600 text-white shadow-xs'
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                    title="Bar Chart (Discrete monthly columns)"
                  >
                    <span>📊 Bar</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setTrendChartType('composed')}
                    className={`px-2.5 py-1 rounded-lg font-bold transition-all cursor-pointer flex items-center gap-1 ${
                      trendChartType === 'composed'
                        ? 'bg-indigo-600 text-white shadow-xs'
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                    title="Mixed Composed Chart (Sales Bars + Profit Line)"
                  >
                    <span>🔀 Mixed</span>
                  </button>
                </div>
              </div>

              {/* Dynamic Live Inspection Strip */}
              <InspectionBanner
                data={hoveredTrend}
                defaultSummary={
                  <span className="flex items-center gap-1.5 font-medium">
                    <span className="text-sm">📈</span>
                    <span>
                      <strong className="text-slate-800">24-Month Trajectory:</strong> Historical sales volume & profit trends across consecutive billing periods.
                    </span>
                  </span>
                }
              />

              <div className="w-full" style={{ height: 280, minHeight: 280 }}>
                <ResponsiveContainer width="100%" height={280}>
                  {trendChartType === 'area' ? (
                    <AreaChart
                      data={edaData.trends}
                      margin={{ top: 10, right: 20, left: 10, bottom: 0 }}
                      onMouseMove={(e: any) => {
                        if (e?.activePayload?.[0]?.payload) setHoveredTrend(e.activePayload[0].payload);
                      }}
                      onMouseLeave={() => setHoveredTrend(null)}
                    >
                      <defs>
                        <linearGradient id="colorSales" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#4f46e5" stopOpacity={0.4} />
                          <stop offset="95%" stopColor="#4f46e5" stopOpacity={0.0} />
                        </linearGradient>
                        <linearGradient id="colorProfit" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                          <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                      <XAxis dataKey="period" tick={{ fontSize: 11 }} />
                      <YAxis domain={trendYDomain} tick={{ fontSize: 11 }} tickFormatter={(val: number) => formatCompact(val)} />
                      <Tooltip content={<CustomChartTooltip />} wrapperStyle={{ zIndex: 1000, pointerEvents: 'none' }} />
                      <Legend wrapperStyle={{ fontSize: '12px' }} />
                      <Area type="monotone" dataKey="sales" name={currencyLabel('Sales')} stroke="#4f46e5" fillOpacity={1} fill="url(#colorSales)" strokeWidth={2} />
                      <Area type="monotone" dataKey="profit" name={currencyLabel('Profit')} stroke="#10b981" fillOpacity={1} fill="url(#colorProfit)" strokeWidth={2} />
                    </AreaChart>
                  ) : trendChartType === 'line' ? (
                    <LineChart
                      data={edaData.trends}
                      margin={{ top: 10, right: 20, left: 10, bottom: 0 }}
                      onMouseMove={(e: any) => {
                        if (e?.activePayload?.[0]?.payload) setHoveredTrend(e.activePayload[0].payload);
                      }}
                      onMouseLeave={() => setHoveredTrend(null)}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                      <XAxis dataKey="period" tick={{ fontSize: 11 }} />
                      <YAxis domain={trendYDomain} tick={{ fontSize: 11 }} tickFormatter={(val: number) => formatCompact(val)} />
                      <Tooltip content={<CustomChartTooltip />} wrapperStyle={{ zIndex: 1000, pointerEvents: 'none' }} />
                      <Legend wrapperStyle={{ fontSize: '12px' }} />
                      <Line type="monotone" dataKey="sales" name={currencyLabel('Sales')} stroke="#4f46e5" strokeWidth={2.5} dot={{ r: 3 }} activeDot={{ r: 6 }} />
                      <Line type="monotone" dataKey="profit" name={currencyLabel('Profit')} stroke="#10b981" strokeWidth={2.5} dot={{ r: 3 }} activeDot={{ r: 6 }} />
                    </LineChart>
                  ) : trendChartType === 'bar' ? (
                    <BarChart
                      data={edaData.trends}
                      margin={{ top: 10, right: 20, left: 10, bottom: 0 }}
                      onMouseMove={(e: any) => {
                        if (e?.activePayload?.[0]?.payload) setHoveredTrend(e.activePayload[0].payload);
                      }}
                      onMouseLeave={() => setHoveredTrend(null)}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                      <XAxis dataKey="period" tick={{ fontSize: 11 }} />
                      <YAxis domain={trendYDomain} tick={{ fontSize: 11 }} tickFormatter={(val: number) => formatCompact(val)} />
                      <Tooltip content={<CustomChartTooltip />} wrapperStyle={{ zIndex: 1000, pointerEvents: 'none' }} />
                      <Legend wrapperStyle={{ fontSize: '12px' }} />
                      <Bar dataKey="sales" name={currencyLabel('Sales')} fill="#6366f1" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="profit" name={currencyLabel('Profit')} fill="#10b981" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  ) : (
                    <ComposedChart
                      data={edaData.trends}
                      margin={{ top: 10, right: 20, left: 10, bottom: 0 }}
                      onMouseMove={(e: any) => {
                        if (e?.activePayload?.[0]?.payload) setHoveredTrend(e.activePayload[0].payload);
                      }}
                      onMouseLeave={() => setHoveredTrend(null)}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                      <XAxis dataKey="period" tick={{ fontSize: 11 }} />
                      <YAxis domain={trendYDomain} tick={{ fontSize: 11 }} tickFormatter={(val: number) => formatCompact(val)} />
                      <Tooltip content={<CustomChartTooltip />} wrapperStyle={{ zIndex: 1000, pointerEvents: 'none' }} />
                      <Legend wrapperStyle={{ fontSize: '12px' }} />
                      <Bar dataKey="sales" name={currencyLabel('Sales')} fill="#6366f1" fillOpacity={0.8} radius={[4, 4, 0, 0]} />
                      <Line type="monotone" dataKey="profit" name={currencyLabel('Profit')} stroke="#10b981" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 7 }} />
                    </ComposedChart>
                  )}
                </ResponsiveContainer>
              </div>
            </div>

            {/* Category & Regional Distribution */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Category Breakdown */}
              <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
                  <div>
                    <h3 className="text-base font-bold text-slate-900">Performance by Product Category</h3>
                    <p className="text-xs text-slate-500">Comparative revenue contribution</p>
                  </div>
                  {/* Category Chart Type Switcher */}
                  <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200/80 text-xs gap-1 self-start sm:self-auto">
                    <button
                      type="button"
                      onClick={() => setCategoryChartType('bar')}
                      className={`px-2 py-1 rounded-lg font-bold transition-all cursor-pointer ${
                        categoryChartType === 'bar'
                          ? 'bg-indigo-600 text-white shadow-xs'
                          : 'text-slate-600 hover:text-slate-900'
                      }`}
                      title="Grouped Bar Chart"
                    >
                      <span>📊 Bar</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => setCategoryChartType('donut')}
                      className={`px-2 py-1 rounded-lg font-bold transition-all cursor-pointer ${
                        categoryChartType === 'donut'
                          ? 'bg-indigo-600 text-white shadow-xs'
                          : 'text-slate-600 hover:text-slate-900'
                      }`}
                      title="Donut Distribution Chart"
                    >
                      <span>🍩 Donut</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => setCategoryChartType('line')}
                      className={`px-2 py-1 rounded-lg font-bold transition-all cursor-pointer ${
                        categoryChartType === 'line'
                          ? 'bg-indigo-600 text-white shadow-xs'
                          : 'text-slate-600 hover:text-slate-900'
                      }`}
                      title="Comparative Line Chart"
                    >
                      <span>📉 Line</span>
                    </button>
                  </div>
                </div>

                {/* Dynamic Live Inspection Strip */}
                <InspectionBanner
                  data={hoveredCategory}
                  defaultSummary={
                    <span className="flex items-center gap-1.5 font-medium">
                      <span className="text-sm">🏆</span>
                      <span>
                        <strong className="text-slate-800">Category Breakdown:</strong> Technology, Furniture, and Office Supplies comparative revenue share.
                      </span>
                    </span>
                  }
                />

                <div className="w-full" style={{ height: 260, minHeight: 260 }}>
                  <ResponsiveContainer width="100%" height={260}>
                    {categoryChartType === 'bar' ? (
                      <BarChart
                        data={edaData.category_performance}
                        margin={{ top: 10, right: 10, left: 10, bottom: 0 }}
                        onMouseMove={(e: any) => {
                          if (e?.activePayload?.[0]?.payload) setHoveredCategory(e.activePayload[0].payload);
                        }}
                        onMouseLeave={() => setHoveredCategory(null)}
                      >
                        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                        <XAxis dataKey="category" tick={{ fontSize: 11 }} />
                        <YAxis tick={{ fontSize: 11 }} tickFormatter={(val: number) => formatCompact(val)} />
                        <Tooltip content={<CustomChartTooltip />} wrapperStyle={{ zIndex: 1000, pointerEvents: 'none' }} />
                        <Legend wrapperStyle={{ fontSize: '12px' }} />
                        <Bar dataKey="sales" name={currencyLabel('Sales')} fill="#6366f1" radius={[6, 6, 0, 0]} />
                        <Bar dataKey="profit" name={currencyLabel('Profit')} fill="#10b981" radius={[6, 6, 0, 0]} />
                      </BarChart>
                    ) : categoryChartType === 'donut' ? (
                      <PieChart margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
                        <Tooltip content={<CustomChartTooltip />} wrapperStyle={{ zIndex: 1000, pointerEvents: 'none' }} />
                        <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                        <Pie
                          data={edaData.category_performance}
                          dataKey="sales"
                          nameKey="category"
                          cx="50%"
                          cy="48%"
                          innerRadius={50}
                          outerRadius={78}
                          paddingAngle={4}
                          label={({ percent }: any) => (percent > 0.05 ? `${(percent * 100).toFixed(0)}%` : '')}
                          labelLine={false}
                          onMouseEnter={(entry: any) => setHoveredCategory(entry)}
                          onMouseLeave={() => setHoveredCategory(null)}
                        >
                          {edaData.category_performance.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={CATEGORY_COLORS[index % CATEGORY_COLORS.length]} />
                          ))}
                        </Pie>
                      </PieChart>
                    ) : (
                      <LineChart
                        data={edaData.category_performance}
                        margin={{ top: 10, right: 10, left: 10, bottom: 0 }}
                        onMouseMove={(e: any) => {
                          if (e?.activePayload?.[0]?.payload) setHoveredCategory(e.activePayload[0].payload);
                        }}
                        onMouseLeave={() => setHoveredCategory(null)}
                      >
                        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                        <XAxis dataKey="category" tick={{ fontSize: 11 }} />
                        <YAxis tick={{ fontSize: 11 }} tickFormatter={(val: number) => formatCompact(val)} />
                        <Tooltip content={<CustomChartTooltip />} wrapperStyle={{ zIndex: 1000, pointerEvents: 'none' }} />
                        <Legend wrapperStyle={{ fontSize: '12px' }} />
                        <Line type="monotone" dataKey="sales" name={currencyLabel('Sales')} stroke="#6366f1" strokeWidth={2.5} dot={{ r: 4 }} />
                        <Line type="monotone" dataKey="profit" name={currencyLabel('Profit')} stroke="#10b981" strokeWidth={2.5} dot={{ r: 4 }} />
                      </LineChart>
                    )}
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Regional Breakdown */}
              <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
                  <div>
                    <h3 className="text-base font-bold text-slate-900">Sales by Geographic Region</h3>
                    <p className="text-xs text-slate-500">Territory performance distribution</p>
                  </div>
                  {/* Regional Chart Type Switcher */}
                  <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200/80 text-xs gap-1 self-start sm:self-auto">
                    <button
                      type="button"
                      onClick={() => setRegionalChartType('bar')}
                      className={`px-2 py-1 rounded-lg font-bold transition-all cursor-pointer ${
                        regionalChartType === 'bar'
                          ? 'bg-indigo-600 text-white shadow-xs'
                          : 'text-slate-600 hover:text-slate-900'
                      }`}
                      title="Grouped Bar Chart"
                    >
                      <span>📊 Bar</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => setRegionalChartType('stacked')}
                      className={`px-2 py-1 rounded-lg font-bold transition-all cursor-pointer ${
                        regionalChartType === 'stacked'
                          ? 'bg-indigo-600 text-white shadow-xs'
                          : 'text-slate-600 hover:text-slate-900'
                      }`}
                      title="Stacked Revenue Breakdown"
                    >
                      <span>🥞 Stacked</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => setRegionalChartType('pie')}
                      className={`px-2 py-1 rounded-lg font-bold transition-all cursor-pointer ${
                        regionalChartType === 'pie'
                          ? 'bg-indigo-600 text-white shadow-xs'
                          : 'text-slate-600 hover:text-slate-900'
                      }`}
                      title="Territory Pie Chart"
                    >
                      <span>🥧 Pie</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => setRegionalChartType('radar')}
                      className={`px-2 py-1 rounded-lg font-bold transition-all cursor-pointer ${
                        regionalChartType === 'radar'
                          ? 'bg-indigo-600 text-white shadow-xs'
                          : 'text-slate-600 hover:text-slate-900'
                      }`}
                      title="Multivariate Radar Chart"
                    >
                      <span>🎯 Radar</span>
                    </button>
                  </div>
                </div>

                {/* Dynamic Live Inspection Strip */}
                <InspectionBanner
                  data={hoveredRegion}
                  defaultSummary={
                    <span className="flex items-center gap-1.5 font-medium">
                      <span className="text-sm">🗺️</span>
                      <span>
                        <strong className="text-slate-800">Geographic Distribution:</strong> Performance across North, West, East, and South territories.
                      </span>
                    </span>
                  }
                />

                <div className="w-full" style={{ height: 260, minHeight: 260 }}>
                  <ResponsiveContainer width="100%" height={260}>
                    {regionalChartType === 'bar' ? (
                      <BarChart
                        data={edaData.regional_performance}
                        margin={{ top: 10, right: 10, left: 10, bottom: 0 }}
                        onMouseMove={(e: any) => {
                          if (e?.activePayload?.[0]?.payload) setHoveredRegion(e.activePayload[0].payload);
                        }}
                        onMouseLeave={() => setHoveredRegion(null)}
                      >
                        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                        <XAxis dataKey="region" tick={{ fontSize: 11 }} />
                        <YAxis tick={{ fontSize: 11 }} tickFormatter={(val: number) => formatCompact(val)} />
                        <Tooltip content={<CustomChartTooltip />} wrapperStyle={{ zIndex: 1000, pointerEvents: 'none' }} />
                        <Legend wrapperStyle={{ fontSize: '12px' }} />
                        <Bar dataKey="sales" name={currencyLabel('Sales')} fill="#8b5cf6" radius={[6, 6, 0, 0]} />
                        <Bar dataKey="profit" name={currencyLabel('Profit')} fill="#06b6d4" radius={[6, 6, 0, 0]} />
                      </BarChart>
                    ) : regionalChartType === 'stacked' ? (
                      <BarChart
                        data={edaData.regional_performance}
                        margin={{ top: 10, right: 10, left: 10, bottom: 0 }}
                        onMouseMove={(e: any) => {
                          if (e?.activePayload?.[0]?.payload) setHoveredRegion(e.activePayload[0].payload);
                        }}
                        onMouseLeave={() => setHoveredRegion(null)}
                      >
                        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                        <XAxis dataKey="region" tick={{ fontSize: 11 }} />
                        <YAxis tick={{ fontSize: 11 }} tickFormatter={(val: number) => formatCompact(val)} />
                        <Tooltip content={<CustomChartTooltip />} wrapperStyle={{ zIndex: 1000, pointerEvents: 'none' }} />
                        <Legend wrapperStyle={{ fontSize: '12px' }} />
                        <Bar dataKey="sales" stackId="stack" name={currencyLabel('Sales')} fill="#8b5cf6" />
                        <Bar dataKey="profit" stackId="stack" name={currencyLabel('Profit')} fill="#06b6d4" radius={[6, 6, 0, 0]} />
                      </BarChart>
                    ) : regionalChartType === 'pie' ? (
                      <PieChart margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
                        <Tooltip content={<CustomChartTooltip />} wrapperStyle={{ zIndex: 1000, pointerEvents: 'none' }} />
                        <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                        <Pie
                          data={edaData.regional_performance}
                          dataKey="sales"
                          nameKey="region"
                          cx="50%"
                          cy="48%"
                          outerRadius={78}
                          label={({ percent }: any) => (percent > 0.05 ? `${(percent * 100).toFixed(0)}%` : '')}
                          labelLine={false}
                          onMouseEnter={(entry: any) => setHoveredRegion(entry)}
                          onMouseLeave={() => setHoveredRegion(null)}
                        >
                          {edaData.regional_performance.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={REGION_COLORS[index % REGION_COLORS.length]} />
                          ))}
                        </Pie>
                      </PieChart>
                    ) : (
                      <RadarChart
                        data={edaData.regional_performance}
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        onMouseMove={(e: any) => {
                          if (e?.activePayload?.[0]?.payload) setHoveredRegion(e.activePayload[0].payload);
                        }}
                        onMouseLeave={() => setHoveredRegion(null)}
                      >
                        <PolarGrid stroke="#e2e8f0" />
                        <PolarAngleAxis dataKey="region" tick={{ fontSize: 11 }} />
                        <PolarRadiusAxis tick={{ fontSize: 10 }} tickFormatter={(val: number) => formatCompact(val)} />
                        <Tooltip content={<CustomChartTooltip />} wrapperStyle={{ zIndex: 1000, pointerEvents: 'none' }} />
                        <Legend wrapperStyle={{ fontSize: '12px' }} />
                        <Radar name={currencyLabel('Sales')} dataKey="sales" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.4} />
                        <Radar name={currencyLabel('Profit')} dataKey="profit" stroke="#06b6d4" fill="#06b6d4" fillOpacity={0.4} />
                      </RadarChart>
                    )}
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            {/* Discount Elasticity Table */}
            <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
              <div className="p-6 border-b border-slate-200/80">
                <h3 className="text-base font-bold text-slate-900">Promotional Discount Elasticity Breakdown</h3>
                <p className="text-xs text-slate-500">Impact of promotional discounts on net profit margins</p>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 text-slate-600 font-semibold uppercase tracking-wider border-b border-slate-200">
                    <tr>
                      <th className="py-3 px-6">Discount Bracket</th>
                      <th className="py-3 px-6 text-right">Gross Sales ({symbol})</th>
                      <th className="py-3 px-6 text-right">Net Profit ({symbol})</th>
                      <th className="py-3 px-6 text-right">Profit Margin %</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {edaData.discount_analysis.map((row, idx) => (
                      <tr key={idx} className="hover:bg-slate-50/50">
                        <td className="py-3 px-6 font-semibold text-slate-800">{row.discount_bucket}</td>
                        <td className="py-3 px-6 text-right font-medium">
                          <AmountDisplay amount={row.sales} />
                        </td>
                        <td className={`py-3 px-6 text-right font-bold ${typeof row.profit === 'number' && row.profit < 0 ? 'text-rose-600' : 'text-slate-800'}`}>
                          <AmountDisplay amount={row.profit} />
                        </td>
                        <td className={`py-3 px-6 text-right font-bold ${typeof row.profit_margin === 'number' && row.profit_margin < 0 ? 'text-rose-600' : 'text-emerald-700'}`}>
                          {typeof row.profit_margin === 'number' ? `${row.profit_margin.toFixed(1)}%` : '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </div>
    </DashboardLayout>
  );
}
