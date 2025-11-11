"""
Mistral Small Analyzer - Lightweight Mistral AI model for news analysis

Uses Mistral Small 3.1 which has:
- Low rate limit tier (15 req/min, 150 req/day)
- Efficient European AI model
- Balanced performance
"""

from agents.news_perspectives.model_analyzer import ModelAnalyzer


def main():
    """Main execution function"""
    analyzer = ModelAnalyzer(
        model_name='mistral-ai/mistral-small-2503',
        display_name='Mistral Small',
        emoji='🟣'
    )
    analyzer.run(
        input_file='data/news_perspectives/news.json',
        output_file='data/news_perspectives/mistral_analysis.json',
        agent_id='mistral-analyzer'
    )


if __name__ == '__main__':
    main()
