"""
GPT-4o Mini Analyzer - Lightweight OpenAI model for news analysis

Uses GPT-4o mini which has:
- Low rate limit tier (15 req/min, 150 req/day)
- Lower cost
- Faster responses
"""

from agents.news_perspectives.model_analyzer import ModelAnalyzer


def main():
    """Main execution function"""
    analyzer = ModelAnalyzer(
        model_name='openai/gpt-4o-mini',
        display_name='GPT-4o Mini',
        emoji='🟢'
    )
    analyzer.run(
        input_file='data/news_perspectives/news.json',
        output_file='data/news_perspectives/gpt_mini_analysis.json',
        agent_id='gpt-mini-analyzer'
    )


if __name__ == '__main__':
    main()
