# Repository Maintenance Guide

This document describes maintenance procedures for the Duke Hackathon 2025 repository.

## Data File Management

### Generated Data Files

The repository generates data files in the following directories:

- `data/academic_research/` - Research paper data and analysis
- `data/market_analysis/` - Market data and digests
- `data/news_perspectives/` - News analysis from different AI models
- `data/stock_monitor/` - Stock price monitoring data
- `data/duke_local/` - Local Duke community data

### Public Deployment Files

Generated files are copied to `public/` for GitHub Pages deployment:

- `public/academic-research-digest.json` - Latest research digest
- `public/market-analysis.json` - Latest market digest
- `public/market-analysis-editorial.json` - John Oliver-style market commentary
- `public/news-perspectives.json` - News analysis compilation
- `public/stock-market-report.json` - Stock analysis report
- `public/stock-prices.json` - Current stock prices

### Archive Digests

Historical digests are stored in:

- `public/digests/academic-research-*.json` - Research digest history
- `public/digests/market-analysis-*.json` - Market digest history
- `public/digests/market-analysis-editorial-*.json` - Editorial digest history
- `public/stock-reports/report-*.json` - Stock report history
- `data/stock_monitor/history/` - Stock monitoring history

## Cleanup Procedures

### Automated Cleanup

Use the cleanup script to remove old digest archives:

```bash
# Keep 5 most recent digests (default)
./scripts/cleanup-old-digests.sh

# Keep only 3 most recent digests
./scripts/cleanup-old-digests.sh 3

# Keep 10 most recent digests
./scripts/cleanup-old-digests.sh 10
```

### Manual Cleanup

To manually clean up old files:

```bash
# Remove old academic research digests (keep 5 most recent)
ls -t public/digests/academic-research-*.json | tail -n +6 | xargs rm -f
ls -t data/academic_research/digests/*.json | tail -n +6 | xargs rm -f

# Remove old market analysis digests (keep 5 most recent)
ls -t public/digests/market-analysis-*.json | tail -n +6 | xargs rm -f

# Remove old stock reports (keep 5 most recent)
ls -t public/stock-reports/report-*.json | tail -n +6 | xargs rm -f
ls -t data/stock_monitor/history/report-*.json | tail -n +6 | xargs rm -f
```

### Git Configuration

The `.gitignore` file excludes generated data files for local development:

```gitignore
# Generated data files (CI/CD will commit when needed)
data/*/
!data/.gitkeep

# Agent execution logs
*.log
agent-*-execution.log
```

**Note:** GitHub Actions workflows will still commit data files when they run. The `.gitignore` prevents accidental commits during local development.

## Workflow Management

### Active Workflows

The repository uses these GitHub Actions workflows:

1. **academic-research.yml** - Daily research paper analysis (6 AM UTC)
2. **market-analysis.yml** - Twice-daily market analysis (9 AM, 9 PM UTC)
3. **news-perspectives.yml** - Daily news analysis (8 AM UTC)
4. **stock-monitor.yml** - 3x daily stock monitoring (6 AM, 12 PM, 6 PM UTC)
5. **duke-local.yml** - Daily Duke community digest (8 AM UTC)
6. **_reusable-agent-runner.yml** - Shared agent runner template

### Removed Workflows

- **deploy-pages.yml** (Removed 2025-11-10) - Outdated deployment workflow
  - Reason: Each pipeline now handles its own deployment
  - Referenced non-existent agent files (agent-a.json, agent-b.json, etc.)

## Best Practices

### Data File Sizes

- Keep digest archives to 5-10 most recent runs
- Run cleanup script weekly or after major changes
- Monitor repository size: `du -sh data/ public/`

### Local Development

```bash
# Don't commit generated data files locally
git add -A
git reset data/  # Unstage data files

# Or use git add with specific files
git add agents/ .github/workflows/
```

### Repository Health

Check repository size periodically:

```bash
# Check total repository size
du -sh .git/

# Check data directory sizes
du -sh data/ public/

# Count digest files
ls public/digests/ | wc -l
ls public/stock-reports/ | wc -l
```

## Troubleshooting

### Large Repository Size

If the repository grows too large:

1. Run the cleanup script: `./scripts/cleanup-old-digests.sh 3`
2. Commit the cleanup: `git add -A && git commit -m "Clean up old digest archives"`
3. Push changes: `git push`

### Missing Data Files

If workflows fail due to missing data files:

1. Check if the previous pipeline stage succeeded
2. Verify file paths in workflow YAML files
3. Check workflow logs in GitHub Actions

### Workflow Failures

Common issues:

- Missing API keys (OPENAI_API_KEY, ALPHA_VANTAGE_API_KEY)
- Rate limiting on external APIs
- Network timeouts during data fetching

Check workflow logs and retry failed jobs if needed.

## Future Improvements

Potential enhancements:

- [ ] Add automated cleanup workflow (monthly)
- [ ] Implement data file rotation based on size limits
- [ ] Create archive compression for old digests
- [ ] Add monitoring for repository size
- [ ] Implement S3/cloud storage for large historical data
