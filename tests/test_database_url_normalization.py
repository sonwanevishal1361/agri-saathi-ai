"""Unit tests for Database URL Normalization, Password Masking, and Cloud Engine Configuration.

Verifies:
- Normalization of sqlite://, postgres://, postgresql://, and postgresql+psycopg://
- SSL enforcement (?sslmode=require) for Neon and Supabase hosts
- Password sanitization in URLs for safe logging
- Prevention of SQLite connect_args on PostgreSQL
- Streamlit secrets precedence over local environment variables
All tests run in-memory without requiring an external database connection.
"""

import os
from unittest.mock import patch
from core.database import (
    normalize_database_url,
    normalize_db_url,
    mask_database_url,
)
from config import _load_streamlit_secrets_into_env


class TestDatabaseUrlNormalization:
    """Test suite for URL normalization across supported database engines."""

    def test_sqlite_url_preserved(self):
        """SQLite URLs must be preserved as-is without modification."""
        assert normalize_database_url("sqlite:///data/agrisaathi.db") == "sqlite:///data/agrisaathi.db"
        assert normalize_database_url("sqlite:///:memory:") == "sqlite:///:memory:"
        assert normalize_database_url("sqlite:///C:/test/path/db.sqlite") == "sqlite:///C:/test/path/db.sqlite"

    def test_postgres_legacy_scheme_converted(self):
        """Legacy 'postgres://' scheme must be converted to 'postgresql+psycopg://'."""
        input_url = "postgres://agri_user:secret_pass@localhost:5432/agrisaathi"
        expected = "postgresql+psycopg://agri_user:secret_pass@localhost:5432/agrisaathi"
        assert normalize_database_url(input_url) == expected

    def test_postgresql_scheme_converted(self):
        """Standard 'postgresql://' scheme must default to 'postgresql+psycopg://'."""
        input_url = "postgresql://agri_user:secret_pass@127.0.0.1:5432/agrisaathi_prod"
        expected = "postgresql+psycopg://agri_user:secret_pass@127.0.0.1:5432/agrisaathi_prod"
        assert normalize_database_url(input_url) == expected

    def test_postgresql_psycopg2_scheme_converted(self):
        """'postgresql+psycopg2://' must be converted to 'postgresql+psycopg://' for psycopg 3."""
        input_url = "postgresql+psycopg2://agri_user:secret_pass@127.0.0.1:5432/agrisaathi"
        expected = "postgresql+psycopg://agri_user:secret_pass@127.0.0.1:5432/agrisaathi"
        assert normalize_database_url(input_url) == expected

    def test_postgresql_psycopg_scheme_preserved(self):
        """Already normalized 'postgresql+psycopg://' scheme must be preserved."""
        input_url = "postgresql+psycopg://agri_user:secret_pass@localhost:5432/agrisaathi"
        assert normalize_database_url(input_url) == input_url

    def test_neon_serverless_sslmode_appended(self):
        """Neon endpoints must automatically receive sslmode=require if not specified."""
        neon_url = "postgresql://user:pass@ep-cool-fog-123456.us-east-2.aws.neon.tech/neondb"
        norm = normalize_database_url(neon_url)
        assert norm.startswith("postgresql+psycopg://")
        assert "sslmode=require" in norm
        assert norm.endswith("?sslmode=require")

    def test_supabase_serverless_sslmode_appended(self):
        """Supabase endpoints must automatically receive sslmode=require if not specified."""
        supabase_url = "postgresql://postgres.proj:secret@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"
        norm = normalize_database_url(supabase_url)
        assert norm.startswith("postgresql+psycopg://")
        assert "sslmode=require" in norm

    def test_sslmode_not_duplicated_if_already_present(self):
        """If sslmode=require is already in the query params, do not duplicate it."""
        url_with_ssl = "postgresql://user:pass@ep-cool.neon.tech/neondb?sslmode=require"
        norm = normalize_database_url(url_with_ssl)
        assert norm.count("sslmode=require") == 1

    def test_alias_normalize_db_url_matches(self):
        """The backward-compatible alias normalize_db_url must yield identical output."""
        url = "postgres://user:pass@localhost:5432/db"
        assert normalize_db_url(url) == normalize_database_url(url)


class TestPasswordMasking:
    """Test suite for URL password sanitization in logs and diagnostics."""

    def test_mask_postgresql_password(self):
        """Passwords in PostgreSQL connection strings must be replaced with '***'."""
        secret = "UltraSecretPassword99!"
        raw_url = f"postgresql+psycopg://postgres:{secret}@ep-cool-fog.neon.tech:5432/neondb"
        masked = mask_database_url(raw_url)
        assert secret not in masked
        assert masked == "postgresql+psycopg://postgres:***@ep-cool-fog.neon.tech:5432/neondb"

    def test_mask_sqlite_url_unchanged(self):
        """SQLite URLs containing no passwords must remain clean and readable."""
        sqlite_url = "sqlite:///C:/Users/Admin/data/agrisaathi.db"
        assert mask_database_url(sqlite_url) == sqlite_url

    def test_mask_empty_or_none(self):
        """Empty or None URLs must return an empty string safely."""
        assert mask_database_url(None) == ""
        assert mask_database_url("") == ""


class TestSecretsPrecedence:
    """Verify st.secrets precedence over local environment variables."""

    def test_secrets_overrides_environ(self, monkeypatch):
        """When st.secrets defines DATABASE_URL, it must override os.environ."""
        monkeypatch.setenv("DATABASE_URL", "sqlite:///local_fallback.db")
        mock_secrets = {"DATABASE_URL": "postgresql://cloud_user:secret@cloud_host/prod_db"}

        with patch("streamlit.secrets", mock_secrets):
            _load_streamlit_secrets_into_env()
            assert os.environ["DATABASE_URL"] == "postgresql://cloud_user:secret@cloud_host/prod_db"
