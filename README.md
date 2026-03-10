# Ad Creatives Machine

AI-агентная система для анализа quiz-воронок и создания рекламных креативов.

## 🎯 Overview

Система состоит из 5 AI-агентов, работающих в pipeline:

| Agent | Role | Input | Output |
|-------|------|-------|--------|
| **Design Analyzer** | Парсинг макетов | Figma/PDF/URL | Структура воронки |
| **Marketing Analyst** | Маркетинговый анализ | Landing page URL | Value props, audiences |
| **Competitor Intel** | Разведка конкурентов | Value props | Winning creatives |
| **Creative Strategist** | Синтез и брифы | All data | Creative briefs |
| **Designer** | Генерация креативов | Briefs | Static/Video ads |

## 📁 Project Structure

```
ad-creatives-machine/
├── agents/
│   ├── design_analyzer/      # Agent 1
│   ├── marketing_analyst/    # Agent 2
│   ├── competitor_intel/     # Agent 3
│   ├── creative_strategist/  # Agent 4
│   └── designer/             # Agent 5
├── shared/
│   ├── schemas/              # JSON schemas for data exchange
│   └── utils/                # Common utilities
├── outputs/
│   ├── analysis/             # Analysis reports
│   ├── creatives/            # Generated creatives
│   └── reports/              # Final reports
└── config/
    └── mcp_config.json       # MCP server configurations
```

## 🔧 MCP Integrations

- **Figma**: `figma-developer-mcp` — design file parsing
- **Playwright**: `@anthropic/mcp-server-playwright` — web scraping
- **Apify**: `@apify/actors-mcp-server` — Meta Ads Library
- **EverArt**: `@anthropic/mcp-server-everart` — image generation

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Configure MCP servers (see config/mcp_config.json)
# Run specific agent
python agents/design_analyzer/run.py --input <figma_url>
```

## ⚙️ Configuration

**Target Market**: North America (English)
**Competitor Limit**: 20 creatives per query
**Platforms**: Meta Ads (Facebook + Instagram)
