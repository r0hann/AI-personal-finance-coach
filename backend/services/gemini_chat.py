"""Financial Q&A chat using Gemini 2.5 Flash with streaming."""
import google.generativeai as genai
from config import settings

genai.configure(api_key=settings.google_api_key)

_model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=(
        "You are a knowledgeable, friendly personal finance coach. "
        "Answer questions about budgeting, saving, investing, and spending habits. "
        "Keep answers concise and practical. When asked about the user's spending, "
        "refer to the spending context provided. Never give specific investment advice. "
        "If spending data is provided, use it to personalize your answers."
    ),
)


def build_spending_context(spending_summary: dict | None) -> str:
    if not spending_summary:
        return ""
    lines = ["User's recent spending summary:"]
    for cat, amount in sorted(spending_summary.items(), key=lambda x: x[1], reverse=True)[:8]:
        lines.append(f"  {cat}: ${amount:.2f}")
    return "\n".join(lines)


def stream_chat_response(
    user_message: str,
    history: list[dict],
    spending_summary: dict | None = None,
):
    """
    Stream a Gemini chat response.
    history: list of {"role": "user"|"model", "parts": [{"text": "..."}]}
    Yields text chunks.
    """
    # Inject spending context as first user message if available
    chat_history = list(history)
    spending_ctx = build_spending_context(spending_summary)
    if spending_ctx and not chat_history:
        chat_history = [{
            "role": "user",
            "parts": [{"text": spending_ctx}],
        }, {
            "role": "model",
            "parts": [{"text": "I can see your recent spending data. How can I help you today?"}],
        }]

    chat = _model.start_chat(history=chat_history)
    response = chat.send_message(user_message, stream=True)

    for chunk in response:
        if chunk.text:
            yield chunk.text
