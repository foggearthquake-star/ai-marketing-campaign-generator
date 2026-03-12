"use client";

import { useEffect, useState } from "react";

import WorkspaceShell from "@/app/components/WorkspaceShell";
import { api, storage } from "@/lib/api";

type Plan = { plan_tier: string };
type Limits = { remaining: Record<string, number>; usage: Record<string, number | string> };

export default function PlanPage() {
  const [plan, setPlan] = useState<Plan | null>(null);
  const [limits, setLimits] = useState<Limits | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    const workspaceId = storage.workspaceId;
    if (!workspaceId) return;
    Promise.all([api<Plan>(`/api/v1/plan?workspace_id=${workspaceId}`), api<Limits>(`/api/v1/limits?workspace_id=${workspaceId}`)])
      .then(([planData, limitsData]) => {
        setPlan(planData);
        setLimits(limitsData);
      })
      .catch((e) => setError(String(e)));
  }, []);

  return (
    <WorkspaceShell>
      <section className="panel grid">
        <h1 className="h-title">Тариф И Лимиты</h1>
        <div className="stat">В MVP встроенные платежи отключены. Оплата вручную по офферу и счету.</div>
        {error ? <div className="error-box">{error}</div> : null}
        {plan ? (
          <div className="stat">
            <strong>Текущий тариф:</strong> {plan.plan_tier}
          </div>
        ) : null}
        {limits ? (
          <div className="grid cols-3">
            {Object.entries(limits.remaining).map(([key, value]) => (
              <div className="stat" key={key}>
                <strong>{key}</strong>
                <div>Осталось: {String(value)}</div>
                <div className="mono-note">Использовано: {String(limits.usage[key] ?? 0)}</div>
              </div>
            ))}
          </div>
        ) : null}
      </section>
    </WorkspaceShell>
  );
}
