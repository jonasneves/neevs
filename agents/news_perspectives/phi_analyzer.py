"""
Phi-4 Mini Analyzer - Lightweight Microsoft model for news analysis

Uses Phi-4 Mini which has:
- Low rate limit tier (15 req/min, 150 req/day)
- Compact model designed for efficiency
- Strong reasoning capabilities
"""

from agents.news_perspectives.model_analyzer import ModelAnalyzer


def main():
    """Main execution function"""
    analyzer = ModelAnalyzer(
        model_name='microsoft/phi-4-mini-instruct',
        display_name='Phi-4 Mini',
        emoji='🟡'
    )
    analyzer.run(
        input_file='data/news_perspectives/news.json',
        output_file='data/news_perspectives/phi_analysis.json',
        agent_id='phi-analyzer'
    )


if __name__ == '__main__':
    main()
