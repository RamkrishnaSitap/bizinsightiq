'use client';

import React, { useState, useEffect } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { useDataset } from '@/lib/dataset-context';
import { useCurrency } from '@/lib/currency-context';
import { analyticsApi } from '@/lib/api';
import {
  QuoteSimulationResponse,
  PredictionTrainingResponse,
  PredictionExplanationResponse,
  ScenarioComparisonResponse,
} from '@/lib/types';
import { formatDateTime } from '@/lib/formatters';
import AmountDisplay from '@/components/AmountDisplay';
import {
  TrendingUp,
  Calculator,
  Award,
  History,
  Loader2,
  AlertCircle,
  FileSpreadsheet,
  CheckCircle2,
  Sparkles,
  ArrowUpRight,
  ArrowDownRight,
  ShieldCheck,
  HelpCircle,
  GitCompare,
  Copy,
  Sliders,
} from 'lucide-react';

export default function PredictionsPage() {
  const { selectedDataset, selectedDatasetId } = useDataset();
  const { formatCurrency, symbol } = useCurrency();

  // Quote Simulation Form States
  const [category, setCategory] = useState('Technology');
  const [region, setRegion] = useState('East');
  const [quantity, setQuantity] = useState(5);
  const [discountPct, setDiscountPct] = useState(10);
  const [modelType, setModelType] = useState('random_forest');
  const [month] = useState(6);
  const [quarter] = useState(2);
  const [dayOfWeek] = useState(2);

  const [isSimulating, setIsSimulating] = useState(false);
  const [simulationResult, setSimulationResult] = useState<QuoteSimulationResponse | null>(null);
  const [simulationError, setSimulationError] = useState<string | null>(null);

  // SHAP Explainable AI States
  const [explanationResult, setExplanationResult] = useState<PredictionExplanationResponse | null>(null);
  const [isExplaining, setIsExplaining] = useState(false);
  const [explanationError, setExplanationError] = useState<string | null>(null);

  // What-If Side-by-Side Comparison States
  const [simulatorMode, setSimulatorMode] = useState<'single' | 'compare'>('single');

  // Comparison Scenario A
  const [categoryA, setCategoryA] = useState('Technology');
  const [regionA, setRegionA] = useState('East');
  const [quantityA, setQuantityA] = useState(5);
  const [discountPctA, setDiscountPctA] = useState(10);
  const [monthA] = useState(6);
  const [quarterA] = useState(2);
  const [dayOfWeekA] = useState(2);

  // Comparison Scenario B (Default: same parameters with Discount 20%)
  const [categoryB, setCategoryB] = useState('Technology');
  const [regionB, setRegionB] = useState('East');
  const [quantityB, setQuantityB] = useState(5);
  const [discountPctB, setDiscountPctB] = useState(20);
  const [monthB] = useState(6);
  const [quarterB] = useState(2);
  const [dayOfWeekB] = useState(2);

  // Shared Model for Comparison
  const [compareModelType, setCompareModelType] = useState('random_forest');

  // Comparison Execution
  const [isComparing, setIsComparing] = useState(false);
  const [comparisonResult, setComparisonResult] = useState<ScenarioComparisonResponse | null>(null);
  const [comparisonError, setComparisonError] = useState<string | null>(null);

  const copyScenarioAToB = () => {
    setCategoryB(categoryA);
    setRegionB(regionA);
    setQuantityB(quantityA);
    setDiscountPctB(discountPctA);
  };

  const handleCompareScenarios = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDatasetId) return;

    setIsComparing(true);
    setComparisonError(null);

    try {
      const res = await analyticsApi.compareScenarios(selectedDatasetId, {
        scenarioA: {
          category: categoryA,
          region: regionA,
          quantity: quantityA,
          discount: discountPctA / 100.0,
          month: monthA,
          quarter: quarterA,
          dayOfWeek: dayOfWeekA,
        },
        scenarioB: {
          category: categoryB,
          region: regionB,
          quantity: quantityB,
          discount: discountPctB / 100.0,
          month: monthB,
          quarter: quarterB,
          dayOfWeek: dayOfWeekB,
        },
        modelType: compareModelType,
      });
      setComparisonResult(res);
    } catch (err: unknown) {
      setComparisonError(err instanceof Error ? err.message : 'Scenario comparison failed');
    } finally {
      setIsComparing(false);
    }
  };

  // Model Training Benchmark States
  const [isTraining, setIsTraining] = useState(false);
  const [trainingResult, setTrainingResult] = useState<PredictionTrainingResponse | null>(null);
  const [trainingError, setTrainingError] = useState<string | null>(null);

  // Quote History
  const [quoteHistory, setQuoteHistory] = useState<QuoteSimulationResponse[]>([]);

  const fetchQuotes = async () => {
    try {
      const history = await analyticsApi.getQuoteHistory();
      setQuoteHistory(history);
    } catch {
      // Optional
    }
  };

  useEffect(() => {
    fetchQuotes();
  }, []);

  const handleExplainQuote = async (overrideModelType?: string) => {
    if (!selectedDatasetId) return;
    setIsExplaining(true);
    setExplanationError(null);

    try {
      const res = await analyticsApi.explainQuote(selectedDatasetId, {
        category,
        region,
        quantity,
        discount: discountPct / 100.0,
        month,
        quarter,
        dayOfWeek,
        modelType: overrideModelType || modelType,
      });
      setExplanationResult(res);
    } catch (err: unknown) {
      setExplanationError(err instanceof Error ? err.message : 'SHAP explanation failed');
    } finally {
      setIsExplaining(false);
    }
  };

  const handleSimulateQuote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDatasetId) return;

    setIsSimulating(true);
    setSimulationError(null);
    setExplanationResult(null);

    try {
      const res = await analyticsApi.simulateQuote(selectedDatasetId, {
        category,
        region,
        quantity,
        discount: discountPct / 100.0,
        month,
        quarter,
        dayOfWeek,
        modelType,
      });
      setSimulationResult(res);
      await fetchQuotes();
      // Automatically trigger SHAP explanation for the simulated quote
      await handleExplainQuote(modelType);
    } catch (err: unknown) {
      setSimulationError(err instanceof Error ? err.message : 'Simulation failed');
    } finally {
      setIsSimulating(false);
    }
  };

  const handleTrainModels = async () => {
    if (!selectedDatasetId) return;

    setIsTraining(true);
    setTrainingError(null);

    try {
      const res = await analyticsApi.trainPredictions(selectedDatasetId, {
        splitStrategy: 'chronological',
        testSize: 0.20,
        randomState: 42,
      });
      setTrainingResult(res);
    } catch (err: unknown) {
      setTrainingError(err instanceof Error ? err.message : 'Model benchmarking failed');
    } finally {
      setIsTraining(false);
    }
  };

  if (!selectedDatasetId) {
    return (
      <DashboardLayout title="Sales Prediction & Quotes">
        <div className="bg-white rounded-2xl border border-slate-200/80 p-12 text-center max-w-xl mx-auto mt-12 shadow-xs">
          <FileSpreadsheet className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-800">No Dataset Selected</h3>
          <p className="text-xs text-slate-500 mt-1">
            Please select an active dataset from the sidebar to train models or simulate scenario quotes.
          </p>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title={`Predictive Analytics — ${selectedDataset?.name || 'Inference'}`}>
      <div className="space-y-8 max-w-7xl mx-auto">
        {/* Section 1: Scenario Quote Simulator */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 pb-4 border-b border-slate-100 gap-4">
            <div>
              <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <Calculator className="w-5 h-5 text-indigo-600" />
                &quot;What-If&quot; Sales Quote Simulation Engine
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Simulate potential transaction gross sales given category, region, and promotional discounts. Powered by machine learning and SHAP attribution.
              </p>
            </div>

            {/* Mode Switcher Tabs */}
            <div className="flex items-center gap-1.5 bg-slate-100/80 p-1 rounded-xl self-start sm:self-auto border border-slate-200/60">
              <button
                type="button"
                onClick={() => setSimulatorMode('single')}
                className={`px-3 py-1.5 text-xs font-semibold rounded-lg flex items-center gap-1.5 transition-all cursor-pointer ${
                  simulatorMode === 'single'
                    ? 'bg-white text-indigo-700 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <Calculator className="w-3.5 h-3.5" />
                <span>Single Quote</span>
              </button>
              <button
                type="button"
                onClick={() => setSimulatorMode('compare')}
                className={`px-3 py-1.5 text-xs font-semibold rounded-lg flex items-center gap-1.5 transition-all cursor-pointer ${
                  simulatorMode === 'compare'
                    ? 'bg-white text-indigo-700 shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                <GitCompare className="w-3.5 h-3.5 text-indigo-600" />
                <span>Side-by-Side What-If Comparison</span>
                <span className="text-[10px] bg-indigo-100 text-indigo-700 px-1.5 py-0.5 rounded-full font-bold">
                  SHAP
                </span>
              </button>
            </div>
          </div>

          {simulatorMode === 'single' && (
            <>
          <form onSubmit={handleSimulateQuote} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5 uppercase tracking-wider">
                  Product Category
                </label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full text-xs border border-slate-200 rounded-xl px-3 py-2 bg-slate-50/50 focus:outline-none focus:border-indigo-500 font-medium"
                >
                  <option value="Technology">Technology</option>
                  <option value="Furniture">Furniture</option>
                  <option value="Office Supplies">Office Supplies</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5 uppercase tracking-wider">
                  Customer Region
                </label>
                <select
                  value={region}
                  onChange={(e) => setRegion(e.target.value)}
                  className="w-full text-xs border border-slate-200 rounded-xl px-3 py-2 bg-slate-50/50 focus:outline-none focus:border-indigo-500 font-medium"
                >
                  <option value="East">East</option>
                  <option value="West">West</option>
                  <option value="Central">Central</option>
                  <option value="South">South</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5 uppercase tracking-wider">
                  Order Quantity (Units)
                </label>
                <input
                  type="number"
                  min="1"
                  max="1000"
                  value={quantity}
                  onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value, 10) || 1))}
                  className="w-full text-xs border border-slate-200 rounded-xl px-3 py-2 bg-slate-50/50 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5 uppercase tracking-wider flex justify-between">
                  <span>Discount</span>
                  <span className="text-indigo-600 font-bold">{discountPct}%</span>
                </label>
                <input
                  type="range"
                  min="0"
                  max="70"
                  step="5"
                  value={discountPct}
                  onChange={(e) => setDiscountPct(parseInt(e.target.value, 10))}
                  className="w-full accent-indigo-600 cursor-pointer mt-2"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5 uppercase tracking-wider">
                  Model Architecture
                </label>
                <select
                  value={modelType}
                  onChange={(e) => setModelType(e.target.value)}
                  className="w-full text-xs border border-slate-200 rounded-xl px-3 py-2 bg-slate-50/50 focus:outline-none focus:border-indigo-500 font-medium"
                >
                  <option value="random_forest">Random Forest (Default)</option>
                  <option value="xgboost">XGBoost Regressor</option>
                  <option value="linear_regression">Linear Regression</option>
                </select>
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                type="submit"
                disabled={isSimulating}
                className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-300 text-white text-xs font-semibold rounded-xl flex items-center gap-2 transition-all cursor-pointer disabled:cursor-not-allowed shadow-xs"
              >
                {isSimulating ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Inference in Progress...</span>
                  </>
                ) : (
                  <>
                    <TrendingUp className="w-4 h-4" />
                    <span>Simulate Quote</span>
                  </>
                )}
              </button>
            </div>
          </form>

          {simulationError && (
            <div className="mt-4 p-4 bg-rose-50 border border-rose-200 rounded-xl flex items-center gap-3 text-xs text-rose-800">
              <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />
              <span>{simulationError}</span>
            </div>
          )}

          {/* Simulation Output Card */}
          {simulationResult && (
            <div className="mt-5 p-5 bg-indigo-50/60 border border-indigo-200/80 rounded-2xl flex items-center justify-between">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-700 bg-indigo-100 px-2 py-0.5 rounded-full">
                  Simulation Outcome
                </span>
                <div className="flex items-baseline gap-3 mt-2">
                  <div className="text-3xl font-extrabold text-slate-900">
                    <AmountDisplay amount={Number(simulationResult.predictedSales)} />
                  </div>
                  <span className="text-xs text-slate-500 font-medium">Estimated Gross Sales</span>
                </div>
                <p className="text-xs text-slate-600 mt-1">
                  Model: <strong>{simulationResult.modelVersion}</strong> • Applied Discount: <strong>{(Number(simulationResult.discount) * 100).toFixed(0)}%</strong>
                </p>
              </div>
              <div className="text-right">
                <span className="inline-flex items-center gap-1 text-xs text-emerald-700 font-semibold bg-emerald-100/80 px-2.5 py-1 rounded-full">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  Persisted to DB
                </span>
                <p className="text-[10px] font-mono text-slate-400 mt-1">ID: {simulationResult.id.substring(0, 8)}...</p>
              </div>
            </div>
          )}

          {/* Section 1.5: SHAP Explainable AI Attribution Breakdown Card */}
          {isExplaining && (
            <div className="mt-5 p-5 bg-slate-50 border border-slate-200/80 rounded-2xl flex items-center justify-center gap-3 text-xs text-slate-600">
              <Loader2 className="w-4 h-4 animate-spin text-indigo-600" />
              <span>Calculating SHapley Additive exPlanations (SHAP) for fitted model...</span>
            </div>
          )}

          {explanationError && (
            <div className="mt-4 p-4 bg-amber-50 border border-amber-200 rounded-xl flex items-center gap-3 text-xs text-amber-800">
              <AlertCircle className="w-5 h-5 text-amber-600 shrink-0" />
              <span>{explanationError}</span>
            </div>
          )}

          {explanationResult && (
            <div className="mt-5 bg-slate-900 text-white rounded-2xl p-6 border border-slate-800 shadow-sm">
              <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-slate-800 gap-3">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="p-1.5 bg-indigo-500/20 text-indigo-400 rounded-lg">
                      <Sparkles className="w-4 h-4" />
                    </span>
                    <h4 className="text-sm font-bold text-white tracking-wide">
                      Explainable AI (SHAP) — Model Decision Attribution
                    </h4>
                  </div>
                  <p className="text-xs text-slate-400 mt-1">
                    Deconstructs the prediction using Shapley values. Baseline expected sales: <strong className="text-slate-200">{symbol}{explanationResult.base_value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</strong>
                  </p>
                </div>

                <div className="flex items-center gap-2 text-[11px] text-slate-300 bg-slate-800/80 px-3 py-1.5 rounded-xl border border-slate-700">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  <span>Explainer: <strong>{explanationResult.explainer_type}</strong></span>
                  {explanationResult.is_additive_exact && (
                    <span className="ml-1 text-[10px] font-mono bg-emerald-950 text-emerald-300 px-1.5 py-0.5 rounded border border-emerald-800">
                      Additive Exact
                    </span>
                  )}
                </div>
              </div>

              {/* Attribution Table */}
              <div className="mt-4 overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="text-[11px] uppercase tracking-wider text-slate-400 border-b border-slate-800">
                    <tr>
                      <th className="py-2.5 px-3">Input Feature</th>
                      <th className="py-2.5 px-3 text-center">Direction</th>
                      <th className="py-2.5 px-3 text-right">SHAP Value ({symbol})</th>
                      <th className="py-2.5 px-3">Relative Impact</th>
                      <th className="py-2.5 px-3">Business Interpretation</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-sans">
                    {explanationResult.feature_contributions.map((fc, idx) => (
                      <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
                        <td className="py-3 px-3">
                          <span className="font-semibold text-white">{fc.feature}</span>
                          <span className="text-[11px] text-slate-400 ml-1.5 font-mono">({fc.input_value})</span>
                        </td>
                        <td className="py-3 px-3 text-center">
                          {fc.direction === 'increased' ? (
                            <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-300 bg-emerald-950/70 border border-emerald-800/80 px-2 py-0.5 rounded-full">
                              <ArrowUpRight className="w-3 h-3 text-emerald-400" />
                              Pushed Up
                            </span>
                          ) : fc.direction === 'decreased' ? (
                            <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-rose-300 bg-rose-950/70 border border-rose-800/80 px-2 py-0.5 rounded-full">
                              <ArrowDownRight className="w-3 h-3 text-rose-400" />
                              Pulled Down
                            </span>
                          ) : (
                            <span className="text-[11px] text-slate-400 bg-slate-800 px-2 py-0.5 rounded-full">
                              Neutral
                            </span>
                          )}
                        </td>
                        <td className={`py-3 px-3 text-right font-mono font-bold ${fc.contribution > 0 ? 'text-emerald-400' : (fc.contribution < 0 ? 'text-rose-400' : 'text-slate-300')}`}>
                          {fc.contribution > 0 ? `+${symbol}${fc.contribution.toFixed(2)}` : (fc.contribution < 0 ? `-${symbol}${Math.abs(fc.contribution).toFixed(2)}` : `${symbol}0.00`)}
                        </td>
                        <td className="py-3 px-3 w-36">
                          <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                            <div
                              className={`h-full rounded-full ${fc.contribution >= 0 ? 'bg-emerald-500' : 'bg-rose-500'}`}
                              style={{ width: `${Math.min(100, fc.percentage_impact)}%` }}
                            />
                          </div>
                          <span className="text-[10px] text-slate-500 font-mono mt-0.5 block">{fc.percentage_impact}%</span>
                        </td>
                        <td className="py-3 px-3 text-slate-300 text-[11px]">
                          {fc.interpretation}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Additive Verification Footnote */}
              <div className="mt-4 pt-3 border-t border-slate-800 flex flex-col md:flex-row md:items-center justify-between text-[11px] text-slate-400 gap-2">
                <div className="flex items-center gap-1.5 font-mono">
                  <span>Base (${explanationResult.base_value.toFixed(2)})</span>
                  <span>+</span>
                  <span className="text-indigo-300">SHAP Sum (${(explanationResult.additive_sum - explanationResult.base_value).toFixed(2)})</span>
                  <span>=</span>
                  <span className="font-bold text-white">Prediction (${explanationResult.predicted_sales.toFixed(2)})</span>
                </div>
                <div className="text-[10px] text-slate-400 italic">
                  *SHAP values explain statistical model mechanics; they indicate correlation within learned weights, not real-world causation.
                </div>
              </div>
            </div>
          )}
          </>
          )}

          {/* Section 1 Mode B: Side-by-Side What-If Comparison */}
          {simulatorMode === 'compare' && (
            <div className="space-y-6">
              {/* Shared Model Selector Banner */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between p-3.5 bg-slate-50 border border-slate-200/80 rounded-xl gap-3">
                <div className="flex items-center gap-2">
                  <Sliders className="w-4 h-4 text-indigo-600" />
                  <span className="text-xs font-semibold text-slate-800">
                    Shared Regression Model (Applied to Both Scenarios):
                  </span>
                </div>
                <select
                  value={compareModelType}
                  onChange={(e) => setCompareModelType(e.target.value)}
                  className="text-xs font-semibold border border-slate-300 rounded-lg px-3 py-1.5 bg-white text-slate-800 focus:outline-none focus:border-indigo-500 shadow-2xs"
                >
                  <option value="random_forest">Random Forest Regressor (Default)</option>
                  <option value="xgboost">XGBoost Regressor</option>
                  <option value="linear_regression">Linear Regression</option>
                </select>
              </div>

              {/* Two-Column Scenario Form */}
              <form onSubmit={handleCompareScenarios} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Scenario A Card */}
                  <div className="p-4 bg-slate-50/70 border border-slate-200 rounded-2xl space-y-3.5">
                    <div className="flex items-center justify-between border-b border-slate-200/80 pb-2">
                      <div className="flex items-center gap-2">
                        <span className="w-6 h-6 rounded-full bg-indigo-600 text-white text-xs font-bold flex items-center justify-center">
                          A
                        </span>
                        <span className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                          Scenario A (Baseline)
                        </span>
                      </div>
                      <span className="text-[11px] text-slate-500 font-medium">Standard Parameters</span>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-[11px] font-semibold text-slate-600 mb-1">Product Category</label>
                        <select
                          value={categoryA}
                          onChange={(e) => setCategoryA(e.target.value)}
                          className="w-full text-xs border border-slate-200 rounded-lg px-2.5 py-1.5 bg-white focus:outline-none focus:border-indigo-500 font-medium"
                        >
                          <option value="Technology">Technology</option>
                          <option value="Furniture">Furniture</option>
                          <option value="Office Supplies">Office Supplies</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-[11px] font-semibold text-slate-600 mb-1">Customer Region</label>
                        <select
                          value={regionA}
                          onChange={(e) => setRegionA(e.target.value)}
                          className="w-full text-xs border border-slate-200 rounded-lg px-2.5 py-1.5 bg-white focus:outline-none focus:border-indigo-500 font-medium"
                        >
                          <option value="East">East</option>
                          <option value="West">West</option>
                          <option value="Central">Central</option>
                          <option value="South">South</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-[11px] font-semibold text-slate-600 mb-1">Quantity (Units)</label>
                        <input
                          type="number"
                          min="1"
                          max="1000"
                          value={quantityA}
                          onChange={(e) => setQuantityA(Math.max(1, parseInt(e.target.value) || 1))}
                          className="w-full text-xs border border-slate-200 rounded-lg px-2.5 py-1.5 bg-white focus:outline-none focus:border-indigo-500 font-medium"
                        />
                      </div>

                      <div>
                        <label className="block text-[11px] font-semibold text-slate-600 mb-1">
                          Discount: <span className="font-bold text-indigo-700">{discountPctA}%</span>
                        </label>
                        <input
                          type="range"
                          min="0"
                          max="100"
                          step="5"
                          value={discountPctA}
                          onChange={(e) => setDiscountPctA(parseInt(e.target.value) || 0)}
                          className="w-full accent-indigo-600 mt-1 cursor-pointer"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Scenario B Card */}
                  <div className="p-4 bg-violet-50/40 border border-violet-200/80 rounded-2xl space-y-3.5">
                    <div className="flex items-center justify-between border-b border-violet-200/60 pb-2">
                      <div className="flex items-center gap-2">
                        <span className="w-6 h-6 rounded-full bg-violet-600 text-white text-xs font-bold flex items-center justify-center">
                          B
                        </span>
                        <span className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                          Scenario B (Counterfactual)
                        </span>
                      </div>
                      <button
                        type="button"
                        onClick={copyScenarioAToB}
                        className="text-[11px] text-indigo-700 hover:text-indigo-900 font-semibold flex items-center gap-1 bg-white hover:bg-indigo-50 px-2 py-0.5 rounded-md border border-indigo-200 shadow-2xs transition-colors cursor-pointer"
                        title="Copy all inputs from Scenario A to Scenario B"
                      >
                        <Copy className="w-3 h-3" />
                        <span>Copy from A</span>
                      </button>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-[11px] font-semibold text-slate-600 mb-1">Product Category</label>
                        <select
                          value={categoryB}
                          onChange={(e) => setCategoryB(e.target.value)}
                          className="w-full text-xs border border-slate-200 rounded-lg px-2.5 py-1.5 bg-white focus:outline-none focus:border-indigo-500 font-medium"
                        >
                          <option value="Technology">Technology</option>
                          <option value="Furniture">Furniture</option>
                          <option value="Office Supplies">Office Supplies</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-[11px] font-semibold text-slate-600 mb-1">Customer Region</label>
                        <select
                          value={regionB}
                          onChange={(e) => setRegionB(e.target.value)}
                          className="w-full text-xs border border-slate-200 rounded-lg px-2.5 py-1.5 bg-white focus:outline-none focus:border-indigo-500 font-medium"
                        >
                          <option value="East">East</option>
                          <option value="West">West</option>
                          <option value="Central">Central</option>
                          <option value="South">South</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-[11px] font-semibold text-slate-600 mb-1">Quantity (Units)</label>
                        <input
                          type="number"
                          min="1"
                          max="1000"
                          value={quantityB}
                          onChange={(e) => setQuantityB(Math.max(1, parseInt(e.target.value) || 1))}
                          className="w-full text-xs border border-slate-200 rounded-lg px-2.5 py-1.5 bg-white focus:outline-none focus:border-indigo-500 font-medium"
                        />
                      </div>

                      <div>
                        <label className="block text-[11px] font-semibold text-slate-600 mb-1">
                          Discount: <span className="font-bold text-violet-700">{discountPctB}%</span>
                        </label>
                        <input
                          type="range"
                          min="0"
                          max="100"
                          step="5"
                          value={discountPctB}
                          onChange={(e) => setDiscountPctB(parseInt(e.target.value) || 0)}
                          className="w-full accent-violet-600 mt-1 cursor-pointer"
                        />
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex justify-end pt-2">
                  <button
                    type="submit"
                    disabled={isComparing}
                    className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-300 text-white text-xs font-semibold rounded-xl flex items-center gap-2 transition-all cursor-pointer shadow-xs"
                  >
                    {isComparing ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Analyzing Scenarios with SHAP...</span>
                      </>
                    ) : (
                      <>
                        <GitCompare className="w-4 h-4" />
                        <span>Compare Scenarios with SHAP</span>
                      </>
                    )}
                  </button>
                </div>
              </form>

              {comparisonError && (
                <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl flex items-center gap-3 text-xs text-rose-800">
                  <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />
                  <span>{comparisonError}</span>
                </div>
              )}

              {/* Side-by-Side Outcome Cards */}
              {comparisonResult && (
                <div className="space-y-6 pt-2">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {/* Card A */}
                    <div className="p-5 bg-slate-50 border border-slate-200 rounded-2xl relative overflow-hidden">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-700 bg-indigo-100 px-2 py-0.5 rounded-full">
                          Scenario A
                        </span>
                        <span className="text-xs text-slate-500 font-mono">Baseline</span>
                      </div>
                      <div className="text-2xl font-black text-slate-900 mt-3">
                        <AmountDisplay amount={comparisonResult.predicted_sales_a} />
                      </div>
                      <p className="text-xs text-slate-500 mt-1">
                        {comparisonResult.scenario_a.feature_contributions.find(f => f.feature === 'Category')?.input_value} •{' '}
                        {comparisonResult.scenario_a.feature_contributions.find(f => f.feature === 'Region')?.input_value} •{' '}
                        {comparisonResult.scenario_a.feature_contributions.find(f => f.feature === 'Quantity')?.input_value} •{' '}
                        {comparisonResult.scenario_a.feature_contributions.find(f => f.feature === 'Discount')?.input_value}
                      </p>
                    </div>

                    {/* Card B */}
                    <div className="p-5 bg-violet-50/50 border border-violet-200 rounded-2xl relative overflow-hidden">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-violet-700 bg-violet-100 px-2 py-0.5 rounded-full">
                          Scenario B
                        </span>
                        <span className="text-xs text-violet-600 font-mono">Counterfactual</span>
                      </div>
                      <div className="text-2xl font-black text-slate-900 mt-3">
                        <AmountDisplay amount={comparisonResult.predicted_sales_b} />
                      </div>
                      <p className="text-xs text-slate-500 mt-1">
                        {comparisonResult.scenario_b.feature_contributions.find(f => f.feature === 'Category')?.input_value} •{' '}
                        {comparisonResult.scenario_b.feature_contributions.find(f => f.feature === 'Region')?.input_value} •{' '}
                        {comparisonResult.scenario_b.feature_contributions.find(f => f.feature === 'Quantity')?.input_value} •{' '}
                        {comparisonResult.scenario_b.feature_contributions.find(f => f.feature === 'Discount')?.input_value}
                      </p>
                    </div>

                    {/* Net Delta Card */}
                    <div className={`p-5 rounded-2xl border ${
                      comparisonResult.absolute_difference > 0
                        ? 'bg-emerald-50/70 border-emerald-200'
                        : comparisonResult.absolute_difference < 0
                        ? 'bg-rose-50/70 border-rose-200'
                        : 'bg-slate-50 border-slate-200'
                    }`}>
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-700 bg-white/80 px-2 py-0.5 rounded-full border border-slate-200">
                          Net Shift (B − A)
                        </span>
                        <span className="text-[11px] font-semibold text-slate-600">
                          {comparisonResult.changed_features_count} {comparisonResult.changed_features_count === 1 ? 'Feature' : 'Features'} Changed
                        </span>
                      </div>
                      <div className="flex items-baseline gap-2 mt-3">
                        <div className={`text-2xl font-black ${
                          comparisonResult.absolute_difference > 0
                            ? 'text-emerald-700'
                            : comparisonResult.absolute_difference < 0
                            ? 'text-rose-700'
                            : 'text-slate-700'
                        }`}>
                          {comparisonResult.absolute_difference > 0 ? '+' : ''}
                          {symbol}{comparisonResult.absolute_difference.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                        </div>
                        <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                          comparisonResult.percentage_difference > 0
                            ? 'bg-emerald-100 text-emerald-800'
                            : comparisonResult.percentage_difference < 0
                            ? 'bg-rose-100 text-rose-800'
                            : 'bg-slate-100 text-slate-700'
                        }`}>
                          {comparisonResult.percentage_difference > 0 ? '+' : ''}
                          {comparisonResult.percentage_difference.toFixed(1)}%
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-600 mt-1">
                        Model: <strong>{comparisonResult.model_used}</strong>
                      </p>
                    </div>
                  </div>

                  {/* Detailed SHAP Attribution Shift Comparison Table */}
                  <div className="bg-slate-900 text-white rounded-2xl p-6 border border-slate-800 shadow-sm">
                    <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-slate-800 gap-3">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="p-1.5 bg-indigo-500/20 text-indigo-400 rounded-lg">
                            <Sparkles className="w-4 h-4" />
                          </span>
                          <h4 className="text-sm font-bold text-white tracking-wide">
                            Side-by-Side Explainable AI (SHAP) Attribution Comparison
                          </h4>
                        </div>
                        <p className="text-xs text-slate-400 mt-1">
                          Decomposes the prediction delta into exact feature-level Shapley value shifts. Baseline expectation: <strong className="text-slate-200">{symbol}{comparisonResult.base_value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</strong>
                        </p>
                      </div>
                      <div className="flex items-center gap-2 text-[11px] text-slate-300 bg-slate-800/80 px-3 py-1.5 rounded-xl border border-slate-700">
                        <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                        <span>Explainer: <strong>{comparisonResult.explainer_type}</strong></span>
                        {comparisonResult.is_difference_additive_exact && (
                          <span className="ml-1 text-[10px] font-mono bg-emerald-950 text-emerald-300 px-1.5 py-0.5 rounded border border-emerald-800">
                            Exact Additivity
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="mt-4 overflow-x-auto">
                      <table className="w-full text-left text-xs">
                        <thead className="text-[11px] uppercase tracking-wider text-slate-400 border-b border-slate-800">
                          <tr>
                            <th className="py-2.5 px-3">Feature</th>
                            <th className="py-2.5 px-3">Scenario A (Input &amp; SHAP)</th>
                            <th className="py-2.5 px-3">Scenario B (Input &amp; SHAP)</th>
                            <th className="py-2.5 px-3 text-right">Attribution Shift (Δφ)</th>
                            <th className="py-2.5 px-3 text-center">Status</th>
                            <th className="py-2.5 px-3">Model Mechanics Interpretation</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800/60 font-sans">
                          {comparisonResult.feature_comparisons.map((fc, idx) => (
                            <tr
                              key={idx}
                              className={`transition-colors ${
                                fc.is_changed ? 'bg-indigo-950/20 hover:bg-indigo-950/30' : 'hover:bg-slate-800/30'
                              }`}
                            >
                              <td className="py-3 px-3">
                                <span className="font-semibold text-white">{fc.feature}</span>
                              </td>
                              <td className="py-3 px-3">
                                <span className="text-slate-300 font-medium">{fc.scenario_a_value}</span>
                                <span className="text-[11px] font-mono text-slate-400 ml-2">
                                  ({fc.scenario_a_contribution > 0 ? '+' : ''}{symbol}{fc.scenario_a_contribution.toFixed(2)})
                                </span>
                              </td>
                              <td className="py-3 px-3">
                                <span className="text-slate-300 font-medium">{fc.scenario_b_value}</span>
                                <span className="text-[11px] font-mono text-slate-400 ml-2">
                                  ({fc.scenario_b_contribution > 0 ? '+' : ''}{symbol}{fc.scenario_b_contribution.toFixed(2)})
                                </span>
                              </td>
                              <td className={`py-3 px-3 text-right font-mono font-bold ${
                                fc.contribution_difference > 0
                                  ? 'text-emerald-400'
                                  : fc.contribution_difference < 0
                                  ? 'text-rose-400'
                                  : 'text-slate-400'
                              }`}>
                                {fc.contribution_difference > 0 ? '+' : ''}
                                {symbol}{fc.contribution_difference.toFixed(2)}
                              </td>
                              <td className="py-3 px-3 text-center">
                                {fc.is_changed ? (
                                  <span className="inline-flex items-center text-[10px] font-bold text-amber-300 bg-amber-950/70 border border-amber-800 px-2 py-0.5 rounded-full">
                                    Changed
                                  </span>
                                ) : (
                                  <span className="text-[10px] text-slate-400 bg-slate-800/60 px-2 py-0.5 rounded-full">
                                    Unchanged
                                  </span>
                                )}
                              </td>
                              <td className="py-3 px-3 text-slate-300 text-[11px]">
                                {fc.interpretation}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                    <div className="mt-4 pt-4 border-t border-slate-800 flex flex-col md:flex-row md:items-center justify-between text-xs text-slate-400 gap-2">
                      <div className="flex items-center gap-2">
                        <span className="text-emerald-400 font-semibold">Mathematical Reconciliation:</span>
                        <span>Predicted A ({symbol}{comparisonResult.predicted_sales_a.toFixed(2)})</span>
                        <span>+</span>
                        <span className="text-indigo-300">Net Feature Shift ({comparisonResult.absolute_difference > 0 ? '+' : ''}{symbol}{comparisonResult.absolute_difference.toFixed(2)})</span>
                        <span>=</span>
                        <span className="font-bold text-white">Predicted B ({symbol}{comparisonResult.predicted_sales_b.toFixed(2)})</span>
                      </div>
                      <div className="text-[10px] text-slate-400 italic">
                        *Attributions reflect mathematical dependencies within the trained model, not guaranteed real-world business causality.
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Section 2: Model Training & Comparative Benchmarking */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                <Award className="w-5 h-5 text-indigo-600" />
                Tri-Model Comparative Machine Learning Benchmark
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Evaluates Linear Regression baseline, Random Forest, and XGBoost Regressor on identical chronological test splits without target leakage.
              </p>
            </div>
            <button
              onClick={handleTrainModels}
              disabled={isTraining}
              className="px-4 py-2 bg-slate-900 hover:bg-slate-800 disabled:bg-slate-300 text-white text-xs font-semibold rounded-xl flex items-center gap-2 transition-all cursor-pointer shadow-xs"
            >
              {isTraining ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Training on Server...</span>
                </>
              ) : (
                <span>Benchmark Models</span>
              )}
            </button>
          </div>

          {trainingError && (
            <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl flex items-center gap-3 text-xs text-rose-800">
              <AlertCircle className="w-5 h-5 text-rose-600 shrink-0" />
              <span>{trainingError}</span>
            </div>
          )}

          {trainingResult && (
            <div className="mt-4 space-y-4">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 text-slate-600 uppercase tracking-wider border-b">
                    <tr>
                      <th className="py-2.5 px-4">Algorithm</th>
                      <th className="py-2.5 px-4 text-right">MAE ({symbol})</th>
                      <th className="py-2.5 px-4 text-right">RMSE ({symbol})</th>
                      <th className="py-2.5 px-4 text-right">R² Score</th>
                      <th className="py-2.5 px-4 text-right">Training Time</th>
                      <th className="py-2.5 px-4 text-right">Test Split</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {trainingResult.comparison.map((item, i) => {
                      const modelName = (item.model || (item as Record<string, unknown>)['Model'] || 'Unknown Model') as string;
                      const maeVal = (typeof item.mae === 'number' ? item.mae : (item as Record<string, unknown>)['MAE ($)']);
                      const rmseVal = (typeof item.rmse === 'number' ? item.rmse : (item as Record<string, unknown>)['RMSE ($)']);
                      const r2Val = (typeof item.r2 === 'number' ? item.r2 : (item as Record<string, unknown>)['R² Score']);
                      const durationVal = (typeof item.training_time === 'number' ? item.training_time : (item as Record<string, unknown>)['Training Time (s)']);
                      return (
                        <tr key={i} className="hover:bg-slate-50/50">
                          <td className="py-3 px-4 font-bold text-slate-900">{modelName}</td>
                          <td className="py-3 px-4 text-right font-medium">
                            {typeof maeVal === 'number' ? <AmountDisplay amount={Number(maeVal)} /> : '—'}
                          </td>
                          <td className="py-3 px-4 text-right font-medium">
                            {typeof rmseVal === 'number' ? <AmountDisplay amount={Number(rmseVal)} /> : '—'}
                          </td>
                          <td className={`py-3 px-4 text-right font-bold ${typeof r2Val === 'number' && Number(r2Val) > 0.7 ? 'text-emerald-600' : 'text-indigo-600'}`}>
                            {typeof r2Val === 'number' ? Number(r2Val).toFixed(3) : '—'}
                          </td>
                          <td className="py-3 px-4 text-right text-slate-600 font-mono text-[11px]">
                            {typeof durationVal === 'number' ? `${Number(durationVal).toFixed(3)}s` : '<0.01s'}
                          </td>
                          <td className="py-3 px-4 text-right text-slate-500">20% chronological</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>

        {/* Section 3: Saved Quote History */}
        {quoteHistory.length > 0 && (
          <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
            <div className="p-5 border-b border-slate-200/80 flex items-center gap-2">
              <History className="w-4 h-4 text-indigo-600" />
              <h3 className="text-sm font-bold text-slate-900">Your Saved Quote Simulations</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-600 uppercase tracking-wider border-b">
                  <tr>
                    <th className="py-3 px-6">Quote ID</th>
                    <th className="py-3 px-6">Category</th>
                    <th className="py-3 px-6">Region</th>
                    <th className="py-3 px-6 text-center">Qty</th>
                    <th className="py-3 px-6 text-center">Discount</th>
                    <th className="py-3 px-6 text-right">Predicted Sales ({symbol})</th>
                    <th className="py-3 px-6">Evaluated At</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {quoteHistory.map((q) => (
                    <tr key={q.id} className="hover:bg-slate-50/50">
                      <td className="py-3 px-6 font-mono text-[11px] text-slate-600">{q.id.substring(0, 8)}...</td>
                      <td className="py-3 px-6 font-semibold text-slate-800">{q.category}</td>
                      <td className="py-3 px-6 text-slate-600">{q.region}</td>
                      <td className="py-3 px-6 text-center font-medium">{q.quantity}</td>
                      <td className="py-3 px-6 text-center font-medium">{(Number(q.discount) * 100).toFixed(0)}%</td>
                      <td className="py-3 px-6 text-right font-bold text-slate-900">
                        <AmountDisplay amount={Number(q.predictedSales)} />
                      </td>
                      <td className="py-3 px-6 text-slate-500">{formatDateTime(q.createdAt)}</td>
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
