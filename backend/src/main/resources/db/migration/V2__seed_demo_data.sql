-- =============================================================================
-- Flyway Database Migration: V2__seed_demo_data.sql
-- Project: BizInsightIQ (Enterprise AI/ML Business Intelligence System)
-- Target DBMS: PostgreSQL 16+
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Seed Initial Demo Users (Pre-computed BCrypt Hashes with Salt Cost 10)
-- -----------------------------------------------------------------------------
INSERT INTO users (id, username, email, password_hash, role)
VALUES 
    (
        '11111111-1111-1111-1111-111111111111',
        'admin',
        'admin@bizinsightiq.com',
        '$2a$10$35QGvtIrveBwcEGj7K5IDOpSDq6UjvzFpAG2AwE0Sw1Bu.nfCbLgW',
        'ROLE_ADMIN'
    ),
    (
        '22222222-2222-2222-2222-222222222222',
        'ramkrishna',
        'analyst@bizinsightiq.com',
        '$2a$10$35QGvtIrveBwcEGj7K5IDOpSDq6UjvzFpAG2AwE0Sw1Bu.nfCbLgW',
        'ROLE_ANALYST'
    )
ON CONFLICT (username) DO NOTHING;

-- -----------------------------------------------------------------------------
-- Seed Benchmark Sample Dataset Metadata
-- -----------------------------------------------------------------------------
INSERT INTO datasets (id, user_id, name, original_filename, storage_key, status, total_rows, total_columns, is_valid)
VALUES 
    (
        '33333333-3333-3333-3333-333333333333',
        '22222222-2222-2222-2222-222222222222',
        'Bundled Benchmark Retail Sales (1,200 Rows)',
        'sample_sales_data.csv',
        'data/sample_sales_data.csv',
        'VALIDATED',
        1200,
        10,
        TRUE
    )
ON CONFLICT (id) DO NOTHING;

-- -----------------------------------------------------------------------------
-- Seed Sample Baseline Quote Simulation
-- -----------------------------------------------------------------------------
INSERT INTO quote_simulations (id, user_id, dataset_id, category, region, quantity, discount, predicted_sales, model_version)
VALUES 
    (
        '44444444-4444-4444-4444-444444444444',
        '22222222-2222-2222-2222-222222222222',
        '33333333-3333-3333-3333-333333333333',
        'Technology',
        'East',
        10,
        0.1500,
        2450.00,
        'RandomForestRegressor-v1.0'
    )
ON CONFLICT (id) DO NOTHING;
