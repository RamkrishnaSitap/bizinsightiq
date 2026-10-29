# BizInsightIQ: FastAPI REST API Implementation Guide (Phase 1)

**System Architecture:** Enterprise Polyglot AI/ML Analytics Workbench  
**Component:** Python Machine Learning & Analytics Microservice Layer  
**Target Audience:** Senior Java/Spring Boot Developer & MCA Capstone Evaluators  

---

## 1. Executive Summary & Purpose

Phase 1 establishes a decoupled **REST API layer** on top of BizInsightIQ's existing pure-Python data science modules (`src/`). 

Instead of confining the machine learning models, statistical aggregations, and business heuristic rules strictly inside the single-workstation Streamlit interface, this FastAPI layer exposes them through standard HTTP endpoints.

### Key Architectural Achievements:
1. **Zero Logic Duplication:** The API imports and calls the existing modules in `src/` directly (`data_loader.py`, `validator.py`, `eda.py`, `segmentation.py`, `prediction.py`, `insights.py`). Not a single machine-learning equation or validation rule was duplicated.
2. **Streamlit Independence:** The existing Streamlit dashboard (`app.py`) remains 100% functional, runnable, and independent. It can be started alongside the API without interference.
3. **Enterprise Readiness for Java & Next.js:** Spring Boot 3 (Java 21) can now call these endpoints via Spring's `RestClient` or `WebClient`, while a Next.js frontend can fetch analytical payloads via `fetch` or React Query.
4. **Verified Rigor:** 20 new automated unit and integration tests were added in `tests/test_api.py`. The entire test suite now passes **111 total automated tests** in ~15 seconds.

---

## 2. Target Polyglot Architecture

```text
+-------------------------------------------------------------------------------------------------+
|                                FRONTEND TIER (Phase 4 Target)                                   |
|   Next.js 15 (React 19 + TypeScript + Tailwind CSS + Lucide Icons + Recharts)                   |
+-------------------------------------------------------------------------------------------------+
                                               │
                                               │ HTTPS / JSON REST APIs (JWT Auth)
                                               ▼
+-------------------------------------------------------------------------------------------------+
|                          ENTERPRISE BACKEND TIER (Phase 3 Target)                               |
|   Java 21 & Spring Boot 3.x (Spring Security, Spring Data JPA, RestClient)                      |
|   - Authentication, Authorization (RBAC), and Tenant Isolation                                  |
|   - PostgreSQL 16 persistence for users, datasets, and quote history                            |
+-------------------------------------------------------------------------------------------------+
                                               │
                                               │ Internal JSON REST API (HTTP:8000)
                                               ▼
+-------------------------------------------------------------------------------------------------+
|                        AI / ML SERVICE TIER (Phase 1 Implemented)                              |
|   Python 3.12 & FastAPI + Uvicorn                                                               |
|   ├── api/main.py            --> Application router, CORS, and sanitized exception handlers    |
|   ├── api/schemas.py         --> Pydantic V2 Request & Response models                         |
|   ├── api/deps.py            --> Upload size enforcement (10MB) & buffer parsing               |
|   └── api/routes/            --> Modular endpoints under /api/v1/                              |
+-------------------------------------------------------------------------------------------------+
                                               │
                                               │ Direct Python Module Imports
                                               ▼
+-------------------------------------------------------------------------------------------------+
|                          EXISTING PURE DOMAIN MODULES (src/)                                    |
|   ├── src/data_loader.py     --> Defensive CSV parsing and buffer rewinding                    |
|   ├── src/validator.py       --> 6-step schema and business integrity rules                   |
|   ├── src/eda.py             --> Executive KPIs and statistical aggregations                    |
|   ├── src/segmentation.py    --> K-Means clustering ($k=2..7$) and 2D PCA projection           |
|   ├── src/prediction.py      --> Linear Regression vs. Random Forest Regressor ($R^2$, MAE)    |
|   └── src/insights.py        --> 4-pillar deterministic heuristic decision engine              |
+-------------------------------------------------------------------------------------------------+
```

---

## 3. Package & Directory Structure

