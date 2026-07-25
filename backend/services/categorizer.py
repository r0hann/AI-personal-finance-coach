"""Transaction categorization — Gemini first, Claude fallback, Ollama last resort."""
import json
import re
from typing import List
from services.ai_provider import complete, CATEGORIZATION
from db.supabase import get_client

_KEYWORD_RULES = {
    # Groceries — supermarkets before generic food rules
    "woolworths": "Groceries", "pak n save": "Groceries", "paknsave": "Groceries",
    "countdown": "Groceries", "new world": "Groceries", "four square": "Groceries",
    "supermarke": "Groceries", "supermarket": "Groceries",
    "raghuveer": "Groceries", "furein": "Groceries",
    "fresh choice": "Groceries", "moore wilson": "Groceries",
    # Transport
    "uber": "Transport", "lyft": "Transport", "metro": "Transport",
    "parking": "Transport",
    # Food & Dining — restaurants and takeaways (after supermarkets)
    "subway": "Food & Dining", "mcdonald": "Food & Dining",
    "starbucks": "Food & Dining", "chipotle": "Food & Dining",
    "doordash": "Food & Dining", "grubhub": "Food & Dining",
    "instacart": "Food & Dining",
    # Subscriptions
    "netflix": "Subscriptions", "spotify": "Subscriptions",
    "amazon prime": "Subscriptions", "hulu": "Subscriptions",
    # Shopping
    "amazon": "Shopping", "walmart": "Shopping", "target": "Shopping",
    "the warehouse": "Shopping",
    # Health
    "cvs": "Health & Medical", "walgreens": "Health & Medical",
    "chemist": "Health & Medical", "pharmacy": "Health & Medical",
    # Utilities
    "electric": "Utilities", "gas bill": "Utilities",
    "water bill": "Utilities", "internet": "Utilities",
    # Income
    "payroll": "Income", "salary": "Income", "direct dep": "Income",
    # Transfers
    "transfer": "Transfers", "zelle": "Transfers", "venmo": "Transfers",
}

_SYSTEM_PROMPT = """You are a financial transaction categorizer. Given a list of bank transaction descriptions, classify each into exactly one of these categories:

Groceries, Food & Dining, Transport, Shopping, Entertainment, Health & Medical, Utilities, Housing, Travel, Subscriptions, Education, Personal Care, Income, Transfers, Other

Rules:
- Return ONLY a JSON object mapping each description to a category name
- Use the exact category names listed above
- Groceries = supermarkets and grocery stores (Woolworths, Pak N Save, Countdown, etc.)
- Food & Dining = restaurants, cafes, takeaways, fast food
- If unsure, use "Other"
- Do not add explanations

Example input: ["WOOLWORTHS NZ 9283", "SUBWAY HOBSON ST", "NETFLIX.COM"]
Example output: {"WOOLWORTHS NZ 9283": "Groceries", "SUBWAY HOBSON ST": "Food & Dining", "NETFLIX.COM": "Subscriptions"}"""


def _keyword_category(description: str) -> str | None:
    lower = description.lower()
    for keyword, category in _KEYWORD_RULES.items():
        if keyword in lower:
            return category
    return None


def _lookup_learned(descriptions: List[str]) -> dict[str, str]:
    """Fetch previously learned mappings from the DB for the given descriptions."""
    if not descriptions:
        return {}
    db = get_client()
    rows = (
        db.table("learned_categories")
        .select("description, category_name")
        .in_("description", descriptions)
        .execute()
        .data
    )
    return {r["description"]: r["category_name"] for r in rows}


def _persist_learned(mappings: dict[str, str], source: str = "ai") -> None:
    """Upsert description → category mappings into learned_categories."""
    if not mappings:
        return
    db = get_client()
    rows = [
        {"description": desc, "category_name": cat, "source": source}
        for desc, cat in mappings.items()
        if cat != "Other"  # don't cache fallback guesses
    ]
    if rows:
        db.table("learned_categories").upsert(rows, on_conflict="description").execute()


def categorize_batch(descriptions: List[str]) -> dict[str, str]:
    """Categorize up to 50 transaction descriptions. Returns {description: category}."""
    result: dict[str, str] = {}

    # Stage 1: keyword rules (free, instant)
    to_lookup: List[str] = []
    for desc in descriptions:
        cat = _keyword_category(desc)
        if cat:
            result[desc] = cat
        else:
            to_lookup.append(desc)

    if not to_lookup:
        return result

    # Stage 2: DB learned mappings (free, fast)
    learned = _lookup_learned(to_lookup)
    result.update(learned)
    to_ai = [d for d in to_lookup if d not in learned]

    if not to_ai:
        return result

    # Stage 3: AI batch for truly unknown descriptions
    try:
        text, _ = complete(
            system=_SYSTEM_PROMPT,
            user=json.dumps(to_ai),
            max_tokens=1024,
            priority=CATEGORIZATION,
        )
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            ai_results = json.loads(match.group())
            result.update(ai_results)
            _persist_learned(ai_results, source="ai")
    except RuntimeError:
        pass  # all providers failed — fall through to default below

    for desc in to_ai:
        if desc not in result:
            result[desc] = "Other"

    return result


def categorize_transactions_bulk(descriptions: List[str]) -> dict[str, str]:
    """Categorize any number of descriptions in batches of 50."""
    all_results: dict[str, str] = {}
    for i in range(0, len(descriptions), 50):
        all_results.update(categorize_batch(descriptions[i:i + 50]))
    return all_results
