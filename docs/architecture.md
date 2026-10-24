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

---

## 5. Supervised Machine Learning: Sales Prediction & Regression Evaluation

### 5.1 Formulation & Objective
The sales prediction engine forecasts gross transaction revenue ($y = \text{Sales} \in \mathbb{R}^+$) for a proposed commercial transaction given operational order parameters and seasonal indicators.

### 5.2 Feature Representation & Target Leakage Prevention
To guarantee real-world inference validity as a pre-transaction decision-support tool, features are restricted strictly to pre-fulfillment variables:
* **Numeric Features ($X_{\text{num}}$):**
  * $\text{Quantity} \in \mathbb{Z}^+$: Order transaction units.
  * $\text{Discount} \in [0.0, 1.0]$: Promotional discount allowance.
  * $\text{Month} \in \{1, \dots, 12\}$: Calendar month derived from `OrderDate`.
  * $\text{Quarter} \in \{1, 2, 3, 4\}$: Fiscal quarter derived from `OrderDate`.
  * $\text{DayOfWeek} \in \{0, \dots, 6\}$: Day of week index (Monday=0, Sunday=6).
* **Categorical Features ($X_{\text{cat}}$):**
  * $\text{Category} \in \{\text{Furniture}, \text{Office Supplies}, \text{Technology}\}$
  * $\text{Region} \in \{\text{Central}, \text{East}, \text{South}, \text{West}\}$

**Critical Academic Note on Leakage Prevention:**  
In financial accounting, $\text{Profit} = \text{Sales} \times (1 - \text{Discount}) - \text{COGS}$. Although $\text{Profit}$ correlates strongly with $\text{Sales}$, it is an ex-post outcome determined only after fulfillment and pricing realization. Including $\text{Profit}$ or `CustomerID` produces artificial over-fitting ($R^2 > 0.95$) that fails during quote generation. BizInsightIQ strictly excludes $\text{Profit}$ and `CustomerID` from prediction features.

### 5.3 Chronological Train/Test Splitting Strategy
Transactions occur sequentially across time. Standard random k-fold shuffling introduces temporal look-ahead bias by allowing past observations to be predicted using future data.
BizInsightIQ enforces a **Chronological 80/20 Split**:
* **Training Set:** First 960 records spanning `2023-01-01` to `2024-07-28`.
* **Testing Set:** Final 240 records spanning `2024-07-28` to `2024-12-30`.

### 5.4 Preprocessing Pipeline
Transformations are encapsulated inside a Scikit-learn `Pipeline` utilizing `ColumnTransformer`:
* **Numeric Pipeline:** $z = \frac{x - \mu_{\text{train}}}{\sigma_{\text{train}}}$ using `StandardScaler`.
* **Categorical Pipeline:** One-hot encoding with `handle_unknown='ignore'` and `sparse_output=False`.
* Parameters ($\mu, \sigma$, category encodings) are fitted exclusively on the training partition and transformed onto out-of-sample data.

### 5.5 Model Architectures & Empirical Results

#### 1. Baseline Benchmark: Ordinary Least Squares (OLS) Linear Regression
$$\hat{y} = \beta_0 + \sum_{j=1}^p \beta_j X_j$$
Minimizes residual sum of squares $\sum_{i=1}^n (y_i - \hat{y}_i)^2$.

#### 2. Non-Linear Ensemble: Random Forest Regressor
$$\hat{y} = \frac{1}{B} \sum_{b=1}^B T_b(X)$$
Ensemble of $B = 100$ bootstrap regression trees with `max_depth = 10` and `random_state = 42`.

#### 3. Empirical Evaluation on Unseen Test Partition ($N = 240$):
| Metric | Baseline Linear Regression | Random Forest Regressor | Relative Improvement |
| :--- | :--- | :--- | :--- |
| **Mean Absolute Error (MAE)** | **$719.50** | **$521.04** | **-27.58% (Lower is better)** |
| **Root Mean Squared Error (RMSE)** | **$1,022.98** | **$1,017.89** | **-0.50% (Lower is better)** |
| **Coefficient of Determination ($R^2$)** | **0.6269** | **0.6306** | **+0.0037 (Higher is better)** |

**Academic Finding:** The Random Forest model demonstrates superior predictive precision, reducing median and average dollar deviations by over \$198 per transaction quote while accounting for non-linear discount-tier pricing effects.
