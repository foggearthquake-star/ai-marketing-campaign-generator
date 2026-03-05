"""LLM client integration."""

import json
from json import JSONDecodeError

from openai import OpenAI

from app.ai.cache import AICache
from app.core.config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL

client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL,
)


def analyze_website(url: str) -> dict[str, str]:
    """Analyze a website URL and return structured marketing insights."""
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set.")

    prompt = (
        "You are a senior marketing strategist.\n"
        f"Analyze this website URL: {url}\n\n"
        "Return JSON with:\n"
        "- positioning\n"
        "- target_audience\n"
        "- strengths\n"
        "- weaknesses\n"
        "- campaign_angle"
    )
    cached = AICache.get(prompt)
    if cached is not None:
        if isinstance(cached, dict):
            return {
                "positioning": str(cached.get("positioning", "")),
                "target_audience": str(cached.get("target_audience", "")),
                "strengths": str(cached.get("strengths", "")),
                "weaknesses": str(cached.get("weaknesses", "")),
                "campaign_angle": str(cached.get("campaign_angle", "")),
            }
        if isinstance(cached, str):
            try:
                cached_parsed = json.loads(cached)
                if isinstance(cached_parsed, dict):
                    return {
                        "positioning": str(cached_parsed.get("positioning", "")),
                        "target_audience": str(cached_parsed.get("target_audience", "")),
                        "strengths": str(cached_parsed.get("strengths", "")),
                        "weaknesses": str(cached_parsed.get("weaknesses", "")),
                        "campaign_angle": str(cached_parsed.get("campaign_angle", "")),
                    }
            except JSONDecodeError:
                pass

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "Return valid JSON only."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    raw_content = response.choices[0].message.content or "{}"
    try:
        parsed = json.loads(raw_content)
    except JSONDecodeError as exc:
        raise ValueError("Model returned non-JSON output.") from exc

    result = {
        "positioning": str(parsed.get("positioning", "")),
        "target_audience": str(parsed.get("target_audience", "")),
        "strengths": str(parsed.get("strengths", "")),
        "weaknesses": str(parsed.get("weaknesses", "")),
        "campaign_angle": str(parsed.get("campaign_angle", "")),
    }
    AICache.set(prompt, result)
    return result
