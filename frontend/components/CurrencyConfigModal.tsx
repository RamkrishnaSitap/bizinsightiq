'use client';

import React, { useState } from 'react';
import { useCurrency, CurrencyCode, RateMode } from '@/lib/currency-context';
import { Settings, X, Check, RefreshCw, Sparkles, HelpCircle } from 'lucide-react';

interface CurrencyConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function CurrencyConfigModal({ isOpen, onClose }: CurrencyConfigModalProps) {
  const {
    currency,
    setCurrency,
    exchangeRate,
    setExchangeRate,
    rateMode,
    setRateMode,
    formatCurrency,
    getHoverDetails,
  } = useCurrency();

  const [inputRate, setInputRate] = useState(exchangeRate.toString());
  const [rateError, setRateError] = useState('');

  if (!isOpen) return null;

  const handleSaveRate = (e: React.FormEvent) => {
    e.preventDefault();
    const parsed = parseFloat(inputRate);
    if (isNaN(parsed) || parsed <= 0) {
      setRateError('Please enter a positive numeric exchange rate.');
      return;
    }
    setRateError('');
    setExchangeRate(parsed);
  };

  const handleResetDefaults = () => {
    setCurrency('INR');
    setExchangeRate(83.0);
    setInputRate('83.0');
    setRateMode('nominal');
    setRateError('');
  };

  const sampleAmount = 1522871.14;
  const hoverPreview = getHoverDetails(sampleAmount);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4 animate-in fade-in duration-150">
      <div className="bg-white rounded-2xl border border-slate-200/90 shadow-2xl max-w-lg w-full overflow-hidden">
        {/* Header */}
        <div className="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-indigo-100 text-indigo-700 rounded-xl">
              <Settings className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900">Currency & Display Configuration</h3>
              <p className="text-xs text-slate-500">Configure Indian Rupee (₹), US Dollar ($), and hover text</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-6">
          {/* Section 1: Active Currency Choice */}
          <div>
            <label className="block text-xs font-bold text-slate-800 uppercase tracking-wider mb-2">
              Primary Currency Display Mode
            </label>
            <div className="grid grid-cols-3 gap-2.5">
              <button
                type="button"
                onClick={() => setCurrency('INR')}
                className={`p-3 rounded-xl border text-center transition-all cursor-pointer ${
                  currency === 'INR'
                    ? 'border-indigo-600 bg-indigo-50/60 text-indigo-900 font-bold shadow-xs'
                    : 'border-slate-200 hover:border-slate-300 text-slate-700 font-medium'
                }`}
              >
                <div className="text-lg font-bold">₹ INR</div>
                <div className="text-[11px] text-slate-500 mt-0.5">Rupee (Default)</div>
              </button>

              <button
                type="button"
                onClick={() => setCurrency('USD')}
                className={`p-3 rounded-xl border text-center transition-all cursor-pointer ${
                  currency === 'USD'
                    ? 'border-indigo-600 bg-indigo-50/60 text-indigo-900 font-bold shadow-xs'
                    : 'border-slate-200 hover:border-slate-300 text-slate-700 font-medium'
                }`}
              >
                <div className="text-lg font-bold">$ USD</div>
                <div className="text-[11px] text-slate-500 mt-0.5">US Dollar</div>
              </button>

              <button
                type="button"
                onClick={() => setCurrency('BOTH')}
                className={`p-3 rounded-xl border text-center transition-all cursor-pointer ${
                  currency === 'BOTH'
                    ? 'border-indigo-600 bg-indigo-50/60 text-indigo-900 font-bold shadow-xs'
                    : 'border-slate-200 hover:border-slate-300 text-slate-700 font-medium'
                }`}
              >
                <div className="text-lg font-bold">₹ & $</div>
                <div className="text-[11px] text-slate-500 mt-0.5">Dual Display</div>
              </button>
            </div>
          </div>

          {/* Section 2: Exchange Rate & Calculation Mode */}
          <div className="pt-2 border-t border-slate-100">
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                Calculation Mode
              </label>
              <div className="flex items-center gap-1 text-[11px] text-slate-500">
                <HelpCircle className="w-3.5 h-3.5" />
                <span>Conversion or Direct 1:1</span>
              </div>
            </div>

            <div className="space-y-2">
              <label className="flex items-start gap-3 p-2.5 rounded-xl border border-slate-200 hover:bg-slate-50/50 cursor-pointer">
                <input
                  type="radio"
                  name="rateMode"
                  checked={rateMode === 'nominal'}
                  onChange={() => setRateMode('nominal')}
                  className="mt-0.5 text-indigo-600 focus:ring-indigo-500"
                />
                <div>
                  <span className="text-xs font-bold text-slate-900">Direct Nominal Display (1:1 Base Units)</span>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    Renders dataset values directly in the selected currency without multiplying.
                  </p>
                </div>
              </label>

              <label className="flex items-start gap-3 p-2.5 rounded-xl border border-slate-200 hover:bg-slate-50/50 cursor-pointer">
                <input
                  type="radio"
                  name="rateMode"
                  checked={rateMode === 'converted'}
                  onChange={() => setRateMode('converted')}
                  className="mt-0.5 text-indigo-600 focus:ring-indigo-500"
                />
                <div>
                  <span className="text-xs font-bold text-slate-900">Convert Using Exchange Rate (USD ↔ INR)</span>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    Converts base USD transaction values to Rupees using the configured rate below.
                  </p>
                </div>
              </label>
            </div>

            {/* Exchange Rate Input */}
            <form onSubmit={handleSaveRate} className="mt-3 flex items-center gap-2">
              <span className="text-xs font-semibold text-slate-600 shrink-0">1 USD = ₹</span>
              <input
                type="number"
                step="0.01"
                min="0.1"
                value={inputRate}
                onChange={(e) => setInputRate(e.target.value)}
                className="w-28 px-3 py-1.5 border border-slate-300 rounded-lg text-xs font-semibold focus:outline-hidden focus:ring-2 focus:ring-indigo-500 text-slate-900"
              />
              <button
                type="submit"
                className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-bold transition-colors cursor-pointer"
              >
                Update Rate
              </button>
            </form>
            {rateError && <p className="text-xs text-rose-600 mt-1">{rateError}</p>}
          </div>

          {/* Section 3: Live Preview & Mouseover Text Demonstration */}
          <div className="pt-2 border-t border-slate-100">
            <div className="flex items-center gap-1.5 mb-2 text-xs font-bold text-slate-800 uppercase tracking-wider">
              <Sparkles className="w-3.5 h-3.5 text-amber-500" />
              <span>Live Formatting & Hover Text Preview</span>
            </div>

            <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200/80 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-600">Sample Value:</span>
                <span className="text-base font-extrabold text-slate-900">
                  {formatCurrency(sampleAmount)}
                </span>
              </div>

              <div className="pt-2 border-t border-slate-200/80 text-[11px]">
                <span className="font-bold text-slate-700 block mb-0.5">🗣️ On Mouseover (Words):</span>
                <p className="text-indigo-900 font-medium bg-white p-2 rounded-lg border border-indigo-100 leading-relaxed">
                  {hoverPreview.inWords}
                </p>
                {hoverPreview.alternateText && (
                  <p className="text-slate-500 mt-1 text-[10px]">
                    💱 Equivalent: {hoverPreview.alternateText}
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-100 bg-slate-50 flex items-center justify-between">
          <button
            type="button"
            onClick={handleResetDefaults}
            className="flex items-center gap-1 text-xs text-slate-600 hover:text-slate-900 font-semibold cursor-pointer"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Reset Defaults</span>
          </button>

          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition-colors cursor-pointer"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
