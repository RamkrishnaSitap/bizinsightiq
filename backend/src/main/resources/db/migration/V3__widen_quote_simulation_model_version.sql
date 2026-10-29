-- =============================================================================
-- Flyway Database Migration: V3__widen_quote_simulation_model_version.sql
-- Project: BizInsightIQ
-- Description: Expand model_version in quote_simulations to VARCHAR(100)
-- =============================================================================

ALTER TABLE quote_simulations ALTER COLUMN model_version TYPE VARCHAR(100);
