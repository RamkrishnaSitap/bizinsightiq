# BizInsightIQ — System Architecture & Extensibility Design

**Project Name:** BizInsightIQ  
**Academic Title:** BizInsightIQ: An AI-Powered Business Intelligence, Customer Segmentation, and Predictive Analytics System  
**Document Purpose:** Architectural Specification & Extensibility Reference for MCA Project Report

---

## 1. Architectural Philosophy: Strict Separation of Concerns

To satisfy both academic rigor and enterprise-grade software standards, BizInsightIQ enforces strict decoupling between:
1. **User Interface Layer:** Responsible only for state display, charts, and user interactions.
2. **Backend Coordination Layer:** Responsible for business routing, orchestration, and API gateway logic.
3. **Machine Learning & Analytical Core:** Pure, framework-agnostic Python functions operating on standard data types (DataFrames, arrays, dictionaries).
4. **Data Access & Persistence Layer:** Clearly isolated repository boundary supporting both offline CSV operation and relational databases (PostgreSQL).

```
                      +-----------------------------+
                      |   Presentation Layer        |
                      |   • Streamlit (Primary MVP) |
                      |   • Next.js + Tailwind (v2) |
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |   Orchestration Layer       |
                      |   • Spring Boot REST Gateway|
                      |   • FastAPI ML Endpoints    |
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |   Domain / ML Engine (src/) |
                      |   • Data Ingestion & Schema |
                      |   • Exploratory Data (EDA)  |
                      |   • K-Means Segmentation    |
                      |   • Regression Forecasting  |
                      |   • Evaluation & Metrics    |
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |   Data Persistence Layer    |
                      |   • Local CSV Repository    |
                      |   • PostgreSQL (Optional v2)|
                      +-----------------------------+
```

---

## 2. Layer Responsibilities & Service Contracts

### 2.1 Domain & ML Core (`src/`)
* **Framework Independence:** Contains zero imports from Streamlit, FastAPI, Flask, or Spring Boot.
* **Deterministic Behavior:** Every function takes explicit inputs, performs pure transformations, and returns structured objects or DataFrames.
* **Immutability:** Input DataFrames are never modified in-place.
* **Modules:**
  * `src/data_loader.py`: Safe CSV loading with IO stream support.
  * `src/validator.py`: Comprehensive schema and numeric boundary verification.
  * `src/eda.py`: Aggregation algorithms for KPIs, chronological trends, category/regional metrics, and discount-profit correlations.
  * `src/segmentation.py` *(Day 3)*: Unsupervised clustering service encapsulating feature scaling, elbow curve, silhouette analysis, and customer persona profiling.
  * `src/prediction.py` *(Day 4)*: Supervised regression service encapsulating feature engineering, train/test split, model training (Linear Regression, Random Forest), and what-if simulation.
  * `src/evaluation.py` *(Day 4/5)*: Standardized regression and clustering evaluation metrics ($R^2$, RMSE, MAE, Silhouette).

### 2.2 Presentation Layer
* **Primary (Streamlit):** Direct offline workstation for academic viva defense. Calls `src/` modules natively. Guarantees 100% offline demonstration reliability.
* **Target Extension (Next.js + Tailwind CSS):** Consumes REST APIs via standard JSON contracts.

### 2.3 Backend API Layer
* **Target Extension (FastAPI):** Exposes `src/` functions over versioned HTTP routes (`/api/v1/eda`, `/api/v1/segmentation`, `/api/v1/predict`).
* **Target Extension (Java 21 + Spring Boot 3):** Enterprise gateway providing request validation and database coordination.

---

## 3. Extensibility Design (Future-Proofing)

1. **Algorithm Swapping:** Customer segmentation is exposed via an abstract service interface. K-Means is the default implementation; DBSCAN, Hierarchical Clustering, or Gaussian Mixture Models can be added without altering UI or API schemas.
2. **Model Extensibility:** Predictive modeling accepts an estimator strategy. Linear Regression and Random Forest can be extended to XGBoost or LightGBM seamlessly.
3. **Database Independence:** Analytical routines consume validated in-memory DataFrames. The data source can be switched from local CSV to PostgreSQL or cloud data lakes without rewriting analytical logic.

---

## 4. Customer Segmentation Methodology & Mathematical Formulation

### 4.1 Feature Engineering & Aggregation
To discover customer behavioral segments, raw transaction records are aggregated into an RFM+ observation vector per unique customer:
* **Recency ($R$):** $R = \text{Date}_{\text{benchmark}} - \max(\text{OrderDate}_i)$, where $\text{Date}_{\text{benchmark}}$ is deterministically fixed to one day post-dataset maximum (`2024-12-31`).
* **Frequency ($F$):** Total transaction rows associated with customer.  
  *(Academic Note: Transaction-row count serves as a proxy for frequency due to the absence of a distinct `OrderID` in the source schema).*
* **Monetary Value ($M$):** $\sum \text{Sales}_i$
* **Total Profit ($P$):** $\sum \text{Profit}_i$
* **Average Discount ($D$):** $\frac{1}{N} \sum \text{Discount}_i$
* **Total Quantity ($Q$):** $\sum \text{Quantity}_i$

### 4.2 Feature Standardization
Because features operate on drastically different numerical scales (e.g. Sales in thousands of dollars vs Discount in decimals), features are normalized using z-score standardization:
$$z = \frac{x - \mu}{\sigma}$$
Zero-variance features are automatically pruned prior to scaling.

### 4.3 K-Means Optimization & Diagnostics
* **Objective Function:** Minimize Within-Cluster Sum of Squares (Inertia):
  $$J = \sum_{j=1}^{k} \sum_{x_i \in C_j} ||x_i - \mu_j||^2$$
* **Silhouette Analysis:** Evaluates cohesion and separation:
  $$s(i) = \frac{b(i) - a(i)}{\max(a(i), b(i))}$$
  where $a(i)$ is mean intra-cluster distance and $b(i)$ is mean nearest-cluster distance.
* **Dimensionality Reduction for Visualization:** Multi-dimensional cluster boundaries are projected onto 2D space using Principal Component Analysis (PCA) preserving the largest variance eigenvectors.
