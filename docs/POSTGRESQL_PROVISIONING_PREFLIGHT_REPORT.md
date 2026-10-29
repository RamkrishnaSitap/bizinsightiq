# BizInsightIQ — Phase 5.1 Database Provisioning Preflight Report
## Relational Configuration Audit, Migration Compatibility, and Safe Provisioning Plan

**Protocol:** Phase 5.1 Preflight Inspection Gate  
**Date:** October 25, 2026  
**Auditor Role:** Senior Full-Stack Integration Engineer, PostgreSQL Database Engineer, and QA Engineer  
**Status:** **READY FOR OPERATOR APPROVAL (Zero Database Writes Executed)**  
**Active Branch:** `feature/nextjs-frontend`  

---

### 1. Current Git Branch & Working-Tree Status

* **Branch:** `feature/nextjs-frontend` (diverged safely from commit `a57846d`).
* **Preservation Status:** All uncommitted changes, modified configuration files, and untracked packages are intact:
  * Modified: `.env.example`, `.gitignore`, `requirements.txt`
  * Untracked: `api/`, `backend/`, `db/`, `docker-compose.yml`, `docs/`, `frontend/`, `scripts/`, `src/main/`, `tests/test_api.py`, `tests/test_database_schema.py`.
* **Zero-Write Guarantee:** No git commit, push, rebase, reset, clean, or branch switching was performed.

---

### 2. Effective Application Database Configuration (Step 1)