```text
BizInsightIQ/
├── api/
│   ├── __init__.py           <-- Package metadata (version 1.0.0)
│   ├── main.py               <-- FastAPI app setup, CORS, global exception handler, router mounting
│   ├── schemas.py            <-- Pydantic request/response models
│   ├── deps.py               <-- Safe CSV extraction & 10 MB payload guard
│   └── routes/
│       ├── __init__.py
│       ├── health.py         <-- GET  /api/v1/health
│       ├── validation.py     <-- POST /api/v1/datasets/validate
│       ├── analytics.py      <-- POST /api/v1/analytics/eda
│       ├── segmentation.py   <-- POST /api/v1/segmentation
│       ├── prediction.py     <-- POST /api/v1/predictions/train & /predict
│       └── insights.py       <-- POST /api/v1/insights
├── src/                      <-- Core ML logic (Completely untouched)
├── tests/
│   ├── test_api.py           <-- 20 new FastAPI endpoint tests
│   └── test_*.py             <-- 91 existing baseline unit tests
├── app.py                    <-- Streamlit UI (Untouched & fully operational)
└── requirements.txt          <-- Updated with fastapi, uvicorn, python-multipart, httpx
```

---

## 4. API Endpoints Specification

Base URL: `http://localhost:8000/api/v1`  
Interactive OpenAPI (Swagger) UI: `http://localhost:8000/docs`  
ReDoc Documentation: `http://localhost:8000/redoc`  

### 4.1 Health Check
* **Route:** `GET /api/v1/health`
* **Purpose:** Liveness and readiness probe for Docker / Kubernetes / Spring Boot health checkers.
* **Response (200 OK):**
```json
{
  "status": "UP",
  "service": "BizInsightIQ AI/ML REST API",
  "version": "1.0.0"
}
```

---

### 4.2 Dataset Validation
* **Route:** `POST /api/v1/datasets/validate`
* **Payload:** `multipart/form-data` with `file: UploadFile` (CSV).
* **Behavior:** Enforces a 10MB file size limit, calls `src.validator.validate_dataset()`.
* **Sample Request (cURL):**
```bash
curl -X POST "http://localhost:8000/api/v1/datasets/validate" \
  -H "accept: application/json" \
  -F "file=@data/sample_sales_data.csv;type=text/csv"
```
* **Response (200 OK):**
```json
{
  "is_valid": true,
  "total_rows": 1200,
  "total_columns": 10,
  "columns_present": ["OrderID", "CustomerID", "OrderDate", "Category", "Region", "Quantity", "UnitPrice", "Discount", "Sales", "Profit"],
  "missing_columns": [],
  "missing_values_by_column": {},
  "duplicate_rows_count": 0,
  "invalid_numeric_counts": {},
  "invalid_date_count": 0,
  "errors": [],
  "warnings": []
}
```

---

### 4.3 Exploratory Data Analysis (EDA)
* **Route:** `POST /api/v1/analytics/eda`
* **Payload:** Optional `file: UploadFile`. If omitted, analyzes the bundled 1,200-row sample dataset.
* **Behavior:** Calculates 8 executive KPIs, monthly trend series, category and regional performance, discount elasticity brackets, and Pearson correlation matrix.
* **Response (200 OK):**
```json
{
  "kpis": {
    "total_sales": 1523983.05,
    "total_profit": 234120.45,
    "total_units": 4580,
    "unique_customers": 150,
    "total_orders": 1200,
    "profit_margin_pct": 15.36,
    "avg_order_value": 1269.99,
    "avg_discount_pct": 9.42
  },
  "trends": [
    {"Period": "2023-01", "Sales": 115200.0, "Profit": 18240.5, "Quantity": 350, "OrderCount": 92, "ProfitMarginPct": 15.83}
  ],
  "category_performance": [
    {"Category": "Technology", "Sales": 836765.9, "Profit": 195804.2, "Quantity": 2150, "OrderCount": 540, "AvgDiscountPct": 8.12, "ProfitMarginPct": 23.4}
  ],
  "regional_performance": [
    {"Region": "East", "Sales": 482100.0, "Profit": 74200.0, "Quantity": 1420, "UniqueCustomers": 62, "ProfitMarginPct": 15.39}
  ],
  "discount_analysis": [
    {"DiscountBracket": ">20% (High Discount)", "OrderCount": 210, "TotalSales": 284100.0, "TotalProfit": -24428.0, "ProfitMarginPct": -8.6}
  ],
  "correlation_matrix": {
    "Sales": {"Sales": 1.0, "Profit": 0.584, "Quantity": 0.612, "Discount": -0.045}
  }
}
```

