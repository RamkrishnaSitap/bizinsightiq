'use client';

import React, { useState } from 'react';
import { useAuth } from '@/lib/auth-context';
import { useDataset } from '@/lib/dataset-context';
import { useCurrency } from '@/lib/currency-context';
import CurrencyConfigModal from './CurrencyConfigModal';
import { ShieldCheck, Database, CheckCircle2, Settings } from 'lucide-react';

export default function Navbar({ title }: { title: string }) {
  const { user } = useAuth();
  const { selectedDataset } = useDataset();
  const { currency, setCurrency } = useCurrency();
  const [isConfigOpen, setIsConfigOpen] = useState(false);

  return (
    <>
      <header className="h-16 bg-white border-b border-slate-200 px-8 flex items-center justify-between sticky top-0 z-10 shadow-xs">
        <div>
          <h2 className="text-xl font-bold text-slate-900">{title}</h2>
        </div>

        <div className="flex items-center gap-4">
          {/* Currency Switcher */}
          <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200/80 text-xs gap-0.5">
            <button
              type="button"
              onClick={() => setCurrency('INR')}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-lg font-bold transition-all cursor-pointer ${
                currency === 'INR'
                  ? 'bg-indigo-600 text-white shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
              title="Display amounts in Indian Rupees (₹) [Default]"
            >
              <span>₹ INR</span>
            </button>
            <button
              type="button"
              onClick={() => setCurrency('USD')}
              className={`flex items-center gap-1 px-2.5 py-1 rounded-lg font-bold transition-all cursor-pointer ${
                currency === 'USD'
                  ? 'bg-indigo-600 text-white shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
              title="Display amounts in US Dollars ($)"
            >
              <span>$ USD</span>
            </button>
            <button
              type="button"
              onClick={() => setCurrency('BOTH')}
              className={`flex items-center gap-1 px-2 py-1 rounded-lg font-bold transition-all cursor-pointer ${
                currency === 'BOTH'
                  ? 'bg-indigo-600 text-white shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
              title="Display amounts in both Rupees and Dollars (₹ & $)"
            >
              <span>₹ & $</span>
            </button>
            <button
              type="button"
              onClick={() => setIsConfigOpen(true)}
              className="p-1.5 text-slate-500 hover:text-indigo-600 hover:bg-slate-200/70 rounded-lg transition-colors cursor-pointer"
              title="Configure currency rates, calculation mode, and mouseover settings"
            >
              <Settings className="w-3.5 h-3.5" />
            </button>
          </div>

        {/* Active Dataset Indicator */}
        {selectedDataset ? (
          <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-200 text-emerald-800 px-3 py-1.5 rounded-full text-xs font-medium">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
            <span className="truncate max-w-[200px]">Active: {selectedDataset.name}</span>
          </div>
        ) : (
          <div className="flex items-center gap-2 bg-amber-50 border border-amber-200 text-amber-800 px-3 py-1.5 rounded-full text-xs font-medium">
            <Database className="w-3.5 h-3.5 text-amber-600" />
            <span>No dataset selected</span>
          </div>
        )}

        {/* User Identity Indicator */}
        <div className="flex items-center gap-2 text-xs text-slate-600 bg-slate-100 px-3 py-1.5 rounded-lg border border-slate-200">
          <ShieldCheck className="w-4 h-4 text-indigo-600" />
          <span>Principal: <strong className="text-slate-800">{user?.username}</strong></span>
        </div>
      </div>
    </header>
    <CurrencyConfigModal isOpen={isConfigOpen} onClose={() => setIsConfigOpen(false)} />
  </>
);
}
