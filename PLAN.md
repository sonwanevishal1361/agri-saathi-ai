# AgriSaathi AI – Multi-Phase Implementation Plan

## Overview
This plan outlines the systematic implementation of security, database production readiness, reliability, DPDP compliance, and documentation upgrades for AgriSaathi AI.

---

## Phase 1: Security
1. **Remove Hardcoded Credentials**:
   - Strip all hardcoded passwords (`Admin@Agri2026!`) and emails (`admin@agrisaathi.com`) from `config.py`, `DOCUMENTATION.md`, `README.md`, `ui/auth_pages.py`, etc.
   - Remove automatic seeding of default admin with fixed credentials in `core/database.py` and `services/user_service.py`.
2. **First Admin Provisioning via CLI & Environment**:
   - Create `scripts/create_admin.py` to create the initial admin from `ADMIN_EMAIL` and `ADMIN_PASSWORD` (or interactive prompts).
   - Add password policy validation (min 8 chars, at least one uppercase, lowercase, digit, and special char).
   - Add `must_change_password` flag to `User` and force password update on first login.
3. **Rate Limiting & Account Lockout**:
   - Add `failed_login_attempts` and `locked_until` columns to `User` with automatic idempotent schema migration.
   - Track failed login attempts; lock account for 15 minutes after 5 consecutive failed attempts.
   - Reset failed attempts counter on successful login.
4. **Daily AI Request Rate Limit**:
   - Add `AI_DAILY_REQUEST_LIMIT` (default: 25) to `config.py` and `.env.example`.
   - Query user's message count for today in `chat_service.py`; display a warm, friendly localized message in Marathi, Hindi, and English when the daily quota is reached.
5. **Configurable Gemini Model & Safe Error Handling**:
   - Confirm `GEMINI_MODEL` in `config.py` has a safe default (`gemini-3.5-flash-lite`), and handle model invocation failures with user-friendly error banners.
6. **Git & Secret Hygiene**:
   - Verify and update `.gitignore` to explicitly ignore `.env`, `.env.*`, `*.db`, `*.db.bak`, `data/backups/`, `data/uploads/`, and temporary log files.
   - Audit tracked files to confirm no live credentials or databases are committed.
7. **Verification**: Run `pytest -v` and `ruff check .`.

---

## Phase 2: Production Database
1. **PostgreSQL Compatibility (Neon/Supabase) & SQLite Support**:
   - Enhance `core/database.py` to detect PostgreSQL (`postgresql://` or `postgres://`), normalize driver to `postgresql+psycopg://` or `postgresql://`.
   - Configure connection pooling for PostgreSQL (`pool_size=10`, `max_overflow=20`, `pool_pre_ping=True`, `pool_recycle=300`).
   - Retain SQLite support for local development with `check_same_thread=False`.
2. **Alembic Cross-Engine Compatibility**:
   - Update `migrations/env.py` and revisions to run cleanly on both SQLite and PostgreSQL.
   - Add migration revision for `must_change_password`, `failed_login_attempts`, and `locked_until`.
3. **SQLite to PostgreSQL Migration Script**:
   - Refine and verify `scripts/migrate_sqlite_to_postgres.py` with batch streaming, topological table ordering, and data integrity verification.
4. **Verification**: Run `pytest -v` and `ruff check .`.

---

## Phase 3: Reliability
1. **Structured Logging, Sentry & Health Check**:
   - Add optional Sentry integration in `utils/logging_config.py` activated when `SENTRY_DSN` is configured.
   - Add a `/health` or programmatic health check utility verifying DB connectivity, AI provider availability, and disk storage.
2. **Mandi Service Hardening**:
   - Add exponential backoff retry logic to `services/mandi_service.py` for external API requests.
   - Enhance stale-data fallback from `mandi_price_cache` if live API is unavailable.
   - Add optional inputs for market fee (APMC cess %) and loading/unloading charges (₹/Qtl) to the net return calculation.
   - Create `scripts/refresh_mandi.py` for automated cron/background cache warming.
3. **CI/CD & Containerization**:
   - Create `.github/workflows/ci.yml` running `pytest` and `ruff` on every push and PR.
   - Add multi-stage `Dockerfile` and `docker-compose.yml` (app + PostgreSQL 16).
4. **Verification**: Run `pytest -v` and `ruff check .`.

---

## Phase 4: Compliance and Safety
1. **DPDP Act 2023 Consent & Privacy Policy**:
   - Add explicit consent checkbox at farmer registration with privacy terms notice.
   - Add dedicated Privacy Policy page explaining data processing, storage, and rights.
2. **Kisan Call Centre & KVK Notice**:
   - Add prominent banner in AI chat with Kisan Call Centre toll-free number (**1800-180-1551**) and advisory to consult local Krishi Vigyan Kendra (KVK) for critical pest, chemical, and dosage guidance.
3. **Farmer Data Sovereignty**:
   - Implement "Export My Data" (download all farmer records in JSON) in profile page.
   - Implement "Delete My Account" with cascade deletion of crops, activities, expenses, and chats.
4. **Verification**: Run `pytest -v` and `ruff check .`.

---

## Phase 5: Documentation
1. **Rewrite README.md & DOCUMENTATION.md**:
   - Plain-text formulas (replace LaTeX KaTeX with readable text).
   - Eliminate hardcoded test counts and credentials.
   - Provide clear, end-to-end deployment instructions for Streamlit Cloud, Docker, and PostgreSQL.
2. **Final Verification**: Run `pytest -v` and `ruff check .`.

