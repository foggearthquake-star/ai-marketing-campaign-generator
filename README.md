# AI Marketing Campaign Generator

AI-powered SaaS платформа для анализа сайтов компаний и автоматической генерации маркетинговых кампаний с использованием multi-agent LLM архитектуры.

AI-powered SaaS platform that analyzes company websites and automatically generates full marketing campaigns using a multi-agent LLM architecture.

---

# О проекте

Этот проект представляет собой MVP AI SaaS платформы для автоматизации маркетингового анализа и генерации рекламных кампаний.

Платформа:

- анализирует сайт компании
- извлекает ключевой контент
- определяет целевую аудиторию
- выявляет сильные и слабые стороны бизнеса
- генерирует маркетинговую стратегию
- создает структуру рекламной кампании

Проект демонстрирует архитектуру AI-системы, которая может быть основой для реального маркетингового SaaS продукта.

---

# About the project

This project is an MVP of an AI SaaS platform that automatically generates marketing campaigns based on company website analysis.

The platform:

- analyzes company websites
- extracts key content
- identifies target audiences
- evaluates strengths and weaknesses
- generates marketing strategy
- builds structured marketing campaigns

The system demonstrates how LLM-based multi-agent architectures can be used to automate marketing workflows.

---

# Архитектура системы

Система построена на **multi-agent архитектуре LLM**.

Pipeline обработки:

1. Website Scraper  
2. Content Analyzer  
3. Audience Analyzer  
4. Campaign Generator  
5. Campaign Evaluator  

Каждый агент выполняет отдельную задачу анализа и генерации.

---

# AI Pipeline
Website URL
│
▼
Website Scraper
│
▼
Content Analysis
│
▼
Audience Identification
│
▼
Campaign Generation
│
▼
Campaign Evaluation

---

# Основные возможности

- анализ сайтов компаний
- извлечение маркетинговых инсайтов
- определение целевой аудитории
- генерация рекламной стратегии
- генерация структуры маркетинговой кампании
- multi-agent AI pipeline

---

# Используемые технологии

Backend:

- Python
- FastAPI

AI:

- LLM API
- embeddings
- RAG pipeline
- prompt engineering
- multi-agent architecture

Infrastructure:

- REST API
- website scraping
- structured outputs
- JSON pipelines

---

# API возможности

Платформа предоставляет API для:

- создания проектов
- анализа сайтов
- генерации маркетинговых кампаний
- сравнения кампаний
- аналитики использования

Основные endpoints:
POST /projects
POST /projects/{project_id}/analyze
GET /analyses/{analysis_id}

POST /campaigns/{analysis_id}
GET /campaigns/{campaign_id}

GET /analytics
GET /analytics/usage

---

# Моя роль в проекте

Проект разработан мной как AI-специалистом.

Я выполнял роли:

- инициатор продукта
- архитектор системы
- разработчик backend
- разработчик AI pipeline

Использовал AI инструменты разработки:

- ChatGPT
- Codex
- Claude Code

Проект демонстрирует применение AI для разработки и прототипирования SaaS продуктов.

---

# Roadmap развития

Планируемые улучшения:

- расширение RAG архитектуры
- подключение vector database
- улучшение анализа сайтов
- добавление AI-агентов
- web интерфейс платформы

---

---

# Статус проекта

MVP AI SaaS платформы.

Проект разработан как демо архитектуры AI-системы для автоматизации маркетинга.