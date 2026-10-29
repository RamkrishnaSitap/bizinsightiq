-- =============================================================================
-- BizInsightIQ: Local PostgreSQL 17 Database Provisioning Script
-- Run in pgAdmin 4 Query Tool connected to the maintenance database 'postgres'
-- =============================================================================

-- Step A: Create Application Role
-- Replace '<YOUR_STRONG_LOCAL_DEV_PASSWORD>' with your chosen strong private password.
CREATE ROLE bizinsight_user
    WITH LOGIN
    PASSWORD '<YOUR_STRONG_LOCAL_DEV_PASSWORD>';

-- Step B: Create Dedicated Database
-- PostgreSQL does not allow CREATE DATABASE inside a transaction block.
CREATE DATABASE bizinsightiq_db
    WITH OWNER = bizinsight_user
         ENCODING = 'UTF8'
         TEMPLATE = template0;

-- Step C: Grant Schema Privileges (PostgreSQL 15+)
-- Connect Query Tool to the newly created 'bizinsightiq_db' database before running:
-- \c bizinsightiq_db
GRANT USAGE, CREATE ON SCHEMA public TO bizinsight_user;
