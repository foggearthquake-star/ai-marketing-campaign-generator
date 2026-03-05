"""Landing page agent."""

from app.ai.llm_client import analyze_website


class LandingAgent:
    """Agent responsible for landing page outline generation."""

    @staticmethod
    def generate_outline(angle: str, analysis: dict) -> list[str] | dict:
        prompt = f"""
Generate a landing page outline for this campaign.

Campaign angle:
{angle}

Company analysis:
{analysis}
"""
        return analyze_website(prompt)
