"""Ads agent."""

from app.ai.llm_client import analyze_website


class AdsAgent:
    """Agent responsible for ad headline generation."""

    @staticmethod
    def generate_ads(angle: str, analysis: dict) -> list[str] | dict:
        prompt = f"""
Write 5 high-converting ad headlines for this campaign.

Campaign angle:
{angle}

Company analysis:
{analysis}
"""
        return analyze_website(prompt)
