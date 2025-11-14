# Automated AI-powered channels

<table>
  <thead>
    <tr>
      <th style="width: 150px;">Channel Status</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="width: 150px;">
        <a href="https://github.com/jonasneves/neevs/actions/workflows/news-perspectives.yml">
          <img src="https://github.com/jonasneves/neevs/actions/workflows/news-perspectives.yml/badge.svg" alt="AI News Bias Detector" style="width: 100%; height: auto;">
        </a>
      </td>
      <td><strong>AI News Bias Detector:</strong> Compare how ChatGPT, Llama, and other AIs interpret the same story</td>
    </tr>
    <tr>
      <td style="width: 150px;">
        <a href="https://github.com/jonasneves/neevs/actions/workflows/academic-research.yml">
          <img src="https://github.com/jonasneves/neevs/actions/workflows/academic-research.yml/badge.svg" alt="Academic Research" style="width: 100%; height: auto;">
        </a>
      </td>
      <td><strong>Academic Research:</strong> Weekly digest of trending research papers with social buzz tracking</td>
    </tr>
    <tr>
      <td style="width: 150px;">
        <a href="https://github.com/jonasneves/neevs/actions/workflows/market-analysis.yml">
          <img src="https://github.com/jonasneves/neevs/actions/workflows/market-analysis.yml/badge.svg" alt="Market Analysis" style="width: 100%; height: auto;">
        </a>
      </td>
      <td><strong>Market Analysis:</strong> Real-time crypto and stock market analysis with AI insights</td>
    </tr>
  </tbody>
</table>

## Overview

AgentFlow is a multi-agent pipeline that flows through specialized agents that fetch, analyze, and synthesize information automatically.

## Tech Stack

- **AI:** OpenAI GPT-4o-mini for summarization, categorization, and analysis
- **Orchestration:** GitHub Actions (free tier)
- **Frontend:** Astro + vanilla JavaScript
- **Deployment:** GitHub Pages (free)
- **Storage:** JSON files in git (no database)

## Project Structure

```
agents/                     # Agent pipelines
├── academic_research/      # Research digest pipeline
├── stock_monitor/          # Stock market monitoring
├── market_analysis/        # Market trends analysis
└── utils.py               # Shared utilities

.github/workflows/          # GitHub Actions
├── news-perspectives.yml   # AI News Bias Detector scheduler
├── academic-research.yml   # Research pipeline scheduler
├── market-analysis.yml     # Market analysis scheduler
└── deploy-site.yml         # GitHub Pages deployment

src/                        # Frontend
├── pages/                  # Astro pages
└── components/             # Reusable components
```
