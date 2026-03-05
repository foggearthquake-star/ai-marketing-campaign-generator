"""Marketing AI orchestration layer."""

import json
from concurrent.futures import ThreadPoolExecutor

from app.ai.agents.ads_agent import AdsAgent
from app.ai.agents.email_agent import EmailAgent
from app.ai.agents.evaluator_agent import EvaluatorAgent
from app.ai.agents.landing_agent import LandingAgent
from app.ai.agents.regeneration_agent import RegenerationAgent
from app.ai.agents.strategist_agent import StrategistAgent
from app.services.campaign_intelligence import CampaignIntelligence


class MarketingOrchestrator:
    """Multi-agent campaign generation orchestrator."""

    @staticmethod
    def build_campaign_output(
        analysis: dict,
        learning_context: dict | None = None,
    ) -> dict:
        output, _usage = MarketingOrchestrator.build_campaign_output_with_usage(
            analysis=analysis,
            learning_context=learning_context,
        )
        return output

    @staticmethod
    def build_campaign_output_with_usage(
        analysis: dict,
        learning_context: dict | None = None,
    ) -> tuple[dict, dict]:
        strategist_input: dict = analysis
        context_block = ""
        default_learning = CampaignIntelligence.build_learning_context([])

        if learning_context:
            context_block = f"""
Previous campaign insights:

Angles used before:
{learning_context.get("previous_angles", default_learning["previous_angles"])}

Previous ads:
{learning_context.get("previous_ads", default_learning["previous_ads"])}
"""
            strategist_input = {
                "analysis": analysis,
                "learning_context": context_block,
            }

        print("AI Strategist generating campaign angle")
        angle_raw = StrategistAgent.generate_angle(strategist_input)
        angle = MarketingOrchestrator._to_angle(angle_raw)
        usage_items: list[dict] = []
        angle_usage = MarketingOrchestrator._extract_usage(angle_raw)
        if angle_usage is not None:
            usage_items.append(angle_usage)

        ads: list[str] = []
        emails: list[dict] = []
        landing: list[str] = []

        with ThreadPoolExecutor(max_workers=3) as executor:
            print("AI AdsAgent generating ads")
            ads_future = executor.submit(AdsAgent.generate_ads, angle, analysis)
            print("AI EmailAgent generating sequence")
            emails_future = executor.submit(EmailAgent.generate_sequence, angle, analysis)
            print("AI LandingAgent generating outline")
            landing_future = executor.submit(LandingAgent.generate_outline, angle, analysis)

            try:
                ads_raw = ads_future.result(timeout=20)
                ads = MarketingOrchestrator._to_ads(ads_raw)
                ads_usage = MarketingOrchestrator._extract_usage(ads_raw)
                if ads_usage is not None:
                    usage_items.append(ads_usage)
            except Exception:
                ads = []

            try:
                emails_raw = emails_future.result(timeout=20)
                emails = MarketingOrchestrator._to_emails(emails_raw)
                emails_usage = MarketingOrchestrator._extract_usage(emails_raw)
                if emails_usage is not None:
                    usage_items.append(emails_usage)
            except Exception:
                emails = []

            try:
                landing_raw = landing_future.result(timeout=20)
                landing = MarketingOrchestrator._to_landing(landing_raw)
                landing_usage = MarketingOrchestrator._extract_usage(landing_raw)
                if landing_usage is not None:
                    usage_items.append(landing_usage)
            except Exception:
                landing = []

        result = {
            "campaign_angle": angle,
            "ads": ads,
            "email_sequence": emails,
            "landing_page_outline": landing,
        }

        try:
            print("AI Evaluator evaluating campaign")
            evaluation = EvaluatorAgent.evaluate_campaign(result)
        except Exception:
            evaluation = {
                "score": 0,
                "strengths": [],
                "weaknesses": [],
                "improvement_suggestions": [],
            }
        result["evaluation"] = evaluation
        usage_totals = MarketingOrchestrator._sum_usage(usage_items)
        return result, usage_totals

    @staticmethod
    def regenerate_campaign(
        analysis: dict,
        previous_campaign: dict,
        evaluation: dict,
    ) -> dict:
        """Regenerate campaign using previous output and evaluation feedback."""
        regenerated = RegenerationAgent.regenerate_campaign(
            analysis=analysis,
            previous_campaign=previous_campaign,
            evaluation=evaluation,
        )

        angle = str(regenerated.get("campaign_angle", "")).strip()
        if not angle:
            angle = str(previous_campaign.get("campaign_angle", "")).strip()

        ads = MarketingOrchestrator._to_ads(regenerated)
        emails = MarketingOrchestrator._to_emails(regenerated)
        landing = MarketingOrchestrator._to_landing(regenerated)

        result = {
            "campaign_angle": angle,
            "ads": ads,
            "email_sequence": emails,
            "landing_page_outline": landing,
        }

        try:
            new_evaluation = EvaluatorAgent.evaluate_campaign(result)
        except Exception:
            new_evaluation = {
                "score": 0,
                "strengths": [],
                "weaknesses": [],
                "improvement_suggestions": [],
            }

        result["evaluation"] = new_evaluation
        return result

    @staticmethod
    def _normalize_result(result: dict | str) -> dict:
        """Ensure LLM result is a dictionary."""
        if isinstance(result, str):
            try:
                result = json.loads(result)
            except Exception as exc:
                raise ValueError("Invalid JSON returned from LLM.") from exc
        if not isinstance(result, dict):
            raise ValueError("Invalid JSON returned from LLM.")
        return result

    @staticmethod
    def _to_angle(result: dict | str) -> str:
        normalized = MarketingOrchestrator._normalize_result(result)
        angle = normalized.get("campaign_angle") or normalized.get("positioning") or ""
        return str(angle).strip()

    @staticmethod
    def _to_ads(result: dict | str) -> list[str]:
        normalized = MarketingOrchestrator._normalize_result(result)
        ads = normalized.get("ads")
        if isinstance(ads, list):
            cleaned = [str(item).strip() for item in ads if str(item).strip()]
            return cleaned[:5]
        if isinstance(ads, str):
            value = ads.strip()
            return [value] if value else []
        return []

    @staticmethod
    def _to_emails(result: dict | str) -> list[dict]:
        normalized = MarketingOrchestrator._normalize_result(result)
        emails = normalized.get("email_sequence")
        if not isinstance(emails, list):
            return []
        if any(not isinstance(item, dict) for item in emails):
            return []

        out: list[dict] = []
        for item in emails:
            out.append(
                {
                    "subject": str(item.get("subject", "")),
                    "body": str(item.get("body", "")),
                }
            )
        return out

    @staticmethod
    def _to_landing(result: dict | str) -> list[str]:
        normalized = MarketingOrchestrator._normalize_result(result)
        outline = normalized.get("landing_page_outline")
        if isinstance(outline, list):
            return [str(item) for item in outline]
        return MarketingOrchestrator._split_lines(str(normalized.get("strengths", "")))

    @staticmethod
    def _split_lines(value: str) -> list[str]:
        """Convert multiline or delimited text to list items."""
        if not value:
            return []
        parts = [item.strip(" -\t") for item in value.replace(";", "\n").split("\n")]
        return [item for item in parts if item]

    @staticmethod
    def _extract_usage(result: dict | str) -> dict | None:
        """Extract usage block from LLM result if present."""
        normalized = MarketingOrchestrator._normalize_result(result)
        usage = normalized.get("usage")
        if not isinstance(usage, dict):
            return None

        prompt_tokens = usage.get("prompt_tokens")
        completion_tokens = usage.get("completion_tokens")
        total_tokens = usage.get("total_tokens")

        return {
            "prompt_tokens": prompt_tokens if isinstance(prompt_tokens, int) else None,
            "completion_tokens": completion_tokens if isinstance(completion_tokens, int) else None,
            "total_tokens": total_tokens if isinstance(total_tokens, int) else None,
        }

    @staticmethod
    def _sum_usage(usages: list[dict]) -> dict:
        """Aggregate usage across agent calls."""
        if not usages:
            return {
                "prompt_tokens": None,
                "completion_tokens": None,
                "total_tokens": None,
            }

        prompt_total = 0
        completion_total = 0
        total_total = 0
        has_prompt = False
        has_completion = False
        has_total = False

        for usage in usages:
            prompt_tokens = usage.get("prompt_tokens")
            completion_tokens = usage.get("completion_tokens")
            total_tokens = usage.get("total_tokens")

            if isinstance(prompt_tokens, int):
                prompt_total += prompt_tokens
                has_prompt = True
            if isinstance(completion_tokens, int):
                completion_total += completion_tokens
                has_completion = True
            if isinstance(total_tokens, int):
                total_total += total_tokens
                has_total = True

        return {
            "prompt_tokens": prompt_total if has_prompt else None,
            "completion_tokens": completion_total if has_completion else None,
            "total_tokens": total_total if has_total else None,
        }
