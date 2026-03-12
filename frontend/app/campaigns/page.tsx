"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

import WorkspaceShell from "@/app/components/WorkspaceShell";
import { api, storage } from "@/lib/api";

type Analysis = { id: number; status: string; error_message?: string | null };
type Campaign = {
  id: number;
  analysis_id: number;
  version: number;
  status: string;
  output: { campaign_angle?: string; ads?: string[] };
};

function isCampaignTerminal(status: string): boolean {
  return status === "completed" || status === "failed";
}

export default function CampaignsPage() {
  const [workspaceId, setWorkspaceId] = useState("");
  const [analysisId, setAnalysisId] = useState("");
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [error, setError] = useState("");

  const activeCampaignIds = useMemo(
    () => campaigns.filter((c) => !isCampaignTerminal(c.status)).map((c) => c.id),
    [campaigns],
  );

  const upsertCampaign = (campaign: Campaign) => {
    setCampaigns((prev) => [campaign, ...prev.filter((p) => p.id !== campaign.id)]);
  };

  const loadAnalyses = async (currentWorkspaceId: string) => {
    if (!currentWorkspaceId) return;

    const projects = await api<Array<{ id: number }>>(`/api/v1/projects/?workspace_id=${currentWorkspaceId}`);
    const all: Analysis[] = [];

    for (const project of projects) {
      const projectAnalyses = await api<Array<{ id: number; status: string; error_message?: string | null }>>(
        `/api/v1/projects/${project.id}/analyses?workspace_id=${currentWorkspaceId}`,
      );
      all.push(...projectAnalyses);
    }

    const done = all
      .filter((item) => item.status === "success")
      .sort((a, b) => b.id - a.id);

    setAnalyses(done);
    const nextAnalysisId = done[0] ? String(done[0].id) : "";
    setAnalysisId((prev) => prev || nextAnalysisId);
  };

  const loadCampaignHistory = async (currentAnalysisId: string) => {
    if (!currentAnalysisId) {
      setCampaigns([]);
      return;
    }

    const history = await api<Campaign[]>(`/analyses/${currentAnalysisId}/campaigns`);
    setCampaigns(history);
  };

  useEffect(() => {
    setWorkspaceId(storage.workspaceId);
  }, []);

  useEffect(() => {
    if (!workspaceId) return;

    loadAnalyses(workspaceId)
      .then(() => setError(""))
      .catch((e) => setError(e instanceof Error ? e.message : "Не удалось загрузить анализы."));
  }, [workspaceId]);

  useEffect(() => {
    loadCampaignHistory(analysisId)
      .then(() => setError(""))
      .catch((e) => setError(e instanceof Error ? e.message : "Не удалось загрузить историю кампаний."));
  }, [analysisId]);

  useEffect(() => {
    if (!workspaceId || activeCampaignIds.length === 0) return;

    const poll = window.setInterval(async () => {
      for (const campaignId of activeCampaignIds) {
        try {
          const campaign = await api<Campaign>(`/api/v1/campaigns/${campaignId}?workspace_id=${workspaceId}`);
          setError("");
          upsertCampaign(campaign);
        } catch {
          // Keep polling others.
        }
      }
    }, 2500);

    return () => window.clearInterval(poll);
  }, [workspaceId, activeCampaignIds.join(",")]);

  const runCampaign = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");

    if (!workspaceId) {
      setError("Сначала войдите в workspace на главной странице.");
      return;
    }
    if (!analysisId) {
      setError("Сначала завершите хотя бы один анализ.");
      return;
    }

    try {
      const payload = await api<{ campaign_id: number }>(`/api/v1/campaigns/${analysisId}?workspace_id=${workspaceId}`, {
        method: "POST",
      });
      const campaign = await api<Campaign>(`/api/v1/campaigns/${payload.campaign_id}?workspace_id=${workspaceId}`);
      upsertCampaign(campaign);
      setError("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Не удалось сгенерировать кампанию.");
    }
  };

  return (
    <WorkspaceShell>
      <section className="panel grid">
        <h1 className="h-title">Кампании</h1>
        <p className="mono-note">Выберите успешный анализ и запустите генерацию. История кампаний сохраняется.</p>

        <form className="row" onSubmit={runCampaign}>
          <select value={analysisId} onChange={(e) => setAnalysisId(e.target.value)}>
            {analyses.map((analysis) => (
              <option key={analysis.id} value={analysis.id}>
                Анализ #{analysis.id}
              </option>
            ))}
          </select>
          <button type="submit" disabled={!analysisId}>
            Сгенерировать кампанию
          </button>
        </form>

        {error ? <div className="error-box">{error}</div> : null}

        {campaigns.length === 0 ? <div className="stat">Пока нет кампаний для выбранного анализа.</div> : null}

        <div className="grid">
          {campaigns.map((campaign) => (
            <article key={campaign.id} className="stat grid">
              <div className="row between">
                <strong>
                  Кампания #{campaign.id} v{campaign.version}
                </strong>
                <span className={`badge ${campaign.status}`}>{campaign.status.toUpperCase()}</span>
              </div>
              <p className="mono-note">{campaign.output?.campaign_angle || "Собираем угол подачи кампании..."}</p>
              {campaign.output?.ads?.length ? (
                <ul>
                  {campaign.output.ads.slice(0, 3).map((ad, index) => (
                    <li key={index}>{ad}</li>
                  ))}
                </ul>
              ) : null}
            </article>
          ))}
        </div>
      </section>
    </WorkspaceShell>
  );
}
