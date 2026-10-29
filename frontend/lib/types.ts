/**
 * Type definitions matching Spring Boot REST API DTOs and database models.
 */

export interface UserProfile {
  id: string;
  username: string;
  email: string;
  role: string;
}

export interface AuthResponse {
  accessToken: string;
  tokenType: string;
  expiresIn: number;
  user: UserProfile;
  token?: string;
  type?: string;
  username?: string;
  email?: string;
  role?: string;
}

export interface Dataset {
  id: string;
  name: string;
  originalFilename: string;
  status: 'PENDING' | 'VALIDATED' | 'FAILED';
  totalRows: number | null;
  totalColumns: number | null;
  isValid: boolean | null;
  uploadedAt?: string;
  createdAt?: string;
}

export interface UploadDatasetResponse {
  id?: string;
  datasetId?: string;
  name: string;
  originalFilename: string;
  status: string;
  totalRows: number;
  totalColumns?: number;
  validRows?: number;
  invalidRows?: number;
  isValid: boolean;
  errors: string[];
  warnings: string[];
  message?: string;
  uploadedAt?: string;
  createdAt?: string;
}

export interface BusinessKPIs {
  total_sales: number;
  total_profit: number;
  total_units: number;
  unique_customers: number;
  total_orders: number;
  profit_margin_pct: number;
  avg_order_value: number;
  avg_discount_pct: number;
}

export interface EDATrendItem {
  period?: string;
  year_month?: string;
  Period?: string;
  sales?: number;
  Sales?: number;
  profit?: number;
  Profit?: number;
  quantity?: number;
  Quantity?: number;
  order_count?: number;
  OrderCount?: number;
  profit_margin_pct?: number;
  ProfitMarginPct?: number;
  [key: string]: unknown;
}

export interface EDACategoryItem {
  category?: string;
  Category?: string;
  sales?: number;
  Sales?: number;
  profit?: number;
  Profit?: number;
  quantity?: number;
  Quantity?: number;
  order_count?: number;
  OrderCount?: number;
  avg_discount_pct?: number;
  AvgDiscountPct?: number;
  profit_margin_pct?: number;
  ProfitMarginPct?: number;
  [key: string]: unknown;
}

export interface EDARegionalItem {
  region?: string;
  Region?: string;
  sales?: number;
  Sales?: number;
  profit?: number;
  Profit?: number;
  quantity?: number;
  Quantity?: number;
  customers?: number;
  UniqueCustomers?: number;
  profit_margin_pct?: number;
  ProfitMarginPct?: number;
  [key: string]: unknown;
}

export interface EDADiscountItem {
  discount_bucket?: string;
  DiscountBracket?: string;
  sales?: number;
  TotalSales?: number;
  profit?: number;
  TotalProfit?: number;
  profit_margin?: number;
  ProfitMarginPct?: number;
  order_count?: number;
  OrderCount?: number;
  [key: string]: unknown;
}

export interface EDAResponse {
  kpis: BusinessKPIs;
  trends: EDATrendItem[];
  category_performance: EDACategoryItem[];
  regional_performance: EDARegionalItem[];
  discount_analysis: EDADiscountItem[];
  correlation_matrix: Record<string, Record<string, number>>;
}

export interface ClusterProfile {
  Cluster: number;
  CustomerCount: number;
  CustomerPct: number;
  DescriptivePersona: string;
  Recency_Mean?: number;
  MeanRecencyDays?: number;
  Frequency_Mean?: number;
  MeanFrequency?: number;
  MonetaryValue_Mean?: number;
  MeanSales?: number;
  TotalSales?: number;
  TotalProfit_Mean?: number;
  MeanProfit?: number;
  TotalProfit?: number;
  AvgDiscount_Mean?: number;
  MeanDiscountPct?: number;
  ProfitMarginPct_Mean?: number;
  ProfitMarginPct?: number;
  MeanUnits?: number;
  [key: string]: unknown;
}

export interface CandidateEvaluation {
  k: number;
  Inertia: number;
  SilhouetteScore: number;
}

export interface SegmentationRunResponse {
  runId: string;
  datasetId: string;
  nClusters: number;
  silhouetteScore: number;
  inertia: number;
  pcaVarianceRatio: number[];
  clusterProfiles: ClusterProfile[];
  candidatesEvaluation: CandidateEvaluation[] | null;
  assignedCustomerCount: number;
  createdAt: string;
}

export interface SegmentationRunHistory {
  id: string;
  datasetId: string;
  kClusters: number;
  silhouetteScore: number;
  inertia: number;
  algorithmVersion: string;
  createdAt: string;
}

export interface RegressionMetrics {
  mae: number;
  rmse: number;
  r2: number;
  test_size: number;
  split_strategy: string;
  training_time?: number;
}

export interface PredictionTrainingResponse {
  comparison: Array<{
    model?: string;
    mae?: number;
    rmse?: number;
    r2?: number;
    training_time?: number;
    [key: string]: unknown;
  }>;
  metrics: Record<string, RegressionMetrics>;
  metadata: Record<string, unknown>;
}

export interface QuoteSimulationRequest {
  category: string;
  region: string;
  quantity: number;
  discount: number;
  month?: number;
  quarter?: number;
  dayOfWeek?: number;
  modelType?: string;
}

export interface QuoteSimulationResponse {
  id: string;
  userId: string;
  datasetId: string | null;
  category: string;
  region: string;
  quantity: number;
  discount: number;
  predictedSales: number;
  modelVersion: string;
  createdAt: string;
}

export interface FeatureContribution {
  feature: string;
  input_value: string;
  contribution: number;
  direction: 'increased' | 'decreased' | 'neutral';
  interpretation: string;
  percentage_impact: number;
}

export interface PredictionExplanationResponse {
  predicted_sales: number;
  base_value: number;
  model_used: string;
  dataset_id: string | null;
  success: boolean;
  feature_contributions: FeatureContribution[];
  additive_sum: number;
  is_additive_exact: boolean;
  explainer_type: string;
  disclaimer: string;
}

export interface FeatureComparisonItem {
  feature: string;
  scenario_a_value: string;
  scenario_b_value: string;
  is_changed: boolean;
  scenario_a_contribution: number;
  scenario_b_contribution: number;
  contribution_difference: number;
  direction: 'increased' | 'decreased' | 'unchanged';
  interpretation: string;
}

export interface ScenarioComparisonResponse {
  scenario_a: PredictionExplanationResponse;
  scenario_b: PredictionExplanationResponse;
  predicted_sales_a: number;
  predicted_sales_b: number;
  absolute_difference: number;
  percentage_difference: number;
  changed_features_count: number;
  feature_comparisons: FeatureComparisonItem[];
  is_difference_additive_exact: boolean;
  explainer_type: string;
  base_value: number;
  model_used: string;
  dataset_id: string | null;
  success: boolean;
  disclaimer: string;
}

export interface CompareScenariosRequest {
  scenarioA: QuoteSimulationRequest;
  scenarioB: QuoteSimulationRequest;
  modelType?: string;
}

export interface InsightItem {
  insight_id: string;
  category: string;
  severity: 'critical' | 'warning' | 'info';
  title: string;
  evidence: Record<string, unknown>;
  recommendation: string;
  limitations: string;
}

export interface InsightsSummary {
  total_insights: number;
  critical_count: number;
  warning_count: number;
  info_count: number;
}

export interface InsightsResponse {
  summary: InsightsSummary;
  insights: InsightItem[];
}

export interface ApiError {
  status: number;
  error: string;
  message: string;
  path?: string;
  validationErrors?: Record<string, string>;
}
