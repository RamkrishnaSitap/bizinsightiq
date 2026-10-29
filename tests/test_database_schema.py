"""
Automated Test Suite for PostgreSQL Schema and Migration Design (Phase 2).

Verifies the integrity of Flyway migration scripts, schema constraints,
table definitions, foreign keys, and security exclusion rules.
"""

from pathlib import Path
import re
import pytest

MIGRATION_DIR = Path("src/main/resources/db/migration")
V1_FILE = MIGRATION_DIR / "V1__init_schema.sql"
V2_FILE = MIGRATION_DIR / "V2__seed_demo_data.sql"


class TestMigrationScriptIntegrity:
    """Verifies existence, naming conventions, and structure of Flyway SQL files."""

    def test_migration_files_exist(self):
        assert V1_FILE.exists(), f"Missing Flyway V1 migration at {V1_FILE}"
        assert V2_FILE.exists(), f"Missing Flyway V2 migration at {V2_FILE}"

    def test_v1_table_definitions(self):
        content = V1_FILE.read_text(encoding="utf-8")
        expected_tables = [
            "users",
            "datasets",
            "sales_transactions",
            "segmentation_runs",
            "customer_clusters",
            "quote_simulations",
        ]
        for tbl in expected_tables:
            pattern = rf"CREATE\s+TABLE\s+(IF\s+NOT\s+EXISTS\s+)?{tbl}\b"
            assert re.search(pattern, content, re.IGNORECASE), f"Table '{tbl}' is missing in V1 schema."

    def test_v1_foreign_key_constraints(self):
        content = V1_FILE.read_text(encoding="utf-8")
        # Ensure foreign keys are explicitly defined with cascading rules
        assert "REFERENCES users(id) ON DELETE CASCADE" in content
        assert "REFERENCES datasets(id) ON DELETE CASCADE" in content
        assert "REFERENCES segmentation_runs(id) ON DELETE CASCADE" in content

    def test_v1_numeric_precision_and_checks(self):
        content = V1_FILE.read_text(encoding="utf-8")
        # Check constraints
        assert "chk_transactions_quantity" in content
        assert "chk_transactions_discount" in content
        assert "chk_transactions_sales" in content
        # Ensure discount is constrained between 0 and 1
        assert "discount >= 0.0000 AND discount <= 1.0000" in content

    def test_v1_performance_indexes(self):
        content = V1_FILE.read_text(encoding="utf-8")
        expected_indexes = [
            "idx_datasets_user_id",
            "idx_sales_transactions_dataset_id",
            "idx_sales_transactions_dataset_date",
            "idx_sales_transactions_dataset_category",
            "idx_sales_transactions_dataset_region",
            "idx_sales_transactions_customer",
            "idx_segmentation_runs_dataset_id",
            "idx_customer_clusters_run_id",
            "idx_customer_clusters_customer",
            "idx_quote_simulations_user_id",
        ]
        for idx in expected_indexes:
            assert idx in content, f"Index '{idx}' missing in V1 schema."

    def test_v1_check_and_unique_constraints(self):
        content = V1_FILE.read_text(encoding="utf-8")
        expected_constraints = [
            "uq_users_username",
            "uq_users_email",
            "chk_users_role",
            "chk_datasets_status",
            "chk_datasets_rows",
            "chk_datasets_cols",
            "chk_transactions_quantity",
            "chk_transactions_discount",
            "chk_transactions_sales",
            "chk_segmentation_k",
            "chk_customer_clusters_recency",
            "chk_customer_clusters_frequency",
            "chk_customer_clusters_monetary",
            "chk_quote_quantity",
            "chk_quote_discount",
            "chk_quote_predicted_sales",
            "uq_run_customer",
        ]
        for c in expected_constraints:
            assert c in content, f"Constraint '{c}' missing in V1 schema."

    def test_root_and_spring_migration_mirrored(self):
        root_v1 = Path("db/migration/V1__init_schema.sql")
        root_v2 = Path("db/migration/V2__seed_demo_data.sql")
        assert root_v1.exists(), "Root db/migration/V1__init_schema.sql must exist"
        assert root_v2.exists(), "Root db/migration/V2__seed_demo_data.sql must exist"
        assert root_v1.read_text(encoding="utf-8") == V1_FILE.read_text(encoding="utf-8")
        assert root_v2.read_text(encoding="utf-8") == V2_FILE.read_text(encoding="utf-8")

    def test_v2_seed_data_integrity(self):
        content = V2_FILE.read_text(encoding="utf-8")
        assert "INSERT INTO users" in content
        assert "INSERT INTO datasets" in content
        assert "INSERT INTO quote_simulations" in content
        # Verify passwords are NOT plaintext
        assert "$2a$10$" in content
        assert "Password@123" not in content  # Plaintext must never appear in SQL


class TestEnvironmentAndSecretSafety:
    """Verifies that secrets are guarded by .gitignore and templates are clean."""

    def test_gitignore_ignores_env_files(self):
        gitignore_path = Path(".gitignore")
        assert gitignore_path.exists()
        content = gitignore_path.read_text(encoding="utf-8")
        assert ".env" in content
        assert "!.env.example" in content

    def test_env_example_has_no_real_secrets(self):
        env_example_path = Path(".env.example")
        assert env_example_path.exists()
        content = env_example_path.read_text(encoding="utf-8")
        assert "POSTGRES_DB=" in content
        assert "POSTGRES_PASSWORD=" in content
        # Must only contain placeholder markers
        assert "replace_with" in content.lower()
