'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  BarChart3,
  Users,
  TrendingUp,
  Lightbulb,
  Database,
  LogOut,
  BrainCircuit,
  FileSpreadsheet,
} from 'lucide-react';
import { useAuth } from '@/lib/auth-context';
import { useDataset } from '@/lib/dataset-context';

export default function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const { datasets, selectedDatasetId, selectDataset } = useDataset();

  const navItems = [
    { name: 'Datasets & Upload', href: '/dashboard', icon: Database },
    { name: 'Exploratory EDA', href: '/eda', icon: BarChart3 },
    { name: 'Customer Segmentation', href: '/segmentation', icon: Users },
    { name: 'Sales Prediction & Quotes', href: '/predictions', icon: TrendingUp },
    { name: 'Decision Insights', href: '/insights', icon: Lightbulb },
  ];

  return (
    <aside className="w-64 bg-slate-900 text-slate-200 flex flex-col min-h-screen border-r border-slate-800">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-6 border-b border-slate-800 gap-3">
        <div className="p-2 bg-indigo-600 rounded-lg text-white">
          <BrainCircuit className="w-5 h-5" />
        </div>
        <div>
          <h1 className="font-bold text-lg text-white leading-tight">BizInsightIQ</h1>
          <p className="text-xs text-indigo-400 font-medium">AI & ML Analytics Platform</p>
        </div>
      </div>

      {/* Dataset Context Selector */}
      <div className="px-4 py-4 border-b border-slate-800 bg-slate-900/60">
        <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
          <FileSpreadsheet className="w-3.5 h-3.5 text-indigo-400" />
          Active Dataset
        </label>
        {datasets.length === 0 ? (
          <p className="text-xs text-slate-500 italic">No datasets uploaded yet</p>
        ) : (
          <select
            value={selectedDatasetId || ''}
            onChange={(e) => selectDataset(e.target.value || null)}
            className="w-full text-xs bg-slate-800 border border-slate-700 text-white rounded px-2.5 py-1.5 focus:outline-none focus:border-indigo-500 font-medium truncate"
          >
            {datasets.map((d) => (
              <option key={d.id} value={d.id}>
                {d.name} ({d.totalRows ? `${d.totalRows} rows` : d.status})
              </option>
            ))}
          </select>
        )}
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* User Info & Logout Footer */}
      <div className="p-4 border-t border-slate-800 bg-slate-950/40">
        <div className="flex items-center justify-between mb-2">
          <div className="truncate">
            <p className="text-sm font-semibold text-white truncate">{user?.username || 'Analyst'}</p>
            <p className="text-xs text-slate-400 truncate">{user?.email || 'authenticated'}</p>
          </div>
          <span className="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800">
            {user?.role?.replace('ROLE_', '') || 'USER'}
          </span>
        </div>
        <button
          onClick={logout}
          className="w-full flex items-center justify-center gap-2 mt-2 px-3 py-2 text-xs font-semibold text-rose-300 hover:text-rose-100 bg-rose-950/40 hover:bg-rose-900/60 border border-rose-800/40 rounded-lg transition-colors"
        >
          <LogOut className="w-3.5 h-3.5" />
          Sign Out
        </button>
      </div>
    </aside>
  );
}
