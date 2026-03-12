import type { Metadata } from "next";
import { Manrope } from "next/font/google";
import "./globals.css";

const mainFont = Manrope({
  subsets: ["latin", "cyrillic"],
  weight: ["400", "500", "600", "700", "800"],
  variable: "--font-main",
});

export const metadata: Metadata = {
  title: "AI Campaign Рабочее Пространство",
  description: "Платформа генерации кампаний для агентств",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru" className={mainFont.variable}>
      <body>{children}</body>
    </html>
  );
}


