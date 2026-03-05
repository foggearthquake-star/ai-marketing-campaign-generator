"""Campaign regeneration agent."""

import json

from app.ai.llm_client import analyze_website


class RegenerationAgent:
    """Agent responsible for campaign improvement using feedback."""

    @staticmethod
    def regenerate_campaign(
        analysis: dict,
        previous_campaign: dict,
        evaluation: dict,
    ) -> dict:
        prompt = f"""
You are a senior marketing strategist.

Your task is to improve the following marketing campaign.

Use the evaluation feedback to improve the campaign.

Return JSON with:

campaign_angle
ads
email_sequence
landing_page_outline


Company analysis:
{analysis}


Previous campaign:
{previous_campaign}


Evaluation feedback:
{evaluation}
"""
        result = analyze_website(prompt)
        return RegenerationAgent._normalize_result(result)

    @staticmethod
    def _normalize_result(result: dict | str) -> dict:
        """Normalize LLM output to dictionary."""
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except Exception:
                return {}
        if not isinstance(result, dict):
            return {}
        return result
