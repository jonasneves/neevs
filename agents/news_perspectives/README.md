# News Perspectives Pipeline

**Multi-AI analysis pipeline that reveals bias in news coverage.**

## Overview

This pipeline fetches the latest news from Google News and analyzes each article using multiple AI models (GPT-4o, Claude 3.5 Sonnet, DeepSeek-R1, and Grok 3) to expose different perspectives, biases, and analytical approaches.

## Purpose

**Understanding AI Bias**: By showing how different AI models interpret the same news, users can:
- See which models lean toward certain viewpoints
- Understand that AI isn't neutral
- Make informed decisions about which AI to trust
- Develop critical thinking about AI-generated content

## Pipeline Architecture

```
┌─────────────────────────────┐
│  1. News Fetcher            │
│  Fetches from Google News   │
└──────────┬──────────────────┘
           │
    ┌──────┴──────┬──────────┬──────────┬──────────┐
    │             │          │          │          │
┌───▼────┐  ┌────▼────┐  ┌──▼────┐  ┌──▼────┐  ┌──▼────┐
│ GPT-4o │  │ Claude  │  │DeepSeek│  │ Grok  │  │ ...   │
│Analyzer│  │Analyzer │  │Analyzer│  │Analyzer│  │       │
└───┬────┘  └────┬────┘  └──┬────┘  └──┬────┘  └──┬────┘
    │            │          │          │          │
    └────────────┴──────────┴──────────┴──────────┘
                 │
        ┌────────▼─────────┐
        │  3. Synthesizer  │
        │  Combines views  │
        └────────┬─────────┘
                 │
        ┌────────▼─────────┐
        │  4. Frontend     │
        │  Beautiful UI    │
        └──────────────────┘
```

## Agents

### 1. News Fetcher (`news_fetcher.py`)
- **Purpose**: Fetch latest news from Google News RSS
- **Topics**: Technology, World, Business
- **Output**: `data/news_perspectives/news.json`
- **No API Key Required**: Uses free RSS feeds

### 2. Model Analyzers (Parallel Execution)
All analyzers run simultaneously for maximum speed:

- **`gpt_analyzer.py`**: GPT-4o analysis
- **`claude_analyzer.py`**: Claude 3.5 Sonnet analysis
- **`deepseek_analyzer.py`**: DeepSeek-R1 analysis
- **`grok_analyzer.py`**: Grok 3 analysis

**Each analyzer provides**:
- Summary from the model's perspective
- Key points and insights
- Sentiment analysis (positive/negative/neutral/mixed)
- Bias check (what biases might exist)
- Missing context (what's not being covered)
- Implications (broader impact)

**Output**: `data/news_perspectives/{model}_analysis.json`

### 3. Perspective Synthesizer (`perspective_synthesizer.py`)
- **Purpose**: Combine all model analyses into a unified view
- **Calculates**: Consensus metrics, agreement percentages
- **Output**: `data/news_perspectives/perspectives.json`

## Frontend

**URL**: `/perspectives`

Features:
- 📰 News-style layout
- 🎨 Color-coded AI models
- 📊 Sentiment indicators
- 🔍 Expandable details (key points, bias checks)
- 🎯 Consensus visualization

## Running the Pipeline

### Manual Trigger
```bash
# In GitHub Actions, go to:
Actions → News Perspectives Pipeline → Run workflow
```

### Automated Schedule
Runs every 6 hours automatically via GitHub Actions.

### Local Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variable
export GH_MODELS_TOKEN="your-github-models-token"

# Run individual agents
python -m agents.news_perspectives.news_fetcher
python -m agents.news_perspectives.gpt_analyzer
python -m agents.news_perspectives.claude_analyzer
python -m agents.news_perspectives.deepseek_analyzer
python -m agents.news_perspectives.grok_analyzer
python -m agents.news_perspectives.perspective_synthesizer
```

## Environment Variables

- **`GH_MODELS_TOKEN`**: GitHub Models API token (required for AI analysis)
  - Set in GitHub repository secrets
  - Provides access to GPT-4o, Claude, DeepSeek, Grok via Azure endpoint

## Data Flow

1. **News Fetcher** → `data/news_perspectives/news.json`
2. **AI Analyzers** (parallel) → `data/news_perspectives/{model}_analysis.json`
3. **Synthesizer** → `data/news_perspectives/perspectives.json`
4. **GitHub Actions** → Copies to `public/news-perspectives.json`
5. **Frontend** → Reads from `public/news-perspectives.json`

## API Costs

- **News Fetching**: $0 (free RSS feeds)
- **AI Analysis**: ~$0.001 - $0.01 per article (depends on model)
- **Total per run**: ~$0.10 - $1.00 (for 10-15 articles × 4 models)

## Key Features

✅ **Parallel execution** - All AI models query simultaneously
✅ **Error resilient** - Continues even if one model fails
✅ **No duplication** - Intelligent deduplication of news articles
✅ **Beautiful UI** - Professional news-style presentation
✅ **Bias transparency** - Shows how different AIs see the same story
✅ **Free infrastructure** - Runs on GitHub Actions & Pages

## Future Enhancements

- [ ] Add more AI models (Llama, Mistral, Gemini)
- [ ] User voting on which perspective is most accurate
- [ ] Historical bias tracking (how models change over time)
- [ ] Article source diversity metrics
- [ ] Export perspectives to PDF/markdown

## License

Part of the AgentFlow project - MIT License