---

### 4.4 Customer Segmentation (K-Means & PCA)
* **Route:** `POST /api/v1/segmentation`
* **Form Parameters:**
  - `file`: Optional custom CSV.
  - `n_clusters`: Integer ($2 \le k \le 7$, default: 4).
  - `random_state`: Seed for reproducible centroid initialization (default: 42).
  - `evaluate_candidates`: Boolean to include Elbow and Silhouette scores for $k=2..6$ (default: true).
* **Response (200 OK):**
```json
{
  "n_clusters": 4,
  "silhouette_score": 0.3842,
  "inertia": 412.58,
  "pca_variance_ratio": [48.12, 26.45],
  "cluster_profiles": [
    {
      "Cluster": 0,
      "CustomerCount": 38,
      "CustomerPct": 25.33,
      "Recency_Mean": 18.4,
      "Frequency_Mean": 12.2,
      "MonetaryValue_Mean": 18450.2,
      "TotalProfit_Mean": 4210.5,
      "AvgDiscount_Mean": 0.05,
      "ProfitMarginPct_Mean": 22.82,
      "DescriptivePersona": "High-Value Loyalists"
    }
  ],
  "candidates_evaluation": [
    {"k": 2, "Inertia": 684.2, "SilhouetteScore": 0.421},
    {"k": 3, "Inertia": 512.1, "SilhouetteScore": 0.395},
    {"k": 4, "Inertia": 412.58, "SilhouetteScore": 0.3842}
  ]
}
```

---

### 4.5 Sales Prediction (Training & What-If Simulation)

#### A. Train & Benchmark Models (`POST /api/v1/predictions/train`)
* Trains both **Linear Regression** and **Random Forest Regressor** with chronological or random splitting.
* Strictly excludes `Profit` and `UnitPrice` to eliminate target leakage.
* **Response (200 OK):**
```json
{
  "comparison": [
    {"Model": "Linear Regression (Baseline)", "MAE ($)": 312.45, "RMSE ($)": 485.12, "R² Score": 0.724, "Test Samples": 240},
    {"Model": "Random Forest Regressor", "MAE ($)": 185.30, "RMSE ($)": 298.40, "R² Score": 0.885, "Test Samples": 240}
  ],
  "metrics": {
    "linear_regression": {"mae": 312.45, "rmse": 485.12, "r2": 0.724, "test_size": 240, "split_strategy": "chronological"},
    "random_forest": {"mae": 185.30, "rmse": 298.40, "r2": 0.885, "test_size": 240, "split_strategy": "chronological"}
  },
  "metadata": {
    "total_records": 1200,
    "train_size": 960,
    "test_size": 240,
    "split_strategy": "chronological",
    "train_period": "2023-01-02 to 2023-10-22",
    "test_period": "2023-10-23 to 2023-12-30",
    "numeric_features": ["Quantity", "Discount", "Month", "Quarter", "DayOfWeek"],
    "categorical_features": ["Category", "Region"]
  }
}
```

#### B. What-If Scenario Prediction (`POST /api/v1/predictions/predict`)
* **Request JSON:**
```json
{
  "category": "Technology",
  "region": "East",
  "quantity": 10,
  "discount": 0.15,
  "month": 10,
  "quarter": 4,
  "day_of_week": 2
}
```
* **Response (200 OK):**
```json
{
  "predicted_sales": 2450.00,
  "category": "Technology",
  "region": "East",
  "quantity": 10,
  "discount": 0.15,
  "month": 10,
  "quarter": 4,
  "day_of_week": 2,
  "model_used": "Random Forest Regressor"
}
```

---

