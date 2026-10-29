-- =============================================================================
-- Flyway Database Migration: V1__init_schema.sql
-- Project: BizInsightIQ (Enterprise AI/ML Business Intelligence System)
-- Target DBMS: PostgreSQL 16+
-- Authoritative Owner: Java 21 / Spring Boot 3 (Spring Data JPA)
-- =============================================================================

-- Enable cryptographic UUID extension if available
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- -----------------------------------------------------------------------------
-- 1. USERS: Identity, Role-Based Access Control (RBAC), and Audit Credentials
-- -----------------------------------------------------------------------------
CREATE TABLE users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username      VARCHAR(50)  NOT NULL,
    email         VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role          VARCHAR(30)  NOT NULL DEFAULT 'ROLE_ANALYST',
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_users_username UNIQUE (username),
    CONSTRAINT uq_users_email UNIQUE (email),
    CONSTRAINT chk_users_role CHECK (role IN ('ROLE_ADMIN', 'ROLE_ANALYST', 'ROLE_SALES'))
);

COMMENT ON TABLE users IS 'Application identities with role-based authorization for Spring Security.';
COMMENT ON COLUMN users.password_hash IS 'BCrypt password hash with salt (Cost Factor >= 10). Plaintext is never stored.';

-- -----------------------------------------------------------------------------
-- 2. DATASETS: Uploaded File Metadata, Validation Status, and Ownership
-- -----------------------------------------------------------------------------
CREATE TABLE datasets (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID NOT NULL,
    name              VARCHAR(150) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    storage_key       VARCHAR(500) NOT NULL,
    status            VARCHAR(30)  NOT NULL DEFAULT 'PENDING',
    total_rows        INTEGER      NOT NULL DEFAULT 0,
    total_columns     INTEGER      NOT NULL DEFAULT 0,
    is_valid          BOOLEAN      NOT NULL DEFAULT FALSE,
    uploaded_at       TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_datasets_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT chk_datasets_status CHECK (status IN ('PENDING', 'VALIDATED', 'FAILED', 'ARCHIVED')),
    CONSTRAINT chk_datasets_rows CHECK (total_rows >= 0),
    CONSTRAINT chk_datasets_cols CHECK (total_columns >= 0)
);

COMMENT ON TABLE datasets IS 'Metadata and validation status for uploaded sales transaction files.';
COMMENT ON COLUMN datasets.storage_key IS 'Controlled internal storage reference (e.g., uploads/{uuid}.csv).';

-- -----------------------------------------------------------------------------
-- 3. SALES_TRANSACTIONS: Normalized Ingested Sales Records
-- -----------------------------------------------------------------------------
CREATE TABLE sales_transactions (
    id          BIGSERIAL PRIMARY KEY,
    dataset_id  UUID NOT NULL,
    order_id    VARCHAR(50),
    customer_id VARCHAR(50) NOT NULL,
    order_date  DATE NOT NULL,
    category    VARCHAR(50) NOT NULL,
    region      VARCHAR(50) NOT NULL,
    quantity    INTEGER NOT NULL,
    unit_price  NUMERIC(12, 2),
    discount    NUMERIC(5, 4) NOT NULL,
    sales       NUMERIC(12, 2) NOT NULL,
    profit      NUMERIC(12, 2) NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_sales_transactions_dataset FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE CASCADE,
    CONSTRAINT chk_transactions_quantity CHECK (quantity >= 0),
    CONSTRAINT chk_transactions_discount CHECK (discount >= 0.0000 AND discount <= 1.0000),
    CONSTRAINT chk_transactions_sales CHECK (sales >= 0.00)
);

COMMENT ON TABLE sales_transactions IS 'Individual transactional records belonging to an uploaded sales dataset.';
COMMENT ON COLUMN sales_transactions.profit IS 'Net profit generated. Can be negative for unprofitable transactions.';

