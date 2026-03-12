"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

import WorkspaceShell from "@/app/components/WorkspaceShell";
import { api, storage } from "@/lib/api";

type Project = { id: number; name: string };
type Analysis = {
  id: number;
  status: string;
  progress_hint?: number | null;
  error_message?: string | null;
  ui_progress?: number;
};

function isTerminal(status: string): boolean {
  return status === "success" || status === "failed";
}

export default function AnalysesPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [error, setError] = useState("");
  const [workspaceId, setWorkspaceId] = useState("");
  const [projectId, setProjectId] = useState("");

  const activeAnalysisIds = useMemo(
    () => analyses.filter((a) => !isTerminal(a.status)).map((a) => a.id),
    [analyses],
  );

  const upsertAnalysis = (item: Analysis) => {
    setAnalyses((prev) => {
      const old = prev.find((p) => p.id === item.id);
      const fallbackProgress = old?.ui_progress ?? 10;
      const nextProgress = item.progress_hint ?? (isTerminal(item.status) ? 100 : Math.min(92, fallbackProgress + 6));
      const merged: Analysis = {
        ...old,
        ...item,
        ui_progress: nextProgress,
      };
      return [merged, ...prev.filter((p) => p.id !== item.id)];
    });
  };

  const loadProjectAnalyses = async (selectedProjectId: string) => {
    if (!workspaceId || !selectedProjectId) return;

    try {
      const projectAnalyses = await api<Array<{ id: number; status: string; error_message?: string | null }>>(
        `/api/v1/projects/${selectedProjectId}/analyses?workspace_id=${workspaceId}`,
      );

      const initial: Analysis[] = projectAnalyses.map((item, index) => ({
        id: item.id,
        status: item.status,
        error_message: item.error_message ?? null,
        ui_progress: isTerminal(item.status) ? 100 : Math.max(10, 26 - index * 2),
      }));

      setAnalyses(initial);

      // Refresh details for the latest analyses from v1 endpoint.
      const latestIds = initial.slice(0, 12).map((a) => a.id);
      await Promise.all(
        latestIds.map(async (id) => {
          const detailed = await api<Analysis>(`/api/v1/analyses/${id}?workspace_id=${workspaceId}`);
          upsertAnalysis(detailed);
        }),
      );
      setError("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Не удалось загрузить историю анализов.");
    }
  };

  useEffect(() => {
    setWorkspaceId(storage.workspaceId);
  }, []);

  useEffect(() => {
    if (!workspaceId) return;
    api<Project[]>(`/api/v1/projects/?workspace_id=${workspaceId}`)
      .then((data) => {
        setError("");
        setProjects(data);
        const firstProjectId = data[0] ? String(data[0].id) : "";
        setProjectId((prev) => prev || firstProjectId);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Не удалось загрузить проекты."));
  }, [workspaceId]);

  useEffect(() => {
    if (!workspaceId || !projectId) return;
    loadProjectAnalyses(projectId);
  }, [workspaceId, projectId]);

  useEffect(() => {
    if (!workspaceId || activeAnalysisIds.length === 0) return;

    const poll = window.setInterval(async () => {
      for (const analysisId of activeAnalysisIds) {
        try {
          const item = await api<Analysis>(`/api/v1/analyses/${analysisId}?workspace_id=${workspaceId}`);
          setError("");
          upsertAnalysis(item);
        } catch {
          // Keep polling for others; a single failure should not break the loop.
        }
      }
    }, 2500);

    return () => window.clearInterval(poll);
  }, [workspaceId, activeAnalysisIds.join(",")]);

  const startAnalysis = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");

    if (!workspaceId) {
      setError("Сначала войдите в workspace на главной странице.");
      return;
    }
    if (!projectId) {
      setError("Выберите проект для запуска анализа.");
      return;
    }

    try {
      const started = await api<{ analysis_id: number }>(`/api/v1/projects/${projectId}/analyze?workspace_id=${workspaceId}`, {
        method: "POST",
      });

      upsertAnalysis({
        id: started.analysis_id,
        status: "pending",
        progress_hint: 8,
        error_message: null,
        ui_progress: 8,
      });

      const firstSnapshot = await api<Analysis>(`/api/v1/analyses/${started.analysis_id}?workspace_id=${workspaceId}`);
      upsertAnalysis(firstSnapshot);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Не удалось запустить анализ.");
    }
  };

  return (
    <WorkspaceShell>
      <section className="panel grid">
        <h1 className="h-title">Лаборатория Анализа</h1>
        <p className="mono-note">
          Выпадающий список нужен, чтобы выбрать конкретный проект, чей сайт сейчас анализируем. Если проектов несколько,
          это защищает от запуска «не туда».
        </p>

        <form onSubmit={startAnalysis} className="row">
          <select value={projectId} onChange={(e) => setProjectId(e.target.value)}>
            {projects.map((project) => (
              <option key={project.id} value={project.id}>
                {project.name} (#{project.id})
              </option>
            ))}
          </select>
          <button type="submit">Запустить анализ</button>
        </form>

        {error ? <div className="error-box">{error}</div> : null}

        <div className="grid">
          {analyses.map((analysis) => {
            const progress = Math.min(100, Math.max(8, analysis.progress_hint ?? analysis.ui_progress ?? 12));
            return (
              <article className="stat grid" key={analysis.id}>
                <div className="row between">
                  <strong>Анализ #{analysis.id}</strong>
                  <span className={`badge ${analysis.status}`}>{analysis.status.toUpperCase()}</span>
                </div>
                <div className="progress">
                  <span style={{ width: `${progress}%` }} />
                </div>
                {analysis.error_message ? <div className="error-box">{analysis.error_message}</div> : null}
              </article>
            );
          })}
        </div>
      </section>
    </WorkspaceShell>
  );
}
