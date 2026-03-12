"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "Что мы делаем" },
  { href: "/projects", label: "Проекты" },
  { href: "/analyses", label: "Лаборатория анализа" },
  { href: "/campaigns", label: "Кампании" },
  { href: "/analytics", label: "Статистика" },
  { href: "/plan", label: "Тариф и лимиты" },
];

export default function WorkspaceShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="site-frame">
      <header className="browser-strip">
        <div className="browser-topline">
          <span className="dot" />
          <span className="dot" />
          <span className="dot" />
        </div>
        <div className="browser-main">
          <div className="url-box">https://ai-campaign.workspace</div>
          <div className="auth-box">
            <Link href="/#auth" className="auth-link">
              Войти
            </Link>
            <Link href="/#auth" className="auth-link">
              Регистрация
            </Link>
          </div>
        </div>
        <div className="chrome-subline">
          <span className="chrome-meta">Контакты: Telegram @nurevegarden</span>
          <span className="chrome-editorial">Редакционный интерфейс</span>
          <span className="chrome-locale">RU / CIS</span>
        </div>
      </header>

      <div className="shell">
        <aside className="sidebar">
          <p className="brand">AI Campaign</p>
          <p className="tagline">Черно-белый редакционный интерфейс для агентской рутины.</p>
          <div className="ink-mascot" aria-hidden="true">
            <span className="ink-mascot-face" />
          </div>
          <nav className="nav">
            {links.map((link) => (
              <Link key={link.href} href={link.href} className={`nav-link ${pathname === link.href ? "active" : ""}`}>
                {link.label}
              </Link>
            ))}
          </nav>
        </aside>
        <main className="main">{children}</main>
      </div>
    </div>
  );
}
