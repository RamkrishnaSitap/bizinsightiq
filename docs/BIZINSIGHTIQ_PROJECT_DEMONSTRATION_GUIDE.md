# BIZINSIGHTIQ: 10-STEP VIVA VOCE PROJECT DEMONSTRATION SCRIPT & EXAMINER GUIDE

**Degree:** Master of Computer Applications (MCA) — Capstone Project  
**Institution:** Centre for Distance and Online Education (CDOE), Lovely Professional University  
**Project Title:** BizInsightIQ: An Enterprise AI-Powered Business Intelligence, Customer Segmentation, and Predictive Analytics System  
**Verified Architecture:** Next.js (:3001) $\\rightarrow$ Spring Boot (:8080) $\\rightarrow$ FastAPI (:8000) $\\rightarrow$ PostgreSQL 17 (:5432)  

---

## 1. System Prerequisites & Startup Verification

Before initiating the viva examination or project demonstration, ensure all four architectural tiers are active and responding.

### Service Ports & Health Probe Checklist

| Architectural Tier | Service Technology | Network Port | Health Probe URL | Expected Healthy Output |
| :--- | :--- | :---: | :--- | :--- |
| **Tier 4: Persistence** | PostgreSQL 17 DBMS | `5432` | `pg_isready -h localhost -p 5432` | `accepting connections` |
| **Tier 3: AI/ML Service** | FastAPI / Python 3.12 | `8000` | `http://localhost:8000/health` | `{"status":"UP","version":"1.0.0"}` |
| **Tier 2: Backend Core** | Spring Boot 3 / Java 21 | `8080` | `http://localhost:8080/api/v1/health` | `{"status":"UP","downstream":{"fastApi":"UP"}}` |
| **Tier 1: Frontend UI** | Next.js 14 / React 18 | `3001` | `http://localhost:3001` | HTTP 200 Login Page |

### Startup Commands (Reference Only — Daemons Pre-Configured)

```powershell
# 1. Start PostgreSQL (Native Windows Service)
net start postgresql-x64-17

# 2. Start FastAPI AI/ML Microservice (Terminal 1)
cd D:\PROJECTS_Workspace_2026\MCA_AI_ML_Project_and_Report\BizInsightIQ
.\.venv\Scripts\uvicorn api.main:app --host 127.0.0.1 --port 8000

# 3. Start Spring Boot Enterprise Core (Terminal 2)
cd D:\PROJECTS_Workspace_2026\MCA_AI_ML_Project_and_Report\BizInsightIQ\backend
mvn spring-boot:run

# 4. Start Next.js Frontend Presentation Layer (Terminal 3)
cd D:\PROJECTS_Workspace_2026\MCA_AI_ML_Project_and_Report\BizInsightIQ\frontend
npm run dev
```

### Demonstration Credentials
- **Role:** Commercial Sales Analyst (Default Test Account)
- **Email:** `analyst@bizinsightiq.com`
- **Password:** `analyst123`
- **Benchmark Dataset:** Pre-loaded *Bundled Benchmark Retail Sales (1,200 Rows)*

---

## 2. The 10-Step Live Demonstration Walkthrough

```
[ Step 1: Login ] 
       |
[ Step 2: Upload CSV ] ---> [ Step 3: Schema Validation ]
                                    |
[ Step 4: Diagnostic EDA & Margin Compression ]
       |
[ Step 5: RFM+D Customer Clustering & 2D PCA ]
       |
[ Step 6: Tri-Model Regression Benchmark (OLS vs RF vs XGBoost) ]
       |
[ Step 7: Single Sales Quote Simulation ]
       |
[ Step 8: SHAP Explainability & Additive Proof ]
       |
[ Step 9: Side-by-Side What-If Scenario Comparison ]
       |
[ Step 10: Prescriptive Strategic Directives & Causal Governance ]
```

---

### Step 1: Secure Analyst Login & JWT Token Issuance

- **URL:** Open browser to `http://localhost:3001/login`
- **Action:**
  1. Review the enterprise login form.
  2. Enter Email: `analyst@bizinsightiq.com` and Password: `analyst123`.
  3. Click **"Sign In"**.
