"""
Perspective Synthesizer - Combines all AI model analyses

Merges perspectives from multiple AI models into a unified view
for frontend display and comparison.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional

from agents.utils import ExecutionTracker, CostCalculator, SummaryWriter, save_output_data, load_input_data


def load_analysis(file_path: str, model_name: str) -> Optional[Dict]:
    """Load analysis from a specific model"""
    try:
        data = load_input_data(file_path)
        return {
            'model': model_name,
            'analyses': data.get('data', {}).get('analyses', []),
            'metadata': data.get('metadata', {}),
            'costs': data.get('costs', {}),
        }
    except FileNotFoundError:
        print(f"  Warning: {model_name} analysis not found at {file_path}")
        return None
    except Exception as e:
        print(f"  Error loading {model_name} analysis: {e}")
        return None


def calculate_consensus(analyses: List[Dict]) -> Dict:
    """Calculate consensus metrics across all models"""
    sentiments = []
    confidence_levels = []

    for model_analyses in analyses:
        if not model_analyses:
            continue
        for item in model_analyses.get('analyses', []):
            analysis = item.get('analysis', {})
            if 'sentiment' in analysis:
                sentiments.append(analysis['sentiment'])
            if 'confidence' in analysis:
                confidence_levels.append(analysis['confidence'])

    # Count sentiment distribution
    sentiment_dist = {}
    for s in sentiments:
        sentiment_dist[s] = sentiment_dist.get(s, 0) + 1

    # Dominant sentiment
    dominant_sentiment = max(sentiment_dist.items(), key=lambda x: x[1])[0] if sentiment_dist else 'unknown'

    # Agreement percentage (how many models agree on dominant sentiment)
    agreement = (sentiment_dist.get(dominant_sentiment, 0) / len(sentiments) * 100) if sentiments else 0

    return {
        'dominant_sentiment': dominant_sentiment,
        'sentiment_distribution': sentiment_dist,
        'agreement_percentage': round(agreement, 1),
        'total_analyses': len(sentiments),
        'confidence_distribution': {
            'high': confidence_levels.count('high'),
            'medium': confidence_levels.count('medium'),
            'low': confidence_levels.count('low'),
        }
    }


def synthesize_perspectives(all_analyses: List[Dict]) -> List[Dict]:
    """
    Synthesize multiple model analyses into article-centric view

    Args:
        all_analyses: List of model analysis dictionaries

    Returns:
        List of articles with all model perspectives
    """
    # Build article index
    article_perspectives = {}

    for model_data in all_analyses:
        if not model_data:
            continue

        model_name = model_data['model']
        for item in model_data.get('analyses', []):
            article = item.get('article', {})
            analysis = item.get('analysis', {})

            article_id = article.get('id', article.get('title', ''))

            if article_id not in article_perspectives:
                article_perspectives[article_id] = {
                    'article': article,
                    'perspectives': []
                }

            article_perspectives[article_id]['perspectives'].append({
                'model': model_name,
                'model_id': analysis.get('model_id', ''),
                'emoji': get_model_emoji(model_name),
                'summary': analysis.get('summary', ''),
                'key_points': analysis.get('key_points', []),
                'sentiment': analysis.get('sentiment', 'unknown'),
                'confidence': analysis.get('confidence', 'unknown'),
                'bias_check': analysis.get('bias_check', ''),
                'missing_context': analysis.get('missing_context', ''),
                'implications': analysis.get('implications', ''),
                'analyzed_at': analysis.get('analyzed_at', ''),
            })

    # Convert to list and calculate consensus for each article
    synthesized = []
    for article_id, data in article_perspectives.items():
        perspectives = data['perspectives']

        # Calculate sentiment consensus for this article
        sentiments = [p['sentiment'] for p in perspectives if p['sentiment'] != 'unknown']
        sentiment_counts = {}
        for s in sentiments:
            sentiment_counts[s] = sentiment_counts.get(s, 0) + 1

        dominant_sentiment = max(sentiment_counts.items(), key=lambda x: x[1])[0] if sentiment_counts else 'mixed'
        agreement = (sentiment_counts.get(dominant_sentiment, 0) / len(sentiments) * 100) if sentiments else 0

        synthesized.append({
            'article': data['article'],
            'perspectives': perspectives,
            'consensus': {
                'dominant_sentiment': dominant_sentiment,
                'agreement_percentage': round(agreement, 1),
                'sentiment_distribution': sentiment_counts,
                'models_analyzed': len(perspectives),
            }
        })

    # Sort by number of perspectives (most analyzed first)
    synthesized.sort(key=lambda x: len(x['perspectives']), reverse=True)

    return synthesized


def get_model_emoji(model_name: str) -> str:
    """Get emoji for model"""
    emoji_map = {
        # Low tier models
        'GPT-4o Mini': '🟢',
        'Llama 3.1 8B': '🔵',
        'Phi-4 Mini': '🟡',
        'Mistral Small': '🟣',
        # High tier models
        'GPT-4o': '🟢',
        'Llama 3.1 405B': '🔵',
        'DeepSeek-V3': '🟣',
        'Grok 3': '🟠',
    }
    return emoji_map.get(model_name, '⚪')


def main():
    """Main execution function"""
    # Track execution
    tracker = ExecutionTracker()

    print("\n🔄 Perspective Synthesizer")
    print("  Combining analyses from all AI models...\n")

    # Load all possible model analyses (both low-tier and high-tier)
    # Only files that exist will be loaded
    models = [
        # Low tier models (better rate limits)
        ('data/news_perspectives/gpt_mini_analysis.json', 'GPT-4o Mini'),
        ('data/news_perspectives/llama_small_analysis.json', 'Llama 3.1 8B'),
        ('data/news_perspectives/phi_analysis.json', 'Phi-4 Mini'),
        ('data/news_perspectives/mistral_analysis.json', 'Mistral Small'),
        # High tier models (restrictive rate limits)
        ('data/news_perspectives/gpt_analysis.json', 'GPT-4o'),
        ('data/news_perspectives/llama_analysis.json', 'Llama 3.1 405B'),
        ('data/news_perspectives/deepseek_analysis.json', 'DeepSeek-V3'),
        ('data/news_perspectives/grok_analysis.json', 'Grok 3'),
    ]

    all_analyses = []
    for file_path, model_name in models:
        print(f"  Loading {model_name} analysis...")
        analysis = load_analysis(file_path, model_name)
        if analysis:
            all_analyses.append(analysis)
            print(f"    ✓ Loaded {len(analysis.get('analyses', []))} analyses")

    # Synthesize perspectives
    print("\n  Synthesizing perspectives...")
    synthesized = synthesize_perspectives(all_analyses)

    # Calculate overall consensus
    consensus = calculate_consensus(all_analyses)

    print(f"\n✓ Perspective Synthesizer completed")
    print(f"  Articles with perspectives: {len(synthesized)}")
    print(f"  Total analyses: {consensus['total_analyses']}")
    print(f"  Dominant sentiment: {consensus['dominant_sentiment']}")
    print(f"  Agreement: {consensus['agreement_percentage']}%")

    # Finish tracking
    tracker.finish()

    # Calculate costs (no API costs for synthesis)
    costs = CostCalculator.calculate_total_cost(tracker)

    print(f"  Execution time: {costs['execution_time']:.2f}s")

    # Create output
    output = {
        'agent': 'perspective-synthesizer',
        'timestamp': datetime.utcnow().isoformat(),
        'status': 'completed',
        'data': {
            'articles': synthesized,
            'count': len(synthesized),
            'consensus': consensus,
            'models': [model_name for _, model_name in models],
        },
        'metadata': {
            'models_included': [model_name for _, model_name in models],
            'total_perspectives': consensus['total_analyses'],
            'generated_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
        },
        'costs': costs
    }

    # Save output
    save_output_data('data/news_perspectives/perspectives.json', output)

    # Write GitHub Actions summary
    summary = SummaryWriter("Perspective Synthesizer", "🔄")
    summary.add_header()
    summary.add_metric("Status", "Completed")
    summary.add_metric("Articles Synthesized", len(synthesized))
    summary.add_metric("Total Perspectives", consensus['total_analyses'])
    summary.add_metric("Dominant Sentiment", consensus['dominant_sentiment'])
    summary.add_metric("Agreement", f"{consensus['agreement_percentage']}%")
    summary.add_timestamps(tracker)
    summary.add_cost_summary(costs)
    summary.write()


if __name__ == '__main__':
    main()
