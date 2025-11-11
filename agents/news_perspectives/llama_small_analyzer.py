"""
Llama 3.1 8B Analyzer - Lightweight Meta model for news analysis

Uses Llama 3.1 8B which has:
- Low rate limit tier (15 req/min, 150 req/day)
- Smaller 8B parameter model
- Faster responses
"""

from agents.news_perspectives.model_analyzer import ModelAnalyzer


def main():
    """Main execution function"""
    analyzer = ModelAnalyzer(
        model_name='meta/meta-llama-3.1-8b-instruct',
        display_name='Llama 3.1 8B',
        emoji='🔵'
    )
    analyzer.run(
        input_file='data/news_perspectives/news.json',
        output_file='data/news_perspectives/llama_small_analysis.json',
        agent_id='llama-small-analyzer'
    )


if __name__ == '__main__':
    main()
