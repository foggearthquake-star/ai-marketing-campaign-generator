"""Smoke tests for API v1."""

import time

from fastapi.testclient import TestClient

from app.db.init_db import init_db
from app.main import app


def test_register_and_create_project_flow() -> None:
    """Ensure core workspace flow works end-to-end."""
    init_db()

    email = f"smoke{int(time.time())}@example.com"
    with TestClient(app) as client:
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "full_name": "Smoke Tester",
                "password": "password123",
                "workspace_name": "Smoke Workspace",
            },
        )
        assert register_response.status_code == 200
        token = register_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        workspaces_response = client.get("/api/v1/workspaces/", headers=headers)
        assert workspaces_response.status_code == 200
        workspace_id = workspaces_response.json()[0]["id"]

        project_response = client.post(
            "/api/v1/projects/",
            headers=headers,
            json={
                "workspace_id": workspace_id,
                "name": "Smoke Project",
                "client_url": "https://mkmebel-ufa.ru/?ct-referrer=perplexity",
            },
        )
        assert project_response.status_code == 200

        usage_response = client.get(f"/api/v1/usage?workspace_id={workspace_id}", headers=headers)
        assert usage_response.status_code == 200
        payload = usage_response.json()
        assert payload["workspace_id"] == workspace_id
        assert payload["total_campaigns"] >= 0
