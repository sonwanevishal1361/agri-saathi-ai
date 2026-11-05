# AgriSaathi AI (कृषी साथी AI) – Complete Technical & Architectural Documentation

> **Your Smart Farming Companion | शेतकऱ्यांचा विश्वासू डिजिटल साथीदार | किसानों का सच्चा साथी**  
> **Platform Architect & Creator:** **Vishal Sonwane**  
> **Official Repository:** [https://github.com/sonwanevishal1361/agri-saathi-ai.git](https://github.com/sonwanevishal1361/agri-saathi-ai.git)  
> **Current Version:** `1.0.0` (Production Ready)  
> **Supported Languages:** Marathi (मराठी), Hindi (हिंदी), English (en)

---

## Table of Contents
1. [Executive Summary & Vision](#1-executive-summary--vision)
2. [High-Level Architecture](#2-high-level-architecture)
3. [Technology Stack](#3-technology-stack)
4. [Functional Modules & Feature Matrix](#4-functional-modules--feature-matrix)
   - [4.1 Farmer Dashboard](#41-farmer-dashboard)
   - [4.2 Multilingual AI Agronomist & Safety Guard](#42-multilingual-ai-agronomist--safety-guard)
   - [4.3 Multi-Market APMC Price Comparison & Logistics](#43-multi-market-apmc-price-comparison--logistics)
   - [4.4 Weather Forecast & Spray Guidance](#44-weather-forecast--spray-guidance)
   - [4.5 Crop Lifecycle & Growth Stage Tracking](#45-crop-lifecycle--growth-stage-tracking)
   - [4.6 Farm Diary & Field Operations](#46-farm-diary--field-operations)
   - [4.7 Expenses & Financial Health](#47-expenses--financial-health)
   - [4.8 Harvest Records & Net Profitability](#48-harvest-records--net-profitability)
   - [4.9 Government Schemes Directory](#49-government-schemes-directory)
   - [4.10 Crop Health & Symptom Analyzer](#410-crop-health--symptom-analyzer)
   - [4.11 Developer Admin Panel & RBAC](#411-developer-admin-panel--rbac)
   - [4.12 DPDP Act 2023 Compliance & Privacy](#412-dpdp-act-2023-compliance--privacy)
5. [Database Architecture & Data Models](#5-database-architecture--data-models)
   - [5.1 Entity Relationship Model](#51-entity-relationship-model)
   - [5.2 Complete Table Schemas (14 Tables)](#52-complete-table-schemas-14-tables)
   - [5.3 Dual Database Engine (SQLite & PostgreSQL)](#53-dual-database-engine-sqlite--postgresql)
   - [5.4 Connection Pooling & Self-Healing Migrations](#54-connection-pooling--self-healing-migrations)
   - [5.5 Topological SQLite to PostgreSQL Migration Engine](#55-topological-sqlite-to-postgresql-migration-engine)
6. [Security, Rate Limiting & Admin Provisioning](#6-security-rate-limiting--admin-provisioning)
   - [6.1 Permissions Matrix](#61-permissions-matrix)
   - [6.2 Tenant Data Isolation](#62-tenant-data-isolation)
   - [6.3 Password Hashing & Strict Security Policy](#63-password-hashing--strict-security-policy)
   - [6.4 Account Rate Limiting & 15-Minute Lockout](#64-account-rate-limiting--15-minute-lockout)
   - [6.5 Initial Administrator Provisioning](#65-initial-administrator-provisioning)
   - [6.6 Per-User Daily AI Chat Request Limit](#66-per-user-daily-ai-chat-request-limit)
7. [Mathematical Formulas (Plain Text)](#7-mathematical-formulas-plain-text)
8. [Installation & Local Setup](#8-installation--local-setup)
   - [8.1 Prerequisites](#81-prerequisites)
   - [8.2 Step-by-Step Setup Guide](#82-step-by-step-setup-guide)
   - [8.3 Environment Variables Reference](#83-environment-variables-reference)
9. [Production Deployment Guide](#9-production-deployment-guide)
   - [9.1 Streamlit Community Cloud](#91-streamlit-community-cloud)
   - [9.2 Persistent PostgreSQL (Neon / Supabase / Cloud SQL)](#92-persistent-postgresql-neon--supabase--cloud-sql)
   - [9.3 Docker & Docker Compose Deployment](#93-docker--docker-compose-deployment)
   - [9.4 Background Schedulers & Health Check](#94-background-schedulers--health-check)
10. [Automated Testing & Code Quality](#10-automated-testing--code-quality)
11. [Directory & File Structure](#11-directory--file-structure)

---

## 1. Executive Summary & Vision

**AgriSaathi AI (कृषी साथी AI)** is an intelligent, full-stack digital companion built to address the day-to-day challenges faced by Indian farmers—with particular emphasis on farmers in Maharashtra and central India.

Smallholder and medium-scale farmers frequently struggle with:
1. **Language & Interface Complexity**: Software dashboards built with corporate UI conventions are unintuitive for rural farmers.
2. **Delayed or Fabricated Advisory**: Misleading pesticide and dosage advice from unverified web sources damages crops and soil health.
3. **Information Asymmetry in Mandi Prices**: Farmers often sell to local middlemen at deflated rates due to a lack of visibility into prevailing APMC prices in neighboring districts.
4. **Unpredictable Weather Risks**: Inopportune fertilizer application or insecticide spraying immediately before heavy rainfall leads to significant financial loss.
5. **Paper-Based Accounting**: Lack of digitized record-keeping leaves farmers unable to calculate true net profitability per acre or secure institutional credit.

AgriSaathi AI solves these challenges through an integrated, mobile-first web platform that combines verified agronomic science (ICAR, CICR Nagpur, IISR Indore) with high-speed LLM inference (Google Gemini) and comprehensive data management.

---

## 2. High-Level Architecture

```text
+---------------------------------------------------------------------------------+
|                        PRESENTATION LAYER (STREAMLIT UI)                        |
| - Multilingual Interface: Marathi (Primary), Hindi, English                     |
| - Mobile-First Responsive CSS Theme (360px - 1440px viewport optimization)      |
| - Navigation: Home, Crops, Mandi, Farm Diary, Expenses, AI Chat, Admin, Profile |
+---------------------------------------------------------------------------------+
                                      |
                                      v
+---------------------------------------------------------------------------------+
|                         APPLICATION CONTROLLER & ROUTING                        |
| - app.py (Automatic bootstrap, theme injector, authentication gate)             |
| - /health diagnostic endpoint for container probes and uptime monitoring        |
| - DPDP Act 2023 Consent Gate & Forced Initial Password Change Flow              |
+---------------------------------------------------------------------------------+
                                      |
                                      v
+---------------------------------------------------------------------------------+
|                           CORE SECURITY & AUTHENTICATION                        |
| - Argon2id Password Hasher (OWASP recommended cryptographic standard)           |
| - Strict Enterprise Password Policy (Length, Case, Digit, Special Character)    |
| - 5-Attempt Rate Limiter with 15-Minute Lockout Window (locked_until)           |
| - Multi-Tenant Authorization Guards (verify_farmer_ownership & require_admin)   |
| - DPDP Act 2023 Data Sovereignty Engine (Export JSON & Cascading Erasure)       |
+---------------------------------------------------------------------------------+
                                      |
                                      v
+---------------------------------------------------------------------------------+
|                              SERVICE LAYER ENGINES                              |
| - UserService: Farmer lifecycle, profile management, admin provisioning         |
| - CropService: Plot registration, multi-stage lifecycle, harvest forecasting    |
| - ActivityService: Farm operations diary, inputs tracking, per-activity costs    |
| - ExpenseService: Cultivation expenditure accounting & category breakdowns      |
| - HarvestService: Yield logs, market sales, net balance accounting             |
| - MandiService: Agmarknet live API, exponential retry, stale fallback, net ret  |
| - ChatService: Gemini streaming, TF-IDF RAG, daily quota limits, KCC safety     |
| - AdminService: Platform analytics, authorized exports (CSV, XLSX, JSON)        |
| - BackupService: Live atomic SQLite backups and pre-restore snapshots          |
+---------------------------------------------------------------------------------+
                   |                                            |
                   v                                            v
+--------------------------------------+     +------------------------------------+
|       EXTERNAL SERVICES & APIS       |     |         PERSISTENCE LAYER          |
| - Google Gemini API (gemini-2.5-flash|     | - SQLAlchemy 2.x Declarative Base  |
| - Local Ollama (qwen2.5:3b fallback) |     | - Alembic Database Migrations      |
| - data.gov.in (Agmarknet Mandi Rates)|     | - SQLite Engine (Local dev)        |
| - Open-Meteo Weather API             |     | - PostgreSQL Engine (Production    |
| - Sentry SDK (Error Observability)   |     |   Neon, Supabase, Cloud SQL)       |
| - Kisan Call Centre (1800-180-1551)  |     | - Connection Pooling & Pre-Ping    |
+--------------------------------------+     +------------------------------------+
```

---

## 3. Technology Stack

| Component | Technology | Rationale & Purpose |
|---|---|---|
| **Programming Language** | Python (3.11, 3.12, 3.13) | Standard ecosystem for agricultural data science and machine learning. |
| **Web Framework** | Streamlit (>= 1.35.0) | High-performance reactive web application framework for mobile and desktop. |
| **Primary AI Provider** | Google Gemini (`google-genai`) | Low-latency (<2s) context-aware streaming responses using `gemini-2.5-flash`. |
| **Offline AI Fallback** | Ollama (`qwen2.5:3b`) | Optional local CPU inference when internet connectivity is intermittent. |
| **RAG Knowledge Engine**| Scikit-Learn TF-IDF | Lightweight, deterministic in-process retrieval without heavy external vector DBs. |
| **ORM / Data Access** | SQLAlchemy (>= 2.0.0) | Enterprise ORM with strict type safety, transaction scoping, and connection pooling. |
| **Database Migrations** | Alembic (>= 1.13.0) | Deterministic schema evolution supporting SQLite batch mode and PostgreSQL. |
| **Production Drivers** | `psycopg[binary]` (>= 3.1.18) | High-throughput, modern PostgreSQL driver with SSL support for Neon & Supabase. |
| **Password Security** | Argon2id (`argon2-cffi`) | Winner of Password Hashing Competition; memory-hard defense against GPU attacks. |
| **Validation / Schemas**| Pydantic v2 & Pydantic-Settings | Robust runtime type validation and environment variable parsing. |
| **Data Processing** | Pandas (>= 2.2.0) | Multi-format aggregations and tabular data transformations. |
| **Excel Export Engine** | OpenPyXL (>= 3.1.0) | Native Microsoft Excel (.xlsx) report generation. |
| **Observability** | Structured Logging & Sentry | Context-rich JSON logging and optional cloud error telemetry. |
| **Testing & Quality** | Pytest & Ruff | Comprehensive automated unit/integration tests and lightning-fast linting. |

---

## 4. Functional Modules & Feature Matrix

| Feature Module | Core Capabilities | Farmer Benefit | Technical Implementation |
|---|---|---|---|
| **Farmer Dashboard** | Mobile-first welcoming agricultural home. Shows local weather, crop status cards, spray window indicators, and rapid action shortcuts. | Understand farm status and navigate to any agricultural feature in under 5 seconds. | Streamlit components, custom CSS themes, session state management. |
| **Multilingual AI Advisor** | Instant agronomic guidance in Marathi, Hindi, and English. Grounded by verified ICAR/CICR research passages. | Reliable farming advice in the farmer's native tongue without complex terminology. | Google Gemini API (`google-genai`), TF-IDF RAG indexing, prompt guardrails. |
| **KCC & KVK Safety Guard** | Automatic detection of pesticide, fungicide, disease, and chemical dosage discussions. Appends official advisories. | Protects farmers against toxic misuse and chemical overdosing. | Automated regex keyword inspection; appends Kisan Call Centre (`1800-180-1551`) and KVK notice. |
| **Mandi Price Comparator** | Real-time multi-market APMC rate analysis. Incorporates road freight, market fees (cess), and loading charges. | Identifies which regional mandi yields highest net profit after transport. | Formula-driven net price calculation; Agmarknet live API with exponential backoff & stale DB cache. |
| **Farm Diary & Activities** | Record tillage, sowing, spraying, weeding, irrigation, fertilizer application, and harvesting with operational costs. | Accurate historical log of all plot treatments and expenditures. | Self-healing schema migrations, foreign key constraints, tenant isolation. |
| **Farm Expense & Profit** | Track expenditures by category (seeds, fertilizer, labor, fuel, machinery). Harvest yield and revenue logging. | Real financial clarity: Net Balance = Total Harvest Revenue - Total Cultivation Expenses. | Aggregation queries, category breakdowns, per-acre investment metrics. |
| **Crop Health Analyzer** | Structured 4-step diagnostic questionnaire for plant disease symptoms with university-backed management steps. | Fast symptom diagnosis for rust, blight, wilt, borer, and sucking pests. | Pillow header byte validation for image uploads; symptom-matching algorithms. |
| **Government Schemes** | Directory of central and Maharashtra state schemes (PM-KISAN, Namo Shetkari, PMFBY, Soil Health Card, e-NAM). | Quick access to subsidy guidelines, eligibility rules, and official application portals. | Static agronomic knowledge database, categorized filters. |
| **Developer Admin Panel** | Protected developer console with Overview KPIs, Farmer Directory, Crop Analytics, Financials, and Audit Logs. | Application owners can monitor adoption and platform health safely. | Role-Based Access Control (`require_admin`), session verification, audit logging. |
| **Authorized Data Exports** | Multi-format exports in CSV (Excel UTF-8 BOM), Excel (.xlsx), and JSON with privacy sanitization. | Research analytics and administrative reporting without risking farmer privacy. | Zero-secret sanitization engine; password hashes and API keys strictly excluded. |
| **DPDP Act 2023 Compliance** | Explicit signup consent, dedicated privacy policy, "Export My Data" JSON download, and account erasure. | Total data sovereignty and legal compliance with Indian privacy laws. | Cascading account deletion, open standard JSON data export, transparent terms. |
| **Security & Rate Limiting** | Strict password policy (8+ chars, upper, lower, digit, special), 5 failed attempts lockout, daily AI query quota. | Defends against brute force attacks and controls cloud API expenses. | Argon2id hashing, lockout timers (`locked_until`), configurable per-user daily limits. |

---

## 5. Database Architecture & Data Models

### 5.1 Entity Relationship Model

```text
       +-----------------------+
       |         User          |
       +-----------------------+
       | id (UUID, PK)         |
       | full_name             |
       | email / phone         |
       | password_hash         |
       | role (farmer/admin)   |
       | must_change_password  |
       | failed_login_attempts |
       | locked_until          |
       +-----------------------+
           |       |       |       |       |
           |       |       |       |       +-------------------+
           |       |       |       +---------------+           |
           |       |       +---------------+       |           |
           v       v                       v       v           v
    +---------+ +---------------+   +----------+ +-----------+ +--------------+
    |  Crop   | | FarmActivity  |   | Expense  | | Harvest   | | Conversation |
    +---------+ +---------------+   +----------+ +-----------+ +--------------+
    | id (PK) | | id (PK)       |   | id (PK)  | | id (PK)   | | id (PK)      |
    | name    | | crop_id (FK)  |   | crop_id  | | crop_id   | | farmer_id(FK)|
    | variety | | farmer_id(FK) |   | farmer_id| | farmer_id | | title        |
    | stage   | | activity_type |   | amount   | | revenue   | +--------------+
    +---------+ | cost          |   +----------+ +-----------+        |
                +---------------+                                     v
                                                               +--------------+
                                                               |   Message    |
                                                               +--------------+
                                                               | id (PK)      |
                                                               | conv_id (FK) |
                                                               | role         |
                                                               | content      |
                                                               +--------------+
```

### 5.2 Complete Table Schemas (14 Tables)

1. **`users`**: Farmer and administrator credentials, location, contact details, security counters, and role.
2. **`crops`**: Individual registered crop plots, sowing dates, expected harvest dates, acreage, soil type, and active growth stage.
3. **`farm_activities`**: Daily agronomic task logs (weeding, fertilization, spraying, irrigation, tillage) with input quantities and operational costs.
4. **`expenses`**: Cultivation cost records grouped by category (seeds, fertilizers, pesticides, labor, machinery, fuel, irrigation).
5. **`harvest_records`**: Harvest yields, unit of measurement, market sale price, and total realized revenue.
6. **`conversations`**: Multi-turn chat session headers, preferred language, and conversation topic.
7. **`messages`**: Individual user queries and assistant responses associated with a specific conversation and farmer.
8. **`health_observations`**: Crop health assessments, plant disease symptoms, infected plot area, and severity index.
9. **`crop_knowledge`**: Agronomic repository covering major crops, climate requirements, fertilizer schedules, and pest thresholds.
10. **`knowledge_documents`**: Pre-indexed research text passages used for TF-IDF RAG retrieval.
11. **`mandi_price_history`**: Historical daily APMC market price snapshots for trend analysis.
12. **`mandi_price_cache`**: Database cache for Agmarknet API responses with automated TTL expiration.
13. **`admin_audit_logs`**: Administrative audit trail tracking logins, record status updates, database backups, and data exports.
14. **`alembic_version`**: Migration revision state tracking.

### 5.3 Dual Database Engine (SQLite & PostgreSQL)

AgriSaathi AI dynamically adapts its engine based on the `DATABASE_URL` environment variable:

- **SQLite (Development)**:
  `DATABASE_URL=sqlite:///./data/agrisaathi.db`
  Configured with `check_same_thread=False` and `PRAGMA foreign_keys=ON`.
- **PostgreSQL (Production - Neon / Supabase / Cloud SQL)**:
  `DATABASE_URL=postgresql+psycopg://user:pass@host:5432/dbname?sslmode=require`
  Configured with connection pooling: `pool_size=10`, `max_overflow=20`, `pool_recycle=300`, `pool_pre_ping=True`.

### 5.4 Connection Pooling & Self-Healing Migrations

To survive intermittent serverless pauses and connection resets:
- **`pool_pre_ping=True`**: Before handing a database connection to an application query, SQLAlchemy issues a fast ping (`SELECT 1`). If the cloud provider closed the socket, the dead connection is recycled seamlessly.
- **`pool_recycle=300`**: Connections older than 5 minutes are refreshed to prevent cloud firewall disconnects.
- **Self-Healing Startup**: On application boot, `bootstrap_database()` verifies schema integrity and runs idempotent column addition checks (`role`, `must_change_password`, `cost`, etc.) so that existing production databases never break on upgrades.

### 5.5 Topological SQLite to PostgreSQL Migration Engine

The platform provides an automated migration script (`scripts/migrate_sqlite_to_postgres.py`) that transfers existing SQLite databases to PostgreSQL while strictly preserving primary keys, timestamps, and foreign key hierarchies:

```powershell
# Step 1: Verify data integrity in dry-run mode
python scripts/migrate_sqlite_to_postgres.py --dry-run

# Step 2: Execute live topological migration to PostgreSQL
python scripts/migrate_sqlite_to_postgres.py --postgres-url "postgresql://user:pass@ep-cool-sample.neon.tech/agrisaathi?sslmode=require"
```

---

## 6. Security, Rate Limiting & Admin Provisioning

### 6.1 Permissions Matrix

| Operation / Endpoint | Unauthenticated Guest | Registered Farmer | Developer / Administrator |
|---|---|---|---|
| View Landing Page / Auth Tabs | Allowed | Allowed | Allowed |
| Register Farmer Account | Allowed (with DPDP consent) | N/A | N/A |
| Access Farmer Dashboard | Denied | Allowed (Own data only) | Allowed |
| Manage Crops, Diary, Expenses | Denied | Allowed (Own data only) | Allowed (Own data only) |
| AI Agronomist Chat | Denied | Allowed (Up to daily limit) | Allowed |
| Export Personal Data (JSON) | Denied | Allowed (Own data only) | Allowed |
| Delete Account (Cascade Erasure)| Denied | Allowed (Own data only) | Allowed |
| Access Admin Panel (`/admin`) | Denied | Denied (Raises 403) | Allowed |
| System Overview & Metrics | Denied | Denied (Raises 403) | Allowed |
| Export System Records (CSV/XLSX)| Denied | Denied (Raises 403) | Allowed (Sanitized) |
| Create / Restore DB Backups | Denied | Denied (Raises 403) | Allowed |

### 6.2 Tenant Data Isolation

AgriSaathi AI strictly isolates farmer records. The service layer enforces `verify_farmer_ownership(current_farmer_id, resource_farmer_id)` on all queries, updates, and deletions. A farmer cannot read, modify, or delete another farmer's crop, activity, expense, or conversation under any circumstance.

### 6.3 Password Hashing & Strict Security Policy

All passwords are cryptographically hashed using **Argon2id**. Plaintext passwords are never stored in databases, logs, or backups.

**Strict Password Policy**:
- Minimum 8 characters in length
- At least one uppercase letter (A-Z)
- At least one lowercase letter (a-z)
- At least one numeric digit (0-9)
- At least one special symbol (`!@#$%^&*()_+-=[]{};':",.<>/?`)

### 6.4 Account Rate Limiting & 15-Minute Lockout

To protect accounts against brute-force attacks:
- Failed login attempts increment `failed_login_attempts`.
- After 5 consecutive failed attempts, the account is locked for 15 minutes (`locked_until = now + 15 mins`).
- Subsequent login attempts during the lockout window are immediately rejected with remaining minutes.
- Authenticating with the correct password resets the counter to 0.

### 6.5 Initial Administrator Provisioning

All hardcoded default administrator credentials have been completely removed from source code, configuration files, and documentation.

To provision the first administrator:
```powershell
# Interactive CLI Provisioning:
python scripts/create_admin.py --email admin@example.com --password "SecurePass@2026!"

# Alternatively, set in .env:
# ADMIN_EMAIL=admin@example.com
# ADMIN_PASSWORD=SecurePass@2026!
python scripts/create_admin.py
```
Administrators provisioned this way are flagged with `must_change_password=True`. Upon first login, they are required to choose a new password before accessing the system.

### 6.6 Per-User Daily AI Chat Request Limit

To control cloud API consumption and prevent denial-of-wallet spikes:
- Configurable via `AI_DAILY_REQUEST_LIMIT` in `.env` (default: 25 requests/day).
- When a farmer reaches the quota, the system responds with a warm, respectful localized message in their selected language (Marathi, Hindi, or English).
- All farm records, crop diaries, weather forecast, and mandi rates remain completely accessible.

---

## 7. Mathematical Formulas (Plain Text)

All agronomic and financial formulas are implemented as plain text logic without LaTeX markup:

### 1. Mandi Logistics & Net Return Formula
```text
Gross Revenue = Modal Price * Quantity
Transport Cost = (Distance in km / 100) * Transport Rate per 100 km * Quantity
Market Fee (APMC Cess) = (Modal Price * Market Fee %) / 100 * Quantity
Loading Charges = Loading Charge per Quintal * Quantity
Total Logistics Deductions = Transport Cost + Market Fee + Loading Charges
Net Return = Gross Revenue - Total Logistics Deductions
Estimated Net Price per Quintal = Net Return / Quantity
```

### 2. Farm Profitability Formula
```text
Gross Harvest Revenue = Sum of (Harvested Quantity * Selling Price)
Total Cultivation Expenses = Sum of all categorized input and labor expenses
Net Farm Profit = Gross Harvest Revenue - Total Cultivation Expenses
Investment per Acre = Total Cultivation Expenses / Total Farm Acreage
```

### 3. Weather Spray Window Advisory Rules
```text
- If Wind Speed > 15 km/h: Issue warning to postpone spraying due to chemical drift hazard.
- If Precipitation Probability > 40% or Rain > 1.0 mm: Issue warning to postpone spraying to prevent wash-off.
- If Relative Humidity >= 75%: Warn of elevated fungal disease risk (blight, downy mildew).
- If Wind Speed <= 15 km/h and Rain Probability < 30%: Conditions favorable for pesticide or fertilizer application.
```

---

## 8. Installation & Local Setup

### 8.1 Prerequisites
- Python 3.11, 3.12, or 3.13
- Windows 10/11, macOS, or Linux
- Git installed and configured

### 8.2 Step-by-Step Setup Guide

```powershell
# 1. Clone repository
git clone https://github.com/sonwanevishal1361/agri-saathi-ai.git
cd agri-saathi-ai

# 2. Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Upgrade pip and install requirements
python -m pip install --upgrade pip
pip install -r requirements.txt

# 4. Configure environment
Copy-Item .env.example .env
# Edit .env and set GEMINI_API_KEY=your_key

# 5. Seed agronomic knowledge base
python scripts/seed_knowledge.py

# 6. Launch AgriSaathi AI
streamlit run app.py
```

### 8.3 Environment Variables Reference

| Variable | Type | Default | Description |
|---|---|---|---|
| `APP_ENV` | string | `"development"` | Application environment (`development` or `production`). |
| `SECRET_KEY` | string | Dev Secret | Secret cryptographic key for session verification. |
| `DATABASE_URL` | string | `sqlite:///data/agrisaathi.db` | SQLAlchemy database connection string (SQLite or PostgreSQL). |
| `AI_PROVIDER` | string | `"gemini"` | Active AI provider (`gemini` or `ollama`). |
| `GEMINI_API_KEY` | string | `""` | Google Gemini API Key from Google AI Studio. |
| `GEMINI_MODEL` | string | `"gemini-2.5-flash"` | Primary Gemini model identifier. |
| `AI_DAILY_REQUEST_LIMIT` | integer | `25` | Maximum AI chat queries permitted per farmer per day. |
| `ADMIN_EMAIL` | string | `""` | Administrator email for initial provisioning. |
| `ADMIN_PASSWORD` | string | `""` | Administrator password for initial provisioning. |
| `SENTRY_DSN` | string | `""` | Optional Sentry DSN for cloud error tracking. |
| `DATA_GOV_API_KEY` | string | `""` | Free API key from data.gov.in for live Agmarknet prices. |
| `MANDI_CACHE_TTL_MINUTES`| integer | `60` | In-memory and database cache expiration in minutes. |

---

## 9. Production Deployment Guide

### 9.1 Streamlit Community Cloud
1. Push your repository to GitHub.
2. Log in to [share.streamlit.io](https://share.streamlit.io) and create a **New app**.
3. Select your repository, set branch to `main`, and main file path to `app.py`.
4. Under **App settings -> Secrets**, enter your production secrets:
```toml
DATABASE_URL = "postgresql://user:password@your-postgres-host.com/dbname?sslmode=require"
GEMINI_API_KEY = "your_google_gemini_api_key"
GEMINI_MODEL = "gemini-2.5-flash"
ADMIN_EMAIL = "admin@yourdomain.com"
ADMIN_PASSWORD = "YourSecurePassword2026!"
AI_DAILY_REQUEST_LIMIT = "25"
```
5. Click **Deploy**. Tables are verified automatically on boot.

### 9.2 Persistent PostgreSQL (Neon / Supabase / Cloud SQL)
For production deployments, persistent PostgreSQL is recommended. Configure your database URL:
```ini
DATABASE_URL=postgresql+psycopg://username:password@your-neon-host.neon.tech/agrisaathi?sslmode=require
```
AgriSaathi AI automatically enables connection pooling (`pool_size=10`, `max_overflow=20`, `pool_recycle=300`, `pool_pre_ping=True`).

### 9.3 Docker & Docker Compose Deployment
AgriSaathi AI includes a production-grade multi-container setup (`Dockerfile` and `docker-compose.yml`):

```bash
# Build and launch application and PostgreSQL database in background
docker-compose up -d --build

# View application logs
docker-compose logs -f app

# Run health diagnostics
curl http://localhost:8501/?health=true
```

### 9.4 Background Schedulers & Health Check
- **Health Check Route**: Access `http://localhost:8501/?health=true` or query parameter `?page=health` for automated container orchestrator probes.
- **Mandi Cache Warmer**: Schedule `scripts/refresh_mandi.py` via cron to maintain fresh APMC price caches:
```bash
0 6 * * * /app/venv/bin/python /app/scripts/refresh_mandi.py --limit 50
```

---

## 10. Automated Testing & Code Quality

AgriSaathi AI includes an extensive automated test suite covering all functional and security modules:

- **Authentication & RBAC**: Registration, password policies, lockout, role enforcement.
- **Tenant Isolation**: Cross-tenant security guards on crops, activities, expenses, and chats.
- **Agronomic Operations**: Plot lifecycles, diary entries, expense summaries, net profits.
- **Mandi Logistics**: Multi-market price comparisons, road distances, market fees, and stale cache fallbacks.
- **AI Safety & RAG**: TF-IDF retrieval, language switches, quota limits, KCC safety notices.
- **Compliance & Privacy**: DPDP Act 2023 data exports and zero-secret guarantees.
- **Reliability**: Database connection pooling, health checks, and JSON log formatting.

```powershell
# Run all automated tests
.\venv\Scripts\pytest.exe -v

# Run code style, imports, and static analysis with Ruff
.\venv\Scripts\ruff.exe check .
```

All tests execute with simulated in-memory databases and mocked external adapters, completing in under 35 seconds without network calls or external cloud API costs.

---

## 11. Directory & File Structure

```text
AI-Farming-Assistant/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI matrix (Python 3.11, 3.12, 3.13)
├── core/
│   ├── auth.py                 # AuthenticatedFarmer identity, require_admin, tenant guards
│   ├── database.py             # SQLAlchemy 2.x engine, connection pool, init_db, bootstrap
│   ├── exceptions.py           # Domain exceptions (AuthenticationError, AuthorizationError)
│   ├── health.py               # Comprehensive system diagnostics (/health)
│   └── security.py             # Argon2id hashing, validate_password_policy, session tokens
├── models/
│   ├── activity.py             # FarmActivity model (with operational cost tracking)
│   ├── admin_log.py            # AdminAuditLog model
│   ├── conversation.py         # Conversation and Message models
│   ├── crop.py                 # Crop plot model
│   ├── expense.py              # Expense model
│   ├── harvest.py              # HarvestRecord model
│   ├── knowledge.py            # CropKnowledge and KnowledgeDocument models
│   ├── mandi_history.py        # MandiPriceHistory and MandiPriceCache models
│   └── user.py                 # User model (role, lockout counters, must_change_password)
├── schemas/
│   ├── activity.py             # Pydantic schemas for farm activities
│   ├── crop.py                 # Pydantic schemas for crops
│   ├── expense.py              # Pydantic schemas for expenses
│   ├── harvest.py              # Pydantic schemas for harvest records
│   └── user.py                 # Pydantic schemas for user registration and authentication
├── services/
│   ├── activity_service.py     # Farm activity CRUD operations
│   ├── admin_service.py        # Platform metrics, user management, and data exports
│   ├── backup_service.py       # Live SQLite backup and restore manager
│   ├── chat_service.py         # Gemini streaming, daily quotas, KCC safety guard
│   ├── crop_service.py         # Crop lifecycle management
│   ├── expense_service.py      # Cultivation financial calculations
│   ├── gemini_service.py       # Google Gemini official SDK integration
│   ├── harvest_service.py      # Harvest yields and net profitability engine
│   ├── knowledge_service.py    # TF-IDF RAG retrieval engine
│   ├── mandi_service.py        # APMC multi-market comparator & net return formulas
│   ├── ollama_service.py       # Local Ollama CPU fallback
│   ├── user_service.py         # Farmer authentication, DPDP exports, account deletion
│   └── weather_service.py      # Weather forecasts and practical spray advisories
├── ui/
│   ├── admin_page.py           # Developer Admin Console
│   ├── auth_pages.py           # Login, Registration, DPDP consent, forced PW change
│   ├── chat_page.py            # Multilingual AI Agronomist interface
│   ├── crop_detail.py          # Detailed plot timeline and activities
│   ├── crops_page.py           # Registered plots overview
│   ├── dashboard.py            # Mobile-first Farmer Home
│   ├── diary_page.py           # Field operations diary
│   ├── expenses_page.py        # Farm expense tracker
│   ├── harvest_page.py         # Harvest and net profit tracker
│   ├── image_page.py           # Crop health and photo symptom check
│   ├── knowledge_page.py       # Verified crop guides library
│   ├── market_page.py          # APMC Mandi comparator
│   ├── privacy_page.py         # DPDP Act 2023 privacy policy page
│   ├── profile_page.py         # Profile, DPDP Data Export JSON, Account Deletion
│   ├── schemes_page.py         # Government subsidy schemes directory
│   ├── state.py                # Session state management
│   ├── theme.py                # Accessible agricultural CSS theme
│   └── weather_page.py         # Detailed weather and spray window forecasts
├── utils/
│   ├── language.py             # Multilingual translations (Marathi, Hindi, English)
│   ├── logging_config.py       # Structured JSON logging and Sentry integration
│   └── prompts.py              # System agronomic instructions and RAG grounding
├── scripts/
│   ├── create_admin.py         # Secure administrator provisioning script
│   ├── init_db.py              # Database initialization utility
│   ├── migrate_sqlite_to_postgres.py # SQLite to PostgreSQL migration engine
│   ├── refresh_mandi.py        # Schedulable APMC mandi cache warmer
│   └── seed_knowledge.py       # Agronomic knowledge database seeder
├── tests/                      # Automated test suite (all modules)
├── alembic.ini                 # Alembic migration configuration
├── config.py                   # Pydantic application settings
├── docker-compose.yml          # Container stack (AgriSaathi AI + PostgreSQL 16)
├── Dockerfile                  # Production container image
├── pyproject.toml              # Project configuration and test tooling
└── requirements.txt            # Production dependencies
```

---

*Authored with pride by Vishal Sonwane — Platform Architect & Creator of AgriSaathi AI.*
