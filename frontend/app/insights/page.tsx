'use client';

import React, { useState, useEffect, useCallback } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { useDataset } from '@/lib/dataset-context';
import { analyticsApi } from '@/lib/api';
import { InsightsResponse } from '@/lib/types';
import {
  Lightbulb,
  AlertTriangle,
  AlertCircle,
  Info,
  CheckCircle2,
  FileSpreadsheet,
  Loader2,
  ShieldAlert,
  ArrowRight,
  Filter,
} from 'lucide-react';

export default function InsightsPage() {
  const { selectedDataset, selectedDatasetId } = useDataset();

  const [severityFilter, setSeverityFilter] = useState<string>('');
  const [insightsData, setInsightsData] = useState<InsightsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchInsights = useCallback(async (datasetId: string, severity?: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await analyticsApi.getInsights(datasetId, {
        severity: severity ? severity.toLowerCase() : undefined,
      });
      setInsightsData(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to generate business insights');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (selectedDatasetId) {
      fetchInsights(selectedDatasetId, severityFilter);
    } else {
      setInsightsData(null);
    }
  }, [selectedDatasetId, severityFilter, fetchInsights]);

  if (!selectedDatasetId) {
    return (
      <DashboardLayout title="Explainable Decision Support Insights">
        <div className="bg-white rounded-2xl border border-slate-200/80 p-12 text-center max-w-xl mx-auto mt-12 shadow-xs">
          <FileSpreadsheet className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-800">No Dataset Selected</h3>
          <p className="text-xs text-slate-500 mt-1">
            Please select an active dataset from the sidebar to evaluate heuristic business decision rules.
          </p>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title={`Business Insights — ${selectedDataset?.name || 'Decision Support'}`}>
      <div className="space-y-8 max-w-7xl mx-auto">
        {/* Header Summary Cards */}
        {insightsData && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs flex items-center gap-4">
              <div className="p-3 bg-indigo-50 text-indigo-600 rounded-xl">
                <Lightbulb className="w-6 h-6" />
              </div>
              <div>
                <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Total Evaluated</p>
                <h4 className="text-2xl font-bold text-slate-900 mt-0.5">{insightsData.summary.total_insights} Rules</h4>
              </div>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs flex items-center gap-4">
              <div className="p-3 bg-rose-50 text-rose-600 rounded-xl">
                <ShieldAlert className="w-6 h-6" />
              </div>
              <div>
                <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Critical Alerts</p>
                <h4 className="text-2xl font-bold text-rose-600 mt-0.5">{insightsData.summary.critical_count}</h4>
              </div>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs flex items-center gap-4">
              <div className="p-3 bg-amber-50 text-amber-600 rounded-xl">
                <AlertTriangle className="w-6 h-6" />
              </div>
              <div>
                <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Warnings</p>
                <h4 className="text-2xl font-bold text-amber-600 mt-0.5">{insightsData.summary.warning_count}</h4>
              </div>
            </div>

            <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs flex items-center gap-4">
              <div className="p-3 bg-blue-50 text-blue-600 rounded-xl">
                <Info className="w-6 h-6" />
              </div>
              <div>
                <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Informational</p>
                <h4 className="text-2xl font-bold text-blue-600 mt-0.5">{insightsData.summary.info_count}</h4>
              </div>
            </div>
          </div>
        )}

        {/* Severity Filter Tabs */}
        <div className="flex items-center gap-2 bg-white p-2 rounded-2xl border border-slate-200/80 shadow-xs w-fit">
          <span className="text-xs font-semibold text-slate-500 px-3 flex items-center gap-1.5">
            <Filter className="w-3.5 h-3.5" /> Filter Severity:
          </span>
          <button
            onClick={() => setSeverityFilter('')}
            className={`px-3 py-1.5 text-xs font-semibold rounded-xl transition-colors cursor-pointer ${
              severityFilter === '' ? 'bg-indigo-600 text-white' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setSeverityFilter('critical')}
            className={`px-3 py-1.5 text-xs font-semibold rounded-xl transition-colors cursor-pointer ${
              severityFilter === 'critical' ? 'bg-rose-600 text-white' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            Critical Only
          </button>
          <button
            onClick={() => setSeverityFilter('warning')}
            className={`px-3 py-1.5 text-xs font-semibold rounded-xl transition-colors cursor-pointer ${
              severityFilter === 'warning' ? 'bg-amber-600 text-white' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            Warnings
          </button>
          <button
            onClick={() => setSeverityFilter('info')}
            className={`px-3 py-1.5 text-xs font-semibold rounded-xl transition-colors cursor-pointer ${
              severityFilter === 'info' ? 'bg-blue-600 text-white' : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            Informational
          </button>
        </div>

        {/* Loading Spinner */}
        {isLoading && (
          <div className="bg-white rounded-2xl p-12 text-center border border-slate-200/80 shadow-xs flex flex-col items-center gap-3">
            <Loader2 className="w-8 h-8 text-indigo-600 animate-spin" />
            <p className="text-sm font-semibold text-slate-700">Evaluating 12 Deterministic Decision Rules...</p>
            <p className="text-xs text-slate-400">Pillars: Sales, Discounting, Segmentation, Predictions</p>
          </div>
        )}

        {/* Error Alert */}
        {error && !isLoading && (
          <div className="bg-rose-50 border border-rose-200 p-4 rounded-xl flex items-start gap-3 text-xs text-rose-800">
            <AlertCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
            <div>
              <p className="font-bold">Failed to generate insights</p>
              <p className="mt-0.5">{error}</p>
            </div>
          </div>
        )}

        {/* Insights Cards List */}
        {insightsData && !isLoading && (
          <div className="space-y-4">
            {insightsData.insights.length === 0 ? (
              <div className="bg-white rounded-2xl p-12 text-center border border-slate-200/80 shadow-xs">
                <CheckCircle2 className="w-10 h-10 text-emerald-500 mx-auto mb-2" />
                <p className="font-semibold text-slate-700 text-sm">No findings for this filter</p>
                <p className="text-xs text-slate-400 mt-1">No business rules triggered matching selected severity.</p>
              </div>
            ) : (
              insightsData.insights.map((item) => {
                const isCritical = item.severity === 'critical';
                const isWarning = item.severity === 'warning';

                return (
                  <div
                    key={item.insight_id}
                    className={`bg-white p-6 rounded-2xl border shadow-xs transition-all ${
                      isCritical
                        ? 'border-rose-200/80 hover:border-rose-300'
                        : isWarning
                        ? 'border-amber-200/80 hover:border-amber-300'
                        : 'border-slate-200/80 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <span
                          className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                            isCritical
                              ? 'bg-rose-100 text-rose-800'
                              : isWarning
                              ? 'bg-amber-100 text-amber-800'
                              : 'bg-blue-100 text-blue-800'
                          }`}
                        >
                          {item.severity}
                        </span>
                        <span className="text-xs font-semibold text-slate-500 bg-slate-100 px-2.5 py-0.5 rounded-full">
                          {item.category}
                        </span>
                      </div>
                      <span className="text-[10px] font-mono text-slate-400">{item.insight_id}</span>
                    </div>

                    <h4 className="text-base font-bold text-slate-900 mb-2">{item.title}</h4>

                    {/* Prescriptive Recommendation */}
                    <div className="p-3.5 bg-indigo-50/60 border border-indigo-100 rounded-xl my-3 flex items-start gap-2.5">
                      <ArrowRight className="w-4 h-4 text-indigo-600 shrink-0 mt-0.5" />
                      <div>
                        <p className="text-xs font-bold text-indigo-950 uppercase tracking-wider">Actionable Recommendation</p>
                        <p className="text-xs text-indigo-900 mt-0.5 font-medium">{item.recommendation}</p>
                      </div>
                    </div>

                    {/* Evidence & Limitations */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs mt-3 pt-3 border-t border-slate-100 text-slate-600">
                      <div>
                        <p className="font-semibold text-slate-700 mb-1">Empirical Evidence:</p>
                        <pre className="bg-slate-50 p-2.5 rounded-lg text-[11px] font-mono text-slate-700 overflow-x-auto">
                          {JSON.stringify(item.evidence, null, 2)}
                        </pre>
                      </div>
                      <div>
                        <p className="font-semibold text-slate-700 mb-1">Analytical Limitations:</p>
                        <p className="text-slate-500 italic bg-slate-50 p-2.5 rounded-lg text-[11px] leading-relaxed">
                          {item.limitations}
                        </p>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