- **Expected UI Behavior:**
  - Authenticates against Spring Boot `POST /api/v1/auth/login`.
  - BCrypt hash verified; signed JWT token stored in browser session.
  - Automatically redirects to the Executive Dashboard at `http://localhost:3001/dashboard`.
- **What to Say to the Examiner:**
  > *"Respected examiners, we begin at the authentication portal. BizInsightIQ does not expose analytical services publicly. Authentication is handled by Spring Security in our Java enterprise tier. Upon submitting valid credentials, a signed JWT token is issued using HMAC-SHA256, establishing role-based access control and tenant dataset isolation."*

---

### Step 2: Dataset Selection and CSV Upload

- **URL:** `http://localhost:3001/dashboard`
- **Action:**
  1. Inspect the dataset selector at the top of the page.
  2. The system displays the active dataset: **"Bundled Benchmark Retail Sales (1,200 Rows)"**.
  3. *(Optional Live Upload Demonstration)*: Click **"Upload New Dataset"**, drag and drop `data/sample_valid_sales.csv`, and observe upload progress.
- **Expected UI Behavior:**
  - File uploaded via multipart stream to Spring Boot `POST /api/v1/datasets/upload`.
  - Spring Boot streams file to FastAPI `POST /api/v1/datasets/validate` for pre-flight checking.
  - Rows batch-inserted into PostgreSQL table `sales_transactions`.
- **What to Say to the Examiner:**
  > *"BizInsightIQ supports multi-tenancy. Datasets uploaded by an analyst are isolated to their account, preventing unauthorized access. We will use the verified 1,200-transaction benchmark dataset spanning 2023 to 2024 across 150 unique customer accounts."*

---

### Step 3: Automated Ingestion & Schema Integrity Validation

- **URL:** `http://localhost:3001/eda` (Validation Card)
- **Action:**
  1. View the Dataset Integrity panel.
- **Expected Metrics on Screen:**
  - Total Rows: **1,200**
  - Missing / Null Values: **0 (100% Complete)**
  - Schema Contract: **8 Required Columns Passed** (`OrderID`, `CustomerID`, `OrderDate`, `Category`, `Region`, `Quantity`, `Discount`, `Sales`)
  - Statistical Outliers (IQR Method): **68 High-Value Transactions Isolated**
- **What to Say to the Examiner:**
  > *"Before any analytics or machine learning can take place, our pre-flight validation engine evaluates the data against strict schema assertions. It verifies non-null constraints, enforces discount boundaries between 0 and 1, and uses the Interquartile Range (IQR) method to isolate extreme transactions without deleting them, ensuring accounting auditability."*

---

### Step 4: Exploratory Data Analysis & The Margin Compression Cliff

- **URL:** `http://localhost:3001/eda`
- **Action:**
  1. Review Executive KPI metric cards.
  2. Scroll down to the **"Discount Margin Elasticity & Compression"** chart and table.
- **Expected Metrics on Screen:**
  - Total Gross Sales: **$1,522,871.14**
  - Total Net Profit: **$340,849.66**
  - Overall Profit Margin: **22.38%**
  - Product Category Revenue: Technology leads at **$1,032,156.46** (67.78% share).
  - Regional Sales: West region leads at **$456,128.84** (29.95% share).
  - **The Margin Compression Breakdown:**
    - Zero Discount (0%): **29.35% Margin** (Baseline)
    - 0% - 10% Discount: **29.92% Margin** (+0.57 pp, volume compensated)
    - 10% - 20% Discount: **20.20% Margin** (-9.15 pp, moderate erosion)
    - **> 20% Discount:** **2.45% Margin** (**-26.90 pp drop — The Margin Cliff!**)
- **What to Say to the Examiner:**
  > *"In our Exploratory Data Analysis, we discovered a vital business phenomenon: the Discount Cannibalization Trap. Offering up to 10% discount preserves our 29.9% margin while driving volume. However, exceeding 20% discount collapses the operating margin down to just 2.45%—a 26.9 percentage point drop. This proves empirically that unmonitored discounting destroys enterprise profitability."*

---

### Step 5: Customer Segmentation via RFM+D & 2D PCA Cluster Map

