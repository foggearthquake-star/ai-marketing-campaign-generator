"use client";

import { FormEvent, useEffect, useState } from "react";

import WorkspaceShell from "@/app/components/WorkspaceShell";
import { api, storage } from "@/lib/api";

type Project = { id: number; workspace_id: number; name: string; client_url: string };

export default function ProjectsPage() {
  const [items, setItems] = useState<Project[]>([]);
  const [error, setError] = useState("");
  const workspaceId = storage.workspaceId;

  const load = async () => {
    if (!workspaceId) return;
    try {
      setItems(await api<Project[]>(`/api/v1/projects/?workspace_id=${workspaceId}`));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Не удалось загрузить проекты.");
    }
  };

  useEffect(() => {
    load();
  }, []);

  const createProject = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setError("");

    if (!workspaceId) {
      setError("Сначала войдите или зарегистрируйтесь на главной странице, чтобы создать workspace.");
      return;
    }

    try {
      await api<Project>("/api/v1/projects/", {
        method: "POST",
        body: JSON.stringify({
          workspace_id: Number(workspaceId),
          name: String(form.get("name") || ""),
          client_url: String(form.get("client_url") || ""),
        }),
      });
      (event.target as HTMLFormElement).reset();
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Не удалось создать проект.");
    }
  };

  return (
    <WorkspaceShell>
      <section className="panel grid">
        <h1 className="h-title">Проекты</h1>
        <p className="mono-note">Сначала добавьте сайт клиента, затем запускайте анализ.</p>
        <form onSubmit={createProject} className="grid cols-3">
          <input name="name" required placeholder="Apple" />
          <input name="client_url" required placeholder="https://apple.com" />
          <button type="submit">Создать проект</button>
        </form>
        {error ? <div className="error-box">{error}</div> : null}
        <div className="grid">
          {items.map((item) => (
            <article key={item.id} className="stat row between">
              <div>
                <strong>{item.name}</strong>
                <p className="mono-note">{item.client_url}</p>
              </div>
              <span>#{item.id}</span>
            </article>
          ))}
        </div>
      </section>
    </WorkspaceShell>
  );
}
