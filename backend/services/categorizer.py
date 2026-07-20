"""AI categorization using Claude Haiku with prompt caching."""
import json
import re
from typing import List
import anthropic
from config import settings

_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

# Keyword fallback rules (avoids burning tokens on obvious cases)
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

    # Apply keyword rules first
    to_ai: List[str] = []
    for desc in descriptions:
        cat = _keyword_category(desc)
        if cat:
            result[desc] = cat
        else:
            to_ai.append(desc)

    if not to_ai:
        return result

    # Batch AI categorization with prompt caching on the system prompt
    response = _client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=[{
            "type": "text",
            "text": _SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"},
        }],
        messages=[{
            "role": "user",
            "content": json.dumps(to_ai),
        }],
    )

    text = response.content[0].text.strip()
    # Extract JSON even if there's surrounding text
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        ai_result = json.loads(match.group())
        result.update(ai_result)

    # Fallback for any missing
    for desc in to_ai:
        if desc not in result:
            result[desc] = "Other"

    return result


def categorize_transactions_bulk(descriptions: List[str]) -> dict[str, str]:
    """Categorize any number of descriptions in batches of 50."""
    all_results: dict[str, str] = {}
    batch_size = 50
    for i in range(0, len(descriptions), batch_size):
        batch = descriptions[i:i + batch_size]
        all_results.update(categorize_batch(batch))
    return all_results
