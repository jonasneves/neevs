"""
DeepSeek Analyzer - Analyze news with DeepSeek-V3

Uses GitHub Models API to access DeepSeek for news analysis.
"""

from agents.news_perspectives.model_analyzer import ModelAnalyzer


def main():
    """Main execution function"""
    analyzer = ModelAnalyzer(
        model_name='deepseek/deepseek-v3-0324',
        display_name='DeepSeek-V3',
        emoji='🟣'
    )

    analyzer.run(
        input_file='data/news_perspectives/news.json',
        output_file='data/news_perspectives/deepseek_analysis.json',
        agent_id='deepseek-analyzer'
    )


if __name__ == '__main__':
    main()
