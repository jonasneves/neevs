"""
Agent C - Duke Daily Digest Writer

Synthesizes categorized posts into an engaging daily digest.
Friendly, informative, and community-focused writing style.
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


def generate_daily_digest(categorized_posts: List[Dict]) -> Tuple[Dict, Dict]:
    """
    Generate daily digest using OpenAI GPT-4o-mini

    Returns:
        Tuple of (digest_dict, token_usage_dict)
    """
    api_key = os.environ.get('OPENAI_API_KEY')
    token_usage = {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}

    if not api_key:
        print("WARNING: OpenAI API key not found - using mock digest")
        return mock_digest(categorized_posts), token_usage

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        # Organize posts by category
        categories_data = {}
        for post in categorized_posts:
            category = post['categorization']['category']
            if category not in categories_data:
                categories_data[category] = []
            categories_data[category].append({
                'title': post['title'],
                'summary': post['categorization'].get('summary', post['title']),
                'sentiment': post['categorization'].get('sentiment', 'Neutral'),
                'upvotes': post.get('upvotes', 0),
                'num_comments': post.get('num_comments', 0),
                'url': post.get('url', ''),
                'flair': post.get('flair', 'General')
            })

        # Sort posts by engagement (upvotes + comments)
        for category in categories_data:
            categories_data[category].sort(
                key=lambda x: x['upvotes'] + x['num_comments'] * 2,
                reverse=True
            )

        # Build the prompt
        prompt = "You're writing a DAILY DUKE DIGEST for Duke students.\n\n"
        prompt += "Your tone: Friendly, helpful, campus-focused. Make students feel connected.\n"
        prompt += "This is what's happening on r/duke in the last 24 hours.\n\n"

        prompt += "Here are today's posts by category:\n\n"

        for category, posts in categories_data.items():
            prompt += f"## {category} ({len(posts)} posts)\n"
            for i, post in enumerate(posts[:5], 1):  # Top 5 per category
                prompt += f"{i}. {post['title']}\n"
                prompt += f"   Summary: {post['summary']}\n"
                prompt += f"   Engagement: {post['upvotes']} upvotes, {post['num_comments']} comments\n"
                prompt += f"   Sentiment: {post['sentiment']}\n\n"

        prompt += "\nCreate a daily digest in this JSON format:\n"
        prompt += '{\n'
        prompt += '  "title": "<engaging title for today\'s digest>",\n'
        prompt += '  "subtitle": "<one-liner about what\'s happening on campus today>",\n'
        prompt += '  "intro": "<2-3 sentences: What\'s the vibe today? What are students talking about?>",\n'
        prompt += '  "sections": [\n'
        prompt += '    {\n'
        prompt += '      "category": "<category name>",\n'
        prompt += '      "emoji": "<relevant emoji>",\n'
        prompt += '      "summary": "<2 sentences about this category today>",\n'
        prompt += '      "top_posts": [\n'
        prompt += '        {\n'
        prompt += '          "title": "<post title>",\n'
        prompt + ='          "summary": "<brief summary>",\n'
        prompt += '          "why_notable": "<why students should care>"\n'
        prompt += '        }\n'
        prompt += '      ]\n'
        prompt += '    }\n'
        prompt += '  ],\n'
        prompt += '  "trending_now": {\n'
        prompt += '    "post_title": "<most engaged post>",\n'
        prompt += '    "reason": "<why this is trending>"\n'
        prompt += '  },\n'
        prompt += '  "quick_hits": ["<brief mention 1>", "<brief mention 2>"],\n'
        prompt += '  "parting_note": "<friendly sign-off>"\n'
        prompt += '}\n\n'
        prompt += 'IMPORTANT:\n'
        prompt += '- Focus on posts with real engagement (upvotes/comments)\n'
        prompt += '- Be helpful and community-focused\n'
        prompt += '- Include 2-3 main sections (most active categories)\n'
        prompt += '- Keep it concise but informative\n'
        prompt += '- Highlight posts that students would want to know about'

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You're a Duke student writing a daily digest for your peers. Be friendly, helpful, and campus-focused. Always respond with valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1200
            )

            # Track token usage
            if response.usage:
                token_usage['prompt_tokens'] = response.usage.prompt_tokens
                token_usage['completion_tokens'] = response.usage.completion_tokens
                token_usage['total_tokens'] = response.usage.total_tokens

            digest_text = response.choices[0].message.content.strip()

            # Extract JSON from response
            if '```json' in digest_text:
                digest_text = digest_text.split('```json')[1].split('```')[0].strip()
            elif '```' in digest_text:
                digest_text = digest_text.split('```')[1].split('```')[0].strip()

            digest_structure = json.loads(digest_text)

            # Attach full post data to sections
            for section in digest_structure.get('sections', []):
                category = section['category']
                if category in categories_data:
                    # Match top_posts from digest to actual posts
                    section['posts_data'] = []
                    for top_post in section.get('top_posts', [])[:3]:
                        # Find matching post
                        matching = next(
                            (p for p in categories_data[category]
                             if p['title'] == top_post['title']),
                            None
                        )
                        if matching:
                            section['posts_data'].append({
                                **matching,
                                **top_post
                            })

            return digest_structure, token_usage

        except Exception as e:
            print(f"Error generating digest: {e}")
            return mock_digest(categorized_posts), token_usage

    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
        return mock_digest(categorized_posts), token_usage


def mock_digest(categorized_posts: List[Dict]) -> Dict:
    """Mock digest for testing without API key"""
    # Group by category
    categories = {}
    for post in categorized_posts:
        cat = post['categorization']['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(post)

    # Build basic digest
    sections = []
    for category, posts in list(categories.items())[:3]:
        sections.append({
            'category': category,
            'emoji': '📚' if category == 'Academic' else '🏠' if category == 'Housing' else '🎉',
            'summary': f"{len(posts)} posts about {category.lower()} today.",
            'posts_data': [{
                'title': p['title'],
                'summary': p['categorization'].get('summary', p['title']),
                'url': p.get('url', ''),
                'upvotes': p.get('upvotes', 0),
                'num_comments': p.get('num_comments', 0)
            } for p in posts[:3]]
        })

    return {
        'title': "Duke Daily Digest",
        'subtitle': "What's happening on campus today",
        'intro': f"Here's what Duke students are talking about today. {len(categorized_posts)} posts across {len(categories)} categories.",
        'sections': sections,
        'trending_now': {
            'post_title': categorized_posts[0]['title'] if categorized_posts else 'No posts',
            'reason': 'Most recent post'
        },
        'quick_hits': [],
        'parting_note': "Stay connected, Blue Devils!"
    }


def main():
    """Main execution function"""
    # Track execution
    tracker = ExecutionTracker()

    # Load categorized posts from Agent B
    posts_data = load_input_data('data/duke_local/categorized-posts.json')
    categorized_posts = posts_data['data']['categorized_posts']

    print(f"Generating digest from {len(categorized_posts)} posts...")

    # Generate digest
    digest, token_usage = generate_daily_digest(categorized_posts)

    print(f"✓ Agent C completed - Generated daily digest")

    # Finish tracking
    tracker.finish()

    # Calculate costs
    costs = CostCalculator.calculate_total_cost(tracker, token_usage)

    print(f"  Execution time: {costs['execution_time']:.2f}s")
    print(f"  Tokens used: {token_usage['total_tokens']}")
    print(f"  Estimated cost: ${costs['total']:.6f}")

    # Create output with archive support
    timestamp = datetime.utcnow()
    timestamp_str = timestamp.strftime('%Y-%m-%d-%H%M%S')

    output = {
        'agent': 'agent-c-digest-writer',
        'timestamp': timestamp.isoformat(),
        'status': 'completed',
        'data': {
            'digest': digest,
            'post_count': len(categorized_posts)
        },
        'metadata': {
            'model': 'gpt-4o-mini',
            'token_usage': token_usage
        },
        'costs': costs
    }

    # Save latest digest
    save_output_data('data/duke_local/digest.json', output)

    # Save timestamped archive
    archive_filename = f'data/duke_local/digests/duke-local-{timestamp_str}.json'
    save_output_data(archive_filename, output)

    print(f"  Saved to: data/duke_local/digest.json")
    print(f"  Archived to: {archive_filename}")

    # Write GitHub Actions summary
    summary = SummaryWriter("Agent C - Digest Writer", "📰")
    summary.add_header()
    summary.add_metric("Status", "Completed")
    summary.add_metric("Posts in Digest", len(categorized_posts))
    summary.add_metric("Sections", len(digest.get('sections', [])))
    summary.add_timestamps(tracker)
    summary.add_cost_summary(costs)
    summary.add_execution_logs('agent-c-execution.log')
    summary.write()


if __name__ == '__main__':
    main()
