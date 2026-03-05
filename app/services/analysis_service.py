"""Analysis persistence service."""

import json

from sqlalchemy.orm import Session

from app.ai.llm_client import analyze_website
from app.ai.embeddings import embed_texts
from app.core.config import OPENAI_MODEL
from app.db.session import SessionLocal
from app.models.analysis import Analysis, AnalysisStatus
from app.models.project import Project
from app.services.scraper_service import scrape_website
from app.vectorstore.chunker import chunk_text
from app.vectorstore.faiss_store import FaissVectorStore
from app.vectorstore.retriever import retrieve


class AnalysisService:
    """Service for creating and updating analysis lifecycle records."""

    @staticmethod
    def create_analysis(db: Session, project_id: int) -> Analysis:
        """Create a new pending analysis record."""
        analysis = Analysis(project_id=project_id, status=AnalysisStatus.PENDING)
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        return analysis

    @staticmethod
    def get_analysis_by_id(db: Session, analysis_id: int) -> Analysis | None:
        """Fetch an analysis by ID."""
        return db.get(Analysis, analysis_id)

    @staticmethod
    def get_analyses_by_project_id(db: Session, project_id: int) -> list[Analysis]:
        """Fetch analyses for a project ordered by newest first."""
        return (
            db.query(Analysis)
            .filter(Analysis.project_id == project_id)
            .order_by(Analysis.created_at.desc())
            .all()
        )

    @staticmethod
    def mark_success(
        db: Session,
        analysis: Analysis,
        raw_response: str | None,
        structured_output: dict | None,
        model: str | None,
        prompt_tokens: int | None,
        completion_tokens: int | None,
        total_tokens: int | None,
        cost: float | None,
    ) -> Analysis:
        """Mark an analysis as successful and persist output metadata."""
        analysis.status = AnalysisStatus.SUCCESS
        analysis.raw_response = raw_response
        analysis.structured_output = structured_output
        analysis.model = model
        analysis.prompt_tokens = prompt_tokens
        analysis.completion_tokens = completion_tokens
        analysis.total_tokens = total_tokens
        analysis.cost = cost
        db.commit()
        db.refresh(analysis)
        return analysis

    @staticmethod
    def mark_failed(db: Session, analysis: Analysis, error_message: str) -> Analysis:
        """Mark an analysis as failed and store error details."""
        analysis.status = AnalysisStatus.FAILED
        analysis.error_message = error_message
        db.commit()
        db.refresh(analysis)
        return analysis

    @staticmethod
    def run_analysis(analysis_id: int) -> None:
        """Run website analysis in background and persist result."""
        db = SessionLocal()
        analysis: Analysis | None = None
        try:
            analysis = db.get(Analysis, analysis_id)
            if analysis is None:
                return

            project = db.get(Project, analysis.project_id)
            if project is None or not project.client_url:
                raise ValueError("Project not found or client_url is missing.")

            website_text = scrape_website(project.client_url)
            chunks = chunk_text(website_text)
            embeddings = embed_texts(chunks)
            store = FaissVectorStore()
            store.add_embeddings(chunks, embeddings)
            query = (
                "Analyze this company website and generate marketing positioning, "
                "target audience and campaign strategy."
            )
            try:
                relevant_chunks = retrieve(store, query, top_k=5)
            except TypeError:
                # Backward compatibility with placeholder retriever(query).
                relevant_chunks = retrieve(query)
            context = "\n".join(relevant_chunks)
            llm_result = analyze_website(context)
            if isinstance(llm_result, str):
                try:
                    llm_result = json.loads(llm_result)
                except Exception as exc:
                    raise ValueError("Invalid JSON returned by LLM") from exc
            if not isinstance(llm_result, dict):
                raise ValueError("LLM output must be a dict")

            print("LLM result parsed successfully")
            usage = llm_result.get("usage") if isinstance(llm_result, dict) else None
            prompt_tokens = usage.get("prompt_tokens") if isinstance(usage, dict) else None
            completion_tokens = usage.get("completion_tokens") if isinstance(usage, dict) else None
            total_tokens = usage.get("total_tokens") if isinstance(usage, dict) else None

            print("Saving structured_output to database")
            AnalysisService.mark_success(
                db=db,
                analysis=analysis,
                raw_response=json.dumps(llm_result),
                structured_output=llm_result,
                model=OPENAI_MODEL,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                cost=None,
            )
        except Exception as exc:
            if analysis is not None:
                AnalysisService.mark_failed(db, analysis, str(exc))
        finally:
            db.close()
