# AI-Powered Business Intelligence, Predictive Analytics and Decision Support System

**Academic Degree:** Master of Computer Applications (MCA)  
**Project Phase:** Day 1 Implementation (Environment, Data Pipeline & Baseline Validation MVP)

---

## 1. Project Overview

This project is an AI/ML-driven business intelligence and decision support system designed to assist retail and enterprise stakeholders in understanding historical business performance, segmenting customer behavior, and forecasting sales trends.

The core analytical pipeline encompasses:
1. **Data Ingestion & Integrity Validation:** Safe CSV loading, schema verification, missing data detection, and business constraint validation.
2. **Exploratory Data Analysis (EDA):** Interactive Plotly visualizations for sales trends, category performance, and geographic distribution *(Planned Day 2)*.
3. **Customer Segmentation:** Unsupervised machine learning using K-Means clustering to uncover customer behavioral segments *(Planned Day 3)*.
4. **Predictive Analytics:** Supervised machine learning using regression models to forecast future sales volume and revenue *(Planned Day 4)*.
5. **Decision Support & Actionable Insights:** Automated heuristic insight generation and recommendations *(Planned Day 5)*.
6. **Interactive Dashboard:** An accessible, self-contained Streamlit web interface.

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
To verify data validation rules, error handling, and file loading integrity:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

All 15 automated test cases should pass without warnings.

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
    ├── requirements.txt         # Pinned production dependencies
    ├── pytest.ini               # Pytest configuration and pythonpath definition
    ├── README.md                # Project documentation and setup guide
    ├── app.py                   # Main Streamlit web application
    ├── data/
    │   └── sample_sales_data.csv# Bundled synthetic sales dataset (1,200 rows)
    ├── src/
    │   ├── __init__.py          # Package initializer
    │   ├── data_loader.py       # Robust CSV loading utility
    │   └── validator.py         # Schema and business rule validation engine
    └── tests/
        └── test_validation.py   # Pytest automated test suite (15 test cases)
```

---

## 7. Current Progress & Development Roadmap

- [x] **Day 1 (Completed):** Python 3.12 environment setup, reproducible sample dataset generation (1,200 rows), CSV data loader, data validator, Pytest test suite (15 passed), and initial Streamlit dashboard skeleton.
- [ ] **Day 2 (Next):** Exploratory Data Analysis (EDA) module with interactive Plotly visualizers (Sales Trends, Category Performance, Regional Distributions).
- [ ] **Day 3:** Unsupervised Machine Learning — K-Means Customer Segmentation with Elbow Method and Silhouette evaluation.
- [ ] **Day 4:** Supervised Machine Learning — Sales Prediction Regression models with $R^2$, RMSE, and MAE evaluation metrics.
- [ ] **Day 5:** Decision Support Engine — Automated business insight generation and full UI integration.
- [ ] **Day 6:** Final End-to-End System Verification, Performance Tables, and MCA Project Report Evidence compilation.
