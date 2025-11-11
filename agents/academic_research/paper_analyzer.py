"""
Agent B - Paper Analyzer

Makes research papers accessible and engaging for blog readers.
Focuses on: What's new? Why care? Who's this for?
NO arbitrary relevance scores - just honest, useful analysis.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Tuple

from agents.utils import (
    ExecutionTracker,
    CostCalculator,
    SummaryWriter,
    load_input_data,
    save_output_data
)


def analyze_papers_with_openai(papers: List[Dict]) -> Tuple[List[Dict], Dict]:
    """
    Analyze papers using OpenAI GPT-4o-mini

    Returns:
        Tuple of (analyzed_papers, token_usage_dict)
    """
    api_key = os.environ.get('OPENAI_API_KEY')
    token_usage = {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}

    if not api_key:
        print("WARNING: OpenAI API key not found - using mock analysis")
        return mock_analysis(papers), token_usage

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        analyzed_papers = []

        for paper in papers[:10]:  # Limit to 10 to save API costs
            print(f"Analyzing: {paper['title'][:50]}...")

            prompt = "You're analyzing this paper for a BLOG about research. Make it accessible and engaging.\n\n"
            prompt += f"Title: {paper['title']}\n"
            prompt += f"Authors: {', '.join(paper['authors'][:5])}\n"
            prompt += f"Abstract: {paper['abstract']}\n\n"
            prompt += "Provide analysis in this exact JSON format:\n"
            prompt += '{\n'
            prompt += '  "tldr": "<2-3 sentences: What is this paper about, in plain English?>",\n'
            prompt += '  "eli5": "<Explain the main idea like I\'m smart but not a PhD in this field>",\n'
            prompt += '  "key_contributions": ["What\'s actually NEW here?", "contribution 2", "contribution 3"],\n'
            prompt += '  "why_care": "<Why should anyone outside academia care? Real-world implications?>",\n'
            prompt += '  "accessibility": "<General Audience|Tech-Savvy|Researchers Only>",\n'
            prompt += '  "spicy_take": "<Optional: A bold opinion or hot take about this work - can be null>",\n'
            prompt += '  "reading_time_minutes": <integer>\n'
            prompt += '}'

            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You're a research blogger who makes complex papers accessible and engaging. Be smart, witty, and honest. Always respond with valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.8,
                    max_tokens=600
                )

                # Track token usage
                if response.usage:
                    token_usage['prompt_tokens'] += response.usage.prompt_tokens
                    token_usage['completion_tokens'] += response.usage.completion_tokens
                    token_usage['total_tokens'] += response.usage.total_tokens

                analysis_text = response.choices[0].message.content.strip()

                # Extract JSON from response
                if '```json' in analysis_text:
                    analysis_text = analysis_text.split('```json')[1].split('```')[0].strip()
                elif '```' in analysis_text:
                    analysis_text = analysis_text.split('```')[1].split('```')[0].strip()

                analysis = json.loads(analysis_text)

                analyzed_papers.append({
                    **paper,
                    'analysis': analysis
                })

            except Exception as e:
                print(f"  Error analyzing paper: {e}")
                # Use mock analysis as fallback
                analyzed_papers.append({
                    **paper,
                    'analysis': mock_analysis([paper])[0]['analysis']
                })

        return analyzed_papers, token_usage

    except Exception as e:
        print(f"Error using OpenAI API: {e}")
        return mock_analysis(papers), token_usage


def mock_analysis(papers: List[Dict]) -> List[Dict]:
    """Mock analysis when API key is not available"""
    analyzed = []
    for i, paper in enumerate(papers[:10]):
        category = paper.get('primary_category', 'research')
        analyzed.append({
            **paper,
            'analysis': {
                'tldr': f"This paper tackles {category} with a novel approach that could change how we think about the field.",
                'eli5': f"Imagine if {category} worked differently - this paper shows us how. It's like finding a shortcut everyone missed.",
                'key_contributions': [
                    f'Novel approach to {category}',
                    'Improved performance over existing methods',
                    'Practical applications demonstrated'
                ],
                'why_care': f"This could actually impact real-world {category} applications we use daily.",
                'accessibility': ['General Audience', 'Tech-Savvy', 'Researchers Only'][i % 3],
                'spicy_take': "This might be the paper everyone talks about next month." if i % 3 == 0 else None,
                'reading_time_minutes': 20 + (i * 5)
            }
        })
    return analyzed


def main():
    """Main execution function"""
    # Track execution
    tracker = ExecutionTracker()

    # Load input data from Agent A
    agent_a_data = load_input_data('data/academic_research/papers.json')
    papers = agent_a_data['data']['papers']

    # Analyze papers
    analyzed_papers, token_usage = analyze_papers_with_openai(papers)

    # Calculate summary statistics
    total_analyzed = len(analyzed_papers)
    accessibility_counts = {
        'General Audience': sum(1 for p in analyzed_papers if p['analysis']['accessibility'] == 'General Audience'),
        'Tech-Savvy': sum(1 for p in analyzed_papers if p['analysis']['accessibility'] == 'Tech-Savvy'),
        'Researchers Only': sum(1 for p in analyzed_papers if p['analysis']['accessibility'] == 'Researchers Only')
    }

    print(f"✓ Agent B completed - Analyzed {total_analyzed} papers")
    print(f"  Accessibility breakdown: {accessibility_counts['General Audience']} general, {accessibility_counts['Tech-Savvy']} tech-savvy, {accessibility_counts['Researchers Only']} researchers-only")

    # Finish tracking
    tracker.finish()

    # Calculate costs
    costs = CostCalculator.calculate_total_cost(tracker, token_usage)

    print(f"  Token usage: {token_usage['total_tokens']} tokens (prompt: {token_usage['prompt_tokens']}, completion: {token_usage['completion_tokens']})")
    print(f"  Execution time: {costs['execution_time']:.2f}s")
    print(f"  Estimated cost: ${costs['total']:.6f}")

    # Create output
    output = {
        'agent': 'agent-b-paper-analyzer',
        'timestamp': datetime.utcnow().isoformat(),
        'status': 'completed',
        'input_from': 'agent-a-paper-fetcher',
        'data': {
            'analyzed_papers': analyzed_papers,
            'summary': {
                'total_analyzed': total_analyzed,
                'by_accessibility': accessibility_counts,
                'avg_reading_time': sum(p['analysis']['reading_time_minutes'] for p in analyzed_papers) / total_analyzed if total_analyzed > 0 else 0
            }
        },
        'metadata': {
            'model': 'gpt-4o-mini',
            'api': 'OpenAI',
            'style': 'blog-accessible'
        },
        'costs': costs
    }

    # Save output
    save_output_data('data/academic_research/analyzed-papers.json', output)

    # Write GitHub Actions summary
    summary = SummaryWriter("Agent B - Paper Analyzer (Blog Style)", "📝")
    summary.add_header()
    summary.add_metric("Status", "Completed")
    summary.add_metric("Papers Analyzed", total_analyzed)
    summary.add_metric("General Audience Papers", accessibility_counts['General Audience'])
    summary.add_metric("Tech-Savvy Papers", accessibility_counts['Tech-Savvy'])
    summary.add_metric("Researchers Only", accessibility_counts['Researchers Only'])
    summary.add_metric("Model", "GPT-4o-mini (OpenAI)")
    summary.add_timestamps(tracker)
    summary.add_cost_summary(costs)
    summary.add_execution_logs('agent-b-execution.log')
    summary.write()


if __name__ == '__main__':
    main()
