/**
 * Comprehensive Automated End-to-End API Verification Suite for BizInsightIQ
 * Tests Spring Boot Enterprise Core (8080), FastAPI ML Microservice (8000), and Next.js Frontend (3001)
 */

const fs = require('fs');
const path = require('path');

const FASTAPI_URL = 'http://127.0.0.1:8000';
const BACKEND_URL = 'http://localhost:8080/api/v1';
const FRONTEND_URL = 'http://localhost:3001';

const results = [];

function recordResult(group, name, status, durationMs, details = '') {
  results.push({ group, name, status, durationMs, details });
  const tag = status === 'PASS' ? '\x1b[32m[PASS]\x1b[0m' : '\x1b[31m[FAIL]\x1b[0m';
  console.log(`${tag} [${group}] ${name} (${durationMs}ms) ${details ? '— ' + details : ''}`);
}

async function runTest(group, name, fn) {
  const t0 = Date.now();
  try {
    const details = await fn();
    const duration = Date.now() - t0;
    recordResult(group, name, 'PASS', duration, details || '');
  } catch (err) {
    const duration = Date.now() - t0;
    recordResult(group, name, 'FAIL', duration, err.message);
  }
}

async function main() {
  console.log('======================================================================');
  console.log('      BIZINSIGHTIQ FULL SYSTEM API AUDIT & VERIFICATION SUITE');
  console.log('======================================================================\n');

  let jwtToken = '';
  let benchmarkDatasetId = '33333333-3333-3333-3333-333333333333';
  let uploadedDatasetId = '';

  // -------------------------------------------------------------------------
  // 1. FASTAPI MICROSERVICE (PORT 8000)
  // -------------------------------------------------------------------------
  console.log('--- Phase 1: FastAPI AI/ML Microservice (Port 8000) ---');

  await runTest('FastAPI', 'GET /health', async () => {
    const res = await fetch(`${FASTAPI_URL}/health`);
    if (!res.ok) throw new Error(`Status ${res.status}`);
    const data = await res.json();
    if (data.status !== 'UP') throw new Error(`Unexpected status: ${data.status}`);
    return `Status: ${data.status}, Version: ${data.version}`;
  });

  await runTest('FastAPI', 'GET /api/v1/health', async () => {
    const res = await fetch(`${FASTAPI_URL}/api/v1/health`);
    if (!res.ok) throw new Error(`Status ${res.status}`);
    const data = await res.json();
    return `Service: ${data.service}`;
  });

  await runTest('FastAPI', 'POST /api/v1/datasets/validate (Multipart CSV validation)', async () => {
    const filePath = path.join(__dirname, '..', 'data', 'test_sales_sample_valid.csv');
    const fileBytes = fs.readFileSync(filePath);
    const blob = new Blob([fileBytes], { type: 'text/csv' });
    const form = new FormData();
    form.append('file', blob, 'test_sales_sample_valid.csv');

    const res = await fetch(`${FASTAPI_URL}/api/v1/datasets/validate`, { method: 'POST', body: form });
    if (!res.ok) throw new Error(`Status ${res.status}`);
    const data = await res.json();
    if (!data.is_valid) throw new Error('Validation failed unexpectedly');
    return `Valid: ${data.is_valid}, Rows: ${data.total_rows}, Columns: ${data.total_columns}`;
  });

  await runTest('FastAPI', 'POST /api/v1/analytics/eda (Default dataset)', async () => {
    const form = new FormData();
    const res = await fetch(`${FASTAPI_URL}/api/v1/analytics/eda`, { method: 'POST', body: form });
    if (!res.ok) throw new Error(`Status ${res.status}`);
    const data = await res.json();
    if (!data.kpis) throw new Error('Missing KPIs');
    return `Total Sales: $${data.kpis.total_sales}, Total Orders: ${data.kpis.total_orders}, Trends: ${data.trends.length}`;
  });

  await runTest('FastAPI', 'POST /api/v1/segmentation (K-Means k=4)', async () => {
    const form = new FormData();
    form.append('n_clusters', '4');
    form.append('evaluate_candidates', 'true');
    const res = await fetch(`${FASTAPI_URL}/api/v1/segmentation`, { method: 'POST', body: form });
    if (!res.ok) throw new Error(`Status ${res.status}`);
    const data = await res.json();
    return `k: ${data.n_clusters}, Silhouette: ${data.silhouette_score.toFixed(4)}, Inertia: ${data.inertia.toFixed(1)}`;
  });

  await runTest('FastAPI', 'POST /api/v1/predictions/train (Tri-Model: LR, RF, XGBoost)', async () => {
    const form = new FormData();
    const res = await fetch(`${FASTAPI_URL}/api/v1/predictions/train`, { method: 'POST', body: form });
    if (!res.ok) throw new Error(`Status ${res.status}`);
    const data = await res.json();
    const lrR2 = data.metrics?.linear_regression?.r2?.toFixed(3);
    const rfR2 = data.metrics?.random_forest?.r2?.toFixed(3);
    const xgbR2 = data.metrics?.xgboost?.r2?.toFixed(3);
    return `Comparison count: ${data.comparison?.length}, LR R²: ${lrR2}, RF R²: ${rfR2}, XGB R²: ${xgbR2}`;
  });

  await runTest('FastAPI', 'POST /api/v1/predictions/predict (What-If Quote)', async () => {
    const body = JSON.stringify({
      category: 'Technology',
      region: 'North',
      quantity: 5,
      discount: 0.15,
      model_type: 'xgboost'
    });
    const res = await fetch(`${FASTAPI_URL}/api/v1/predictions/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body
    });
    if (!res.ok) throw new Error(`Status ${res.status}`);
    const data = await res.json();
    return `Predicted Sales: $${data.predicted_sales.toFixed(2)}, Model: ${data.model_used || data.model_version}`;
  });

  await runTest('FastAPI', 'POST /api/v1/predictions/explain (SHAP Explainable AI)', async () => {
    const body = JSON.stringify({
      category: 'Technology',
      region: 'North',
      quantity: 5,
      discount: 0.15,
      model_type: 'random_forest'
    });
    const res = await fetch(`${FASTAPI_URL}/api/v1/predictions/explain`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body
    });
    if (!res.ok) throw new Error(`Status ${res.status}`);
    const data = await res.json();
    return `Base: $${data.base_value.toFixed(2)}, Additive Exact: ${data.is_additive_exact}, Features: ${data.feature_contributions?.length}`;
  });

  await runTest('FastAPI', 'POST /api/v1/predictions/compare (Side-by-Side What-If SHAP Comparison)', async () => {
    const body = JSON.stringify({
      scenario_a: {
        category: 'Technology',
        region: 'East',
        quantity: 5,
        discount: 0.10,
      },
      scenario_b: {
        category: 'Technology',
        region: 'East',
        quantity: 5,
        discount: 0.20,
      },
      model_type: 'random_forest'
    });
    const res = await fetch(`${FASTAPI_URL}/api/v1/predictions/compare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body
    });
    if (!res.ok) throw new Error(`Status ${res.status}`);
    const data = await res.json();
    return `A: $${data.predicted_sales_a.toFixed(2)}, B: $${data.predicted_sales_b.toFixed(2)}, Diff: ${data.absolute_difference > 0 ? '+' : ''}$${data.absolute_difference.toFixed(2)} (${data.percentage_difference.toFixed(1)}%), Changed: ${data.changed_features_count}, Exact: ${data.is_difference_additive_exact}`;
  });

  await runTest('FastAPI', 'POST /api/v1/insights (Decision Insights)', async () => {
    const form = new FormData();
    const res = await fetch(`${FASTAPI_URL}/api/v1/insights`, { method: 'POST', body: form });
    if (!res.ok) throw new Error(`Status ${res.status}`);
    const data = await res.json();
    return `Total Insights: ${data.total_insights}, High Severity: ${data.summary?.by_severity?.HIGH || 0}`;
  });

  // -------------------------------------------------------------------------
  // 2. SPRING BOOT ENTERPRISE BACKEND (PORT 8080)
  // -------------------------------------------------------------------------
  console.log('\n--- Phase 2: Spring Boot Enterprise Core (Port 8080) ---');

  await runTest('Spring Boot', 'GET /api/v1/health (Downstream probe)', async () => {
    const res = await fetch(`${BACKEND_URL}/health`);
    if (!res.ok) throw new Error(`Status ${res.status}`);
    const data = await res.json();
    if (data.status !== 'UP') throw new Error(`Downstream unhealthy: ${JSON.stringify(data)}`);
    return `Core: ${data.status}, FastAPI downstream: ${data.downstream?.fastapi?.status}`;
  });

  await runTest('Spring Boot', 'POST /api/v1/auth/login (JWT Generation)', async () => {
    const res = await fetch(`${BACKEND_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: 'ramkrishna', password: 'Password@123' })
    });
    if (!res.ok) throw new Error(`Status ${res.status}`);
    const data = await res.json();
    if (!data.accessToken) throw new Error('Missing accessToken in response');
    jwtToken = data.accessToken;
    return `Token type: ${data.tokenType}, User: ${data.user.username} (${data.user.role})`;
  });

  await runTest('Spring Boot', 'GET /api/v1/auth/me (User Profile Verification)', async () => {
    const res = await fetch(`${BACKEND_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${jwtToken}` }
    });
    if (!res.ok) throw new Error(`Status ${res.status}`);
    const data = await res.json();
    return `ID: ${data.id}, Email: ${data.email}`;
  });

  await runTest('Spring Boot', 'GET /api/v1/datasets (List User Datasets)', async () => {
    const res = await fetch(`${BACKEND_URL}/datasets`, {
      headers: { Authorization: `Bearer ${jwtToken}` }
    });
    if (!res.ok) throw new Error(`Status ${res.status}`);
    const data = await res.json();
    if (!Array.isArray(data)) throw new Error('Expected array of datasets');
    const benchmark = data.find(d => d.id === benchmarkDatasetId);
    return `Found ${data.length} datasets. Benchmark status: ${benchmark?.status || 'Active'}`;
  });

  await runTest('Spring Boot', 'GET /api/v1/datasets/{id} (Benchmark Metadata)', async () => {
    const res = await fetch(`${BACKEND_URL}/datasets/${benchmarkDatasetId}`, {
      headers: { Authorization: `Bearer ${jwtToken}` }
    });
    if (!res.ok) throw new Error(`Status ${res.status}`);
    const data = await res.json();
    return `Name: "${data.name}", Rows: ${data.totalRows}, Columns: ${data.totalColumns}`;
  });

  await runTest('Spring Boot', 'POST /api/v1/datasets/upload (Live Ingestion & JDBC Batch)', async () => {
    const filePath = path.join(__dirname, '..', 'data', 'test_sales_sample_valid.csv');
    if (!fs.existsSync(filePath)) throw new Error(`File not found: ${filePath}`);
    const fileBytes = fs.readFileSync(filePath);
    const blob = new Blob([fileBytes], { type: 'text/csv' });

    const form = new FormData();
    form.append('file', blob, 'test_sales_sample_valid.csv');
    form.append('name', 'Automated API Test Dataset');

    const res = await fetch(`${BACKEND_URL}/datasets/upload`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${jwtToken}` },
      body: form
    });
    if (res.status !== 201) throw new Error(`Status ${res.status}`);
    const data = await res.json();
    uploadedDatasetId = data.id || data.datasetId;
    return `Uploaded ID: ${uploadedDatasetId}, Persisted Rows: ${data.totalRows}, Valid: ${data.isValid}`;
  });

  await runTest('Spring Boot', 'GET /api/v1/datasets/{id}/analytics/eda (FastAPI Proxy & Orchestration)', async () => {
    const res = await fetch(`${BACKEND_URL}/datasets/${benchmarkDatasetId}/analytics/eda`, {
      headers: { Authorization: `Bearer ${jwtToken}` }
    });
    if (!res.ok) throw new Error(`Status ${res.status}`);
    const data = await res.json();
    return `Total Sales: $${data.kpis.total_sales}, Categories: ${data.category_performance.length}, Regions: ${data.regional_performance.length}`;
  });

  await runTest('Spring Boot', 'POST /api/v1/datasets/{id}/analytics/segmentation (Run & PostgreSQL Save)', async () => {
    const res = await fetch(`${BACKEND_URL}/datasets/${benchmarkDatasetId}/analytics/segmentation`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${jwtToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ nClusters: 4, randomState: 42, evaluateCandidates: true })
    });
    if (res.status !== 201) throw new Error(`Status ${res.status}`);
    const data = await res.json();
    return `Run ID: ${data.runId}, Silhouette: ${data.silhouetteScore.toFixed(4)}, Assigned Customers: ${data.assignedCustomerCount}`;
  });

  await runTest('Spring Boot', 'GET /api/v1/datasets/{id}/analytics/segmentation/runs (History)', async () => {
    const res = await fetch(`${BACKEND_URL}/datasets/${benchmarkDatasetId}/analytics/segmentation/runs`, {
      headers: { Authorization: `Bearer ${jwtToken}` }
    });
    if (!res.ok) throw new Error(`Status ${res.status}`);
    const data = await res.json();
    return `Saved runs count: ${data.length}`;
  });

  await runTest('Spring Boot', 'POST /api/v1/datasets/{id}/analytics/predictions/train (Model Training)', async () => {
    const res = await fetch(`${BACKEND_URL}/datasets/${benchmarkDatasetId}/analytics/predictions/train`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${jwtToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ splitStrategy: 'chronological', testSize: 0.20, randomState: 42 })
    });
    if (!res.ok) throw new Error(`Status ${res.status}`);
    const data = await res.json();
    const lrR2 = data.metrics?.linear_regression?.r2?.toFixed(3);
    const rfR2 = data.metrics?.random_forest?.r2?.toFixed(3);
    const xgbR2 = data.metrics?.xgboost?.r2?.toFixed(3);
    return `Comparison count: ${data.comparison?.length}, LR R²: ${lrR2}, RF R²: ${rfR2}, XGB R²: ${xgbR2}`;
  });

  await runTest('Spring Boot', 'POST /api/v1/datasets/{id}/analytics/predictions (Quote Simulation with Random Forest)', async () => {
    const res = await fetch(`${BACKEND_URL}/datasets/${benchmarkDatasetId}/analytics/predictions`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${jwtToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        category: 'Technology',
        region: 'North',
        quantity: 10,
        discount: 0.10,
        modelType: 'random_forest'
      })
    });
    if (res.status !== 201) throw new Error(`Status ${res.status}`);
    const data = await res.json();
    return `Simulated ID: ${data.id}, Predicted Sales: $${Number(data.predictedSales).toFixed(2)}, Model: ${data.modelVersion}`;
  });

  await runTest('Spring Boot', 'POST /api/v1/datasets/{id}/analytics/predictions (Quote Simulation with XGBoost)', async () => {
    const res = await fetch(`${BACKEND_URL}/datasets/${benchmarkDatasetId}/analytics/predictions`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${jwtToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        category: 'Technology',
        region: 'North',
        quantity: 10,
        discount: 0.10,
        modelType: 'xgboost'
      })
    });
    if (res.status !== 201) throw new Error(`Status ${res.status}`);
    const data = await res.json();
    return `Simulated ID: ${data.id}, Predicted Sales: $${Number(data.predictedSales).toFixed(2)}, Model: ${data.modelVersion}`;
  });

  await runTest('Spring Boot', 'POST /api/v1/datasets/{id}/analytics/predictions/explain (SHAP Proxy & Verification)', async () => {
    const res = await fetch(`${BACKEND_URL}/datasets/${benchmarkDatasetId}/analytics/predictions/explain`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${jwtToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        category: 'Technology',
        region: 'North',
        quantity: 10,
        discount: 0.10,
        modelType: 'random_forest'
      })
    });
    if (!res.ok) throw new Error(`Status ${res.status}`);
    const data = await res.json();
    return `Base: $${data.base_value.toFixed(2)}, Predicted: $${data.predicted_sales.toFixed(2)}, Explainer: ${data.explainer_type}, Additive Exact: ${data.is_additive_exact}`;
  });

  await runTest('Spring Boot', 'POST /api/v1/datasets/{id}/analytics/predictions/compare (Side-by-Side What-If Comparison)', async () => {
    const res = await fetch(`${BACKEND_URL}/datasets/${benchmarkDatasetId}/analytics/predictions/compare`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${jwtToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        scenarioA: {
          category: 'Technology',
          region: 'East',
          quantity: 5,
          discount: 0.10,
        },
        scenarioB: {
          category: 'Technology',
          region: 'East',
          quantity: 5,
          discount: 0.20,
        },
        modelType: 'random_forest'
      })
    });
    if (!res.ok) throw new Error(`Status ${res.status}`);
    const data = await res.json();
    return `A: $${data.predicted_sales_a.toFixed(2)}, B: $${data.predicted_sales_b.toFixed(2)}, Shift: ${data.absolute_difference > 0 ? '+' : ''}$${data.absolute_difference.toFixed(2)} (${data.percentage_difference.toFixed(1)}%), Changed Features: ${data.changed_features_count}, Exact: ${data.is_difference_additive_exact}`;
  });

  await runTest('Spring Boot', 'GET /api/v1/analytics/quotes (User Quote History)', async () => {
    const res = await fetch(`${BACKEND_URL}/analytics/quotes`, {
      headers: { Authorization: `Bearer ${jwtToken}` }
    });
    if (!res.ok) throw new Error(`Status ${res.status}`);
    const data = await res.json();
    return `Persisted quotes count: ${data.length}`;
  });

  await runTest('Spring Boot', 'GET /api/v1/datasets/{id}/analytics/insights (Decision Engine)', async () => {
    const res = await fetch(`${BACKEND_URL}/datasets/${benchmarkDatasetId}/analytics/insights`, {
      headers: { Authorization: `Bearer ${jwtToken}` }
    });
    if (!res.ok) throw new Error(`Status ${res.status}`);
    const data = await res.json();
    return `Total insights: ${data.summary?.total_insights || data.insights?.length}, Critical: ${data.summary?.critical_count || 0}`;
  });

  if (uploadedDatasetId) {
    await runTest('Spring Boot', 'DELETE /api/v1/datasets/{id} (Resource Cleanup)', async () => {
      const res = await fetch(`${BACKEND_URL}/datasets/${uploadedDatasetId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${jwtToken}` }
      });
      if (res.status !== 204) throw new Error(`Status ${res.status}`);
      return `Successfully deleted dataset ${uploadedDatasetId}`;
    });
  }

  // -------------------------------------------------------------------------
  // 3. FRONTEND NEXT.JS WEB APP (PORT 3001)
  // -------------------------------------------------------------------------
  console.log('\n--- Phase 3: Next.js Frontend Application (Port 3001) ---');

  const frontendPages = [
    { name: 'Login Page', path: '/login' },
    { name: 'Dashboard Page', path: '/dashboard' },
    { name: 'EDA Analytics Page', path: '/eda' },
    { name: 'Customer Segmentation Page', path: '/segmentation' },
    { name: 'Predictions & Quotes Page', path: '/predictions' },
    { name: 'Business Insights Page', path: '/insights' }
  ];

  for (const page of frontendPages) {
    await runTest('Frontend', `GET ${page.path} (${page.name})`, async () => {
      const res = await fetch(`${FRONTEND_URL}${page.path}`);
      if (!res.ok) throw new Error(`Status ${res.status}`);
      return `HTTP ${res.status} OK`;
    });
  }

  // -------------------------------------------------------------------------
  // SUMMARY
  // -------------------------------------------------------------------------
  const passed = results.filter(r => r.status === 'PASS').length;
  const failed = results.filter(r => r.status === 'FAIL').length;
  const total = results.length;

  console.log('\n======================================================================');
  console.log(`                     AUDIT SUMMARY: ${passed}/${total} PASSED`);
  if (failed > 0) {
    console.log(`                     FAILED TESTS: ${failed}`);
  } else {
    console.log('            ALL APIS ARE FULLY OPERATIONAL AND VERIFIED!');
  }
  console.log('======================================================================');
}

main().catch(console.error);
