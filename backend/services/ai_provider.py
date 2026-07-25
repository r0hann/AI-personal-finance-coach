"""
Unified AI provider with automatic fallback.

Priority chains:
  categorization : gemini → github → ollama
  insights       : github → gemini → ollama
  forecast       : github → gemini → ollama
  chat (stream)  : gemini → github → ollama
"""
import json
import logging
import requests
from openai import OpenAI
import google.generativeai as genai
from config import settings
from services.error_logger import log_error

log = logging.getLogger(__name__)

# ── Priority chains ────────────────────────────────────────────────────────
CATEGORIZATION = ["gemini", "github", "ollama"]
INSIGHTS       = ["github", "gemini", "ollama"]
FORECAST       = ["github", "gemini", "ollama"]
CHAT           = ["gemini", "github", "ollama"]

# ── Clients ────────────────────────────────────────────────────────────────
_github = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=settings.github_token,
) if settings.github_token else None
if settings.google_api_key:
    genai.configure(api_key=settings.google_api_key)


class ProviderUnavailable(Exception):
    """Raised when a provider hits rate limits, quota, or is unreachable."""


# ── Non-streaming completions ──────────────────────────────────────────────

def _complete_github(system: str, user: str, max_tokens: int) -> str:
    if not _github:
        raise ProviderUnavailable("github: no GITHUB_TOKEN configured")
    try:
        resp = _github.chat.completions.create(
            model=settings.github_model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return resp.choices[0].message.content
    except Exception as e:
        msg = str(e).lower()
        if "429" in msg or "rate" in msg or "quota" in msg:
            raise ProviderUnavailable(f"github: rate limited") from e
        raise


def _complete_gemini(system: str, user: str, max_tokens: int) -> str:
    if not settings.google_api_key:
        raise ProviderUnavailable("gemini: no API key configured")
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=system,
        )
        resp = model.generate_content(
            user,
            generation_config={"max_output_tokens": max_tokens},
        )
        return resp.text
    except Exception as e:
        msg = str(e).lower()
        if "quota" in msg or "429" in msg or "resource exhausted" in msg:
            raise ProviderUnavailable(f"gemini: quota exceeded") from e
        raise


def _complete_ollama(system: str, user: str, max_tokens: int) -> str:
    try:
        resp = requests.post(
            f"{settings.ollama_base_url}/api/chat",
            json={
                "model": settings.ollama_model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "stream": False,
                "options": {"num_predict": max_tokens},
            },
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"]
    except requests.exceptions.ConnectionError as e:
        raise ProviderUnavailable("ollama: not running (install from ollama.com)") from e
    except Exception as e:
        raise ProviderUnavailable(f"ollama: {e}") from e


_COMPLETE = {
    "github": _complete_github,
    "gemini": _complete_gemini,
    "ollama": _complete_ollama,
}


def complete(system: str, user: str, max_tokens: int, priority: list[str]) -> tuple[str, str]:
    """
    Run completion with automatic provider fallback.
    Returns (text, provider_used).
    Raises RuntimeError if all providers fail.
    """
    errors = []
    for provider in priority:
        try:
            text = _COMPLETE[provider](system, user, max_tokens)
            if len(errors):
                log.info("Fell back to %s after: %s", provider, "; ".join(errors))
            return text, provider
        except ProviderUnavailable as e:
            log.warning("Provider %s unavailable: %s", provider, e)
            log_error("ai_provider", e, {"provider": provider, "chain": priority})
            errors.append(str(e))
    raise RuntimeError(f"All AI providers failed: {'; '.join(errors)}")


# ── Streaming completions ──────────────────────────────────────────────────

def _stream_gemini(system: str, user: str, history: list[dict]):
    model = genai.GenerativeModel(model_name="gemini-2.0-flash", system_instruction=system)
    chat = model.start_chat(history=history)
    try:
        response = chat.send_message(user, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        msg = str(e).lower()
        if "quota" in msg or "429" in msg or "resource exhausted" in msg:
            raise ProviderUnavailable("gemini: quota exceeded") from e
        raise


def _stream_github(system: str, user: str, history: list[dict]):
    if not _github:
        raise ProviderUnavailable("github: no GITHUB_TOKEN configured")
    messages = [{"role": "system", "content": system}]
    for msg in history:
        role = "assistant" if msg["role"] == "model" else "user"
        text = msg["parts"][0]["text"] if "parts" in msg else msg.get("content", "")
        messages.append({"role": role, "content": text})
    messages.append({"role": "user", "content": user})
    try:
        with _github.chat.completions.stream(
            model=settings.github_model,
            max_tokens=1024,
            messages=messages,
        ) as s:
            for chunk in s:
                text = chunk.choices[0].delta.content if chunk.choices else None
                if text:
                    yield text
    except Exception as e:
        msg = str(e).lower()
        if "429" in msg or "rate" in msg or "quota" in msg:
            raise ProviderUnavailable("github: rate limited") from e
        raise


def _stream_ollama(system: str, user: str, history: list[dict]):
    messages = [{"role": "system", "content": system}]
    for msg in history:
        role = "assistant" if msg["role"] == "model" else "user"
        text = msg["parts"][0]["text"] if "parts" in msg else msg.get("content", "")
        messages.append({"role": role, "content": text})
    messages.append({"role": "user", "content": user})
    try:
        resp = requests.post(
            f"{settings.ollama_base_url}/api/chat",
            json={"model": settings.ollama_model, "messages": messages, "stream": True},
            stream=True,
            timeout=60,
        )
        resp.raise_for_status()
        for line in resp.iter_lines():
            if line:
                data = json.loads(line)
                content = data.get("message", {}).get("content", "")
                if content:
                    yield content
    except requests.exceptions.ConnectionError as e:
        raise ProviderUnavailable("ollama: not running") from e


_STREAM = {
    "gemini": _stream_gemini,
    "github": _stream_github,
    "ollama": _stream_ollama,
}


def stream(system: str, user: str, history: list[dict], priority: list[str]):
    """
    Stream a response with automatic provider fallback.
    Falls back before first chunk; once streaming starts, stays on that provider.
    Yields text chunks.
    """
    errors = []
    for provider in priority:
        try:
            gen = _STREAM[provider](system, user, history)
            first = next(gen)         # triggers rate-limit errors before we commit
            if errors:
                log.info("Chat fell back to %s after: %s", provider, "; ".join(errors))
            yield first
            yield from gen
            return
        except StopIteration:
            return                    # empty but valid response
        except ProviderUnavailable as e:
            log.warning("Stream provider %s unavailable: %s", provider, e)
            errors.append(str(e))
    yield "Sorry, all AI providers are currently unavailable. Please try again later."
