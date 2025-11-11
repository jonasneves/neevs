"""
GPT Analyzer - Analyze news with GPT-4o

Uses GitHub Models API to access GPT-4o for news analysis.
"""

from agents.news_perspectives.model_analyzer import ModelAnalyzer


def main():
    """Main execution function"""
    # Use GPT-4o (GPT-5 may not be available yet)
    analyzer = ModelAnalyzer(
        model_name='openai/gpt-4o',
        display_name='GPT-4o',
        emoji='🟢'
    )

    analyzer.run(
        input_file='data/news_perspectives/news.json',
        output_file='data/news_perspectives/gpt_analysis.json',
        agent_id='gpt-analyzer'
    )


if __name__ == '__main__':
    main()
