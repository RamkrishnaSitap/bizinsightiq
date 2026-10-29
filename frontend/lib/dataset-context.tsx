'use client';

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { Dataset } from './types';
import { datasetApi } from './api';
import { useAuth } from './auth-context';

interface DatasetContextType {
  datasets: Dataset[];
  selectedDataset: Dataset | null;
  selectedDatasetId: string | null;
  isLoading: boolean;
  error: string | null;
  selectDataset: (id: string | null) => void;
  refreshDatasets: () => Promise<void>;
}

const DatasetContext = createContext<DatasetContextType | undefined>(undefined);

export function DatasetProvider({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshDatasets = useCallback(async () => {
    if (!isAuthenticated) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await datasetApi.list();
      setDatasets(data);

      // Auto-select the latest VALIDATED dataset if none is selected
      setSelectedDatasetId((prev) => {
        if (prev && data.some((d) => d.id === prev)) {
          return prev;
        }
        const validated = data.find((d) => d.status === 'VALIDATED');
        return validated ? validated.id : data[0]?.id || null;
      });
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load datasets');
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    if (isAuthenticated) {
      refreshDatasets();
    } else {
      setDatasets([]);
      setSelectedDatasetId(null);
    }
  }, [isAuthenticated, refreshDatasets]);

  const selectDataset = (id: string | null) => {
    setSelectedDatasetId(id);
  };

  const selectedDataset = datasets.find((d) => d.id === selectedDatasetId) || null;

  return (
    <DatasetContext.Provider
      value={{
        datasets,
        selectedDataset,
        selectedDatasetId,
        isLoading,
        error,
        selectDataset,
        refreshDatasets,
      }}
    >
      {children}
    </DatasetContext.Provider>
  );
}

export function useDataset() {
  const context = useContext(DatasetContext);
  if (!context) {
    throw new Error('useDataset must be used within a DatasetProvider');
  }
  return context;
}