- **URL:** `http://localhost:3001/segmentation`
- **Action:**
  1. Click **"Run Customer Segmentation"** (or view active run).
  2. Inspect the 4 Cluster Persona Summary Cards.
  3. Interact with the **2D PCA Cluster Map** (hover over points, zoom, pan).
- **Expected Metrics on Screen:**
  - Clusters: **$k=4$**, Algorithm: **K-Means**, Quality: **Silhouette Score $S = 0.3582$**
  - PCA Variance Explained: **59.48%** (PC1 explains 34.56%, PC2 explains 24.92%)
  - **Cluster 0 (At-Risk High-Value — 38 accounts):** High historic spend ($10,512.63) but inactive for **180.6 days**.
  - **Cluster 1 (VIP Champions — 35 accounts):** Highest spend ($12,714.49), lowest recency (**57.2 days**), low discount (8.4%).
  - **Cluster 2 (Occasional Buyers — 48 accounts):** Moderate spend ($4,821.15), 112 days recency.
  - **Cluster 3 (Discount Bargain Hunters — 29 accounts):** High spend ($10,488.08), high order cadence (8.8 orders), but **26.2% average discount** and lowest total profit ($452.20).
- **What to Say to the Examiner:**
  > *"Here is our unsupervised machine learning engine. Traditional RFM segmentation only looks at Recency, Frequency, and Monetary spend. We formulated **RFM+D**, adding Average Discount ($D$). Notice Cluster 3: traditional RFM would call them VIPs because they spent over $10,000 across 8.8 orders. But RFM+D reveals their average discount is 26.2%, yielding only $452 in total profit! They are bargain hunters who erode margins. We validate this using K-Means with a Silhouette Score of 0.3582 and project it onto a 2D PCA subspace."*

---

### Step 6: Tri-Model Predictive Quoting Benchmark

- **URL:** `http://localhost:3001/predictions`
- **Action:**
  1. Inspect the **"Model Benchmarking & Comparison"** table at the top of the page.
- **Expected Metrics on Screen:**

| Model Architecture | R² Score | Mean Absolute Error (MAE) | Root Mean Squared Error (RMSE) | Training Time |
| :--- | :---: | :---: | :---: | :---: |
| **Linear Regression** | **0.6486** | **$482.10** | **$986.30** | **0.008 sec** |
| **Random Forest Regressor** | 0.6322 | $495.40 | $1,009.80 | 0.420 sec |
| **XGBoost Regressor** | 0.5912 | $512.60 | $1,065.20 | 0.095 sec |

- **What to Say to the Examiner:**
  > *"To ensure scientific rigor, we benchmark three distinct algorithms: Ordinary Least Squares Linear Regression, Random Forest Regressor, and XGBoost. We train them using an out-of-time chronological 80/20 train/test split at August 17, 2024, eliminating temporal and target leakage.  
  Notice that Linear Regression achieves the lowest MAE ($482.10) and highest R² (0.6486). This occurs because sales is fundamentally a continuous multiplicative target that behaves smoothly over standard ranges. Decision trees approximate smooth continuous functions using step-functions, introducing slight discretization errors on moderate sample sizes. We report the true measured results rather than assuming a complex ensemble is automatically superior."*

---

### Step 7: Single Sales Quote Simulation with Random Forest

- **URL:** `http://localhost:3001/predictions` (Single Quote Mode)
- **Action:**
  1. Ensure the mode toggle is set to **"Single Quote Simulator"**.
  2. Set Model: **Random Forest Regressor**.
  3. Enter Parameters:
     - Category: `Technology`
     - Region: `East`
     - Quantity: `5`
     - Discount: `0.10` (10%)
     - Month: `6` (June)
  4. Click **"Simulate Sales Quote"**.
- **Expected Output on Screen:**
  - **Predicted Sales Amount:** **$2,141.83**
  - Quoting Confidence Interval: $1,646.43 — $2,637.23 ($\pm \text{MAE}$)
- **What to Say to the Examiner:**
  > *"Our sales simulator allows commercial officers to test proposed transaction terms before sending a formal quotation. For 5 units of Technology in the East with a 10% discount in June, our Random Forest model predicts $2,141.83 in gross sales. But a business analyst needs to know: why did the model predict this number?"*

