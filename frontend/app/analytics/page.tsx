"use client";

import { useEffect, useState } from "react";

import WorkspaceShell from "@/app/components/WorkspaceShell";
import { api, storage } from "@/lib/api";

type Usage = { total_analyses: number; total_campaigns: number; total_tokens: number; total_cost: number };

export default function AnalyticsPage() {
  const [usage, setUsage] = useState<Usage | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const workspaceId = storage.workspaceId;
    if (!workspaceId) return;
    api<Usage>(`/api/v1/usage?workspace_id=${workspaceId}`)
      .then(setUsage)
      .catch((e) => setError(String(e)));
  }, []);

  return (
    <WorkspaceShell>
      <section className="panel grid">
        <h1 className="h-title">Статистика Использования</h1>
        {error ? <div className="error-box">{error}</div> : null}
        {usage ? (
          <div className="grid cols-2">
            <div className="stat">
              <strong>Анализы</strong>
              <div>{usage.total_analyses}</div>
            </div>
            <div className="stat">
              <strong>Кампании</strong>
              <div>{usage.total_campaigns}</div>
            </div>
            <div className="stat">
              <strong>Токены</strong>
              <div>{usage.total_tokens}</div>
            </div>
            <div className="stat">
              <strong>Стоимость</strong>
              <div>${usage.total_cost?.toFixed?.(4) ?? usage.total_cost}</div>
            </div>
          </div>
        ) : (
          <div className="stat">Пока нет данных. Запустите первый анализ и первую кампанию.</div>
        )}
      </section>
    </WorkspaceShell>
  );
}
