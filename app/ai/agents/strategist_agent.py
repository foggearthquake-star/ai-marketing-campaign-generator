"""Strategist agent."""

from app.ai.llm_client import analyze_website


class StrategistAgent:
    """Agent responsible for campaign angle strategy."""

    @staticmethod
    def generate_angle(analysis: dict) -> str | dict:
        prompt = f"""
You are a senior marketing strategist.

Based on this company analysis generate ONE strong marketing campaign angle.

Analysis:
{analysis}
"""
        return analyze_website(prompt)