---

### Step 8: SHAP Explainability & Exact Additive Proof

- **URL:** `http://localhost:3001/predictions` (Under Single Quote Results)
- **Action:**
  1. Click **"Explain Prediction with SHAP"** (or view the rendered SHAP waterfall).
  2. Inspect the Baseline Value, Feature Contribution Waterfall, and Exact Additivity Badge.
- **Expected Output on Screen:**
  - **Dataset Baseline Expected Value ($E[f(x)]$):** **$1,261.08**
  - **Feature Contribution Breakdown:**
    - `Category = Technology`: **+$620.15** (Pushes UP)
    - `Quantity = 5`: **+$198.42** (Pushes UP)
    - `Discount = 0.10`: **+$87.41** (Pushes UP)
    - `Quarter = Q2`: **+$12.30** (Pushes UP)
    - `Month = June`: **+$1.85** (Pushes UP)
    - `Is_Weekend = False`: **-$1.26** (Pulls DOWN)
    - `Region = East`: **-$38.12** (Pulls DOWN)
  - **Net Sum of Contributions ($\sum \phi_i$):** **+$880.75**
  - **Mathematical Verification:**
    $$\$1,261.08 + \$880.75 = \mathbf{\$2,141.83} \quad (\text{Error } \epsilon = \$0.00)$$
  - Badge: **Exact Additivity Verified (`is_additive_exact = true`)**.
- **What to Say to the Examiner:**
  > *"Here is our Explainable AI engine. Instead of a black box, TreeSHAP decomposes the $2,141.83 prediction into exact dollar contributions relative to our dataset baseline of $1,261.08. Being in the Technology category adds $620.15, ordering 5 units adds $198.42, while the East region subtracts $38.12. Notice the mathematical check: the baseline plus the sum of all attributions equals the exact prediction down to the cent, with zero residual error."*

---

### Step 9: Side-by-Side What-If Scenario Comparison

- **URL:** `http://localhost:3001/predictions`
- **Action:**
  1. Click the top mode toggle: **"Side-by-Side What-If Comparison"**.
  2. Scenario A will populate with baseline defaults (`Technology`, `East`, `Qty: 5`, `Discount: 0.10`, `Month: 6`).
  3. In Scenario B, click **"Copy from Scenario A"** to synchronize.
  4. In Scenario B, change **Discount** from `0.10` to `0.20` (20%).
  5. Select Model: **Random Forest Regressor**.
  6. Click **"Simulate & Compare Scenarios"**.
- **Expected Output on Screen:**
  - **Scenario A Predicted Sales:** **$2,141.83**
  - **Scenario B Predicted Sales:** **$1,554.33**
  - **Net Difference:** **-$587.50 (-27.43%)**
  - **Feature Attribution Shift Table:**
    - `Discount (Changed: 0.10 -> 0.20)`: Shift $\Delta \phi = \mathbf{-\$348.54}$ (Primary Driver)
    - `Category (Unchanged)`: Shift $\Delta \phi = -\$155.80$ (Tree leaf reassignment)
    - `Quantity (Unchanged)`: Shift $\Delta \phi = -\$76.31$ (Interaction effect)
    - `Region (Unchanged)`: Shift $\Delta \phi = +\$22.69$
    - `Quarter (Unchanged)`: Shift $\Delta \phi = -\$18.19$
    - `Month (Unchanged)`: Shift $\Delta \phi = -\$13.59$
    - `Is_Weekend (Unchanged)`: Shift $\Delta \phi = +\$2.23$
  - **Sum of Attribution Shifts:** $\sum \Delta \phi_i = \mathbf{-\$587.51} \approx \mathbf{-\$587.50}$
  - **Badge:** **Exact Difference Additivity Verified (`is_difference_additive_exact = true`)**.
  - **Governance Warning:** Attribution $\neq$ Causation banner rendered at bottom.
