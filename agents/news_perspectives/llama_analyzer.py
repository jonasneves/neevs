"""
Llama Analyzer - Analyze news with Meta Llama 3.1

Uses GitHub Models API to access Meta's Llama 3.1 405B for news analysis.
"""

from agents.news_perspectives.model_analyzer import ModelAnalyzer


def main():
    """Main execution function"""
    analyzer = ModelAnalyzer(
        model_name='meta/meta-llama-3.1-405b-instruct',
        display_name='Llama 3.1 405B',
        emoji='🔵'
    )

    analyzer.run(
        input_file='data/news_perspectives/news.json',
        output_file='data/news_perspectives/llama_analysis.json',
        agent_id='llama-analyzer'
    )


if __name__ == '__main__':
    main()
