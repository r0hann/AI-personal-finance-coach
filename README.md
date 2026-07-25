# AI Personal Finance Coach

A full-stack personal finance app that ingests bank CSV exports, auto-categorizes transactions with AI, and provides insights, budget forecasting, and a conversational financial coach — all powered by a multi-provider AI fallback chain (Gemini → GitHub Models → Ollama).

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture & Workflow](#architecture--workflow)
  - [1. CSV Import & Parsing](#1-csv-import--parsing)
  - [2. AI Categorization](#2-ai-categorization)
  - [3. Transaction Storage & Retrieval](#3-transaction-storage--retrieval)
  - [4. Monthly Insights](#4-monthly-insights)
  - [5. Budget Forecasting](#5-budget-forecasting)
  - [6. Financial Q&A Chat](#6-financial-qa-chat)
  - [7. AI Provider Fallback Chain](#7-ai-provider-fallback-chain)
- [Database Schema](#database-schema)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Environment Variables](#environment-variables)
  - [Run Locally](#run-locally)
  - [Run with Docker](#run-with-docker)
- [API Reference](#api-reference)
- [Frontend Pages](#frontend-pages)

---

## Features

| Feature | Description |
|---|---|
| CSV Import | Upload bank statements from any bank — auto-detects column names |
| AI Categorization | Batch-classifies transactions into 14 categories via keyword rules + AI |
| Monthly Insights | AI-generated spending analysis with patterns, anomalies, and savings suggestions |
| Budget Forecasting | 3-month rolling averages compared against user-set limits, with AI narrative |
| Financial Chat | Streaming conversational coach grounded in your actual spending data |
| Error Logging | In-app log of all AI provider failures and import errors |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI, uvicorn |
| Frontend | React, TypeScript, Tailwind CSS, Recharts |
| Database | Supabase (hosted Postgres) |
| Data import | pandas |
| AI (primary) | Gemini 2.0 Flash (`google-generativeai`) |
| AI (fallback) | GitHub Models — GPT-4o-mini (OpenAI-compatible SDK) |
| AI (local fallback) | Ollama — llama3.2 |
| Container | Docker + Docker Compose |

---

## Architecture & Workflow

```
User Browser
    │
    │  React + TypeScript + Tailwind
    ▼
FastAPI Backend (port 8000)
    │
    ├── /transactions  ──▶  CSV Parser ──▶ Categorizer ──▶ Supabase DB
    ├── /insights      ──▶  insights_cache check ──▶ AI Coach ──▶ Supabase DB
    ├── /budget        ──▶  Forecaster ──▶ AI Coach ──▶ Supabase DB
    └── /chat          ──▶  Gemini Chat (streaming) ──▶ SSE to browser
                               │
                      AI Provider Layer
                      Gemini → GitHub → Ollama
```

### 1. CSV Import & Parsing

**Endpoint:** `POST /transactions/import/csv`

The CSV parser (`backend/services/csv_parser.py`) handles bank statements from any institution by auto-detecting column names using a fuzzy mapping:

| Column type | Accepted header names |
|---|---|
| Date | `date`, `transaction date`, `posted date`, `trans. date`, `value date` |
| Description | `description`, `memo`, `details`, `narrative`, `payee`, `merchant name` |
| Amount | `amount`, `debit`, `credit`, `transaction amount` |
| Reference | `reference`, `ref`, `transaction id`, `txn id` |

Amounts follow standard bank convention: **expenses are negative, income is positive**. Rows with missing/invalid data are skipped silently; the rest are returned as `Transaction` Pydantic models.

### 2. AI Categorization

**Service:** `backend/services/categorizer.py`

Categorization runs in two stages to minimize AI costs:

**Stage 1 — Keyword rules (free, instant):**
A dictionary of ~40 merchant keywords maps descriptions directly to categories (e.g. `woolworths` → `Groceries`, `netflix` → `Subscriptions`). Supermarket rules are checked before generic food rules to avoid misclassification.

**Stage 2 — AI batch (for unknowns only):**
Descriptions that don't match any keyword are batched in groups of up to 50 and sent to the AI with a structured system prompt. The AI returns a JSON object mapping each description to one of 14 categories. Unknown or failed results fall back to `"Other"`.

**Categories:** Groceries, Food & Dining, Transport, Shopping, Entertainment, Health & Medical, Utilities, Housing, Travel, Subscriptions, Education, Personal Care, Income, Transfers, Other

After categorization, transactions are upserted into Supabase using `external_ref` as the deduplication key — reimporting the same CSV is safe.

### 3. Transaction Storage & Retrieval

**Endpoints:**
- `GET /transactions/` — list transactions, optionally filtered by `month_year` (e.g. `2024-01`)
- `PATCH /transactions/{id}` — manually re-assign a category
- `GET /transactions/summary/monthly` — category totals for a given month

All amounts are stored as `numeric(12, 2)` in Postgres. The frontend joins with the `categories` table to get display color and icon.

### 4. Monthly Insights

**Endpoint:** `GET /insights/monthly?month_year=2024-01`

**Workflow:**
1. Check `insights_cache` table — if a cached result exists and is less than 24 hours old, return it immediately (no AI call).
2. Aggregate spending by category for the requested month (expenses only, `amount < 0`).
3. Fetch the previous month's spending for comparison.
4. Call the AI with a structured 6-layer data analysis prompt (Overview → Patterns → Anomalies → Drivers → Opportunities → Risks).
5. Parse the JSON response and upsert into `insights_cache`.

**AI response shape:**
```json
{
  "summary": "2-3 sentence overview",
  "insights": [
    { "title": "...", "description": "...", "type": "warning|info|success" }
  ],
  "savings_suggestions": [
    { "category": "...", "suggestion": "...", "estimated_savings": 0.0 }
  ]
}
```

### 5. Budget Forecasting

**Endpoint:** `GET /budget/forecast`

**Workflow:**
1. `get_rolling_averages(months=3)` — queries the past 3 months of expenses and computes a per-category average monthly spend.
2. `get_budget_limits(month_year)` — fetches user-set monthly limits from the `budgets` table.
3. `get_over_budget_categories()` — flags any category where rolling average ≥ 90% of the limit.
4. `generate_budget_forecast()` — sends the comparison to the AI, which returns a 3-4 sentence plain-English narrative (overall status → top risks → bright spots → one action item).

Users can create/delete budget limits via `POST /budget/` and `DELETE /budget/{id}`.

### 6. Financial Q&A Chat

**Endpoint:** `POST /chat/` → `StreamingResponse`

**Workflow:**
1. Pull the last 2 months of spending from the DB and summarize it by category.
2. Inject the spending summary as a synthetic first exchange in the chat history (so the AI is grounded in real data without counting against message history).
3. Keep the last 6 messages of history for multi-turn context.
4. Stream the response via `StreamingResponse(media_type="text/plain")`.
5. The frontend reads chunks with `fetch` + `response.body.getReader()` and appends them to the message in real time.

The AI coach follows a behavioral finance framework: warm, non-judgmental, grounded in actual dollar amounts, with 1-2 actionable next steps per response.

### 7. AI Provider Fallback Chain

**Service:** `backend/services/ai_provider.py`

All AI calls go through a unified `complete()` / `stream()` interface — no router or service imports an AI SDK directly. Each feature has a priority chain:

| Feature | Primary | Fallback 1 | Fallback 2 |
|---|---|---|---|
| Categorization | Gemini | GitHub Models | Ollama |
| Insights | GitHub Models | Gemini | Ollama |
| Forecast | GitHub Models | Gemini | Ollama |
| Chat | Gemini | GitHub Models | Ollama |

**How fallback works:**
- `complete()`: tries each provider in order; catches `ProviderUnavailable` (rate limits, quota, connection errors), logs the failure, then tries the next. Raises `RuntimeError` only if all three fail.
- `stream()`: pulls the first chunk from a provider before committing — if it raises `ProviderUnavailable`, it falls back before any output is sent to the client. Once streaming starts, it stays on that provider.

Provider errors are written to the `error_logs` table so failures are visible in the in-app Error Logs page.

---

## Database Schema

```
categories          transactions            budgets
──────────────      ────────────────────    ──────────────────
id (uuid PK)        id (uuid PK)            id (uuid PK)
name (unique)       date                    category_id → categories
color               description             monthly_limit
icon                amount (numeric 12,2)   month_year ("2024-01")
is_custom           merchant                created_at
created_at          category_id → categories
                    raw_csv_row (jsonb)     insights_cache
                    external_ref            ──────────────────
                    created_at              id (uuid PK)
                                            month_year (unique)
                                            content_json (jsonb)
                                            generated_at
```

**Key constraints:**
- `amount` is always `numeric(12, 2)` — never `float`
- Expenses are **negative**; income is positive (standard bank convention)
- `transactions.external_ref` is used for CSV deduplication on upsert
- `budgets` has a unique constraint on `(category_id, month_year)`
- `insights_cache` is keyed by `month_year` with a 24-hour TTL enforced in code

---

## Project Structure

```
AiPersonalFinanceCoach/
├── backend/
│   ├── main.py                  # FastAPI app, CORS, router registration
│   ├── config.py                # Pydantic settings (reads .env)
│   ├── db/
│   │   └── supabase.py          # get_client() singleton
│   ├── models/
│   │   ├── transaction.py       # Transaction, TransactionUpdate
│   │   ├── budget.py            # BudgetCreate
│   │   └── category.py
│   ├── routers/
│   │   ├── transactions.py      # /transactions — import, list, update
│   │   ├── insights.py          # /insights — monthly AI insights
│   │   ├── chat.py              # /chat — streaming Q&A
│   │   ├── budget.py            # /budget — CRUD + forecast
│   │   └── error_logs.py        # /error-logs
│   └── services/
│       ├── ai_provider.py       # Unified complete()/stream() with fallback
│       ├── categorizer.py       # Keyword rules + AI batch categorization
│       ├── csv_parser.py        # Bank CSV ingestion (pandas)
│       ├── ai_coach.py          # Insights + forecast generation
│       ├── gemini_chat.py       # Chat system prompt + spending context
│       ├── forecaster.py        # Rolling averages + over-budget detection
│       └── error_logger.py      # DB error logging
├── frontend/
│   └── src/
│       ├── App.tsx              # Router + nav
│       ├── api/index.ts         # Typed API client
│       └── pages/
│           ├── Dashboard.tsx
│           ├── Transactions.tsx
│           ├── Insights.tsx
│           ├── Chat.tsx
│           ├── Budget.tsx
│           └── ErrorLogs.tsx
├── supabase/
│   └── schema.sql               # Full DB schema + seed data
├── docker-compose.yml
└── .env.example
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- A [Supabase](https://supabase.com) project (free tier works)
- At least one AI provider key (Gemini recommended — has a free tier)

### Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```env
GITHUB_TOKEN=github_pat_...       # GitHub → Settings → Developer settings → PAT
GOOGLE_API_KEY=AIza...            # Google AI Studio — free tier, ~1500 req/day
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=eyJ...

# Frontend (Vite)
VITE_API_BASE_URL=http://localhost:8000

# Ollama (optional — local free fallback)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
```

You need **at least one** of `GOOGLE_API_KEY` or `GITHUB_TOKEN`. With neither, only Ollama is available as a fallback.

### Run Locally

```bash
# 1. Apply the database schema
# Paste supabase/schema.sql into the Supabase SQL editor and run it

# 2. Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
# API available at http://localhost:8000
# Docs at http://localhost:8000/docs

# 3. Frontend (new terminal)
cd frontend
npm install
npm run dev
# App available at http://localhost:5173
```

### Run with Docker

```bash
# Requires .env to exist before starting
cp .env.example .env   # then fill in your values

docker compose up --build
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/transactions/import/csv` | Upload a bank CSV file |
| `GET` | `/transactions/` | List transactions (optional `?month_year=2024-01`) |
| `PATCH` | `/transactions/{id}` | Re-assign a transaction's category |
| `GET` | `/transactions/summary/monthly` | Category totals for a month |
| `GET` | `/insights/monthly` | AI-generated monthly insights (cached 24h) |
| `GET` | `/budget/forecast` | 3-month rolling forecast + AI narrative |
| `GET` | `/budget/` | List budget limits |
| `POST` | `/budget/` | Create or update a budget limit |
| `DELETE` | `/budget/{id}` | Delete a budget limit |
| `POST` | `/chat/` | Streaming financial Q&A (SSE) |
| `GET` | `/error-logs/` | View AI/import error log |
| `GET` | `/health` | Health check |

Interactive docs: `http://localhost:8000/docs`

---

## Frontend Pages

| Page | Route | What it does |
|---|---|---|
| Dashboard | `/` | Spending overview, category breakdown chart |
| Transactions | `/transactions` | Table of all transactions, manual re-categorization |
| Insights | `/insights` | AI-generated monthly analysis cards |
| Ask AI | `/chat` | Real-time streaming financial coach chat |
| Budget | `/budget` | Set monthly limits, view forecast and alerts |
| Error Logs | `/error-logs` | Developer view of AI failures and import errors |