- **What to Say to the Examiner:**
  > *"This is our counterfactual scenario simulator. An analyst compares Scenario A (10% discount) with Scenario B (20% discount). The predicted revenue drops by $587.50 (a 27.4% decline).  
  Our SHAP attribution shift table proves mathematically that increasing the discount was the primary negative driver ($-\$348.54). Notice that Category and Quantity also shifted slightly because in non-linear tree ensembles, changing the discount routes the sample to different tree leaves.  
  Crucially, we display an ethical Causal Modesty warning: this model reflects historical observational correlations—where deep discounts were applied to clearance or low-ticket items. It does not prove that discounts cause lower sales."*

---

### Step 10: Prescriptive Strategic Directives & Causal Governance

- **URL:** `http://localhost:3001/insights`
- **Action:**
  1. Review the prioritized Strategic Recommendations table.
  2. Inspect severity badges (`Critical`, `High`, `Medium`).
- **Expected Directives on Screen:**
  - **INS-03 (Critical — Discount Governance):** Transactions with $>20\%$ discount collapse to 2.45% margin. Directive: Mandate executive VP approval for any quote above 15% discount.
  - **INS-06 (Critical — Customer Retention):** Cluster 0 has 38 high-value accounts inactive for 180 days. Directive: Deploy immediate executive win-back campaigns.
  - **INS-01 (High — Revenue & Growth):** Technology drives 67.8% of sales at 22.2% margin. Directive: Prioritize Technology catalog expansion.
  - **INS-05 (High — VIP Retention):** Cluster 1 VIPs spend $12,714 at low discount. Directive: Assign dedicated Key Account Executive coverage.
- **What to Say to the Examiner:**
  > *"Finally, BizInsightIQ closes the prescriptive gap. Dashboards show numbers, but our heuristic decision engine translates analytical findings into eight prioritized strategic directives. It tells executive leadership exactly what policy actions to take—such as placing a discount ceiling of 15% to protect operating margins and launching targeted outreach for at-risk accounts.  
  This completes the full cycle: from raw transactional ingestion to explainable AI and strategic executive action across our decoupled four-tier architecture. Thank you, and I welcome any questions."*

---

## 3. Quick Reference: Key Numbers to Remember

| Metric / Parameter | Value | What It Represents |
| :--- | :---: | :--- |
| **Total Gross Revenue** | **$1,522,871.14** | Benchmark dataset gross sales across 1,200 transactions. |
| **Total Net Operating Profit** | **$340,849.66** | Benchmark dataset net profit. |
| **Baseline Profit Margin** | **22.38%** | Company-wide aggregate operating profit margin. |
| **Zero Discount Margin** | **29.35%** | Profit margin when zero discount is offered. |
| **Deep Discount Margin (>20%)** | **2.45%** | **The Margin Cliff:** 26.90 percentage point drop under deep discounting. |
| **Customer Count / Clusters** | **150 Customers / $k=4$** | Segmented via RFM+D K-Means ($S=0.3582$). |
| **PCA Variance Explained** | **59.48%** | Captured across the first two principal components. |
| **Best Regression Model** | **Linear Regression** | $R^2 = 0.6486$, $\text{MAE} = \$482.10$, $\text{RMSE} = \$986.30$. |
| **Random Forest Performance** | $R^2 = 0.6322$ | $\text{MAE} = \$495.40$, $\text{RMSE} = \$1,009.80$. |
| **XGBoost Performance** | $R^2 = 0.5912$ | $\text{MAE} = \$512.60$, $\text{RMSE} = \$1,065.20$. |
| **SHAP Baseline Expectation** | **$1,261.08** | Mean prediction of Random Forest across training background. |
| **Scenario A Quote (10% Disc)** | **$2,141.83** | Technology, East, Qty 5, 10% Discount. |
| **Scenario B Quote (20% Disc)** | **$1,554.33** | Technology, East, Qty 5, 20% Discount. |
| **Scenario Delta ($\Delta \hat{y}$)** | **-$587.50 (-27.43%)** | Revenue difference between Scenario A and B. |
| **Discount Attribution Shift** | **-$348.54** | Net SHAP attribution shift on Discount feature ($\phi_B - \phi_A$). |
| **Automated Test Count** | **239 Tests (100% Pass)** | 145 Pytest, 61 Maven, 33 E2E Integration tests. |
