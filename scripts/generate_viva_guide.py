"""
Generate the comprehensive, beginner-friendly MCA Viva Voce Preparation Guide
for BizInsightIQ covering project fundamentals, 4-tier architecture, ML algorithms,
SHAP explainability, side-by-side what-if simulation, security, and empirical results.
"""
import os

DOCS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs"))
VIVA_MD_PATH = os.path.join(DOCS_DIR, "viva_preparation.md")

def generate_viva_guide():
    content = """# BIZINSIGHTIQ: MCA VIVA VOCE MASTER PREPARATION GUIDE & DEFENSE CHEAT SHEET

**Degree:** Master of Computer Applications (MCA) — Capstone Project  
**Institution:** Centre for Distance and Online Education (CDOE), Lovely Professional University  
**Project Title:** BizInsightIQ: An Enterprise AI-Powered Business Intelligence, Customer Segmentation, and Predictive Analytics System  
**Verified Baseline:** 239 / 239 Passing Automated Tests (145 Pytest, 61 Maven, 33 E2E)  
**Architecture:** 4-Tier Microservices (Next.js 14 :3001 $\\rightarrow$ Spring Boot 3 :8080 $\\rightarrow$ FastAPI :8000 $\\rightarrow$ PostgreSQL 17 :5432)  

---

## 1. Executive Summary & Elevator Pitches

### The 30-Second "Elevator Pitch" (Quick Summary)
> *"BizInsightIQ is a four-tier enterprise decision support system that bridges the gap between conventional descriptive BI dashboards and black-box machine learning. Built with Next.js, Spring Boot, FastAPI, and PostgreSQL, it ingests transactional sales data, diagnoses non-linear margin compression across discount tiers, segments customers using RFM+D K-Means clustering, benchmarks three regression models (Linear Regression, Random Forest, and XGBoost), and provides transparent Explainable AI via SHAP and side-by-side counterfactual What-If simulation with verified mathematical additivity."*

### The 2-Minute Comprehensive Viva Pitch (Formal Opening)
> *"Respected external examiner and members of the evaluation committee:*
>
> *Commercial enterprises face a persistent analytical barrier: enterprise BI suites like Tableau and Power BI are expensive, proprietary, and primarily descriptive—they show what happened in the past, but offer no predictive capabilities or mathematical explainability. On the other hand, ad-hoc spreadsheets lack data validation, suffer from formula corruption, and have zero machine learning integration.*
>
> *To solve this, I designed and developed **BizInsightIQ**, an enterprise-grade AI decision-support platform engineered across a strictly decoupled four-tier architecture:*
> 1. *First, **Data Ingestion and Integrity Validation**: Enforcing schema contracts, range constraints, and IQR anomaly detection on 1,200 transactions across 150 customer entities.*
> 2. *Second, **Exploratory Data Analysis**: Where we discovered a crucial business finding—a severe **margin compression cliff**, where profit margin plunges from **29.35% at zero discount to just 2.45% at discounts above 20%**.*
> 3. *Third, **Unsupervised Machine Learning**: Using **RFM+D (Recency, Frequency, Monetary, and Average Discount)** with **K-Means clustering** ($k=4$, Silhouette Score $0.3582$) and 2D **PCA projection** (explaining 59.48% of variance) to unmask margin-depleting bargain hunters.*
> 4. *Fourth, **Supervised Predictive Analytics**: Forecasting sales using a strict chronological 80/20 train/test split. Benchmarking **Linear Regression**, **Random Forest**, and **XGBoost Regressor**, demonstrating empirically why Linear Regression achieved top accuracy ($R^2=0.6486$, MAE=$482.10) on this smooth continuous target.*
> 5. *Fifth, **Explainable AI (SHAP)**: Integrating TreeSHAP to compute local feature attributions for individual quotes, proving exact mathematical additivity ($\\hat{y} = E[f(x)] + \\sum \\phi_i$) with zero residual error against a dataset baseline of $1,261.08.*
> 6. *Sixth, **Side-by-Side What-If Scenario Comparison**: Allowing analysts to compare baseline and counterfactual scenarios side-by-side, isolating attribution shifts while enforcing ethical causal modesty (Attribution $\\neq$ Causation).*
> 7. *Finally, the system is secured via **Spring Security and JWT tokens**, persisted in **PostgreSQL 17** via **Flyway migrations**, and backed by **239 automated tests** with 100% pass fidelity.*
>
> *I am prepared to walk through the architecture, algorithmic mathematics, or demonstrate the live system."*

---

## 2. Topic 1: Project Fundamentals

### Q1: What specific problem does BizInsightIQ solve?
**Spoken Answer:**  
*"BizInsightIQ solves the 'prescriptive and explainability gap' in business analytics. Most retail businesses use spreadsheets or basic dashboards that only show past sales. They don't know:
1. Which customers are actually profitable versus those who only buy heavily discounted clearance items;
2. How offering a discount will impact future sales revenue;
3. Exactly which variables (like region, product category, or quantity) drove an AI prediction.  
BizInsightIQ combines data validation, customer clustering, tri-model sales forecasting, and SHAP explainability into a single secure platform."*

### Q2: Who are the intended users of the system?
**Spoken Answer:**  
*"BizInsightIQ is built for three primary roles in small-to-medium retail or wholesale distribution enterprises:
1. **Sales Analysts & Commercial Quoting Officers:** Who simulate pricing quotes and What-If discount scenarios before finalizing commercial contracts.
2. **Marketing & CRM Managers:** Who use RFM+D customer segmentation to design targeted retention campaigns for at-risk accounts or VIP customers.
3. **Executive Management / CFOs:** Who monitor operating margins, enforce company-wide discount governance ceilings, and review high-priority strategic insights."*

### Q3: What makes BizInsightIQ different from conventional dashboards like Power BI or Tableau?
**Spoken Answer:**  
*"Three key differences:
1. **Explainable AI vs. Black-Box:** Conventional BI tools cannot explain individual predictions down to the dollar. BizInsightIQ uses SHAP cooperative game theory to prove mathematically how each feature pushed or pulled the quote from the average baseline.
2. **Side-by-Side Counterfactual Analysis:** Analysts can compare Scenario A (10% discount) with Scenario B (20% discount) side-by-side and see the exact attribution shift for each feature.
3. **Decoupled 4-Tier Open Architecture:** Instead of a closed proprietary desktop app, BizInsightIQ has a standalone Next.js frontend, an enterprise Spring Boot backend with JWT security, and a dedicated FastAPI Python ML microservice backed by PostgreSQL."*

### Q4: Why did you select this particular capstone project?
**Spoken Answer:**  
*"I wanted to build a project that bridges full-stack enterprise software engineering with real applied data science. Many academic ML projects are confined to a Jupyter Notebook that never gets deployed, or basic CRUD apps without intelligence. BizInsightIQ combines enterprise Java Spring Boot, modern Next.js/React, and production Python AI microservices to solve real commercial problems like margin erosion and customer churn."*

---

## 3. Topic 2: Architecture & System Engineering

### Q5: Why did you choose Next.js for the frontend presentation layer?
**Spoken Answer:**  
*"Next.js 14 with React and TypeScript gives us:
1. **Enterprise Type Safety:** TypeScript ensures that request and response structures match backend DTOs at compile time, eliminating runtime undefined errors.
2. **Component Modularity:** Reusable UI components for metric cards, data tables, Plotly charts, and dual-scenario input forms.
3. **Clean Separation:** The frontend is strictly a presentation client. It has zero business logic and zero direct database access, communicating with Spring Boot via secure REST APIs with JWT tokens."*

### Q6: Why use Java and Spring Boot for the enterprise application tier?
**Spoken Answer:**  
*"In an enterprise environment, business governance, authentication, and transaction security belong in a robust, mature application core:
1. **Spring Security & JWT:** Handles stateless token verification, BCrypt password hashing, and role-based access control.
2. **Tenant Isolation:** Enforces dataset ownership checks before any analytical request is forwarded downstream.
3. **Spring Data JPA & Flyway:** Provides object-relational mapping and version-controlled, reproducible database migrations.
4. **Resilient Gateway:** Acts as an architectural shield, protecting the Python ML microservice from unauthenticated external access."*

### Q7: Why use Python and FastAPI for the AI/ML service instead of doing everything in Java?
**Spoken Answer:**  
*"Python is the undisputed industry standard for scientific computing and machine learning. Libraries like Scikit-learn, XGBoost, SHAP, Pandas, and NumPy have optimized C and Fortran backends that would be impractical to replicate in Java.  
FastAPI was chosen because:
1. It is asynchronous, lightweight, and extremely fast (built on Starlette and Uvicorn);
2. Native Pydantic models automatically validate incoming JSON payloads and generate interactive Swagger/OpenAPI documentation."*

### Q8: Why did you choose PostgreSQL 17 as the database?
**Spoken Answer:**  
*"PostgreSQL is the gold standard for open-source ACID-compliant relational databases. It provides strong schema constraints, check assertions (e.g., ensuring discount is between 0 and 1, quantity is positive), foreign key cascades, and high-performance B-tree indexing on tenant lookup columns."*

### Q9: Walk me through the exact lifecycle of a request across the four tiers.
**Spoken Answer:**  
*"Let's trace a user clicking **'Simulate & Compare Scenarios'** on the `/predictions` page:
1. **Tier 1 (Next.js :3001):** The user enters parameters for Scenario A and B. The browser sends a `POST` request to `http://localhost:8080/api/v1/datasets/{id}/analytics/predictions/compare` with an `Authorization: Bearer <jwt_token>` header.
2. **Tier 2 (Spring Boot :8080):** 
   - `JwtAuthenticationFilter` intercepts the request, validates the HMAC-SHA256 signature, and sets the authenticated user in the `SecurityContext`.
   - `AnalyticsController` receives the typed `CompareScenariosRequest`.
   - `AnalyticsOrchestrationService` queries PostgreSQL to verify that the logged-in user owns the requested dataset.
   - Using pooled `Apache HttpClient 5`, it forwards the validated request downstream to FastAPI.
3. **Tier 3 (FastAPI :8000):** 
   - Route `POST /api/v1/predictions/compare` receives the payload and validates it via Pydantic schemas.
   - It retrieves the fitted model pipeline (e.g., Random Forest) from the model registry.
   - It computes predictions $\\hat{y}_A$ and $\\hat{y}_B$, invokes `TreeExplainer` for both scenarios, calculates attribution shifts $\\Delta \\phi_i$, and verifies exact difference additivity.
   - Returns a structured JSON response back to Spring Boot.
4. **Tier 4 (PostgreSQL :5432):** Queried during Step 2 for tenant validation, and asynchronously saves simulated quote records.
5. **Back to Tier 1:** Spring Boot maps the response to `ScenarioComparisonResponseDto`, returns HTTP 200 to Next.js, and the React page updates the side-by-side KPI cards and SHAP attribution table."*

---

## 4. Topic 3: Machine Learning & Algorithms

### Q10: What is the fundamental difference between Supervised and Unsupervised Learning?
**Spoken Answer:**  
*"In **Supervised Learning**, the training data contains both input features ($X$) and ground-truth target labels ($y$). The algorithm learns a mapping function $f: X \\rightarrow y$. Examples in BizInsightIQ: sales prediction using Linear Regression, Random Forest, and XGBoost.  
In **Unsupervised Learning**, there are no target labels. The algorithm discovers hidden patterns, groupings, or geometric distributions inherent in the feature space. Example in BizInsightIQ: customer segmentation using K-Means clustering on RFM+D metrics."*

### Q11: What is Regression, and how does Linear Regression work?
**Spoken Answer:**  
*"Regression is a supervised learning task where the target output variable $y$ is continuous rather than categorical.  
**Ordinary Least Squares (OLS) Linear Regression** models the relationship as a linear combination of features:
$$\\hat{y} = \\beta_0 + \\beta_1 x_1 + \\dots + \\beta_p x_p$$
It finds the coefficient vector $\\boldsymbol{\\beta}$ that minimizes the sum of squared differences between actual and predicted values: $\\sum (y_i - \\hat{y}_i)^2$."*

### Q12: How does a Random Forest Regressor work?
**Spoken Answer:**  
*"Random Forest is an ensemble bagging (Bootstrap Aggregating) algorithm:
1. It builds an ensemble of $B$ independent decision trees (in our project, $n=100$).
2. Each tree is trained on a random bootstrap sample of the training rows (sampling with replacement).
3. At every node split, it only considers a random subset of features (typically $\\sqrt{p}$ or $p/3$).
4. The final prediction is the unweighted average of all individual tree predictions:
   $$\\hat{y} = \\frac{1}{B} \\sum_{b=1}^B T_b(x)$$
This decorrelates the trees and significantly reduces prediction variance without increasing bias."*

### Q13: What is XGBoost, and how does Boosting differ from Bagging?
**Spoken Answer:**  
*"**XGBoost (eXtreme Gradient Boosting)** is a sequential boosting ensemble:
- In **Bagging (Random Forest)**, trees are built in parallel independently. Each tree tries to predict the target $y$.
- In **Boosting (XGBoost)**, trees are built sequentially. Each new tree fits the residual errors (pseudo-residuals) made by the previous ensemble of trees.
XGBoost adds gradient descent in function space with $L_1$ (Lasso) and $L_2$ (Ridge) tree regularization to penalize model complexity and prevent overfitting."*

### Q14: Explain the evaluation metrics: $R^2$, MAE, and RMSE.
**Spoken Answer:**  
*"1. **MAE (Mean Absolute Error):** The average absolute dollar error:
   $$\\text{MAE} = \\frac{1}{n} \\sum |y_i - \\hat{y}_i|$$
   In BizInsightIQ, Linear Regression achieved $\\text{MAE} = $482.10$, meaning quotes deviate by $482 on average.
2. **RMSE (Root Mean Squared Error):** The square root of average squared errors:
   $$\\text{RMSE} = \\sqrt{\\frac{1}{n} \\sum (y_i - \\hat{y}_i)^2}$$
   Because it squares errors before averaging, RMSE heavily penalizes large outlier mistakes.
3. **$R^2$ (Coefficient of Determination):** The proportion of variance in sales explained by the model:
   $$R^2 = 1 - \\frac{\\sum (y_i - \\hat{y}_i)^2}{\\sum (y_i - \\bar{y})^2}$$
   Our Linear Regression model achieved $R^2 = 0.6486$, meaning it explains ~65% of sales variance."*

### Q15: What is Overfitting, and how did you prevent it?
**Spoken Answer:**  
*"Overfitting happens when a model memorizes training noise rather than generalizable patterns, scoring high on training data but failing on unseen data.  
We prevented overfitting by:
1. Setting maximum tree depths (`max_depth=10` for Random Forest, `max_depth=6` for XGBoost);
2. Enforcing minimum samples per leaf;
3. Using strict out-of-time chronological 80/20 train/test splitting;
4. Completely removing high-cardinality identity keys (`CustomerID`, `OrderID`) and post-sale realization features (`Profit`)."*

### Q16: How does K-Means clustering work, and how did you choose $k=4$?
**Spoken Answer:**  
*"K-Means partitions $n$ customer feature vectors into $k$ clusters:
1. Initializes $k$ centroids in normalized RFM+D space;
2. Assigns each customer to the nearest centroid using Euclidean distance;
3. Recalculates centroids as the mean of all assigned points;
4. Repeats until centroid movements fall below a convergence tolerance.  
We selected $k=4$ because it provided the optimal trade-off between mathematical cluster compactness (Silhouette Score $S = 0.3582$) and practical managerial interpretability (isolating VIPs, At-Risk accounts, Occasional buyers, and Bargain Hunters)."*

### Q17: What is the Silhouette Score?
**Spoken Answer:**  
*"The Silhouette Score measures how similar a customer is to their own cluster compared to neighboring clusters. It ranges from $-1$ to $+1$:
- $+1$: Perfectly clustered and well-separated;
- $0$: On the decision boundary between two clusters;
- Negative: Misclassified in the wrong cluster.  
Our score of $0.3582$ represents robust, well-defined clusters for customer behavioral data without artificial boundaries."*

---

## 5. Topic 4: Explainable AI & Counterfactual Analytics

### Q18: What is SHAP, and why is it superior to traditional Feature Importance?
**Spoken Answer:**  
*"**SHAP (Shapley Additive exPlanations)** is an Explainable AI method grounded in cooperative game theory:
- **Traditional Feature Importance:** Only gives a single global ranking for the entire model across the training set (e.g., 'Discount is important'). It cannot tell you what happened on an individual customer's quote.
- **SHAP:** Provides **local explanations** for individual transactions. It tells you exactly how many dollars feature $i$ added or subtracted on a specific quote.
- Furthermore, SHAP is the only method that satisfies the mathematical axioms of **Efficiency (Exact Additivity)**, **Symmetry**, and **Additivity**."*

### Q19: What is the "Baseline Expected Value" in SHAP?
**Spoken Answer:**  
*"The Baseline Expected Value, denoted $E[f(x)]$, is the mean prediction of the model across the background training dataset. In BizInsightIQ's benchmark, $E[f(x)] = $1,261.08$.  
Every individual prediction starts at this baseline. Features with positive SHAP values push the quote above $1,261.08, while features with negative values pull it below."*

### Q20: How do you prove that SHAP is mathematically exact?
**Spoken Answer:**  
*"By verifying the **Efficiency Axiom**:
$$\\hat{y} = E[f(x)] + \\sum_{i=1}^M \\phi_i$$
In our system, when we simulate a quote for Technology in the East with 5 units and 10% discount:
- Baseline $E[f(x)] = $1,261.08$
- Sum of SHAP contributions $\\sum \\phi_i = +$880.75$
- Model prediction $\\hat{y} = $2,141.83$
Since $1,261.08 + 880.75 = 2,141.83$, residual error $\\epsilon = $0.00$. Our code asserts this condition programmatically on every execution (`is_additive_exact = true`)."*

### Q21: What is Counterfactual Analysis, and how does the What-If Simulator use it?
**Spoken Answer:**  
*"Counterfactual analysis answers: *'What would the outcome be if one specific input were changed, holding all other variables constant (ceteris paribus)?'*  
Our What-If simulator compares Scenario A (baseline) against Scenario B (counterfactual). Because both scenarios evaluate against the identical model and background data, the baseline expectation $E[f(x)]$ cancels out:
$$\\hat{y}_B - \\hat{y}_A = \\sum_{i=1}^M (\\phi_{B, i} - \\phi_{A, i})$$
The net change in predicted sales equals the sum of individual feature attribution shifts down to the cent."*

### Q22: Why did increasing discount from 10% to 20% reduce predicted sales? (Correlation vs. Causation)
**Spoken Answer:**  
*"This is a crucial distinction between statistical correlation and market causation:
- **What the ML Model Learned:** In historical retail transactions, high discounts (20%-30%) were applied to clearance or low-ticket distressed items. Premium hardware was sold at low discounts (0%-10%). The model accurately learned this historical correlation.
- **Why It's Not Causation:** Giving a discount does not physically cause customers to buy less. If an analyst assumed causality, they would make bad pricing decisions. BizInsightIQ explicitly displays a **Causal Modesty Disclaimer** reminding managers that SHAP explains historical model attributions, not causal guarantees."*

---

## 6. Topic 5: Engineering, Security & Testing

### Q23: How does JWT Authentication work in your project?
**Spoken Answer:**  
*"We use stateless JSON Web Tokens (JWT) signed with HMAC-SHA256:
1. The user logs in with email and password via `POST /api/v1/auth/login`.
2. Spring Security validates the password against the stored BCrypt hash.
3. Spring issues a signed JWT token containing the user ID, email, role, and a 24-hour expiration claim.
4. Next.js stores the token and includes it in the `Authorization: Bearer <token>` header for all subsequent API requests.
5. The `JwtAuthenticationFilter` validates the signature before the request reaches the controller."*

### Q24: How do you enforce Multi-Tenant Dataset Ownership?
**Spoken Answer:**  
*"In `AnalyticsOrchestrationService.java`, before any EDA, segmentation, or prediction call is processed, we fetch the dataset record from PostgreSQL:
- We check if `dataset.getUser().getId().equals(currentUser.getId())` or if the dataset is flagged as the public benchmark.
- If an unauthenticated user or another tenant tries to access a dataset ID they do not own, Spring Boot immediately throws an `AccessDeniedException` and returns HTTP 403 Forbidden.
- This guarantees complete tenant isolation in a shared database environment."*

### Q25: Why do you use Flyway for database migrations?
**Spoken Answer:**  
*"Flyway ensures version-controlled, repeatable database schema evolution:
- Rather than running manual SQL scripts on development and production databases, migrations are written in versioned SQL files (`V1__init_schema.sql`, `V2__seed_demo_data.sql`).
- On Spring Boot startup, Flyway inspects the `flyway_schema_history` table, executes any unapplied scripts in sequence, and records their cryptographic checksums.
- This eliminates 'schema drift' across developer machines and production servers."*

### Q26: What automated testing suites exist, and what are the results?
**Spoken Answer:**  
*"We implemented a comprehensive three-tier test harness with **239 total automated tests**:
1. **Pytest (145 tests):** Validates schema validation, IQR outlier detection, RFM+D extraction, K-Means silhouette, OLS/RF/XGBoost training, TreeSHAP exact additivity, scenario comparison shifts, and FastAPI REST routes.
2. **Maven / JUnit 5 (61 tests):** Tests Spring Boot security filters, JWT issuance, BCrypt password hashing, controller proxy routes, dataset ownership, and MockMvc integration.
3. **E2E Integration Suite (33 tests):** Validates live HTTP communication across Next.js (:3001), Spring Boot (:8080), and FastAPI (:8000) against PostgreSQL 17.
**100% of the 239 tests pass with zero errors.**"*

---

## 7. Topic 6: Empirical Results & Critical Discussion

### Q27: Which regression model performed best on your benchmark dataset?
**Spoken Answer:**  
*"**Ordinary Least Squares (OLS) Linear Regression** performed best across all predictive accuracy metrics:
- Linear Regression: $R^2 = 0.6486$, $\\text{MAE} = $482.10$, $\\text{RMSE} = $986.30$
- Random Forest: $R^2 = 0.6322$, $\\text{MAE} = $495.40$, $\\text{RMSE} = $1,009.80$
- XGBoost: $R^2 = 0.5912$, $\\text{MAE} = $512.60$, $\\text{RMSE} = $1,065.20$"*

### Q28: Why did a simple model like Linear Regression outperform advanced algorithms like XGBoost?
**Spoken Answer:**  
*"This is one of the most important scientific findings of our project, attributable to three mathematical factors:
1. **The Nature of Sales Revenue:** Sales is fundamentally multiplicative: $\\text{Sales} = \\text{Quantity} \\times \\text{Unit Price} \\times (1 - \\text{Discount})$. Across typical ranges, this surface is smooth and continuous. Linear Regression fits an optimal continuous plane through this envelope.
2. **Piecewise Constant Step Error in Trees:** Decision trees split space into rectangular boxes and output a constant mean in each leaf. They approximate smooth continuous slopes as step-functions, introducing discretization errors.
3. **Sample Size ($N=960$ Training Rows):** Tree ensembles require tens of thousands of rows to populate dense leaf splits across multi-dimensional feature space without overfitting. With 960 rows, gradient boosting partitions data into sparse leaves susceptible to noise from tail outliers, whereas Linear Regression regularizes naturally."*

### Q29: What are the main limitations of BizInsightIQ?
**Spoken Answer:**  
*"1. **Single-Node Execution:** The Python AI service currently runs in-memory on a single node, suitable for datasets up to several million rows, but requiring Apache Spark or Ray for distributed terabyte-scale data.
2. **Deterministic Heuristic Rules:** The prescriptive business rules use fixed expert thresholds (e.g., 10% discount cap). Dynamic environments would benefit from automated threshold optimization.
3. **Observational Data:** Models reflect historical correlations rather than true causal market interventions."*

### Q30: What would you implement next if you had another month?
**Spoken Answer:**  
*"I would implement **Prescriptive Optimization**: rather than just asking What-If for a single scenario, an optimization algorithm (like linear programming or genetic algorithms) would recommend the exact discount and quantity that maximizes operating profit subject to warehouse inventory bounds."*

---

## 8. Rapid-Fire Examiner "Trap" Questions & Defense Strategies

| Trap Question | The Examiner's Intention | How to Answer Confidently |
| :--- | :--- | :--- |
| *"Why didn't you use Deep Learning / Neural Networks for sales prediction?"* | Testing if you use hype buzzwords without justification. | *"Tabular enterprise sales data with 1,200 rows is fundamentally unsuitable for deep neural networks, which require massive data to avoid severe overfitting. Industry benchmarks consistently prove that regularized linear models and gradient-boosted trees outperform deep learning on tabular business data."* |
| *"Did you include Profit in your sales prediction model?"* | Checking for **Target Leakage**. | *"Absolutely not! Net profit is a post-sale financial realization that cannot be known prior to manufacturing and transaction closing. Including profit would cause target leakage, artificially creating a 0.99 $R^2$ model that completely fails in real-world quoting."* |
| *"Why didn't you use cross-validation (K-Fold)?"* | Checking for **Temporal Leakage**. | *"In time-series sales transactions, random K-Fold cross-validation leaks future data into the past. We strictly enforced an out-of-time chronological 80/20 train/test split at August 17, 2024, ensuring the model is evaluated solely on future unseen data."* |
| *"Why did you build four tiers instead of just using Streamlit?"* | Checking your software engineering maturity. | *"While Streamlit is great for prototypes, production enterprise software requires separation of concerns. Next.js provides modern UI reactivity, Spring Boot provides enterprise security, RBAC, and tenant isolation, FastAPI provides dedicated scientific Python computing, and PostgreSQL provides ACID persistence."* |

---

## 9. Viva Day Practical Demonstration Checklist

1. **Verify Daemons Before Entering:**
   - PostgreSQL 17 active on port `5432`
   - FastAPI active on `http://127.0.0.1:8000` (test `/docs`)
   - Spring Boot active on `http://localhost:8080` (test `/api/v1/health`)
   - Next.js active on `http://localhost:3001` (open `/login`)
2. **Default Demo Credentials:**
   - Email: `analyst@bizinsightiq.com`
   - Password: `analyst123`
3. **Key Pages to Showcase in Sequence:**
   - `/login` $\\rightarrow$ Show JWT authentication.
   - `/dashboard` $\\rightarrow$ Highlight $1.52M sales and 22.38% margin.
   - `/eda` $\\rightarrow$ Show the **Margin Compression Cliff** chart (>20% discount drops margin to 2.45%).
   - `/segmentation` $\\rightarrow$ Explain **Cluster 3** (Discount Bargain Hunters unmasked by RFM+D).
   - `/predictions` (Single Quote) $\\rightarrow$ Show Random Forest prediction ($2,141.83), baseline ($1,261.08), and exact SHAP additivity ($0.00 error).
   - `/predictions` (Comparison Mode) $\\rightarrow$ Compare 10% vs. 20% discount, show net -$587.50 drop, explain delta SHAP shifts, and quote the Causal Modesty Disclaimer.
   - `/insights` $\\rightarrow$ Show the 8 prioritized strategic directives.
"""
    print(f"Writing updated Viva Voce Guide to: {VIVA_MD_PATH}")
    with open(VIVA_MD_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print("viva_preparation.md successfully generated!")

if __name__ == "__main__":
    generate_viva_guide()
