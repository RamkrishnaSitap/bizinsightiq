# AI-Powered Business Intelligence, Predictive Analytics and Decision Support System

**Academic Degree:** Master of Computer Applications (MCA)

---

## 1. Project Overview

This project is an AI/ML-driven business intelligence and decision support system designed to assist retail and enterprise stakeholders in understanding historical business performance, segmenting customer behavior, and forecasting sales trends.

The core analytical pipeline encompasses:
1. **Data Ingestion & Integrity Validation:** Safe CSV loading, schema verification, missing data detection, and business constraint validation.
2. **Exploratory Data Analysis (EDA):** Interactive Plotly visualizations for sales trends, category performance, and geographic distribution.
3. **Customer Segmentation:** Unsupervised machine learning using K-Means clustering to uncover customer behavioral segments.
4. **Predictive Analytics:** Supervised machine learning using regression models to forecast future sales volume and revenue.
5. **Decision Support & Actionable Insights:** Automated heuristic insight generation and recommendations (`src/insights.py`).
6. **Interactive Dashboard:** An accessible, self-contained Streamlit web interface with 6 analytical modules.

---

## 2. Technology Stack

* **Language:** Python 3.12 (64-bit)
* **Web Interface:** Streamlit (v1.66.1)
* **Data Manipulation:** Pandas (v3.1.0), NumPy (v2.5.4)
* **Machine Learning:** Scikit-learn (v1.9.1), SciPy (v1.18.1)
* **Visualization:** Plotly (v7.1.0)
* **Testing & Quality Assurance:** Pytest (v9.1.1)

---

## 3. Dataset Specification & Synthetic Data Disclaimer

The bundled sample dataset is located at `data/sample_sales_data.csv`.

> [!NOTE]
> **Synthetic Dataset Disclaimer:**  
> The bundled dataset is a **synthetic retail sales dataset** generated locally with a fixed pseudo-random seed (`seed=42`) using standard statistical distributions for educational and academic evaluation purposes. It does **not** represent real proprietary customer data or actual corporate transactions.

### Dataset Schema (8 Columns, 1,200 Rows):

| Column Name | Data Type | Description | Range / Categories |
| :--- | :--- | :--- | :--- |
| `CustomerID` | String | Unique customer identifier | `CUST-1001` to `CUST-1150` |
| `OrderDate` | Date String | Transaction timestamp (`YYYY-MM-DD`) | `2023-01-01` to `2024-12-30` |
| `Category` | Categorical | Product category | `Technology`, `Furniture`, `Office Supplies` |
| `Region` | Categorical | Geographic sales region | `North`, `South`, `East`, `West` |
| `Quantity` | Integer | Units ordered | 1 to 15 units |
| `Discount` | Float | Applied promotional discount rate | 0.00 to 0.40 (0% to 40%) |
| `Sales` | Float | Gross order amount in currency units | \$11.50 to \$13,011.58 |
| `Profit` | Float | Net profit earned on order | -\$453.67 to \$5,562.98 |

---

## 4. Setup and Installation (Windows)

### 4.1 Prerequisites
* Python 3.12.x installed on your Windows machine.
* Git (optional, for version control).

### 4.2 Virtual Environment Setup
Open PowerShell or Command Prompt inside the project root directory:

```powershell
# 1. Verify working directory
cd D:\PROJECTS_Workspace_2026\MCA_AI_ML_Project_and_Report\BizInsightIQ

# 2. Create the project-local virtual environment
python -m venv .venv

# 3. Activate the virtual environment
# In PowerShell:
.\.venv\Scripts\Activate.ps1
# Or in Command Prompt:
.\.venv\Scripts\activate.bat

# 4. Install verified dependencies
pip install -r requirements.txt
```

---

## 5. Running the Application and Tests

### 5.1 Run Automated Unit Tests
To verify data validation rules, error handling, EDA aggregations, segmentation clustering, regression predictions, and heuristic business recommendations:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

All 91 automated test cases across five test suites pass cleanly.

### 5.2 Launch the Interactive Dashboard
To start the Streamlit web dashboard:

```powershell
.\.venv\Scripts\streamlit.exe run app.py
```

The application will launch and be accessible in your default web browser at:
`http://localhost:8501`

---

## 6. Project Architecture

```text
MCA_AI_ML_Project_and_Report/
└── BizInsightIQ/
    ├── .gitignore               # Ignored environments, cache, and OS artifacts
    ├── .env.example             # Externalized configuration template
    ├── requirements.txt         # Pinned production dependencies
    ├── pytest.ini               # Pytest configuration and pythonpath definition
    ├── README.md                # Project documentation and setup guide
    ├── app.py                   # Main Streamlit web application (6 Interactive Tabs)
    ├── data/
    │   └── sample_sales_data.csv# Bundled synthetic sales dataset (1,200 rows)
    ├── docs/
    │   └── architecture.md      # Modular architecture and extensibility design
    ├── src/
    │   ├── __init__.py          # Package initializer
    │   ├── data_loader.py       # Robust CSV loading utility
    │   ├── validator.py         # Schema and business rule validation engine
    │   ├── eda.py               # Framework-agnostic EDA computations & charts
    │   ├── segmentation.py      # K-Means clustering, PCA projection, & profiling
    │   ├── prediction.py        # Supervised regression, evaluation & what-if simulator
    │   └── insights.py          # Decision support & actionable business insights
    └── tests/
        ├── test_validation.py   # Pytest automated test suite (15 test cases)
        ├── test_eda.py          # Pytest EDA analytical test suite (16 test cases)
        ├── test_ml_segmentation.py # Pytest customer segmentation test suite (17 test cases)
        ├── test_ml_prediction.py   # Pytest sales prediction test suite (22 test cases)
        └── test_insights.py        # Pytest decision support insights test suite (21 test cases)
```

---

## 7. Current Progress & Development Roadmap

- [x] **Day 1 (Completed):** Python 3.12 environment setup, reproducible sample dataset generation (1,200 rows), CSV data loader, data validator, Pytest test suite (15 passed), and initial Streamlit dashboard skeleton.
- [x] **Day 2 (Completed):** Framework-agnostic EDA engine (`src/eda.py`), interactive Plotly visualizers (Sales Trends, Category Performance, Regional Distributions, Discount Impact, Correlation Heatmap), full UI integration in `app.py`, and 31 passed unit tests.
- [x] **Day 3 (Completed):** Unsupervised Machine Learning — Customer Segmentation Engine (`src/segmentation.py`) using Scikit-learn K-Means, RFM feature aggregation, StandardScaler, Elbow/Silhouette diagnostics, 2D PCA visual projection, persona profiling, dashboard integration, and 48 passed unit tests.
- [x] **Day 4 (Completed):** Supervised Machine Learning — Sales Prediction Regression models (`src/prediction.py`) comparing Linear Regression baseline vs Random Forest Regressor, chronological 80/20 train/test split, target leakage prevention, what-if scenario simulator, regression diagnostics ($R^2$, RMSE, MAE), dashboard integration, and 70 passed unit tests.
- [x] **Day 5 (Completed):** Decision Support & Actionable Insights Engine (`src/insights.py`) — Explainable rule-based recommendations across Sales, Discounts, Segmentation, and Predictions, severity categorization, interactive UI cards, and 91 passed unit tests.
- [ ] **Day 6 (Next):** Final End-to-End System Verification, Performance Tables, Viva Presentation Preparation, and MCA Project Report Evidence compilation.
