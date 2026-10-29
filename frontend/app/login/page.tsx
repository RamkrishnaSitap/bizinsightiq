'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';
import { BrainCircuit, Lock, User, AlertCircle, Loader2, Eye, EyeOff } from 'lucide-react';

export default function LoginPage() {
  const { login, isAuthenticated, isLoading: authLoading } = useAuth();
  const router = useRouter();

  const [username, setUsername] = useState('ramkrishna');
  const [password, setPassword] = useState('Password@123');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      router.replace('/dashboard');
    }
  }, [authLoading, isAuthenticated, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      await login(username.trim(), password);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Invalid username or password. Please try again.';
      setError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col justify-center items-center p-4 selection:bg-indigo-500 selection:text-white">
      {/* Brand Header */}
      <div className="flex items-center gap-3 mb-8">
        <div className="p-3 bg-indigo-600 rounded-2xl shadow-lg shadow-indigo-600/30 text-white">
          <BrainCircuit className="w-8 h-8" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">BizInsightIQ</h1>
          <p className="text-xs text-indigo-400 font-medium">Enterprise AI/ML Retail Intelligence Platform</p>
        </div>
      </div>

      {/* Login Card */}
      <div className="w-full max-w-md bg-slate-800/90 border border-slate-700/80 rounded-2xl p-8 shadow-2xl backdrop-blur-md">
        <div className="mb-6">
          <h2 className="text-xl font-bold text-white">Sign In to Dashboard</h2>
          <p className="text-xs text-slate-400 mt-1">Authenticate using your Spring Boot credentials to access analytical engines.</p>
        </div>

        {error && (
          <div className="mb-5 p-3.5 bg-rose-950/60 border border-rose-800/80 rounded-xl flex items-start gap-2.5 text-xs text-rose-200">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">Authentication Failed</p>
              <p className="text-rose-300 mt-0.5">{error}</p>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5 uppercase tracking-wider">
              Username
            </label>
            <div className="relative">
              <User className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="e.g. data_analyst"
                className="w-full bg-slate-900/80 border border-slate-700 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5 uppercase tracking-wider">
              Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
              <input
                type={showPassword ? 'text' : 'password'}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full bg-slate-900/80 border border-slate-700 rounded-xl pl-10 pr-10 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3.5 top-3 text-slate-400 hover:text-slate-200 transition-colors focus:outline-none"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
                title={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full mt-2 py-3 px-4 bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-800/60 text-white text-sm font-semibold rounded-xl shadow-lg shadow-indigo-600/30 flex items-center justify-center gap-2 transition-all cursor-pointer disabled:cursor-not-allowed"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Authenticating...</span>
              </>
            ) : (
              <span>Sign In with Spring Boot JWT</span>
            )}
          </button>
        </form>

        {/* Demo Credentials Box */}
        <div className="mt-6 pt-5 border-t border-slate-700/60 text-xs text-slate-400">
          <p className="font-semibold text-slate-300 mb-1">Development Test Shortcuts (Flyway Seeded):</p>
          <div className="grid grid-cols-2 gap-2 mt-2">
            <button
              type="button"
              onClick={() => {
                setUsername('ramkrishna');
                setPassword('Password@123');
              }}
              className="p-2 bg-slate-900/60 hover:bg-slate-900 border border-slate-700 rounded-lg text-left transition-colors"
            >
              <p className="font-medium text-slate-200">Lead Analyst</p>
              <p className="text-[10px] text-indigo-400">ramkrishna (Analyst)</p>
            </button>
            <button
              type="button"
              onClick={() => {
                setUsername('admin');
                setPassword('Password@123');
              }}
              className="p-2 bg-slate-900/60 hover:bg-slate-900 border border-slate-700 rounded-lg text-left transition-colors"
            >
              <p className="font-medium text-slate-200">System Admin</p>
              <p className="text-[10px] text-amber-400">admin (Admin)</p>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
