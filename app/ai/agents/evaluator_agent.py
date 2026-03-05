"""Campaign evaluator agent."""

import json

from app.ai.llm_client import analyze_website


class EvaluatorAgent:
    """Agent responsible for campaign quality evaluation."""

    @staticmethod
    def evaluate_campaign(campaign_output: dict) -> dict:
        prompt = f"""
You are a senior marketing strategist.

Evaluate the following marketing campaign.

Return JSON with:

score (0-10)
strengths (list)
weaknesses (list)
improvement_suggestions (list)

Campaign:
{campaign_output}
"""
        result = analyze_website(prompt)
        normalized = EvaluatorAgent._normalize_evaluation(result)
        if normalized.get("score", 0) == 0:
            retry_result = analyze_website(prompt)
            retry_normalized = EvaluatorAgent._normalize_evaluation(retry_result)
            if retry_normalized.get("score", 0) != 0:
                return retry_normalized
        return normalized

    @staticmethod
    def _normalize_evaluation(result: dict | str) -> dict:
        """Normalize evaluator output to a strict dictionary schema."""
        fallback = {
            "score": 0,
            "strengths": [],
            "weaknesses": [],
            "improvement_suggestions": [],
        }

        if isinstance(result, str):
            try:
                result = json.loads(result)
            except Exception:
                return fallback

        if not isinstance(result, dict):
            return fallback

        score_raw = result.get("score", 0)
        try:
            score = int(float(score_raw))
        except (TypeError, ValueError):
            score = 0
        score = max(0, min(10, score))

        strengths_raw = result.get("strengths", [])
        weaknesses_raw = result.get("weaknesses", [])
        suggestions_raw = result.get("improvement_suggestions", [])

        strengths = strengths_raw if isinstance(strengths_raw, list) else []
        weaknesses = weaknesses_raw if isinstance(weaknesses_raw, list) else []
        improvement_suggestions = suggestions_raw if isinstance(suggestions_raw, list) else []

        return {
            "score": score,
            "strengths": [str(item) for item in strengths],
            "weaknesses": [str(item) for item in weaknesses],
            "improvement_suggestions": [str(item) for item in improvement_suggestions],
        }
