"""
Grok Analyzer - Analyze news with Grok 3

Uses GitHub Models API to access Grok for news analysis.
"""

from agents.news_perspectives.model_analyzer import ModelAnalyzer


def main():
    """Main execution function"""
    analyzer = ModelAnalyzer(
        model_name='xai/grok-3',
        display_name='Grok 3',
        emoji='🟠'
    )

    analyzer.run(
        input_file='data/news_perspectives/news.json',
        output_file='data/news_perspectives/grok_analysis.json',
        agent_id='grok-analyzer'
    )


if __name__ == '__main__':
    main()
