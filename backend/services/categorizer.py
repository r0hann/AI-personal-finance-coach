"""Transaction categorization — Gemini first, Claude fallback, Ollama last resort."""
import json
import re
from typing import List
from services.ai_provider import complete, CATEGORIZATION

_KEYWORD_RULES = {
    "uber": "Transport", "lyft": "Transport", "metro": "Transport",
    "subway": "Transport", "parking": "Transport",
    "starbucks": "Food & Dining", "mcdonald": "Food & Dining",
    "chipotle": "Food & Dining", "doordash": "Food & Dining",
    "grubhub": "Food & Dining", "instacart": "Food & Dining",
    "netflix": "Subscriptions", "spotify": "Subscriptions",
    "amazon prime": "Subscriptions", "hulu": "Subscriptions",
    "amazon": "Shopping", "walmart": "Shopping", "target": "Shopping",
    "cvs": "Health & Medical", "walgreens": "Health & Medical",
    "electric": "Utilities", "gas bill": "Utilities",
    "water bill": "Utilities", "internet": "Utilities",
    "payroll": "Income", "salary": "Income", "direct dep": "Income",
    "transfer": "Transfers", "zelle": "Transfers", "venmo": "Transfers",
}

_SYSTEM_PROMPT = """You are a financial transaction categorizer. Given a list of bank transaction descriptions, classify each into exactly one of these categories:

Food & Dining, Transport, Shopping, Entertainment, Health & Medical, Utilities, Housing, Travel, Subscriptions, Education, Personal Care, Income, Transfers, Other

Rules:
- Return ONLY a JSON object mapping each description to a category name
- Use the exact category names listed above
- If unsure, use "Other"
- Do not add explanations

Example input: ["STARBUCKS #1234", "UBER TRIP", "NETFLIX.COM"]
Example output: {"STARBUCKS #1234": "Food & Dining", "UBER TRIP": "Transport", "NETFLIX.COM": "Subscriptions"}"""


def _keyword_category(description: str) -> str | None:
    lower = description.lower()
    for keyword, category in _KEYWORD_RULES.items():
        if keyword in lower:
            return category
    return None


def categorize_batch(descriptions: List[str]) -> dict[str, str]:
    """Categorize up to 50 transaction descriptions. Returns {description: category}."""
    result: dict[str, str] = {}

    to_ai: List[str] = []
    for desc in descriptions:
        cat = _keyword_category(desc)
        if cat:
            result[desc] = cat
        else:
            to_ai.append(desc)

    if not to_ai:
        return result

    text, _ = complete(
        system=_SYSTEM_PROMPT,
        user=json.dumps(to_ai),
        max_tokens=1024,
        priority=CATEGORIZATION,
    )

    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        result.update(json.loads(match.group()))

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
