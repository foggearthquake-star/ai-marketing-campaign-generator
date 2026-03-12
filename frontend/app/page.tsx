"use client";

import { FormEvent, useState } from "react";

import WorkspaceShell from "./components/WorkspaceShell";
import { api, storage } from "@/lib/api";

export default function HomePage() {
  const [mode, setMode] = useState<"register" | "login">("register");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const handleAuth = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    setMessage("");
    const formData = new FormData(event.currentTarget);

    try {
      if (mode === "register") {
        const payload = {
          email: String(formData.get("email") || ""),
          full_name: String(formData.get("full_name") || ""),
          password: String(formData.get("password") || ""),
          workspace_name: String(formData.get("workspace_name") || ""),
        };
        const token = await api<{ access_token: string }>("/api/v1/auth/register", {
          method: "POST",
          body: JSON.stringify(payload),
        });
        storage.token = token.access_token;
      } else {
        const payload = {
          email: String(formData.get("email") || ""),
          password: String(formData.get("password") || ""),
        };
        const token = await api<{ access_token: string }>("/api/v1/auth/login", {
          method: "POST",
          body: JSON.stringify(payload),
        });
        storage.token = token.access_token;
      }

      const workspaces = await api<Array<{ id: number }>>("/api/v1/workspaces/");
      if (workspaces.length > 0) {
        storage.workspaceId = String(workspaces[0].id);
      }
      setMessage("Доступ открыт. Перейдите в «Проекты» и запустите первый клиентский пайплайн.");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ошибка авторизации.");
    }
  };

  return (
    <WorkspaceShell>
      <section className="panel grid">
        <div className="hero-grid">
          <div className="logo-card">
            <img src="/logo.jpg" alt="Логотип AI Campaign" />
            <div className="logo-meta">
              <p className="logo-meta-title">Миссия сервиса</p>
              <p className="logo-meta-note mission-text">
                Помогать агентствам запускать сильные маркетинговые кампании быстрее: от анализа сайта клиента до готовых
                версий объявлений и прозрачной аналитики в одном рабочем пространстве.
              </p>
            </div>
          </div>
          <div className="manifesto">
            Мы не «крутим кнопки рекламы». Мы строим систему кампаний из сырых данных сайта: с ритмом, логикой и
            сильным результатом.
          </div>
        </div>
      </section>

      <section className="panel grid newspaper">
        <h1 className="newspaper-title">Что мы делаем</h1>
        <p className="newspaper-deck">Спецвыпуск редакции AI Campaign</p>
        <div className="newspaper-columns">
          <p className="dropcap">
            Платформа принимает сайт клиента, собирает структуру и контент, запускает анализ и показывает статус каждой
            задачи в реальном времени.
          </p>
          <p>
            Дальше система генерирует версии кампаний: угол подачи, объявления, связки сообщений. Команда сравнивает
            варианты и выбирает лучший без хаоса в таблицах.
          </p>
          <p>
            Внутри есть рабочие пространства, проекты, история запусков, учет использования и лимитов по тарифу. Для
            агентства это один понятный контур вместо разрозненных сервисов.
          </p>
          <p>
            Ошибки, таймауты и повторные попытки не прячутся: видно, где задача упала, что делать дальше, и как быстро
            перезапустить процесс.
          </p>
        </div>
      </section>

      <section className="panel grid" id="auth">
        <h1 className="h-title">Доступ в workspace</h1>
        <p className="h-sub">Регистрация для новой команды, вход для существующей.</p>
        <div className="row">
          <button type="button" className={mode === "register" ? "" : "secondary"} onClick={() => setMode("register")}>
            Регистрация
          </button>
          <button type="button" className={mode === "login" ? "" : "secondary"} onClick={() => setMode("login")}>
            Войти
          </button>
        </div>

        <form onSubmit={handleAuth} className="grid cols-2">
          <label className="grid">
            Почта
            <input name="email" type="email" required placeholder="team@agency.ru" />
          </label>
          {mode === "register" ? (
            <label className="grid">
              Имя и фамилия
              <input name="full_name" required placeholder="Анна Иванова" />
            </label>
          ) : null}
          <label className="grid">
            Пароль
            <input name="password" type="password" required minLength={8} placeholder="********" />
          </label>
          {mode === "register" ? (
            <label className="grid">
              Название workspace
              <input name="workspace_name" required placeholder="Агентство Уфа" />
            </label>
          ) : null}
          <div className="row">
            <button type="submit">Продолжить</button>
          </div>
        </form>

        {error ? <div className="error-box">{error}</div> : null}
        {message ? <div className="stat">{message}</div> : null}
      </section>
    </WorkspaceShell>
  );
}