-- -----------------------------------------------------------------------------
-- 4. SEGMENTATION_RUNS: K-Means Execution Records & Clustering Quality Metrics
-- -----------------------------------------------------------------------------
CREATE TABLE segmentation_runs (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_id        UUID NOT NULL,
    k_clusters        INTEGER NOT NULL,
    silhouette_score  NUMERIC(6, 4) NOT NULL,
    inertia           NUMERIC(14, 4) NOT NULL,
    algorithm_version VARCHAR(50) NOT NULL DEFAULT 'KMeans-v1.0',
    created_at        TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_segmentation_runs_dataset FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE CASCADE,
    CONSTRAINT chk_segmentation_k CHECK (k_clusters >= 2 AND k_clusters <= 10)
);

COMMENT ON TABLE segmentation_runs IS 'Historical execution runs of unsupervised K-Means customer segmentation.';

-- -----------------------------------------------------------------------------
-- 5. CUSTOMER_CLUSTERS: Customer Assignments & Behavioral Persona Metrics
-- -----------------------------------------------------------------------------
CREATE TABLE customer_clusters (
    id                  BIGSERIAL PRIMARY KEY,
    segmentation_run_id UUID NOT NULL,
    customer_id         VARCHAR(50) NOT NULL,
    cluster_id          INTEGER NOT NULL,
    recency             INTEGER NOT NULL,
    frequency           INTEGER NOT NULL,
    monetary_value      NUMERIC(12, 2) NOT NULL,
    total_profit        NUMERIC(12, 2) NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_customer_clusters_run FOREIGN KEY (segmentation_run_id) REFERENCES segmentation_runs(id) ON DELETE CASCADE,
    CONSTRAINT uq_run_customer UNIQUE (segmentation_run_id, customer_id),
    CONSTRAINT chk_customer_clusters_recency CHECK (recency >= 0),
    CONSTRAINT chk_customer_clusters_frequency CHECK (frequency >= 1),
    CONSTRAINT chk_customer_clusters_monetary CHECK (monetary_value >= 0.00)
);

COMMENT ON TABLE customer_clusters IS 'Assigned cluster IDs and RFM summary values per customer for a segmentation run.';

-- -----------------------------------------------------------------------------
-- 6. QUOTE_SIMULATIONS: Saved "What-If" Predictive Scenario Quotes
-- -----------------------------------------------------------------------------
CREATE TABLE quote_simulations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL,
    dataset_id      UUID,
    category        VARCHAR(50) NOT NULL,
    region          VARCHAR(50) NOT NULL,
    quantity        INTEGER NOT NULL,
    discount        NUMERIC(5, 4) NOT NULL,
    predicted_sales NUMERIC(12, 2) NOT NULL,
    model_version   VARCHAR(50) NOT NULL DEFAULT 'RandomForestRegressor-v1.0',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_quote_simulations_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_quote_simulations_dataset FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE SET NULL,
    CONSTRAINT chk_quote_quantity CHECK (quantity >= 1),
    CONSTRAINT chk_quote_discount CHECK (discount >= 0.0000 AND discount <= 1.0000),
    CONSTRAINT chk_quote_predicted_sales CHECK (predicted_sales >= 0.00)
);

COMMENT ON TABLE quote_simulations IS 'Persisted sales quote scenarios evaluated through the supervised regression engine.';

-- -----------------------------------------------------------------------------
-- PERFORMANCE INDEXES (Optimized for Query Access Patterns)
-- -----------------------------------------------------------------------------
CREATE INDEX idx_datasets_user_id ON datasets(user_id);
CREATE INDEX idx_sales_transactions_dataset_id ON sales_transactions(dataset_id);
CREATE INDEX idx_sales_transactions_dataset_date ON sales_transactions(dataset_id, order_date);
CREATE INDEX idx_sales_transactions_dataset_category ON sales_transactions(dataset_id, category);
CREATE INDEX idx_sales_transactions_dataset_region ON sales_transactions(dataset_id, region);
CREATE INDEX idx_sales_transactions_customer ON sales_transactions(dataset_id, customer_id);
CREATE INDEX idx_segmentation_runs_dataset_id ON segmentation_runs(dataset_id);
CREATE INDEX idx_customer_clusters_run_id ON customer_clusters(segmentation_run_id);
CREATE INDEX idx_customer_clusters_customer ON customer_clusters(segmentation_run_id, customer_id);
CREATE INDEX idx_quote_simulations_user_id ON quote_simulations(user_id);
