"""Email agent."""

from app.ai.llm_client import analyze_website


class EmailAgent:
    """Agent responsible for email sequence generation."""

    @staticmethod
    def generate_sequence(angle: str, analysis: dict) -> list[dict] | dict:
        prompt = f"""
Create a 3-email marketing sequence.

Return JSON with:
subject
body

Campaign angle:
{angle}

Company analysis:
{analysis}
"""
        return analyze_website(prompt)
