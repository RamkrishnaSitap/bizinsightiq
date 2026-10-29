'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import DashboardLayout from '@/components/DashboardLayout';
import { useDataset } from '@/lib/dataset-context';
import { datasetApi } from '@/lib/api';
import { UploadDatasetResponse } from '@/lib/types';
import { formatDateTime } from '@/lib/formatters';
import {
  UploadCloud,
  FileSpreadsheet,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Database,
  Trash2,
  BarChart3,
  Loader2,
  Layers,
  TrendingUp,
} from 'lucide-react';

export default function DashboardPage() {
  const router = useRouter();
  const { datasets, selectedDatasetId, selectDataset, refreshDatasets, isLoading: datasetsLoading } = useDataset();

  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [datasetName, setDatasetName] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<UploadDatasetResponse | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setUploadFile(file);
      setUploadResult(null);
      setUploadError(null);
      if (!datasetName) {
        setDatasetName(file.name.replace(/\.csv$/i, ''));
      }
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) return;

    setIsUploading(true);
    setUploadError(null);
    setUploadResult(null);

    try {
      const result = await datasetApi.upload(uploadFile, datasetName.trim());
      setUploadResult(result);
      setUploadFile(null);
      setDatasetName('');
      await refreshDatasets();
      if (result.isValid) {
        const newId = result.id || result.datasetId;
        if (newId) selectDataset(newId);
      }
    } catch (err: unknown) {
      setUploadError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`Are you sure you want to delete dataset "${name}"? This removes all stored transactions and analysis runs.`)) {
      return;
    }

    setDeletingId(id);
    try {
      await datasetApi.delete(id);
      await refreshDatasets();
    } catch (err: unknown) {
      alert(`Failed to delete dataset: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setDeletingId(null);
    }
  };

  const totalRowsSum = datasets.reduce((acc, d) => acc + (d.totalRows || 0), 0);
  const validatedCount = datasets.filter((d) => d.status === 'VALIDATED').length;

  return (
    <DashboardLayout title="Dataset Management & Ingestion">
      <div className="space-y-8 max-w-7xl mx-auto">
        {/* KPI Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
          <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs flex items-center gap-4">
            <div className="p-3 bg-indigo-50 text-indigo-600 rounded-xl">
              <Database className="w-6 h-6" />
            </div>
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Datasets</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-0.5">{datasets.length}</h3>
            </div>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs flex items-center gap-4">
            <div className="p-3 bg-emerald-50 text-emerald-600 rounded-xl">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Validated & Ready</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-0.5">{validatedCount}</h3>
            </div>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs flex items-center gap-4">
            <div className="p-3 bg-blue-50 text-blue-600 rounded-xl">
              <Layers className="w-6 h-6" />
            </div>
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Persisted Records</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-0.5">{totalRowsSum.toLocaleString()}</h3>
            </div>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs flex items-center gap-4">
            <div className="p-3 bg-purple-50 text-purple-600 rounded-xl">
              <TrendingUp className="w-6 h-6" />
            </div>
            <div>
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">ML Engines Active</p>
              <h3 className="text-2xl font-bold text-slate-900 mt-0.5">4 Engines</h3>
            </div>
          </div>
        </div>

        {/* Upload & Ingestion Section */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-bold text-slate-900">Upload Sales Dataset (CSV)</h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Files are validated against business rules by Python ML engine, confined safely in storage, and batch-persisted in PostgreSQL.
              </p>
            </div>
          </div>

          <form onSubmit={handleUpload} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5 uppercase tracking-wider">
                  Select CSV File (.csv)
                </label>
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleFileChange}
                  className="block w-full text-xs text-slate-500 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 border border-slate-200 rounded-xl p-1.5 bg-slate-50/50 cursor-pointer"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5 uppercase tracking-wider">
                  Dataset Display Name (Optional)
                </label>
                <input
                  type="text"
                  placeholder="e.g. Q4 2026 Sales Report"
                  value={datasetName}
                  onChange={(e) => setDatasetName(e.target.value)}
                  className="w-full text-sm border border-slate-200 rounded-xl px-4 py-2 bg-slate-50/50 focus:outline-none focus:border-indigo-500 focus:bg-white transition-colors"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                type="submit"
                disabled={!uploadFile || isUploading}
                className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-300 text-white text-xs font-semibold rounded-xl flex items-center gap-2 transition-all cursor-pointer disabled:cursor-not-allowed shadow-xs"
              >
                {isUploading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Validating & Ingesting via FastAPI...</span>
                  </>
                ) : (
                  <>
                    <UploadCloud className="w-4 h-4" />
                    <span>Upload & Ingest Dataset</span>
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Validation Feedback Card */}
          {uploadResult && (
            <div
              className={`mt-5 p-4 rounded-xl border flex items-start gap-3 text-xs ${
                uploadResult.isValid
                  ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
                  : 'bg-rose-50 border-rose-200 text-rose-900'
              }`}
            >
              {uploadResult.isValid ? (
                <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
              ) : (
                <XCircle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
              )}
              <div className="flex-1">
                <p className="font-bold text-sm">
                  {uploadResult.isValid ? 'Validation Succeeded & Ingested' : 'Validation Failed — Rejected'}
                </p>
                <p className="mt-1">
                  Dataset <strong>&quot;{uploadResult.name}&quot;</strong> processed {uploadResult.totalRows.toLocaleString()} rows and {uploadResult.totalColumns} columns.
                </p>
                {uploadResult.errors && uploadResult.errors.length > 0 && (
                  <div className="mt-2 text-rose-800 font-medium">
                    <p className="font-bold">Errors:</p>
                    <ul className="list-disc list-inside space-y-0.5">
                      {uploadResult.errors.map((err, i) => (
                        <li key={i}>{err}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {uploadResult.warnings && uploadResult.warnings.length > 0 && (
                  <div className="mt-2 text-amber-800 font-medium">
                    <p className="font-bold">Warnings:</p>
                    <ul className="list-disc list-inside space-y-0.5">
                      {uploadResult.warnings.map((warn, i) => (
                        <li key={i}>{warn}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}

          {uploadError && (
            <div className="mt-5 p-4 bg-rose-50 border border-rose-200 rounded-xl flex items-center gap-3 text-xs text-rose-800 font-medium">
              <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0" />
              <span>{uploadError}</span>
            </div>
          )}
        </div>

        {/* Datasets Table */}
        <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-200/80 flex items-center justify-between">
            <div>
              <h3 className="text-base font-bold text-slate-900">Your Sales Datasets</h3>
              <p className="text-xs text-slate-500">Datasets uploaded by your account in PostgreSQL</p>
            </div>
            <button
              onClick={() => refreshDatasets()}
              className="text-xs font-semibold text-indigo-600 hover:text-indigo-800 transition-colors"
            >
              Refresh Table
            </button>
          </div>

          {datasetsLoading && datasets.length === 0 ? (
            <div className="p-8 text-center text-slate-500 text-xs flex flex-col items-center gap-2">
              <Loader2 className="w-6 h-6 animate-spin text-indigo-600" />
              <span>Loading registered datasets...</span>
            </div>
          ) : datasets.length === 0 ? (
            <div className="p-12 text-center text-slate-500 text-sm flex flex-col items-center gap-3">
              <FileSpreadsheet className="w-12 h-12 text-slate-300" />
              <p className="font-semibold text-slate-700">No datasets found</p>
              <p className="text-xs text-slate-400 max-w-sm">
                Upload your first retail transactions CSV file using the form above to begin EDA and ML analytics.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50/80 text-slate-600 font-semibold uppercase tracking-wider border-b border-slate-200/80">
                  <tr>
                    <th className="py-3 px-6">Dataset Name</th>
                    <th className="py-3 px-6">Source File</th>
                    <th className="py-3 px-6">Status</th>
                    <th className="py-3 px-6 text-right">Rows</th>
                    <th className="py-3 px-6 text-right">Columns</th>
                    <th className="py-3 px-6">Created At</th>
                    <th className="py-3 px-6 text-center">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {datasets.map((d) => {
                    const isSelected = d.id === selectedDatasetId;
                    return (
                      <tr
                        key={d.id}
                        className={`hover:bg-slate-50/60 transition-colors ${
                          isSelected ? 'bg-indigo-50/40' : ''
                        }`}
                      >
                        <td className="py-3.5 px-6 font-semibold text-slate-900">
                          <div className="flex items-center gap-2">
                            <span>{d.name}</span>
                            {isSelected && (
                              <span className="px-2 py-0.5 text-[10px] bg-indigo-600 text-white rounded-full font-bold">
                                ACTIVE
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="py-3.5 px-6 text-slate-600 font-mono text-[11px]">{d.originalFilename}</td>
                        <td className="py-3.5 px-6">
                          <span
                            className={`px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                              d.status === 'VALIDATED'
                                ? 'bg-emerald-100 text-emerald-800'
                                : d.status === 'PENDING'
                                ? 'bg-amber-100 text-amber-800'
                                : 'bg-rose-100 text-rose-800'
                            }`}
                          >
                            {d.status}
                          </span>
                        </td>
                        <td className="py-3.5 px-6 text-right font-medium text-slate-800">
                          {d.totalRows !== null ? d.totalRows.toLocaleString() : '—'}
                        </td>
                        <td className="py-3.5 px-6 text-right font-medium text-slate-800">
                          {d.totalColumns !== null ? d.totalColumns : '—'}
                        </td>
                        <td className="py-3.5 px-6 text-slate-500 text-[11px]">
                          {formatDateTime(d.uploadedAt || d.createdAt)}
                        </td>
                        <td className="py-3.5 px-6 text-center">
                          <div className="flex items-center justify-center gap-2">
                            <button
                              onClick={() => {
                                selectDataset(d.id);
                                router.push('/eda');
                              }}
                              className="px-2.5 py-1 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-semibold rounded-lg flex items-center gap-1 transition-colors cursor-pointer"
                              title="Analyze with EDA"
                            >
                              <BarChart3 className="w-3.5 h-3.5" />
                              <span>Analyze</span>
                            </button>

                            <button
                              onClick={() => handleDelete(d.id, d.name)}
                              disabled={deletingId === d.id}
                              className="p-1.5 text-rose-500 hover:text-rose-700 hover:bg-rose-50 rounded-lg transition-colors cursor-pointer disabled:opacity-50"
                              title="Delete dataset"
                            >
                              {deletingId === d.id ? (
                                <Loader2 className="w-4 h-4 animate-spin" />
                              ) : (
                                <Trash2 className="w-4 h-4" />
                              )}
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
