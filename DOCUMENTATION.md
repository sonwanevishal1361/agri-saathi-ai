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
4. [Functional Modules & User Experience](#4-functional-modules--user-experience)
   - [4.1 Farmer Dashboard](#41-farmer-friendly-home-dashboard)
   - [4.2 Multilingual AI Agronomist](#42-multilingual-ai-agronomist-advisor)
   - [4.3 Multi-Market APMC Price Comparison](#43-multi-market-apmc-price-comparison-agmarknet)
   - [4.4 Weather Forecast & Spray Guidance](#44-weather-forecast--crop-spray-guidance)
   - [4.5 Crop Lifecycle & Growth Stage Tracking](#45-crop-lifecycle--growth-stage-tracking)
   - [4.6 Farm Diary & Field Operations](#46-farm-diary--field-operations)
   - [4.7 Expenses & Financial Health](#47-expenses--cultivation-financial-health)
   - [4.8 Harvest Records & Net Profitability](#48-harvest-records--net-profitability)
   - [4.9 Government Schemes Directory](#49-government-schemes-directory)
   - [4.10 Crop Health & Photo Symptom Check](#410-crop-health--photo-symptom-check)
   - [4.11 Developer Admin Panel & Data Management](#411-developer-admin-panel--data-management)
5. [Database Architecture & Data Models](#5-database-architecture--data-models)
   - [5.1 Entity Relationship Diagram](#51-entity-relationship-diagram)
   - [5.2 Complete Table Schemas](#52-complete-table-schemas)
   - [5.3 Self-Healing & Idempotent Migrations](#53-self-healing--idempotent-migrations)
   - [5.4 PostgreSQL Production Migration Pipeline](#54-postgresql-production-migration-pipeline)
6. [Security & Role-Based Access Control (RBAC)](#6-security--role-based-access-control-rbac)
   - [6.1 Permissions Matrix](#61-permissions-matrix)
   - [6.2 Tenant Data Isolation](#62-tenant-data-isolation)
   - [6.3 Password Hashing & Secret Protection](#63-password-hashing--secret-protection)
   - [6.4 Default Administrator Account](#64-default-administrator-account)
7. [Installation & Local Setup](#7-installation--local-setup)
   - [7.1 Prerequisites](#71-prerequisites)
   - [7.2 Step-by-Step PowerShell Guide](#72-step-by-step-powershell-guide)
   - [7.3 Environment Variables Reference](#73-environment-variables-reference)
8. [Production Deployment Guide](#8-production-deployment-guide)
   - [8.1 Streamlit Community Cloud](#81-streamlit-community-cloud)
   - [8.2 Persistent PostgreSQL Deployment](#82-persistent-postgresql-deployment)
   - [8.3 Docker Deployment](#83-docker-deployment)
9. [Automated Testing & Code Quality](#9-automated-testing--code-quality)
   - [9.1 Test Suite Breakdown (101 Tests)](#91-test-suite-breakdown-101-tests)
   - [9.2 Static Analysis & Linting](#92-static-analysis--linting)
10. [Directory & File Structure](#10-directory--file-structure)

---

## 1. Executive Summary & Vision

**AgriSaathi AI (कृषी साथी AI)** is an intelligent, full-stack digital companion built to address the day-to-day challenges faced by Indian farmers—with particular emphasis on farmers in Maharashtra and central India.

Smallholder and medium-scale farmers frequently struggle with:
1. **Language & Interface Complexity**: Software dashboards built with corporate UI conventions are unintuitive for rural farmers.
2. **Delayed or Fabricated Advisory**: Misleading pesticide and dosage advice from unverified web sources damages crops and soil health.
3. **Information Asymmetry in Mandi Prices**: Farmers often sell to local middlemen at deflated rates due to a lack of visibility into prevailing APMC prices in neighboring districts.
4. **Unpredictable Weather Risks**: Inopportune fertilizer application or insecticide spraying immediately before heavy rainfall leads to significant financial loss.
5. **Fragmented Record Keeping**: Farm expenses, labor payments, and harvest outputs are rarely tracked systematically, obscuring whether a cultivation season yielded genuine net profit.

AgriSaathi AI solves these problems by providing:
- A warm, accessible interface designed around agricultural mental models in **Marathi**, **Hindi**, and **English**.
- Real-time AI advisory grounded in official agronomic guidelines from **ICAR** (Indian Council of Agricultural Research), **CICR** (Central Institute for Cotton Research, Nagpur), and **IISR** (Indian Institute of Soybean Research, Indore).
- A multi-market APMC comparison engine integrating Government of India **Agmarknet** data (`data.gov.in`) with transport cost formulas to rank markets by **net profit per quintal**.
- Practical weather advisories that translate meteorological metrics (wind speed, rain probability, humidity) into actionable guidance (e.g., *“Do not spray insecticide today due to high wind speed and imminent rain”*).
- An enterprise-grade **Developer Admin Panel** providing the application owner with real-time analytics, RBAC security, sanitized multi-format exports (CSV, XLSX, JSON), atomic database backups, and automated migration tooling.

---

## 2. High-Level Architecture

AgriSaathi AI follows a clean, decoupled **Three-Tier Service Architecture**:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                                 PRESENTATION TIER                                │
│                     Streamlit UI Layer with Mobile-First CSS                     │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┬────────────────┐  │
│  │ Farmer Home  │  AI Advisor  │  Mandi APMC  │  Crop & Diary│  Admin Panel   │  │
│  │  Dashboard   │  (Chat UI)   │  Comparison  │  Management  │  (9 Tab Suite) │  │
│  └──────────────┴──────────────┴──────────────┴──────────────┴────────────────┘  │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │
┌────────────────────────────────────────▼─────────────────────────────────────────┐
│                                  SERVICE TIER                                    │
│                     Modular Business Logic & Core Security                       │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┬────────────────┐  │
│  │ Gemini / RAG │ Mandi Engine │ Weather API  │ CRUD & Diary │ Admin Service  │  │
│  │ Chat Service │ Cache & Rank │ Advisory Svc │ Calculations │ & Data Export  │  │
│  └──────────────┴──────────────┴──────────────┴──────────────┴────────────────┘  │
│  ┌────────────────────────────────────────────────────────────────────────────┐  │
│  │           Core Security: Argon2id Hashing | RBAC Guard | Tenant Boundary   │  │
│  └────────────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │
┌────────────────────────────────────────▼─────────────────────────────────────────┐
│                                   DATA TIER                                      │
│                      SQLAlchemy 2.x ORM & Persistence Engine                     │
│  ┌──────────────────────────────────────┬─────────────────────────────────────┐  │
│  │ SQLite (Local & Streamlit Cloud)     │ Persistent PostgreSQL (Production)  │  │
│  │ Self-Healing Idempotent Schema Check │ Alembic Migration Revisions         │  │
│  └──────────────────────────────────────┴─────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────────────────────────┐  │
│  │  External Integrations: data.gov.in Agmarknet API | Open-Meteo Weather API │  │
│  └────────────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Technology Stack

| Domain | Technology | Purpose |
|---|---|---|
| **Language** | Python 3.11 – 3.13 | Core programming language across entire system. |
| **User Interface** | Streamlit ($\ge 1.32.0$) | High-performance reactive web application framework. |
| **AI / LLM Provider** | Google GenAI SDK (`google-genai`) | Official SDK calling `gemini-3.5-flash-lite` for $<2\text{s}$ streaming responses. |
| **Offline Fallback AI**| Local Ollama (`qwen2.5:3b`) | Optional local CPU inference when external internet is constrained. |
| **RAG Retrieval** | Scikit-Learn TF-IDF | Lightweight in-memory retrieval-augmented generation from verified ICAR docs. |
| **ORM & Database** | SQLAlchemy 2.x & SQLite / PostgreSQL | Database abstraction, type safety, relationships, and connection pooling. |
| **Schema Migrations**| Alembic & Dynamic Schema Check | Version-controlled migrations (`alembic upgrade head`) + self-healing runtime check. |
| **Data Processing** | Pandas & NumPy | Dataframe transformations, Mandi market ranking, and analytics aggregation. |
| **Spreadsheet Engine**| OpenPyXL ($\ge 3.1.0$) | Native Microsoft Excel (`.xlsx`) report and data export generation. |
| **Security & Auth** | Argon2id (`argon2-cffi`) | Industry-standard memory-hard password hashing with per-tenant authorization. |
| **Weather API** | Open-Meteo API | Free, non-commercial, no-key-required meteorological forecast API. |
| **Mandi Price API** | Government of India (data.gov.in) | Agmarknet live daily agricultural commodity market arrivals and rates. |
| **Testing** | Pytest & AnyIO | 101 automated unit, integration, RBAC, and regression test suites. |
| **Code Quality** | Ruff | Modern Python linter enforcing zero-warning code health. |

---

## 4. Functional Modules & User Experience

### 4.1 Farmer-Friendly Home Dashboard ([`ui/dashboard.py`](file:///C:/Users/Admin/Desktop/AI-Farming-Assistant/ui/dashboard.py))
- **Persistent Header**: Displays AgriSaathi logo, current farmer name, village, district, state, one-click language switcher (`मराठी`, `हिंदी`, `English`), and logout button.
- **Localized Greeting**: Personal greeting in the farmer's language (e.g., *"राम राम, तुकारामजी! आज तुमच्या शेतीसाठी काय मदत हवी आहे?"*).
- **Practical Weather Guidance**: Real-time temperature, condition, rain probability, wind speed, and humidity translated into clear, actionable advice (e.g., *“पावसाची शक्यता आहे. फवारणी आज टाळावी.”*).
- **Active Crop Cards**: Displays crop variety, sowing date, acreage, current growth stage, expected harvest date, and stage-specific care advice.
- **Mandi Price Teaser**: Quick overview of cotton and soybean rates with a direct button to open the comparison engine.
- **Quick Action Grid**: Large, accessible cards with agricultural icons to quickly navigate to AI Advisory, Crop Detail, Farm Diary, Expense Tracker, Market Rates, and Government Schemes.
- **Recent Farm Diary**: List of recent farm activities with an actionable empty state button (`➕ नवीन शेती कृती नोंदवा`) when 0 activities are logged.

### 4.2 Multilingual AI Agronomist Advisor ([`services/chat_service.py`](file:///C:/Users/Admin/Desktop/AI-Farming-Assistant/services/chat_service.py))
- **Dual-Engine Architecture**: Connects to **Google Gemini** (`gemini-3.5-flash-lite`) via `google-genai` SDK with live character streaming. Can seamlessly fall back to **Local Ollama** (`qwen2.5:3b`) if enabled.
- **Agronomic Safety Guardrails**: Strict system prompts prevent the AI from fabricating pesticide dosage instructions or dangerous chemical recommendations.
- **RAG Context Grounding**: Injects verified reference documents from ICAR and State Agricultural Universities based on TF-IDF semantic query matching.
- **Bounded Conversation Memory**: Retains the last 4 conversational turns per farmer to ensure context awareness while preventing context overflow and latency degradation.

### 4.3 Multi-Market APMC Price Comparison ([`services/mandi_service.py`](file:///C:/Users/Admin/Desktop/AI-Farming-Assistant/services/mandi_service.py))
- **Source**: Agmarknet resource on Open Government Data Platform (`data.gov.in`).
- **Net Profit Ranking**: Calculates estimated transportation costs based on district coordinates (Haversine formula) and vehicle freight rates:
  $$\text{Transport Cost per Qtl} = \frac{\text{Distance (km)} \times \text{Rate per km (₹)}}{\text{Batch Size (Qtl)}}$$
  $$\text{Estimated Net Return (₹/Qtl)} = \text{Modal Price} - \text{Transport Cost per Qtl}$$
- **Sorting Options**: Sort markets by highest raw modal price or highest estimated net return after freight.
- **Freshness Labels**: Shows arrival date with tags: `Fresh (Today)`, `Recent (Yesterday)`, or `Older Data`.
- **Resilient Fallback**: 60-minute in-memory + database cache. If the live government API is temporarily unreachable, it serves the cached daily snapshot with a clear indicator.
- **Multilingual Commodity Mapping**: Automatically resolves names like *कापूस / कपास / Cotton*, *सोयाबीन / Soybean*, *कांदा / प्याज / Onion*, *हरभरा / चना / Gram*.

### 4.4 Weather Forecast & Crop Spray Guidance ([`services/weather_service.py`](file:///C:/Users/Admin/Desktop/AI-Farming-Assistant/services/weather_service.py))
- Real-time Open-Meteo weather forecasts for all districts across Maharashtra and India.
- Evaluates spray feasibility based on threshold rules:
  - If Wind Speed $> 15\text{ km/h}$ or Precipitation $> 1.0\text{ mm}$: Issues an explicit spray warning.
  - If Humidity $\ge 75\%$: Warns about fungal disease risks (e.g., blight, downy mildew).

### 4.5 Crop Lifecycle & Growth Stage Tracking ([`services/crop_service.py`](file:///C:/Users/Admin/Desktop/AI-Farming-Assistant/services/crop_service.py))
- Track individual crop plots with plot name, crop name, variety, land area (Acres / Gunthas), sowing date, and expected harvest date.
- Tracks progression through 6 agronomic stages:
  1. **पेरणी (Sowing / Germination)**
  2. **शाकीय वाढ (Vegetative Growth)**
  3. **फुलोरा (Flowering)**
  4. **बोंड / शेंग विकास (Pod / Boll Development)**
  5. **परिपक्वता (Maturity / Ripening)**
  6. **कापणी (Harvesting)**
- Provides contextual care recommendations customized for each growth stage.

### 4.6 Farm Diary & Field Operations ([`services/activity_service.py`](file:///C:/Users/Admin/Desktop/AI-Farming-Assistant/services/activity_service.py))
- Digital field activity ledger for Land Preparation, Sowing, Weeding, Irrigation, Fertilizer Application, Spraying, and Harvesting.
- Records date, operation type, linked crop plot, product/fertilizer name, quantity, unit, and **cost incurred (₹)**.
- Equipped with **self-healing schema migration**: if an existing database table lacks the `cost` column, it automatically adds the column on-the-fly without throwing errors or dropping data.

### 4.7 Expenses & Cultivation Financial Health ([`services/expense_service.py`](file:///C:/Users/Admin/Desktop/AI-Farming-Assistant/services/expense_service.py))
- Categorized input cost tracking: *Seeds (बियाणे)*, *Fertilizers (खते)*, *Pesticides (कीटकनाशके)*, *Labor (मजुरी)*, *Machinery/Diesel (मशिनरी/डिझेल)*, *Irrigation (सिंचन)*, *Transport (वाहतूक)*, and *Other*.
- Computes total investment per crop plot and across the whole farm.

### 4.8 Harvest Records & Net Profitability ([`services/harvest_service.py`](file:///C:/Users/Admin/Desktop/AI-Farming-Assistant/services/harvest_service.py))
- Log harvest date, quantity produced, unit (Quintals, Tonnes, Kg), quantity sold, selling price per unit, buyer name, and market location.
- **Net Cultivation Profit Calculation**:
  $$\text{Net Agricultural Profit} = \sum \text{Harvest Revenue} - \sum \text{Cultivation Expenses}$$
- Gives farmers clear insight into their financial surplus or deficit per crop.

### 4.9 Government Schemes Directory ([`services/schemes_service.py`](file:///C:/Users/Admin/Desktop/AI-Farming-Assistant/services/schemes_service.py))
- Curated repository of central and Maharashtra state schemes:
  - **PM-KISAN (प्रधानमंत्री किसान सन्मान निधी)**
  - **Namo Shetkari Maha Samman Nidhi (नमो शेतकरी महासन्मान निधी)**
  - **PMFBY (प्रधानमंत्री पीक विमा योजना - Crop Insurance)**
  - **Soil Health Card Scheme (मृदा आरोग्य पत्रिका)**
  - **Kisan Credit Card (KCC - किसान क्रेडिट कार्ड)**
  - **Pradhan Mantri Krishi Sinchayee Yojana (ठिबक व तुषार सिंचन अनुदान)**
  - **e-NAM (राष्ट्रीय कृषी बाजार)**
  - **Magel Tyala Shettale (मागेल त्याला शेततळे)**
- Provides eligibility summaries, subsidy details, required documents, and direct links to official application portals.

### 4.10 Crop Health & Photo Symptom Check ([`services/image_service.py`](file:///C:/Users/Admin/Desktop/AI-Farming-Assistant/services/image_service.py))
- Farmer photo upload tool for affected crop leaves, stems, or fruits.
- Validates file format using Pillow magic-byte verification (restricting to `.jpg`, `.jpeg`, `.png` under $5\text{MB}$).
- Accompanied by a 4-step diagnostic questionnaire: affected plant part, symptom appearance, progression rate, and recent weather context.

### 4.11 Developer Admin Panel & Data Management ([`ui/admin_page.py`](file:///C:/Users/Admin/Desktop/AI-Farming-Assistant/ui/admin_page.py))
Accessible strictly to authenticated accounts with `role="admin"`. Consists of 9 operational tabs:

1. **📊 Overview**: Platform KPIs (registered farmers, active rate, crops tracked, field activities, expenses, harvest yield, AI consultation volume, language distribution, top districts).
2. **👥 Farmer Management**: Real-time directory with filters for search query, state, district, village, and status. One-click account activation/deactivation toggle. Password hashes and credentials are strictly concealed.
3. **🌾 Crop Analytics**: Popular crops by frequency and total acreage, growth stage distribution, and district-level cultivation patterns.
4. **🚜 Activity Analytics**: Breakdown of farming operations by category, timeline trends, and operations cost aggregation.
5. **💰 Financial Health**: Platform-wide expense breakdown, revenue by crop type, and aggregate net agricultural profit.
6. **🤖 AI Usage Analytics**: Question counts, language preference breakdown, and topic modeling (pink bollworm, fertilizers, blight, mandi prices, weather). Individual chat contents remain private by default.
7. **📥 Authorized Data Exports**:
   - Multi-format generation: **CSV** (with `utf-8-sig` BOM for native Excel Devanagari display), **Excel (.xlsx)** via OpenPyXL, and structured **JSON**.
   - Granular filters by date, state, district, and crop.
   - Zero-secret guarantee: passwords, tokens, API keys, and hashes are strictly stripped from all export payloads.
8. **🛡️ Backup & Maintenance**:
   - Live SQLite online backup API (`sqlite3.Connection.backup`) avoiding database locking.
   - Automated `PRAGMA integrity_check` verification.
   - Pre-restore safety snapshots (`pre_restore_safety_*.db`) preventing data loss.
9. **📜 Admin Audit Logs**: Complete audit trail (`AdminAuditLog` table) recording admin actions, target resources, details, timestamps, and IP addresses.

---

## 5. Database Architecture & Data Models

### 5.1 Entity Relationship Diagram

```mermaid
erDiagram
    USERS ||--o{ CROPS : owns
    USERS ||--o{ FARM_ACTIVITIES : logs
    USERS ||--o{ EXPENSES : incurs
    USERS ||--o{ HARVEST_RECORDS : yields
    USERS ||--o{ CONVERSATIONS : conducts
    USERS ||--o{ HEALTH_OBSERVATIONS : submits
    USERS ||--o{ ADMIN_AUDIT_LOGS : performs
    
    CROPS ||--o{ FARM_ACTIVITIES : receives
    CROPS ||--o{ EXPENSES : accumulates
    CROPS ||--o{ HARVEST_RECORDS : produces
    CROPS ||--o{ HEALTH_OBSERVATIONS : inspects
    
    CONVERSATIONS ||--o{ MESSAGES : contains

    USERS {
        string id PK
        string full_name
        string phone
        string email
        string password_hash
        string role "farmer | admin"
        string preferred_language "en | mr | hi"
        string state
        string district
        string village
        float farm_size
        string farm_area_unit
        string soil_type
        string irrigation_method
        boolean is_active
        datetime created_at
    }

    CROPS {
        string id PK
        string farmer_id FK
        string name
        string variety
        string plot_name
        float area
        string area_unit
        date sowing_date
        date expected_harvest_date
        string growth_stage
        string status "active | harvested | failed"
    }

    FARM_ACTIVITIES {
        string id PK
        string farmer_id FK
        string crop_id FK
        string activity_type
        date activity_date
        string description
        float quantity
        string unit
        string product_name
        float cost
        datetime created_at
    }

    EXPENSES {
        string id PK
        string farmer_id FK
        string crop_id FK
        string category
        float amount
        string currency
        date expense_date
        string description
        string vendor
    }

    HARVEST_RECORDS {
        string id PK
        string farmer_id FK
        string crop_id FK
        date harvest_date
        float quantity
        string quantity_unit
        float sale_quantity
        float selling_price
        string buyer_name
        string market_location
    }

    CONVERSATIONS {
        string id PK
        string farmer_id FK
        string title
        datetime created_at
    }

    MESSAGES {
        string id PK
        string conversation_id FK
        string role "user | assistant | system"
        text content
        datetime created_at
    }

    MANDI_PRICE_CACHE {
        string id PK
        string state
        string district
        string market
        string commodity
        string variety
        string grade
        date arrival_date
        float min_price
        float max_price
        float modal_price
        datetime fetched_at
    }

    MANDI_PRICE_HISTORY {
        string id PK
        date snapshot_date
        string state
        string district
        string market
        string commodity
        float modal_price
    }

    ADMIN_AUDIT_LOGS {
        string id PK
        string admin_id FK
        string admin_name
        string action
        string resource_type
        string resource_id
        text details
        string ip_address
        datetime created_at
    }
```

### 5.2 Complete Table Schemas

The database consists of **14 relational tables**:
1. `users`: Stores farmer and administrator credentials, role (`farmer` / `admin`), language preference, contact details, landholding size, soil classification, and irrigation profile.
2. `crops`: Stores cultivated crop plots, sowing dates, projected harvest dates, land area, variety, and growth stage.
3. `farm_activities`: Stores field diary entries (weeding, fertilization, spraying, irrigation, etc.) with input quantities and costs.
4. `expenses`: Stores categorized agricultural inputs and costs (seeds, labor, diesel, fertilizers, pesticides).
5. `harvest_records`: Stores crop yield logs, sold quantities, rates per quintal, total revenue, and buyer details.
6. `conversations`: Stores multi-turn chat sessions between farmers and the AI advisor.
7. `messages`: Stores individual dialogue turns with roles (`user`, `assistant`, `system`).
8. `crop_knowledge`: Stores verified ICAR agronomic reference cards (soils, seed rates, irrigation, pests).
9. `knowledge_documents`: Stores chunked agronomic passages indexed for TF-IDF retrieval.
10. `health_observations`: Stores crop disease observations, symptom answers, and image upload references.
11. `mandi_price_cache`: Stores Agmarknet daily price records with TTL freshness metadata.
12. `mandi_price_history`: Stores long-term daily APMC commodity price snapshots for historical trend charts.
13. `admin_audit_logs`: Records all administrative actions (logins, status toggles, exports, backups, restores).
14. `alembic_version`: Tracks applied migration revisions.

### 5.3 Self-Healing & Idempotent Migrations

To prevent downtime or `OperationalError` when deployed on Streamlit Community Cloud (where terminal access is unavailable), the database engine in [`core/database.py`](file:///C:/Users/Admin/Desktop/AI-Farming-Assistant/core/database.py) implements **idempotent startup checks**:
- Automatically checks for missing columns (e.g., `role` in `users`, `cost` in `farm_activities`).
- Executes safe `ALTER TABLE ... ADD COLUMN ...` statements inside committed transactions.
- **In-flight Self-Healing**: In [`services/activity_service.py`](file:///C:/Users/Admin/Desktop/AI-Farming-Assistant/services/activity_service.py), if an `OperationalError` indicates a missing `cost` column, the query handler catches the exception, auto-migrates the table on-the-fly, and transparently retries the query without failing the user request.

### 5.4 PostgreSQL Production Migration Pipeline

For production deployments scaling beyond SQLite, an automated migration tool is included:  
**File**: [`scripts/migrate_sqlite_to_postgres.py`](file:///C:/Users/Admin/Desktop/AI-Farming-Assistant/scripts/migrate_sqlite_to_postgres.py)

#### Features:
- Migrates tables in strict **topological foreign key order**:
  `users` $\rightarrow$ `crops` $\rightarrow$ `farm_activities` $\rightarrow$ `expenses` $\rightarrow$ `harvest_records` $\rightarrow$ `conversations` $\rightarrow$ `messages` $\rightarrow$ `health_observations` $\rightarrow$ `crop_knowledge` $\rightarrow$ `knowledge_documents` $\rightarrow$ `mandi_price_history` $\rightarrow$ `mandi_price_cache` $\rightarrow$ `admin_audit_logs`.
- Preserves all primary key UUIDs, timestamps, and relational integrity.
- Supports dry-run validation mode:
  ```powershell
  python scripts/migrate_sqlite_to_postgres.py --sqlite data/agrisaathi.db --pg "postgresql://user:password@localhost:5432/agrisaathi" --dry-run
  ```
- Executes batch streaming to migrate tens of thousands of records without memory spikes.

---

## 6. Security & Role-Based Access Control (RBAC)

### 6.1 Permissions Matrix

| Feature / Resource | Unauthenticated | Regular Farmer (`role="farmer"`) | Administrator (`role="admin"`) |
|---|:---:|:---:|:---:|
| Farmer Registration & Login | ✅ | ✅ | ✅ |
| Farmer Dashboard & Weather | ❌ | ✅ (Own data only) | ✅ |
| AI Chatbot & Agronomic Advice | ❌ | ✅ (Own history) | ✅ |
| Crop, Diary, Expense, Harvest CRUD | ❌ | ✅ (Own records only) | ✅ (Own records only) |
| Mandi Price Comparison | ❌ | ✅ | ✅ |
| Government Schemes Directory | ❌ | ✅ | ✅ |
| Admin Panel Navigation Tab | ❌ | ❌ (Hidden & Guarded) | ✅ |
| Platform Overview KPIs | ❌ | ❌ (403 Forbidden) | ✅ |
| Manage Farmer Accounts / Deactivate | ❌ | ❌ (403 Forbidden) | ✅ |
| Aggregated Analytics (Crops/Fin/AI) | ❌ | ❌ (403 Forbidden) | ✅ |
| Export Data (CSV / XLSX / JSON) | ❌ | ❌ (403 Forbidden) | ✅ |
| Database Backup & Restore | ❌ | ❌ (403 Forbidden) | ✅ |
| Admin Audit Logs | ❌ | ❌ (403 Forbidden) | ✅ |

### 6.2 Tenant Data Isolation
Every data-access method in `CropService`, `ActivityService`, `ExpenseService`, and `HarvestService` strictly enforces ownership checks via `verify_farmer_ownership()` in [`core/auth.py`](file:///C:/Users/Admin/Desktop/AI-Farming-Assistant/core/auth.py):
```python
def verify_farmer_ownership(requesting_farmer_id: str, resource_farmer_id: str, resource_name: str = "Resource"):
    if requesting_farmer_id != resource_farmer_id:
        raise AuthorizationError(f"Access denied: You do not own this {resource_name.lower()}.")
```
Cross-farmer data access is mathematically impossible at the service layer, backed by unit tests (`tests/test_authorization.py`).

### 6.3 Password Hashing & Secret Protection
- **Argon2id**: Farmer and admin passwords are never stored in plaintext. They are hashed using Argon2id with random salts via `argon2-cffi`.
- **Zero-Secret Export Guarantee**: All data exports (CSV, Excel, JSON) strictly exclude `password`, `password_hash`, `token`, and API keys.
- **Error Privacy**: Production configurations redact internal SQL statements and connection strings from the frontend, logging full diagnostic details solely to server logs.

### 6.4 Default Administrator Account
Configurable via environment variables (with development defaults in `config.py`):
- **Email:** `admin@agrisaathi.com`
- **Password:** `Admin@Agri2026!`
- **Phone:** `9999999999`
- **Access Route:** Login screen $\rightarrow$ 3rd tab: **`🛠️ ॲडमिन (Admin Login)`**.

---

## 7. Installation & Local Setup

### 7.1 Prerequisites
- **Python**: Version 3.11, 3.12, or 3.13.
- **Operating System**: Windows 10/11, Ubuntu/Debian Linux, or macOS.
- **Gemini API Key**: Free API key from [Google AI Studio](https://aistudio.google.com/).

### 7.2 Step-by-Step PowerShell Guide

```powershell
# 1. Navigate to project root
cd "$env:USERPROFILE\Desktop\AI-Farming-Assistant"

# 2. Create and activate a Python virtual environment
python -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1

# 3. Upgrade pip and install all required dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# 4. Create environment file from template
Copy-Item .env.example .env

# 5. Edit .env and paste your GEMINI_API_KEY
# (Optional) Add your DATA_GOV_API_KEY for live Agmarknet prices

# 6. Initialize database and seed verified ICAR agronomic knowledge
python scripts/seed_knowledge.py

# 7. Start the AgriSaathi AI application
streamlit run app.py
```
The application will launch in your default web browser at `http://localhost:8501`.

### 7.3 Environment Variables Reference

| Variable | Type | Default | Description |
|---|---|---|---|
| `APP_NAME` | string | `"AgriSaathi AI"` | Application title. |
| `APP_ENV` | string | `"development"` | Environment (`development` / `production`). |
| `SECRET_KEY` | string | `dev-secret-...` | Secret key for session security. |
| `DATABASE_URL` | string | `sqlite:///./data/agrisaathi.db` | SQLAlchemy connection URL (SQLite or PostgreSQL). |
| `AI_PROVIDER` | string | `"gemini"` | Primary AI provider (`"gemini"` or `"ollama"`). |
| `GEMINI_API_KEY` | string | `""` | Google Gemini API key from AI Studio. |
| `GEMINI_MODEL` | string | `"gemini-3.5-flash-lite"` | Primary Gemini model. |
| `ENABLE_OLLAMA_FALLBACK` | boolean | `false` | Enable fallback to local Ollama if Gemini fails. |
| `OLLAMA_BASE_URL` | string | `"http://localhost:11434"` | URL for local Ollama daemon. |
| `OLLAMA_MODEL` | string | `"qwen2.5:3b"` | Model tag for Ollama. |
| `DATA_GOV_API_KEY` | string | `""` | API key from data.gov.in for live Mandi rates. |
| `MANDI_CACHE_TTL_MINUTES`| int | `60` | In-memory and DB cache TTL for market prices. |
| `MANDI_MAX_RECORDS` | int | `100` | Max APMC records fetched per commodity query. |
| `ADMIN_DEFAULT_EMAIL` | string | `"admin@agrisaathi.com"` | Default seeded administrator email. |
| `ADMIN_DEFAULT_PASSWORD`| string | `"Admin@Agri2026!"` | Default seeded administrator password. |

---

## 8. Production Deployment Guide

### 8.1 Streamlit Community Cloud
1. Push repository to GitHub: `https://github.com/<your-username>/agri-saathi-ai`.
2. Connect repository to [share.streamlit.io](https://share.streamlit.io).
3. Set **Main file path** to `app.py`.
4. In **App settings $\rightarrow$ Secrets**, enter:
   ```toml
   GEMINI_API_KEY = "AIzaSy..."
   DATA_GOV_API_KEY = "579b464db66ec23bdd000001..."
   ADMIN_DEFAULT_PASSWORD = "YourStrongAdminPassword2026!"
   ```
5. Deploy! On boot, `app.py` runs `bootstrap_database()` to configure the schema, tables, seed knowledge, and create the admin user automatically.

### 8.2 Persistent PostgreSQL Deployment
1. Provision a PostgreSQL instance (e.g. AWS RDS, Railway, Supabase, Neon).
2. Set `DATABASE_URL=postgresql://user:password@host:5432/agrisaathi` in environment.
3. Run migrations:
   ```bash
   alembic upgrade head
   ```
4. If migrating from SQLite with existing farmer data:
   ```bash
   python scripts/migrate_sqlite_to_postgres.py --sqlite data/agrisaathi.db --pg "postgresql://user:password@host:5432/agrisaathi"
   ```

### 8.3 Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

---

## 9. Automated Testing & Code Quality

### 9.1 Test Suite Breakdown (101 Tests)

All 101 tests run using mocked external APIs to ensure tests execute offline in $<30\text{s}$ without consuming paid API quotas:

```powershell
.\venv\Scripts\pytest.exe -v
```

```text
============================= test session starts =============================
platform win32 -- Python 3.13.1, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\Admin\Desktop\AI-Farming-Assistant
configfile: pyproject.toml
testpaths: tests
collected 101 items

tests/test_activities.py ......                                          [  5%]
tests/test_admin_rbac_and_exports.py ...........                         [ 16%]
tests/test_auth.py .........                                             [ 25%]
tests/test_authorization.py .....                                        [ 30%]
tests/test_chat.py ......                                                [ 37%]
tests/test_crops.py ......                                               [ 43%]
tests/test_crud_operations.py ....                                       [ 47%]
tests/test_database_init.py ....                                         [ 51%]
tests/test_expenses.py ....                                              [ 55%]
tests/test_gemini.py ..........                                          [ 65%]
tests/test_harvest.py ..                                                 [ 67%]
tests/test_knowledge.py ...                                              [ 70%]
tests/test_mandi_multi_market.py ............                            [ 81%]
tests/test_safety.py ...                                                 [ 84%]
tests/test_services.py ....                                              [ 88%]
tests/test_ui_theme_and_navigation.py .......                            [ 95%]
tests/test_uploads.py .....                                              [100%]

============================ 101 passed in 29.70s =============================
```

### 9.2 Static Analysis & Linting

```powershell
.\venv\Scripts\ruff.exe check .
```
Result: **All checks passed! Zero warnings or lint errors.**

---

## 10. Directory & File Structure

```
AI-Farming-Assistant/
├── app.py                      # Main Streamlit application entrypoint & routing
├── config.py                   # Pydantic Settings & environment variable configuration
├── requirements.txt            # Python production dependencies (google-genai, openpyxl, etc.)
├── pyproject.toml              # Ruff and packaging configuration
├── alembic.ini                 # Alembic database migration config
├── README.md                   # Quickstart guide & repository overview
├── DOCUMENTATION.md            # Master technical and architectural documentation
├── .env.example                # Sanitized template for environment variables
├── .gitignore                  # Git ignore rules (secrets, venv, sqlite files)
│
├── .streamlit/
│   └── config.toml             # Streamlit server and theme configuration
│
├── core/                       # Core system architecture
│   ├── auth.py                 # AuthenticatedFarmer identity, require_admin, tenant guards
│   ├── database.py             # SQLAlchemy engine, session maker, idempotent init_db
│   ├── exceptions.py           # Standard application exceptions (NotFoundError, etc.)
│   └── security.py             # Argon2id password hashing and verification
│
├── models/                     # SQLAlchemy 2.x relational ORM models
│   ├── __init__.py             # Model exports and registration
│   ├── user.py                 # User model (farmer profile & role: farmer / admin)
│   ├── crop.py                 # Crop model (variety, plot, sowing, growth stage)
│   ├── activity.py             # FarmActivity model (diary operations, inputs, cost)
│   ├── expense.py              # Expense model (categorized farm input expenses)
│   ├── harvest.py              # HarvestRecord model (yields, sold rates, revenue)
│   ├── conversation.py         # Conversation & Message models for AI dialogue
│   ├── knowledge.py            # CropKnowledge & KnowledgeDocument for RAG library
│   ├── health_observation.py   # HealthObservation model for disease checks
│   ├── mandi.py                # MandiPriceCache & MandiPriceHistory models
│   └── admin_log.py            # AdminAuditLog model for developer audit trail
│
├── schemas/                    # Pydantic validation schemas
│   ├── user.py                 # Registration, login, profile schemas
│   ├── crop.py                 # CropCreate, CropUpdate, CropResponse
│   ├── activity.py             # ActivityCreate, ActivityUpdate, ActivityResponse
│   ├── expense.py              # ExpenseCreate, ExpenseSummary
│   ├── harvest.py              # HarvestCreate, HarvestSummary
│   └── chat.py                 # Message & conversation schemas
│
├── services/                   # Application service layer
│   ├── user_service.py         # Farmer authentication & admin seeding
│   ├── crop_service.py         # Multi-tenant crop management
│   ├── activity_service.py     # Farm diary logging with self-healing migration
│   ├── expense_service.py      # Expense tracking & summary calculations
│   ├── harvest_service.py      # Harvest yield & net profit calculations
│   ├── gemini_service.py       # Google GenAI SDK integration with streaming
│   ├── ollama_service.py       # Local Ollama client (offline fallback)
│   ├── chat_service.py         # Multi-provider routing, RAG context injection
│   ├── knowledge_service.py    # TF-IDF RAG retrieval over verified agronomy docs
│   ├── weather_service.py      # Open-Meteo forecasts & practical spray advisory
│   ├── mandi_service.py        # Agmarknet multi-market comparison & net profit ranking
│   ├── schemes_service.py      # Government agricultural schemes explorer
│   ├── image_service.py        # Magic-byte upload verification & diagnosis
│   ├── admin_service.py        # Developer Admin analytics & multi-format exports
│   └── backup_service.py       # Atomic SQLite online backup & safe restore
│
├── ui/                         # Streamlit user interface layer
│   ├── state.py                # Session state initialization and page navigation
│   ├── theme.py                # Mobile-first CSS styles, typography, and badges
│   ├── auth_pages.py           # Farmer login, registration & Admin Login tabs
│   ├── dashboard.py            # Farmer-friendly homepage with weather & crop cards
│   ├── crops_page.py           # Crop plots overview and active/harvested tabs
│   ├── crop_detail.py          # Detailed timeline, diary, and finances per crop
│   ├── chat_page.py            # Interactive multilingual AI chatbot with streaming
│   ├── diary_page.py           # Farm diary activity logger
│   ├── expenses_page.py        # Farm expense logger with categorical breakdown
│   ├── harvest_page.py         # Harvest yields, selling rates & net profit ledger
│   ├── weather_page.py         # Live weather forecast and spray advisory
│   ├── market_page.py          # APMC mandi multi-market comparison engine
│   ├── schemes_page.py         # Welfare schemes & subsidy directory
│   ├── image_page.py           # Crop symptom checker & photo uploader
│   ├── profile_page.py         # Farmer profile editor & account security
│   └── admin_page.py           # 9-tab Developer Admin Panel & Data Management
│
├── utils/                      # Helper utilities
│   ├── formatting.py           # Indian Rupee (INR) and localized date formatting
│   ├── language.py             # Multilingual dictionary (mr, hi, en)
│   ├── logging_config.py       # Structured logging with Windows UTF-8 safety
│   ├── prompts.py              # Context-aware agricultural system prompts
│   └── validation.py           # File extension, size, and header validation
│
├── scripts/                    # CLI tools & maintenance utilities
│   ├── init_db.py              # Standalone database initialization
│   ├── seed_knowledge.py      # Seed verified ICAR crop library & RAG passages
│   └── migrate_sqlite_to_postgres.py # SQLite -> PostgreSQL migration CLI
│
├── migrations/                 # Alembic migration revisions
│   ├── env.py
│   └── versions/
│       ├── 2026_10_29_26a2e603f0b0_initial_schema.py
│       ├── 2026_10_30_add_mandi_history.py
│       ├── 2026_10_31_add_admin_and_role.py
│       └── 2026_10_31_add_cost_to_farm_activities.py
│
└── tests/                      # Automated Pytest suite (101 tests)
    ├── conftest.py             # Fixtures: in-memory DB, farmers, crops, admin
    ├── test_activities.py      # Farm diary, tenant isolation, self-healing migration
    ├── test_admin_rbac_and_exports.py # Admin RBAC, analytics, CSV/XLSX/JSON exports
    ├── test_auth.py            # Registration, login, password hashing
    ├── test_authorization.py   # Strict tenant isolation verification
    ├── test_chat.py            # Chat routing, bounded memory, streaming
    ├── test_crops.py           # Crop CRUD and lifecycle stages
    ├── test_crud_operations.py # Full CRUD lifecycle across all modules
    ├── test_database_init.py   # Database bootstrap and users table existence
    ├── test_expenses.py        # Expense creation, validation, summaries
    ├── test_gemini.py          # Google Gemini SDK unit tests (mocked)
    ├── test_harvest.py         # Harvest recording & net profit calculations
    ├── test_knowledge.py       # TF-IDF RAG retrieval and ICAR crop lookups
    ├── test_mandi_multi_market.py # Agmarknet normalization, net return ranking
    ├── test_safety.py          # Prompt injection & chemical dosage guardrails
    ├── test_services.py        # Weather, schemes, and mandi services
    ├── test_ui_theme_and_navigation.py # Navigation states & i18n keys
    └── test_uploads.py         # Magic byte validation & file security
```

---

*Authored by Vishal Sonwane — Platform Architect & Creator of AgriSaathi AI.*
