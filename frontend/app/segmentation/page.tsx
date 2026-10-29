'use client';

import React, { useState, useEffect, useCallback } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { useDataset } from '@/lib/dataset-context';
import { useCurrency } from '@/lib/currency-context';
import { analyticsApi } from '@/lib/api';
import { SegmentationRunResponse, SegmentationRunHistory } from '@/lib/types';
import { formatDateTime } from '@/lib/formatters';
import AmountDisplay from '@/components/AmountDisplay';
import {
  Play,
  Clock,
  Loader2,
  AlertCircle,
  FileSpreadsheet,
  Award,
} from 'lucide-react';

export default function SegmentationPage() {
  const { selectedDataset, selectedDatasetId } = useDataset();
  const { formatCurrency } = useCurrency();

  const [nClusters, setNClusters] = useState(4);
  const [randomState, setRandomState] = useState(42);
  const [evaluateCandidates, setEvaluateCandidates] = useState(true);

  const [isRunning, setIsRunning] = useState(false);
  const [result, setResult] = useState<SegmentationRunResponse | null>(null);
  const [history, setHistory] = useState<SegmentationRunHistory[]>([]);
  const [error, setError] = useState<string | null>(null);

  const fetchHistory = useCallback(async (datasetId: string) => {
    try {
      const runs = await analyticsApi.getSegmentationRuns(datasetId);
      setHistory(runs);
    } catch {
      // Historical runs optional
    }
  }, []);

  useEffect(() => {
    if (selectedDatasetId) {
      fetchHistory(selectedDatasetId);
      setResult(null);
    }
  }, [selectedDatasetId, fetchHistory]);

  const handleRunSegmentation = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDatasetId) return;

    setIsRunning(true);
    setError(null);

    try {
      const runResult = await analyticsApi.runSegmentation(selectedDatasetId, {
        nClusters,
        randomState,
        evaluateCandidates,
      });
      setResult(runResult);
      await fetchHistory(selectedDatasetId);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Segmentation execution failed');
    } finally {
      setIsRunning(false);
    }
  };

  if (!selectedDatasetId) {
    return (
      <DashboardLayout title="Customer Segmentation (K-Means & PCA)">
        <div className="bg-white rounded-2xl border border-slate-200/80 p-12 text-center max-w-xl mx-auto mt-12 shadow-xs">
          <FileSpreadsheet className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-800">No Dataset Selected</h3>
          <p className="text-xs text-slate-500 mt-1">
            Please select an active dataset from the sidebar or upload a CSV on the Datasets page to perform customer clustering.
          </p>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title={`Customer Segmentation — ${selectedDataset?.name || 'Clustering'}`}>
      <div className="space-y-8 max-w-7xl mx-auto">
        {/* Controls Panel */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-slate-900">Unsupervised K-Means Clustering Parameters</h3>
              <p className="text-xs text-slate-500">
                Aggregates customer RFM features, standardizes scales, and computes optimal cluster personas.
              </p>
            </div>
          </div>

          <form onSubmit={handleRunSegmentation} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5 uppercase tracking-wider flex items-center justify-between">
                  <span>Number of Clusters (k)</span>
                  <span className="text-indigo-600 font-bold">{nClusters}</span>
                </label>
                <input
                  type="range"
                  min="2"
                  max="7"
                  value={nClusters}
                  onChange={(e) => setNClusters(parseInt(e.target.value, 10))}
                  className="w-full accent-indigo-600 cursor-pointer"
                />
                <div className="flex justify-between text-[10px] text-slate-400 mt-1">
                  <span>k=2 (Broad)</span>
                  <span>k=4 (Recommended)</span>
                  <span>k=7 (Granular)</span>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5 uppercase tracking-wider">
                  Random Seed (Reproducibility)
                </label>
                <input
                  type="number"
                  value={randomState}
                  onChange={(e) => setRandomState(parseInt(e.target.value, 10) || 42)}
                  className="w-full text-xs border border-slate-200 rounded-xl px-3.5 py-2 bg-slate-50/50 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="flex flex-col justify-center">
                <label className="flex items-center gap-2 cursor-pointer mt-3">
                  <input
                    type="checkbox"
                    checked={evaluateCandidates}
                    onChange={(e) => setEvaluateCandidates(e.target.checked)}
                    className="w-4 h-4 text-indigo-600 rounded focus:ring-indigo-500 border-slate-300"
                  />
                  <span className="text-xs font-medium text-slate-700">Compute Elbow & Silhouette Sweep (k=2..6)</span>
                </label>
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                type="submit"
                disabled={isRunning}
                className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-300 text-white text-xs font-semibold rounded-xl flex items-center gap-2 transition-all cursor-pointer disabled:cursor-not-allowed shadow-xs"
              >
                {isRunning ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Executing K-Means & PCA...</span>
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4" />
                    <span>Execute Segmentation Run</span>
                  </>
                )}
              </button>
            </div>
          </form>

          {error && (
            <div className="mt-4 p-4 bg-rose-50 border border-rose-200 rounded-xl flex items-center gap-3 text-xs text-rose-800">
              <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />
              <span>{error}</span>
            </div>
          )}
        </div>

        {/* Results Panel */}
        {result && (
          <div className="space-y-6">
            {/* Run KPI Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
                <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Clusters Formed</span>
                <h4 className="text-2xl font-bold text-slate-900 mt-1">{result.nClusters} Groups</h4>
                <p className="text-[11px] text-slate-400 mt-0.5">k-means algorithm</p>
              </div>

              <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
                <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Silhouette Score</span>
                <h4 className="text-2xl font-bold text-indigo-600 mt-1">
                  {result.silhouetteScore != null ? Number(result.silhouetteScore).toFixed(3) : '—'}
                </h4>
                <p className="text-[11px] text-slate-400 mt-0.5">Cluster cohesion (-1 to +1)</p>
              </div>

              <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
                <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Inertia (WCSS)</span>
                <h4 className="text-2xl font-bold text-slate-900 mt-1">
                  {result.inertia != null ? Number(result.inertia).toLocaleString(undefined, { maximumFractionDigits: 1 }) : '—'}
                </h4>
                <p className="text-[11px] text-slate-400 mt-0.5">Within-cluster sum of squares</p>
              </div>

              <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
                <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">2D PCA Variance</span>
                <h4 className="text-2xl font-bold text-emerald-600 mt-1">
                  {Array.isArray(result.pcaVarianceRatio)
                    ? result.pcaVarianceRatio.reduce((a, b) => a + Number(b), 0).toFixed(1)
                    : '—'}%
                </h4>
                <p className="text-[11px] text-slate-400 mt-0.5">
                  PC1 ({result.pcaVarianceRatio?.[0] != null ? Number(result.pcaVarianceRatio[0]).toFixed(1) : '—'}%) + PC2 ({result.pcaVarianceRatio?.[1] != null ? Number(result.pcaVarianceRatio[1]).toFixed(1) : '—'}%)
                </p>
              </div>
            </div>

            {/* Persona Cards */}
            <div>
              <h3 className="text-base font-bold text-slate-900 mb-4">Cluster Persona Profiles & Behavioral Signatures</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {result.clusterProfiles?.map((p) => {
                  const recency = p.MeanRecencyDays ?? p.Recency_Mean;
                  const frequency = p.MeanFrequency ?? p.Frequency_Mean;
                  const monetary = p.MeanSales ?? p.MonetaryValue_Mean ?? p.TotalSales;
                  const profitMargin = p.ProfitMarginPct ?? p.ProfitMarginPct_Mean;
                  const customerPct = p.CustomerPct;
                  const customerCount = p.CustomerCount;

                  return (
                    <div key={p.Cluster} className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs flex flex-col justify-between">
                      <div>
                        <div className="flex items-center justify-between mb-3">
                          <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-indigo-100 text-indigo-800">
                            Cluster {p.Cluster}
                          </span>
                          <span className="text-xs font-semibold text-slate-500">
                            {customerPct != null ? `${Number(customerPct).toFixed(1)}%` : '—'}
                          </span>
                        </div>
                        <h4 className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
                          <Award className="w-4 h-4 text-amber-500" />
                          {p.DescriptivePersona}
                        </h4>
                        <p className="text-xs text-slate-500 mt-0.5">
                          {customerCount != null ? customerCount.toLocaleString() : '—'} Customers
                        </p>

                        <div className="mt-4 space-y-2 text-xs border-t border-slate-100 pt-3">
                          <div className="flex justify-between">
                            <span className="text-slate-500">Recency:</span>
                            <span className="font-semibold text-slate-800">
                              {recency != null ? `${Number(recency).toFixed(0)} days` : '—'}
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-500">Frequency:</span>
                            <span className="font-semibold text-slate-800">
                              {frequency != null ? `${Number(frequency).toFixed(1)} orders` : '—'}
                            </span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-slate-500">Avg Monetary:</span>
                            <span className="font-semibold text-slate-800">
                              <AmountDisplay amount={monetary != null ? Number(monetary) : null} />
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-500">Profit Margin:</span>
                            <span className={`font-bold ${profitMargin != null && Number(profitMargin) >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                              {profitMargin != null ? `${Number(profitMargin).toFixed(1)}%` : '—'}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Candidate Evaluation (Elbow / Sweep) */}
            {result.candidatesEvaluation && result.candidatesEvaluation.length > 0 && (
              <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs">
                <h4 className="text-sm font-bold text-slate-900 mb-2">Cluster Candidate Diagnostic Evaluation</h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-50 text-slate-600 uppercase tracking-wider border-b">
                      <tr>
                        <th className="py-2.5 px-4">Candidate (k)</th>
                        <th className="py-2.5 px-4 text-right">Inertia</th>
                        <th className="py-2.5 px-4 text-right">Silhouette Score</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {result.candidatesEvaluation.map((cand) => (
                        <tr key={cand.k}>
                          <td className="py-2.5 px-4 font-bold text-slate-900">k = {cand.k}</td>
                          <td className="py-2.5 px-4 text-right">
                            {cand.Inertia != null ? Number(cand.Inertia).toLocaleString(undefined, { maximumFractionDigits: 1 }) : '—'}
                          </td>
                          <td className="py-2.5 px-4 text-right font-bold text-indigo-600">
                            {cand.SilhouetteScore != null ? Number(cand.SilhouetteScore).toFixed(3) : '—'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Historical Runs in PostgreSQL */}
        {history.length > 0 && (
          <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
            <div className="p-5 border-b border-slate-200/80 flex items-center gap-2">
              <Clock className="w-4 h-4 text-indigo-600" />
              <h3 className="text-sm font-bold text-slate-900">Persisted Segmentation Runs (PostgreSQL)</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-600 uppercase tracking-wider border-b">
                  <tr>
                    <th className="py-3 px-6">Run ID</th>
                    <th className="py-3 px-6 text-center">Clusters (k)</th>
                    <th className="py-3 px-6 text-right">Silhouette</th>
                    <th className="py-3 px-6 text-right">Inertia</th>
                    <th className="py-3 px-6">Algorithm</th>
                    <th className="py-3 px-6">Created At</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {history.map((r) => (
                    <tr key={r.id} className="hover:bg-slate-50/50">
                      <td className="py-3 px-6 font-mono text-[11px] text-slate-600">{r.id.substring(0, 8)}...</td>
                      <td className="py-3 px-6 text-center font-bold text-slate-900">{r.kClusters}</td>
                      <td className="py-3 px-6 text-right font-semibold text-indigo-600">
                        {r.silhouetteScore != null && !isNaN(Number(r.silhouetteScore))
                          ? Number(r.silhouetteScore).toFixed(4)
                          : '—'}
                      </td>
                      <td className="py-3 px-6 text-right">
                        {r.inertia != null && !isNaN(Number(r.inertia))
                          ? Number(r.inertia).toLocaleString(undefined, { maximumFractionDigits: 1 })
                          : '—'}
                      </td>
                      <td className="py-3 px-6 text-slate-600">{r.algorithmVersion}</td>
                      <td className="py-3 px-6 text-slate-500">{formatDateTime(r.createdAt)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
