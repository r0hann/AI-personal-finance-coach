"""Generate project documentation PDF."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from datetime import date

OUTPUT = "AI_Personal_Finance_Coach_Documentation.pdf"

doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    leftMargin=2*cm, rightMargin=2*cm,
    topMargin=2*cm, bottomMargin=2*cm,
)

styles = getSampleStyleSheet()

# Custom styles
H1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=22, textColor=colors.HexColor("#4F46E5"), spaceAfter=6)
H2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=14, textColor=colors.HexColor("#1F2937"), spaceBefore=14, spaceAfter=4)
H3 = ParagraphStyle("H3", parent=styles["Heading3"], fontSize=11, textColor=colors.HexColor("#374151"), spaceBefore=8, spaceAfter=2)
BODY = ParagraphStyle("BODY", parent=styles["Normal"], fontSize=10, leading=15, spaceAfter=4)
CODE = ParagraphStyle("CODE", parent=styles["Code"], fontSize=8.5, leading=13, backColor=colors.HexColor("#F3F4F6"), borderPadding=(4, 6, 4, 6))
SUBTITLE = ParagraphStyle("SUBTITLE", parent=styles["Normal"], fontSize=11, textColor=colors.HexColor("#6B7280"), spaceAfter=20, alignment=TA_CENTER)
TITLE_STYLE = ParagraphStyle("TITLE", parent=H1, fontSize=28, alignment=TA_CENTER, spaceAfter=8)

TABLE_STYLE = TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F46E5")),
    ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
    ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
    ("FONTSIZE",   (0, 0), (-1, 0), 9),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
    ("FONTSIZE",   (0, 1), (-1, -1), 9),
    ("GRID",       (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
    ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
    ("LEFTPADDING",  (0, 0), (-1, -1), 8),
    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ("TOPPADDING",   (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
])

def table(headers, rows, col_widths):
    data = [[Paragraph(f"<b>{h}</b>", ParagraphStyle("TH", parent=BODY, textColor=colors.white, fontSize=9)) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(cell), BODY) for cell in row])
    t = Table(data, colWidths=col_widths)
    t.setStyle(TABLE_STYLE)
    return t

def hr():
    return HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E5E7EB"), spaceAfter=8, spaceBefore=4)

story = []

# ── Title page ──────────────────────────────────────────────────────────────
story += [
    Spacer(1, 2*cm),
    Paragraph("💰 AI Personal Finance Coach", TITLE_STYLE),
    Paragraph("Project Documentation", SUBTITLE),
    Paragraph(f"Generated: {date.today().strftime('%B %d, %Y')}", SUBTITLE),
    Spacer(1, 1*cm),
    hr(),
]

# ── 1. Overview ──────────────────────────────────────────────────────────────
story += [
    Paragraph("1. Project Overview", H2),
    Paragraph(
        "AI Personal Finance Coach is a full-stack web application that helps users track, "
        "categorize, and understand their personal finances using AI. Users import bank CSV "
        "exports, and the app automatically categorizes transactions, generates monthly insights, "
        "tracks budgets, and provides a conversational AI finance coach.",
        BODY,
    ),
    Spacer(1, 0.3*cm),
]

# Architecture diagram (text-based)
story += [
    Paragraph("Architecture", H3),
    Paragraph(
        "Browser (React + TypeScript)  ←→  FastAPI (Python 3.11)  ←→  Supabase (Postgres)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
        "↕<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;AI Providers: Gemini · GitHub Models · Ollama",
        CODE,
    ),
    Spacer(1, 0.3*cm),
]

# Tech stack table
story += [
    Paragraph("Tech Stack", H3),
    table(
        ["Layer", "Technology", "Purpose"],
        [
            ["Frontend", "React + TypeScript + Tailwind CSS + Recharts", "UI, charts, streaming chat"],
            ["Backend", "Python 3.11 + FastAPI + uvicorn", "REST API, business logic"],
            ["Database", "Supabase (hosted Postgres)", "Transactions, budgets, cache"],
            ["AI — Categorization", "Gemini 2.0 Flash (primary)", "Batch transaction classification"],
            ["AI — Insights/Budget", "GitHub Models (primary)", "Monthly analysis, forecast narrative"],
            ["AI — Chat", "Gemini 2.0 Flash (primary)", "Streaming finance Q&A"],
            ["AI — Fallback", "Ollama (local)", "Offline fallback for all features"],
            ["Data Import", "pandas", "CSV parsing and column detection"],
        ],
        [3.5*cm, 7*cm, 5.5*cm],
    ),
    Spacer(1, 0.5*cm),
]

# ── 2. Data Flow ─────────────────────────────────────────────────────────────
story += [
    hr(),
    Paragraph("2. Data Flow — CSV Import", H2),
    Paragraph(
        "The CSV import is the entry point for all financial data. The pipeline runs in sequence:",
        BODY,
    ),
    Paragraph(
        "1. User uploads bank CSV via the Transactions page<br/>"
        "2. <b>csv_parser.py</b> auto-detects column names (Date / Details / Amount / Reference)<br/>"
        "3. <b>categorizer.py</b> classifies each transaction in two stages:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>Stage 1 — Keywords</b> (instant, free): e.g. \"woolworths\" → Groceries<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;<b>Stage 2 — AI</b> (for unmatched): sends batches of 50 to Gemini<br/>"
        "4. Transactions are upserted into Supabase using the bank's <b>Reference</b> column as the "
        "unique key — re-importing the same CSV skips duplicates automatically<br/>"
        "5. If all AI providers fail, transactions are saved as \"Other\" (import never crashes)",
        BODY,
    ),
    Spacer(1, 0.5*cm),
]

# ── 3. AI Provider System ────────────────────────────────────────────────────
story += [
    hr(),
    Paragraph("3. AI Provider System", H2),
    Paragraph(
        "All AI calls go through a unified ai_provider.py layer with automatic fallback chains. "
        "No router or service calls SDK libraries directly.",
        BODY,
    ),
    table(
        ["Feature", "Primary", "Fallback 1", "Fallback 2"],
        [
            ["Transaction categorization", "Gemini 2.0 Flash", "GitHub Models", "Ollama (local)"],
            ["Monthly insights",           "GitHub Models",    "Gemini",        "Ollama (local)"],
            ["Budget forecast narrative",  "GitHub Models",    "Gemini",        "Ollama (local)"],
            ["Finance chat (streaming)",   "Gemini 2.0 Flash", "GitHub Models", "Ollama (local)"],
        ],
        [5*cm, 4*cm, 3.5*cm, 3.5*cm],
    ),
    Spacer(1, 0.3*cm),
    Paragraph(
        "Provider failures are automatically logged to the error_logs table and visible in the "
        "frontend Errors page. Gemini free tier limit is ~1,500 requests/day.",
        BODY,
    ),
    Spacer(1, 0.5*cm),
]

# ── 4. Database Schema ───────────────────────────────────────────────────────
story += [
    hr(),
    Paragraph("4. Database Schema", H2),
    table(
        ["Table", "Key Columns", "Purpose"],
        [
            ["categories",     "id, name, color, icon",                       "Predefined + custom spending categories (15 defaults)"],
            ["transactions",   "id, date, description, amount, category_id, external_ref", "Every bank transaction, linked to a category"],
            ["budgets",        "id, category_id, monthly_limit, month_year",  "Monthly spending limits per category"],
            ["insights_cache", "id, month_year, content_json, generated_at",  "AI-generated insights cached for 24 hours"],
            ["error_logs",     "id, timestamp, source, error_type, message, details", "Auto-logged backend errors"],
        ],
        [3.5*cm, 6.5*cm, 6*cm],
    ),
    Spacer(1, 0.3*cm),
    Paragraph(
        "Important: expenses are stored as negative amounts (e.g. -37.50). Income is positive. "
        "All money values use numeric(12,2) — never float — to avoid rounding errors. "
        "The service_role Supabase key is used server-side, bypassing RLS.",
        BODY,
    ),
    Spacer(1, 0.5*cm),
]

# ── 5. API Routes ─────────────────────────────────────────────────────────────
story += [
    hr(),
    Paragraph("5. API Endpoints", H2),
    table(
        ["Method", "Route", "Description"],
        [
            ["POST",   "/transactions/import/csv",        "Parse, categorize, and store a bank CSV"],
            ["GET",    "/transactions/",                  "List transactions, filtered by month"],
            ["PATCH",  "/transactions/:id",               "Manually update a transaction's category"],
            ["GET",    "/transactions/summary/monthly",   "Spending totals grouped by category"],
            ["GET",    "/insights/monthly",               "AI monthly analysis (cached 24h)"],
            ["GET",    "/budget/forecast",                "3-month rolling avg vs budget limits"],
            ["GET",    "/budget/",                        "List budget limits for a month"],
            ["POST",   "/budget/",                        "Create/update a monthly budget limit"],
            ["DELETE", "/budget/:id",                     "Delete a budget limit"],
            ["POST",   "/chat/",                          "Streaming AI finance Q&A"],
            ["GET",    "/error-logs/",                    "Fetch recent error logs"],
            ["DELETE", "/error-logs/",                    "Clear all error logs"],
            ["GET",    "/health",                         "Health check"],
        ],
        [2*cm, 6*cm, 8*cm],
    ),
    Spacer(1, 0.5*cm),
]

# ── 6. Frontend Pages ─────────────────────────────────────────────────────────
story += [
    hr(),
    Paragraph("6. Frontend Pages", H2),
    table(
        ["Page", "Route", "What it shows"],
        [
            ["Dashboard",     "/",            "Pie chart of this month's spending + 5 recent transactions"],
            ["Transactions",  "/transactions","Full transaction list with manual category editing"],
            ["Insights",      "/insights",    "AI-generated monthly analysis with savings suggestions"],
            ["Budget",        "/budget",      "Set spending limits, view forecast, over-budget alerts"],
            ["Ask AI",        "/chat",        "Streaming conversational finance coach with spending context"],
            ["Error Logs",    "/error-logs",  "Auto-logged backend errors with copy and clear actions"],
        ],
        [3.5*cm, 3.5*cm, 9*cm],
    ),
    Spacer(1, 0.5*cm),
]

# ── 7. Key Features ───────────────────────────────────────────────────────────
story += [
    hr(),
    Paragraph("7. Key Design Decisions", H2),
    Paragraph("<b>Duplicate detection:</b> The bank's Reference column is stored as external_ref with a unique index. Re-importing the same CSV is safe — existing rows are skipped.", BODY),
    Paragraph("<b>Non-fatal categorization:</b> If all AI providers fail during CSV import, transactions are saved with category \"Other\" so the import always succeeds.", BODY),
    Paragraph("<b>Insights caching:</b> AI insights are cached in the database for 24 hours to avoid burning API quota on every page load.", BODY),
    Paragraph("<b>Streaming chat:</b> The chat page uses fetch() with response.body.getReader() (not axios) to stream tokens word-by-word. Spending context is injected automatically.", BODY),
    Paragraph("<b>Provider abstraction:</b> ai_provider.py is the only file that imports SDK libraries. All services call complete() or stream() — making it trivial to swap or add providers.", BODY),
    Paragraph("<b>Error logging:</b> errors_logger.py writes failures to the error_logs table silently — it never raises, so a logging failure cannot crash the app.", BODY),
    Spacer(1, 0.5*cm),
]

# ── 8. Environment Variables ──────────────────────────────────────────────────
story += [
    hr(),
    Paragraph("8. Environment Variables", H2),
    table(
        ["Variable", "Used by", "Description"],
        [
            ["GOOGLE_API_KEY",      "Backend", "Gemini API key for categorization and chat"],
            ["GITHUB_TOKEN",        "Backend", "GitHub Models PAT (needs 'models' permission)"],
            ["SUPABASE_URL",        "Backend", "Supabase project URL"],
            ["SUPABASE_SERVICE_KEY","Backend", "Supabase service_role JWT (long, starts with eyJ...)"],
            ["VITE_API_BASE_URL",   "Frontend","Backend base URL (default: http://localhost:8000)"],
        ],
        [4.5*cm, 2.5*cm, 9*cm],
    ),
    Spacer(1, 0.3*cm),
    Paragraph("All variables live in the .env file at the project root. The backend config.py loads them via pydantic-settings using an absolute path, so they are accessible regardless of which directory uvicorn is launched from.", BODY),
    Spacer(1, 0.5*cm),
]

# ── 9. Running Locally ────────────────────────────────────────────────────────
story += [
    hr(),
    Paragraph("9. Running Locally", H2),
    Paragraph("<b>Backend:</b>", BODY),
    Paragraph(
        "cd backend<br/>"
        "source ../.venv/bin/activate<br/>"
        "pip install -r requirements.txt<br/>"
        "uvicorn main:app --reload",
        CODE,
    ),
    Spacer(1, 0.2*cm),
    Paragraph("<b>Frontend:</b>", BODY),
    Paragraph(
        "cd frontend<br/>"
        "npm install<br/>"
        "npm run dev",
        CODE,
    ),
    Spacer(1, 0.3*cm),
    Paragraph("Backend runs on http://localhost:8000 · Frontend on http://localhost:5173", BODY),
]

doc.build(story)
print(f"PDF generated: {OUTPUT}")