### 4.6 Business Insights & Recommendations
* **Route:** `POST /api/v1/insights`
* **Form Parameters:** Optional `severity` (`CRITICAL`, `WARNING`, `INFO`) and `category`.
* **Behavior:** Evaluates the 12 deterministic heuristic business rules across all 4 analytical pillars.
* **Response (200 OK):**
```json
{
  "summary": {
    "total_insights": 12,
    "critical_count": 2,
    "warning_count": 5,
    "info_count": 5
  },
  "insights": [
    {
      "insight_id": "INS-DISC-MARGIN-COMPRESSION",
      "category": "Discount Effectiveness",
      "severity": "critical",
      "title": "Severe Margin Collapse in High-Discount Tier (>20%)",
      "evidence": {
        "high_discount_margin_pct": -8.6,
        "zero_discount_margin_pct": 21.4,
        "margin_delta": 30.0
      },
      "recommendation": "Cap standard promotional discount thresholds at 15%. Require executive approval for discounts exceeding 20%.",
      "limitations": "Correlation does not establish causal necessity; item-level cost accounting audits should be conducted before adjusting pricing tiers."
    }
  ]
}
```

---

## 5. Java / Spring Boot Comparison Guide

For a senior Java developer transitioning to Python, here is how FastAPI concepts map to familiar Spring Boot constructs:

| Spring Boot 3 Concept | FastAPI Equivalent in BizInsightIQ | Explanation |
| :--- | :--- | :--- |
| `@RestController` | `APIRouter()` in `api/routes/*.py` | Defines a collection of HTTP-exposed endpoints. |
| `@GetMapping` / `@PostMapping` | `@router.get(...)` / `@router.post(...)` | Maps HTTP verbs to handler functions. |
| Java 17 `record` / DTO | Pydantic `BaseModel` in `api/schemas.py` | Strongly-typed request/response data contracts with automatic validation. |
| `@Valid` / Bean Validation | Automatic Pydantic validation | Invalid numbers or out-of-range floats automatically return `422 Unprocessable Entity`. |
| `@ExceptionHandler` / `@ControllerAdvice` | `@app.exception_handler(Exception)` | Global safe exception filter that sanitizes error outputs and hides stack traces. |
| `MultipartFile` | `UploadFile = File(...)` | Handles incoming binary file streams without reading the entire file into memory at once. |
| Spring `RestClient` / `WebClient` | HTTP client calling FastAPI | Spring Boot will call `restClient.post().uri("/api/v1/predictions/predict").body(dto).retrieve().body(PredictionResult.class)`. |

---

## 6. How to Run & Verify the API

### Prerequisites
Activate the project's virtual environment in PowerShell:
```powershell
cd D:\PROJECTS_Workspace_2026\MCA_AI_ML_Project_and_Report\BizInsightIQ
```

### Start the API Server:
```powershell
.\.venv\Scripts\uvicorn.exe api.main:app --host 127.0.0.1 --port 8000 --reload
```
Once started, open your browser:
* **Interactive Swagger UI:** [`http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs)
* **ReDoc Documentation:** [`http://127.0.0.1:8000/redoc`](http://127.0.0.1:8000/redoc)

### Run the Automated API Test Suite:
```powershell
.\.venv\Scripts\pytest.exe tests/test_api.py -v
```

### Run the Entire Test Suite (111 Tests):
```powershell
.\.venv\Scripts\pytest.exe -v
```

### Start the Streamlit Dashboard (In parallel on a separate port):
```powershell
.\.venv\Scripts\streamlit.exe run app.py
```

---

## 7. Security & Enterprise Boundary Considerations

1. **Upload File Limits:** Enforces a hard 10 MB payload limit to prevent denial-of-service (DoS) via memory exhaustion (`MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024`).
2. **Error Sanitization:** Unhandled runtime exceptions are intercepted by `global_exception_handler`, ensuring Windows filesystem paths (`D:\...`), environment configurations, and stack traces are never leaked in client responses.
3. **No Premature Authentication:** Authentication is deliberately deferred to Spring Security (Phase 3). FastAPI is designed to run in a private network or container sidecar where Spring Boot acts as the public-facing API Gateway.
4. **Stateless Inference:** All prediction and clustering endpoints are stateless, allowing the FastAPI process to scale horizontally behind a load balancer.
