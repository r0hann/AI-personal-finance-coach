# Graph Report - /Users/rohan/Desktop/Project/LLM/AiPersonalFinanceCoach  (2026-07-21)

## Corpus Check
- Corpus is ~4,872 words - fits in a single context window. You may not need a graph.

## Summary
- 178 nodes · 205 edges · 18 communities (15 shown, 3 thin omitted)
- Extraction: 80% EXTRACTED · 20% INFERRED · 0% AMBIGUOUS · INFERRED: 40 edges (avg confidence: 0.84)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Frontend API Client Layer|Frontend API Client Layer]]
- [[_COMMUNITY_Python Dependencies & Packages|Python Dependencies & Packages]]
- [[_COMMUNITY_Backend Routing & Database|Backend Routing & Database]]
- [[_COMMUNITY_React Frontend & Dependencies|React Frontend & Dependencies]]
- [[_COMMUNITY_Data Models & Schemas|Data Models & Schemas]]
- [[_COMMUNITY_TypeScript Configuration|TypeScript Configuration]]
- [[_COMMUNITY_AI Categorization & CSV Import|AI Categorization & CSV Import]]
- [[_COMMUNITY_Gemini Chat Service|Gemini Chat Service]]
- [[_COMMUNITY_App Configuration & Settings|App Configuration & Settings]]
- [[_COMMUNITY_Claude Code Local Settings|Claude Code Local Settings]]
- [[_COMMUNITY_Pydantic Validation|Pydantic Validation]]
- [[_COMMUNITY_File Upload Support|File Upload Support]]

## God Nodes (most connected - your core abstractions)
1. `get_client()` - 13 edges
2. `AI Personal Finance Coach — Project Guide` - 13 edges
3. `compilerOptions` - 12 edges
4. `.env Environment File` - 6 edges
5. `forecast()` - 5 edges
6. `Backend Docker Service` - 5 edges
7. `Monthly Insights & Savings Feature (Claude claude-haiku-4-5-20251001)` - 5 edges
8. `scripts` - 4 edges
9. `import_csv()` - 4 edges
10. `monthly_insights()` - 4 edges

## Surprising Connections (you probably didn't know these)
- `Backend Docker Service` --semantically_similar_to--> `Backend Stack: Python 3.11 + FastAPI + uvicorn`  [INFERRED] [semantically similar]
  docker-compose.yml → CLAUDE.md
- `Frontend Docker Service` --semantically_similar_to--> `Frontend Stack: React + TypeScript + Tailwind CSS + Recharts`  [INFERRED] [semantically similar]
  docker-compose.yml → CLAUDE.md
- `Frontend Entry Script (src/main.tsx)` --semantically_similar_to--> `Frontend Stack: React + TypeScript + Tailwind CSS + Recharts`  [INFERRED] [semantically similar]
  frontend/index.html → CLAUDE.md
- `python-dotenv==1.0.1` --references--> `.env Environment File`  [INFERRED]
  backend/requirements.txt → docker-compose.yml
- `ANTHROPIC_API_KEY env var` --conceptually_related_to--> `.env Environment File`  [INFERRED]
  CLAUDE.md → docker-compose.yml

## Communities (18 total, 3 thin omitted)

### Community 0 - "Frontend API Client Layer"
Cohesion: 0.08
Nodes (16): api, getForecast(), importCSV(), listTransactions(), monthlyInsights(), monthlySummary(), Alert, ForecastData (+8 more)

### Community 1 - "Python Dependencies & Packages"
Cohesion: 0.09
Nodes (32): anthropic==0.43.0, fastapi==0.115.6, google-generativeai==0.8.3, pandas==2.2.3, python-dotenv==1.0.1, supabase==2.11.0, uvicorn[standard]==0.32.1, Frontend Entry Point (index.html) (+24 more)

### Community 2 - "Backend Routing & Database"
Cohesion: 0.10
Nodes (22): get_client(), create_budget(), delete_budget(), forecast(), list_budgets(), _get_spending_by_category(), monthly_insights(), list_transactions() (+14 more)

### Community 3 - "React Frontend & Dependencies"
Cohesion: 0.08
Nodes (23): dependencies, axios, react, react-dom, react-router-dom, recharts, devDependencies, autoprefixer (+15 more)

### Community 4 - "Data Models & Schemas"
Cohesion: 0.19
Nodes (10): BaseModel, Budget, BudgetCreate, Category, Transaction, TransactionUpdate, chat(), ChatMessage (+2 more)

### Community 5 - "TypeScript Configuration"
Cohesion: 0.14
Nodes (13): compilerOptions, allowImportingTsExtensions, isolatedModules, jsx, lib, module, moduleResolution, noEmit (+5 more)

### Community 6 - "AI Categorization & CSV Import"
Cohesion: 0.24
Nodes (9): import_csv(), categorize_batch(), categorize_transactions_bulk(), _keyword_category(), AI categorization using Claude Haiku with prompt caching., Categorize up to 50 transaction descriptions. Returns {description: category}., Categorize any number of descriptions in batches of 50., _find_col() (+1 more)

### Community 7 - "Gemini Chat Service"
Cohesion: 0.50
Nodes (4): build_spending_context(), Financial Q&A chat using Gemini 2.5 Flash with streaming., Stream a Gemini chat response.     history: list of {"role": "user"|"model", "pa, stream_chat_response()

### Community 8 - "App Configuration & Settings"
Cohesion: 0.50
Nodes (3): Config, Settings, BaseSettings

## Knowledge Gaps
- **56 isolated node(s):** `name`, `private`, `version`, `type`, `dev` (+51 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_client()` connect `Backend Routing & Database` to `Data Models & Schemas`, `AI Categorization & CSV Import`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Why does `import_csv()` connect `AI Categorization & CSV Import` to `Backend Routing & Database`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `get_client()` (e.g. with `list_budgets()` and `create_budget()`) actually correct?**
  _`get_client()` has 12 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `private`, `version` to the rest of the system?**
  _69 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Frontend API Client Layer` be split into smaller, more focused modules?**
  _Cohesion score 0.07765151515151515 - nodes in this community are weakly interconnected._
- **Should `Python Dependencies & Packages` be split into smaller, more focused modules?**
  _Cohesion score 0.08870967741935484 - nodes in this community are weakly interconnected._
- **Should `Backend Routing & Database` be split into smaller, more focused modules?**
  _Cohesion score 0.10052910052910052 - nodes in this community are weakly interconnected._