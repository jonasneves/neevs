"""
Agent B - Post Categorizer

Categorizes Duke Reddit posts using AI to make them easier to browse.
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


def categorize_posts_with_openai(posts: List[Dict]) -> Tuple[List[Dict], Dict]:
    """
    Categorize posts using OpenAI GPT-4o-mini

    Returns:
        Tuple of (categorized_posts, token_usage_dict)
    """
    api_key = os.environ.get('OPENAI_API_KEY')
    token_usage = {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}

    if not api_key:
        print("WARNING: OpenAI API key not found - using mock categorization")
        return mock_categorization(posts), token_usage

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        categorized_posts = []

        # Process posts in batches to save API calls
        batch_size = 10
        for i in range(0, len(posts), batch_size):
            batch = posts[i:i+batch_size]

            print(f"Categorizing batch {i//batch_size + 1} ({len(batch)} posts)...")

            # Build prompt with all posts in batch
            prompt = "Categorize these Duke Reddit posts into categories. For EACH post, provide:\n\n"

            for idx, post in enumerate(batch):
                prompt += f"Post {idx}:\n"
                prompt += f"Title: {post['title']}\n"
                prompt += f"Body: {post['body'][:200] if post['body'] else 'No body'}\n"
                prompt += f"Flair: {post.get('flair', 'General')}\n\n"

            prompt += "Respond with a JSON array where each object has:\n"
            prompt += '{\n'
            prompt += '  "post_index": <index>,\n'
            prompt += '  "category": "<Academic|Housing|Events|Social|Memes|Sports|Campus Life|Resources|Other>",\n'
            prompt += '  "tags": ["tag1", "tag2"],\n'
            prompt += '  "summary": "<1 sentence: what is this about?>",\n'
            prompt += '  "sentiment": "<Positive|Neutral|Negative|Question>"\n'
            prompt += '}'

            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You're a Duke student helping categorize campus discussions. Be helpful and accurate. Always respond with valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=1000
                )

                # Track token usage
                if response.usage:
                    token_usage['prompt_tokens'] += response.usage.prompt_tokens
                    token_usage['completion_tokens'] += response.usage.completion_tokens
                    token_usage['total_tokens'] += response.usage.total_tokens

                categorization_text = response.choices[0].message.content.strip()

                # Extract JSON from response
                if '```json' in categorization_text:
                    categorization_text = categorization_text.split('```json')[1].split('```')[0].strip()
                elif '```' in categorization_text:
                    categorization_text = categorization_text.split('```')[1].split('```')[0].strip()

                categorizations = json.loads(categorization_text)

                # Merge categorizations with posts
                for cat in categorizations:
                    idx = cat['post_index']
                    if idx < len(batch):
                        categorized_posts.append({
                            **batch[idx],
                            'categorization': {
                                'category': cat['category'],
                                'tags': cat.get('tags', []),
                                'summary': cat.get('summary', ''),
                                'sentiment': cat.get('sentiment', 'Neutral')
                            }
                        })

            except Exception as e:
                print(f"  Error categorizing batch: {e}")
                # Use mock categorization as fallback
                for post in batch:
                    categorized_posts.append({
                        **post,
                        'categorization': {
                            'category': 'Other',
                            'tags': [],
                            'summary': post['title'],
                            'sentiment': 'Neutral'
                        }
                    })

        return categorized_posts, token_usage

    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
        return mock_categorization(posts), token_usage


def mock_categorization(posts: List[Dict]) -> List[Dict]:
    """Mock categorization for testing without API key"""
    categorized_posts = []

    for post in posts:
        # Simple keyword-based categorization
        title_lower = post['title'].lower()
        body_lower = post.get('body', '').lower()

        category = 'Other'
        tags = []

        if any(word in title_lower or word in body_lower for word in ['class', 'course', 'exam', 'professor', 'grade', 'study']):
            category = 'Academic'
            tags = ['classes']
        elif any(word in title_lower or word in body_lower for word in ['housing', 'dorm', 'apartment', 'roommate']):
            category = 'Housing'
            tags = ['housing']
        elif any(word in title_lower or word in body_lower for word in ['event', 'club', 'meeting', 'party']):
            category = 'Events'
            tags = ['events']
        elif any(word in title_lower or word in body_lower for word in ['basketball', 'football', 'game', 'sports']):
            category = 'Sports'
            tags = ['sports']

        categorized_posts.append({
            **post,
            'categorization': {
                'category': category,
                'tags': tags,
                'summary': post['title'],
                'sentiment': 'Neutral'
            }
        })

    return categorized_posts


def main():
    """Main execution function"""
    # Track execution
    tracker = ExecutionTracker()

    # Load posts from Agent A
    posts_data = load_input_data('data/duke_local/posts.json')
    posts = posts_data['data']['posts']

    print(f"Processing {len(posts)} posts...")

    # Categorize posts
    categorized_posts, token_usage = categorize_posts_with_openai(posts)

    print(f"✓ Agent B completed - Categorized {len(categorized_posts)} posts")

    # Finish tracking
    tracker.finish()

    # Calculate costs
    costs = CostCalculator.calculate_total_cost(tracker, token_usage)

    print(f"  Execution time: {costs['execution_time']:.2f}s")
    print(f"  Tokens used: {token_usage['total_tokens']}")
    print(f"  Estimated cost: ${costs['total']:.6f}")

    # Group by category for summary
    categories = {}
    for post in categorized_posts:
        cat = post['categorization']['category']
        categories[cat] = categories.get(cat, 0) + 1

    # Create output
    output = {
        'agent': 'agent-b-post-categorizer',
        'timestamp': datetime.utcnow().isoformat(),
        'status': 'completed',
        'data': {
            'categorized_posts': categorized_posts,
            'count': len(categorized_posts),
            'categories': categories
        },
        'metadata': {
            'model': 'gpt-4o-mini',
            'token_usage': token_usage
        },
        'costs': costs
    }

    # Save output
    save_output_data('data/duke_local/categorized-posts.json', output)

    # Write GitHub Actions summary
    summary = SummaryWriter("Agent B - Post Categorizer", "🏷️")
    summary.add_header()
    summary.add_metric("Status", "Completed")
    summary.add_metric("Posts Categorized", len(categorized_posts))
    summary.add_metric("Categories", ', '.join(categories.keys()))
    summary.add_timestamps(tracker)
    summary.add_cost_summary(costs)
    summary.add_execution_logs('agent-b-execution.log')
    summary.write()


if __name__ == '__main__':
    main()
