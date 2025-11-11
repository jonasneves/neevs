"""
Agent E - Editorial Digest Writer

Synthesizes papers, analysis, and social buzz into an engaging weekly digest.
Smart, witty, accessible, and opinionated writing style.
Groups papers thematically and writes compelling narratives.
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


def generate_editorial_digest(analyzed_papers: List[Dict], buzz_papers: List[Dict]) -> Tuple[Dict, Dict]:
    """
    Generate editorial digest using OpenAI GPT-4o-mini

    Returns:
        Tuple of (digest_dict, token_usage_dict)
    """
    api_key = os.environ.get('OPENAI_API_KEY')
    token_usage = {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}

    if not api_key:
        print("WARNING: OpenAI API key not found - using mock digest")
        return mock_digest(analyzed_papers, buzz_papers), token_usage

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        # Merge analysis and buzz data
        papers_data = []
        for analyzed in analyzed_papers[:10]:
            # Find matching buzz data
            buzz_data = next((b for b in buzz_papers if b['id'] == analyzed['id']), None)

            buzz_info = ""
            buzz_details = None
            if buzz_data and buzz_data.get('social_buzz', {}).get('has_buzz'):
                sb = buzz_data['social_buzz']
                buzz_info = f"\nSOCIAL BUZZ: Score {sb['buzz_score']}/100"
                if sb['trending']:
                    buzz_info += " TRENDING"
                if sb['hacker_news'].get('found'):
                    buzz_info += f" | HN: {sb['hacker_news']['points']} pts, {sb['hacker_news']['comments']} comments"
                if sb['reddit'].get('found'):
                    buzz_info += f" | Reddit: {sb['reddit']['upvotes']} upvotes"

                # Store buzz details for frontend
                buzz_details = {
                    'buzz_score': sb['buzz_score'],
                    'trending': sb['trending'],
                    'hacker_news': sb['hacker_news'] if sb['hacker_news'].get('found') else None,
                    'reddit': sb['reddit'] if sb['reddit'].get('found') else None
                }

            papers_data.append({
                'title': analyzed['title'],
                'authors': analyzed['authors'][:3],
                'tldr': analyzed['analysis']['tldr'],
                'eli5': analyzed['analysis']['eli5'],
                'why_care': analyzed['analysis']['why_care'],
                'key_contributions': analyzed['analysis']['key_contributions'],
                'accessibility': analyzed['analysis']['accessibility'],
                'spicy_take': analyzed['analysis'].get('spicy_take'),
                'buzz_info': buzz_info,
                'buzz_details': buzz_details,
                'categories': analyzed.get('categories', []),
            })

        # Build the prompt for editorial digest
        prompt = "You're writing a WEEKLY RESEARCH DIGEST blog post for a broad audience.\n\n"
        prompt += "Your tone: Smart, witty, accessible. Strong opinions. Make complex things understandable.\n"
        prompt += "Don't dumb things down, but don't gatekeep either.\n\n"
        prompt += "Here are this week's papers:\n\n"

        for i, paper in enumerate(papers_data, 1):
            prompt += f"{i}. {paper['title']}\n"
            prompt += f"   Authors: {', '.join(paper['authors'])}\n"
            prompt += f"   Categories: {', '.join(paper['categories'][:2])}\n"
            prompt += f"   TLDR: {paper['tldr']}\n"
            prompt += f"   Why care: {paper['why_care']}\n"
            prompt += f"   Accessibility: {paper['accessibility']}\n"
            if paper['spicy_take']:
                prompt += f"   Hot take: {paper['spicy_take']}\n"
            if paper['buzz_info']:
                prompt += f"   {paper['buzz_info']}\n"
            prompt += "\n"

        prompt += "\nCreate a weekly digest in this JSON format:\n"
        prompt += '{\n'
        prompt += '  "title": "<catchy weekly digest title>",\n'
        prompt += '  "subtitle": "<witty one-liner about this week\'s theme>",\n'
        prompt += '  "intro": "<3-4 sentences: What\'s the vibe this week? Any patterns? Get readers excited>",\n'
        prompt += '  "sections": [\n'
        prompt += '    {\n'
        prompt += '      "title": "<thematic section name>",\n'
        prompt += '      "papers": [1, 3],  // paper indices that fit this theme\n'
        prompt += '      "commentary": "<2-3 sentences connecting these papers and why they matter>"\n'
        prompt += '    }\n'
        prompt += '  ],\n'
        prompt += '  "editors_pick": {\n'
        prompt += '    "paper_index": 1,\n'
        prompt += '    "reason": "<Why THIS paper deserves the spotlight?>"\n'
        prompt += '  },\n'
        prompt += '  "honorable_mentions": [5, 7],  // paper indices worth a quick shout\n'
        prompt += '  "parting_thoughts": "<2-3 sentences: What\'s the big picture? What should readers remember?>"\n'
        prompt += '}\n\n'
        prompt += 'IMPORTANT:\n'
        prompt += '- Group papers thematically (AI/ML, Physics, Robotics, Theory, etc)\n'
        prompt += '- Prioritize papers with ACTUAL social buzz (high buzz scores, trending status)\n'
        prompt += '- ONLY mention specific platforms (HN/Reddit) if they appear in the buzz data\n'
        prompt += '- Do NOT make up buzz or say "the internet is talking" unless there is real data\n'
        prompt += '- Make it ENGAGING - people should want to read this\n'
        prompt += '- Be opinionated but fair\n'
        prompt += '- If a paper has buzz data, acknowledge it specifically in your commentary'

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You're a research blogger with personality. Be smart, funny, and honest. Always respond with valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=1500
            )

            # Track token usage
            if response.usage:
                token_usage['prompt_tokens'] = response.usage.prompt_tokens
                token_usage['completion_tokens'] = response.usage.completion_tokens
                token_usage['total_tokens'] = response.usage.total_tokens

            digest_text = response.choices[0].message.content.strip()

            # Extract JSON
            if '```json' in digest_text:
                digest_text = digest_text.split('```json')[1].split('```')[0].strip()
            elif '```' in digest_text:
                digest_text = digest_text.split('```')[1].split('```')[0].strip()

            digest = json.loads(digest_text)

            # Map paper indices to actual papers
            result = {
                'title': digest['title'],
                'subtitle': digest['subtitle'],
                'intro': digest['intro'],
                'sections': [],
                'editors_pick': None,
                'honorable_mentions': [],
                'parting_thoughts': digest['parting_thoughts']
            }

            # Map sections with buzz data
            for section in digest['sections']:
                section_papers = []
                for idx in section['papers']:
                    if 1 <= idx <= len(analyzed_papers):
                        paper = analyzed_papers[idx - 1].copy()
                        # Add buzz data from papers_data
                        paper_data = papers_data[idx - 1]
                        if paper_data['buzz_details']:
                            paper['buzz'] = paper_data['buzz_details']
                        section_papers.append(paper)

                result['sections'].append({
                    'title': section['title'],
                    'papers': section_papers,
                    'commentary': section['commentary']
                })

            # Map editor's pick with buzz data
            if digest['editors_pick']:
                idx = digest['editors_pick']['paper_index']
                if 1 <= idx <= len(analyzed_papers):
                    paper = analyzed_papers[idx - 1].copy()
                    paper_data = papers_data[idx - 1]
                    if paper_data['buzz_details']:
                        paper['buzz'] = paper_data['buzz_details']
                    result['editors_pick'] = {
                        'paper': paper,
                        'reason': digest['editors_pick']['reason']
                    }

            # Map honorable mentions with buzz data
            for idx in digest.get('honorable_mentions', []):
                if 1 <= idx <= len(analyzed_papers):
                    paper = analyzed_papers[idx - 1].copy()
                    paper_data = papers_data[idx - 1]
                    if paper_data['buzz_details']:
                        paper['buzz'] = paper_data['buzz_details']
                    result['honorable_mentions'].append(paper)

            return result, token_usage

        except Exception as e:
            print(f"  Error generating digest: {e}")
            return mock_digest(analyzed_papers, buzz_papers), token_usage

    except Exception as e:
        print(f"Error using OpenAI API: {e}")
        return mock_digest(analyzed_papers, buzz_papers), token_usage


def mock_digest(analyzed_papers: List[Dict], buzz_papers: List[Dict]) -> Dict:
    """Mock digest when API key is not available"""
    # Attach buzz data to papers
    papers_with_buzz = []
    for paper in analyzed_papers:
        paper_copy = paper.copy()
        # Find matching buzz data
        buzz_data = next((b for b in buzz_papers if b['id'] == paper['id']), None)
        if buzz_data and buzz_data.get('social_buzz', {}).get('has_buzz'):
            sb = buzz_data['social_buzz']
            paper_copy['buzz'] = {
                'buzz_score': sb.get('buzz_score', 0),
                'trending': sb.get('trending', False),
                'hacker_news': sb['hacker_news'] if sb['hacker_news'].get('found') else None,
                'reddit': sb['reddit'] if sb['reddit'].get('found') else None
            }
        papers_with_buzz.append(paper_copy)

    return {
        'title': 'This Week in Research: AI Gets Weird, Physics Gets Weirder',
        'subtitle': 'Plus: Why robots still can\'t fold your laundry',
        'intro': 'This week\'s papers are a wild ride through the bleeding edge of research. We\'ve got AI models learning to see dark energy, robots learning from YouTube (sort of), and some truly spicy takes on machine learning. Buckle up.',
        'sections': [
            {
                'title': 'The Robot Revolution (Still Loading...)',
                'papers': papers_with_buzz[:2],
                'commentary': 'Turns out teaching robots is hard. Who knew? These papers are taking different approaches to the same problem: how do we make machines that don\'t need a PhD to operate.'
            },
            {
                'title': 'AI Doing AI Things',
                'papers': papers_with_buzz[2:4],
                'commentary': 'The meta-ness of AI systems analyzing other AI systems never gets old. These papers push the boundaries of what\'s possible when machines think about thinking.'
            }
        ],
        'editors_pick': {
            'paper': papers_with_buzz[0],
            'reason': 'This paper is doing something genuinely novel - and the internet noticed. When both Hacker News and Reddit are talking about your research, you know you\'re onto something.'
        },
        'honorable_mentions': papers_with_buzz[4:6] if len(papers_with_buzz) >= 6 else [],
        'parting_thoughts': 'The theme this week? Convergence. Whether it\'s combining different ML techniques or merging human and robot learning, the frontier is in how we combine things. See you next week!'
    }


def main():
    """Main execution function"""
    # Track execution
    tracker = ExecutionTracker()

    # Load input data from Agent B only
    agent_b_data = load_input_data('data/academic_research/analyzed-papers.json')
    analyzed_papers = agent_b_data['data']['analyzed_papers']

    print(f"✍️ Writing editorial digest from {len(analyzed_papers)} papers...")

    # Generate digest (no buzz data)
    digest, token_usage = generate_editorial_digest(analyzed_papers, [])

    print(f"✓ Agent E completed - Generated weekly digest")
    print(f"  Title: {digest['title']}")
    print(f"  Sections: {len(digest['sections'])}")
    print(f"  Editor's pick: {digest['editors_pick']['paper']['title'][:50] if digest['editors_pick'] else 'None'}")

    # Finish tracking
    tracker.finish()

    # Calculate costs
    costs = CostCalculator.calculate_total_cost(tracker, token_usage)

    print(f"  Token usage: {token_usage['total_tokens']} tokens")
    print(f"  Execution time: {costs['execution_time']:.2f}s")
    print(f"  Estimated cost: ${costs['total']:.6f}")

    # Create output
    output = {
        'agent': 'agent-e-editorial-digest-writer',
        'timestamp': datetime.utcnow().isoformat(),
        'status': 'completed',
        'input_from': ['agent-b-paper-analyzer'],
        'data': {
            'digest': digest,
            'metadata': {
                'total_papers_reviewed': len(analyzed_papers),
                'sections': len(digest['sections']),
                'featured_papers': sum(len(s['papers']) for s in digest['sections']),
                'has_editors_pick': digest['editors_pick'] is not None
            }
        },
        'metadata': {
            'model': 'gpt-4o-mini',
            'api': 'OpenAI',
            'style': 'john-oliver-science'
        },
        'costs': costs
    }

    # Save output - both latest and dated archive
    save_output_data('data/academic_research/digest.json', output)

    # Also save to dated archive with timestamp for uniqueness
    # Format: academic-research-YYYY-MM-DD-HHMMSS (e.g., academic-research-2025-11-09-143022)
    # This ensures each pipeline has its own namespace
    archive_timestamp = datetime.utcnow().strftime('%Y-%m-%d-%H%M%S')
    pipeline_name = 'academic-research'
    archive_filename = f'{pipeline_name}-{archive_timestamp}'
    save_output_data(f'data/academic_research/digests/{archive_filename}.json', output)
    print(f"  Saved to archive: data/academic_research/digests/{archive_filename}.json")

    # Write GitHub Actions summary
    summary = SummaryWriter("Agent E - Editorial Digest Writer", "✍️")
    summary.add_header()
    summary.add_metric("Status", "Completed")
    summary.add_metric("Digest Title", digest['title'])
    summary.add_metric("Sections", len(digest['sections']))
    summary.add_metric("Featured Papers", sum(len(s['papers']) for s in digest['sections']))
    summary.add_metric("Model", "GPT-4o-mini (OpenAI)")
    summary.add_timestamps(tracker)
    summary.add_cost_summary(costs)
    summary.add_execution_logs('agent-e-execution.log')
    summary.write()


if __name__ == '__main__':
    main()
