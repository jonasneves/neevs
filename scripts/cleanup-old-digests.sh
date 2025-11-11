#!/bin/bash
#
# Cleanup old digest archives
# Keeps only the N most recent digests to prevent repository bloat
#
# Usage: ./scripts/cleanup-old-digests.sh [keep_count]
# Default: keeps 5 most recent digests per category

set -e

KEEP_COUNT=${1:-5}

echo "🧹 Cleaning up old digest archives..."
echo "📦 Keeping $KEEP_COUNT most recent digests per category"
echo ""

# Function to cleanup old files in a directory
cleanup_old_files() {
    local pattern=$1
    local name=$2

    # Count files before cleanup
    local before_count=$(ls -1 $pattern 2>/dev/null | wc -l)

    if [ $before_count -gt $KEEP_COUNT ]; then
        # Remove files older than the Nth most recent
        ls -t $pattern | tail -n +$((KEEP_COUNT + 1)) | xargs rm -f
        local after_count=$(ls -1 $pattern 2>/dev/null | wc -l)
        local removed=$((before_count - after_count))
        echo "✓ $name: removed $removed old files ($after_count remaining)"
    else
        echo "✓ $name: $before_count files (no cleanup needed)"
    fi
}

# Cleanup public digests
echo "📂 Cleaning public/digests/..."
cleanup_old_files "public/digests/academic-research-*.json" "Academic research digests"
cleanup_old_files "public/digests/market-analysis-*.json" "Market analysis digests"
cleanup_old_files "public/digests/market-analysis-editorial-*.json" "Market editorial digests"

echo ""
echo "📂 Cleaning data/academic_research/digests/..."
cleanup_old_files "data/academic_research/digests/academic-research-*.json" "Data academic digests"

echo ""
echo "📂 Cleaning public/stock-reports/..."
cleanup_old_files "public/stock-reports/report-*.json" "Stock reports"

echo ""
echo "📂 Cleaning data/stock_monitor/history/..."
cleanup_old_files "data/stock_monitor/history/report-*.json" "Stock report history"
cleanup_old_files "data/stock_monitor/history/prices-*.json" "Stock price history"

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "💡 Tip: Run this script periodically to keep repository size manageable"
echo "💡 Example: ./scripts/cleanup-old-digests.sh 3  # Keep only 3 most recent"
