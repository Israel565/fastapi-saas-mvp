import httpx

from .config import settings


class AIError(Exception):
    pass


async def ask_ai(message: str) -> str:
    """Route to Ollama (local) or OpenAI based on env config."""
    if settings.ai_provider == "openai":
        return await _ask_openai(message)
    return await _ask_ollama(message)


async def _ask_ollama(message: str) -> str:
    payload = {
        "model": settings.ollama_model,
        "messages": [{"role": "user", "content": message}],
        "stream": False,
    }
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(f"{settings.ollama_base_url}/api/chat", json=payload)
            r.raise_for_status()
            return r.json()["message"]["content"]
    except httpx.ConnectError:
        raise AIError(
            "Ollama not reachable at "
            f"{settings.ollama_base_url}. Start it with `ollama serve` "
            "or set AI_PROVIDER=openai with OPENAI_API_KEY."
        )
    except httpx.HTTPStatusError as e:
        raise AIError(f"Ollama returned {e.response.status_code}")


async def _ask_openai(message: str) -> str:
    if not settings.openai_api_key:
        raise AIError("OPENAI_API_KEY is not set")
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": message}],
    }
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
            )
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
    except httpx.HTTPStatusError as e:
        raise AIError(f"OpenAI returned {e.response.status_code}")
