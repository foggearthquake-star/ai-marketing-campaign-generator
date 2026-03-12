"""API v1 project service wrapper."""

from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.project_workspace import ProjectWorkspace


class ProjectV1Service:
    """Workspace-scoped project operations."""

    @staticmethod
    def create_project(
        db: Session,
        workspace_id: int,
        created_by_user_id: int,
        name: str,
        client_url: str,
    ) -> tuple[Project, ProjectWorkspace]:
        """Create legacy project and map it to workspace."""
        project = Project(name=name, client_url=client_url)
        db.add(project)
        db.commit()
        db.refresh(project)

        mapping = ProjectWorkspace(
            project_id=project.id,
            workspace_id=workspace_id,
            created_by_user_id=created_by_user_id,
        )
        db.add(mapping)
        db.commit()
        db.refresh(mapping)
        return project, mapping

    @staticmethod
    def list_projects(db: Session, workspace_id: int) -> list[Project]:
        """List workspace projects by mapped relation."""
        return (
            db.query(Project)
            .join(ProjectWorkspace, ProjectWorkspace.project_id == Project.id)
            .filter(ProjectWorkspace.workspace_id == workspace_id)
            .order_by(Project.created_at.desc())
            .all()
        )

    @staticmethod
    def ensure_workspace_project(db: Session, workspace_id: int, project_id: int) -> Project:
        """Ensure a project belongs to workspace."""
        project = (
            db.query(Project)
            .join(ProjectWorkspace, ProjectWorkspace.project_id == Project.id)
            .filter(ProjectWorkspace.workspace_id == workspace_id, Project.id == project_id)
            .first()
        )
        if project is None:
            raise ValueError("Project not found in workspace.")
        return project