Inspected [`backend/src/main/resources/application.yml`](file:///d:/PROJECTS_Workspace_2026/MCA_AI_ML_Project_and_Report/BizInsightIQ/backend/src/main/resources/application.yml) and verified effective runtime settings:

| Parameter | Configuration Property / Expression | Effective Runtime Value (Redacted) |
| :--- | :--- | :--- |
| **JDBC Connection URL** | `${SPRING_DATASOURCE_URL:jdbc:postgresql://${POSTGRES_HOST:127.0.0.1}:${POSTGRES_PORT:5432}/${POSTGRES_DB:bizinsightiq_db}}` | `jdbc:postgresql://127.0.0.1:5432/bizinsightiq_db` |
| **Database Username** | `${SPRING_DATASOURCE_USERNAME:${POSTGRES_USER:bizinsight_user}}` | `bizinsight_user` |
| **Password Source** | `${SPRING_DATASOURCE_PASSWORD:${POSTGRES_PASSWORD:...}}` | Read dynamically from environment (`SPRING_DATASOURCE_PASSWORD` or `POSTGRES_PASSWORD`); fallback default defined |
| **Active Profile** | Default / Production Profile | `default` (H2 is isolated strictly to `@ActiveProfiles("test")` in `application-test.yml`) |
| **Flyway State** | `spring.flyway.enabled: true`<br>`spring.flyway.baseline-on-migrate: true` | **Enabled** (executes on startup) |
| **Migration Locations** | `spring.flyway.locations: classpath:db/migration` | `backend/src/main/resources/db/migration/` |
| **Hibernate DDL Policy** | `spring.jpa.hibernate.ddl-auto: validate` | **Strict Validation Only** (Hibernate will not create, alter, or drop tables) |
| **CORS Origins** | `${CORS_ALLOWED_ORIGINS:http://localhost:3000,http://127.0.0.1:3000,http://localhost:8501}` | Permitted for ports 3000, 8501. Note: port 3001 must be added if Next.js runs on 3001 |
| **JWT Signing Secret** | `${JWT_SECRET:}` | **Strictly required from environment**; [`JwtTokenProvider.java`](file:///d:/PROJECTS_Workspace_2026/MCA_AI_ML_Project_and_Report/BizInsightIQ/backend/src/main/java/com/bizinsightiq/security/JwtTokenProvider.java#L28-L33) enforces $\ge 256$ bits with no hardcoded fallback |

---

### 3. PostgreSQL Server & Local Instance State (Step 2)

* **Server Service:** Native Windows Service `postgresql-x64-17` is active and running (`PID 7576`).
* **Version:** PostgreSQL 17.5.
* **Connectivity:** `pg_isready` confirms `127.0.0.1:5432 - accepting connections`.
* **Host Authentication Policy (`pg_hba.conf`):**
  * Lines 89–93 enforce `scram-sha-256` password hashing for all IPv4 (`127.0.0.1/32`) and IPv6 (`::1/128`) loopback connections.
  * Peer/trust authentication is disabled.
* **Administrative Connection Status:**
  * Non-interactive administrative connection without credentials timed out as expected because `scram-sha-256` requires valid authentication.
  * In compliance with safety rules, no password cracking, credential modification, or service alteration was attempted.
  * The target database `bizinsightiq_db` and role `bizinsight_user` are not yet accessible with application defaults.

---

### 4. Migration & Authentication Compatibility Audit (Step 3)

#### A. Flyway Migration Integrity
1. **File Ordering & Naming:**
   * [`V1__init_schema.sql`](file:///d:/PROJECTS_Workspace_2026/MCA_AI_ML_Project_and_Report/BizInsightIQ/backend/src/main/resources/db/migration/V1__init_schema.sql): DDL for 6 core tables (`users`, `datasets`, `sales_transactions`, `segmentation_runs`, `customer_clusters`, `quote_simulations`), 10 performance indexes, foreign key cascades, and numeric check constraints.
   * [`V2__seed_demo_data.sql`](file:///d:/PROJECTS_Workspace_2026/MCA_AI_ML_Project_and_Report/BizInsightIQ/backend/src/main/resources/db/migration/V2__seed_demo_data.sql): Seeds initial system identities, baseline benchmark dataset metadata, and initial quote simulation.
2. **PostgreSQL 17 Compatibility:**
   * Natively compatible. Uses standard `gen_random_uuid()` (built into PostgreSQL 13+ core without external dependencies), `BIGSERIAL` sequences, `TIMESTAMPTZ`, and ANSI standard check constraints.
3. **Privilege Requirements for PostgreSQL 15+:**
   * In PostgreSQL 15+, public schema permissions were tightened (`CREATE` was removed from `PUBLIC`).
   * Therefore, granting database privileges alone is insufficient. The application user `bizinsight_user` must be granted explicit `CREATE` and `USAGE` privileges on `SCHEMA public`, or be assigned as database owner.

#### B. Password Encoder & Seed Accounts
* **Spring Boot Encoder:** [`SecurityConfig.java`](file:///d:/PROJECTS_Workspace_2026/MCA_AI_ML_Project_and_Report/BizInsightIQ/backend/src/main/java/com/bizinsightiq/config/SecurityConfig.java#L78-L81) configures:
  ```java
  @Bean
  public PasswordEncoder passwordEncoder() {
      return new BCryptPasswordEncoder(10);
  }
  ```
* **Seeded Accounts in `V2__seed_demo_data.sql`:**
  * `admin` (Role: `ROLE_ADMIN`) with BCrypt hash `$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy` (Password: `Password@123`).
  * `ramkrishna` (Role: `ROLE_ANALYST`) with BCrypt hash `$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy` (Password: `Password@123`).
* **Frontend Shortcuts Discrepancy:**
  * [`frontend/app/login/page.tsx`](file:///d:/PROJECTS_Workspace_2026/MCA_AI_ML_Project_and_Report/BizInsightIQ/frontend/app/login/page.tsx#L123-L145) hardcodes shortcut buttons for `data_analyst / AnalystPass2026!` and `sarah_analyst / AnalystPass2026!`.
  * *Alignment Plan:* The frontend shortcuts should be updated to `ramkrishna` and `admin` with `Password@123`, or `data_analyst` can be added to the seed migration. To maintain immutability of migrations, aligning the frontend shortcuts to `ramkrishna` is the cleanest, zero-risk solution.

---

### 5. Minimal, Safe Database Provisioning Plan (Step 4)

To provision a dedicated, isolated development database for BizInsightIQ **without affecting any existing database or role**, the following minimal script should be reviewed and approved by the operator.

#### A. Proposed SQL Operations (Run as PostgreSQL Superuser `postgres`)
```sql
-- 1. Create dedicated development database for BizInsightIQ
CREATE DATABASE bizinsightiq_db
    WITH OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'English_United States.1252'
    LC_CTYPE = 'English_United States.1252'
    TEMPLATE = template0;

-- 2. Create application user (replace placeholder with your chosen local dev password)
CREATE USER bizinsight_user WITH ENCRYPTED PASSWORD 'bizinsight_secret_pass';

-- 3. Grant database connection and ownership privileges
ALTER DATABASE bizinsightiq_db OWNER TO bizinsight_user;
GRANT ALL PRIVILEGES ON DATABASE bizinsightiq_db TO bizinsight_user;

-- 4. Connect to bizinsightiq_db and grant schema privileges (Mandatory for PostgreSQL 15/16/17)
\c bizinsightiq_db

GRANT ALL ON SCHEMA public TO bizinsight_user;
ALTER SCHEMA public OWNER TO bizinsight_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO bizinsight_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO bizinsight_user;
```

#### B. Risk & Isolation Assessment
* **No Shared State:** `bizinsightiq_db` is completely separate from any other project database on the instance (such as `saralkaksha_dev`).
* **Least Privilege:** `bizinsight_user` has full permissions on `bizinsightiq_db` and its `public` schema, but zero permissions on other databases.
* **No Secret Leakage:** The password is kept in local environment variables (`SPRING_DATASOURCE_PASSWORD`) and never committed to source control.

---

### 6. Stop Condition & Required Operator Action (Step 5)

In strict accordance with the mandatory safety rules, **all database-changing commands were halted**. 

#### Next Action Required from Project Owner:
1. Review and authorize the proposed SQL script above.
2. Execute the script in pgAdmin 4 or via `psql` as superuser `postgres`.
3. Inform Antigravity once executed, so we can proceed with starting Spring Boot, verifying Flyway execution, and completing the browser-to-database integration workflow.
