"""
Agent A - Reddit Post Fetcher

Fetches latest posts from r/duke subreddit.
"""

import json
import urllib.request
from datetime import datetime, timedelta
from typing import List, Dict

from agents.utils import ExecutionTracker, CostCalculator, SummaryWriter, save_output_data


def fetch_reddit_posts(subreddit: str = 'duke', limit: int = 100) -> List[Dict]:
    """
    Fetch latest posts from Reddit using public JSON API (no auth required)

    Args:
        subreddit: Subreddit name (default: duke)
        limit: Maximum number of posts to fetch

    Returns:
        List of post dictionaries
    """
    url = f"https://www.reddit.com/r/{subreddit}/new.json?limit={limit}"

    print(f"Fetching posts from r/{subreddit}")

    try:
        # Reddit requires a user agent
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'AgentFlow/1.0 (Duke Hackathon Project)'}
        )

        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))

        # Filter posts from last 7 days (168 hours) - more likely to have content
        cutoff_time = datetime.utcnow() - timedelta(days=7)

        posts = []
        for child in data['data']['children']:
            post_data = child['data']

            # Convert Unix timestamp to datetime
            post_time = datetime.utcfromtimestamp(post_data['created_utc'])

            # Skip posts older than 7 days
            if post_time < cutoff_time:
                continue

            # Extract relevant fields
            post = {
                'id': post_data['id'],
                'title': post_data['title'],
                'body': post_data.get('selftext', '')[:1000],  # Limit body length
                'author': post_data['author'],
                'upvotes': post_data['ups'],
                'num_comments': post_data['num_comments'],
                'url': f"https://reddit.com{post_data['permalink']}",
                'created_utc': post_data['created_utc'],
                'created_readable': post_time.strftime('%Y-%m-%d %H:%M UTC'),
                'flair': post_data.get('link_flair_text', 'General'),
                'is_self': post_data['is_self'],
                'domain': post_data.get('domain', ''),
            }
            posts.append(post)

        return posts

    except Exception as e:
        print(f"Error fetching from Reddit: {e}")
        return []


def main():
    """Main execution function"""
    # Track execution
    tracker = ExecutionTracker()

    # Fetch posts
    posts = fetch_reddit_posts(subreddit='duke', limit=100)

    print(f"✓ Agent A completed - Fetched {len(posts)} posts from last 7 days")

    # Finish tracking
    tracker.finish()

    # Calculate costs
    costs = CostCalculator.calculate_total_cost(tracker)

    print(f"  Execution time: {costs['execution_time']:.2f}s")
    print(f"  Estimated cost: ${costs['total']:.6f}")

    # Create output
    output = {
        'agent': 'agent-a-reddit-fetcher',
        'timestamp': datetime.utcnow().isoformat(),
        'status': 'completed',
        'data': {
            'posts': posts,
            'count': len(posts),
            'subreddit': 'duke',
            'fetch_date': datetime.utcnow().strftime('%Y-%m-%d'),
            'time_window': '7 days'
        },
        'metadata': {
            'source': 'Reddit public JSON API',
            'subreddit': 'r/duke'
        },
        'costs': costs
    }

    # Save output
    save_output_data('data/duke_local/posts.json', output)

    # Write GitHub Actions summary
    summary = SummaryWriter("Agent A - Reddit Fetcher", "🎓")
    summary.add_header()
    summary.add_metric("Status", "Completed")
    summary.add_metric("Posts Fetched", len(posts))
    summary.add_metric("Subreddit", "r/duke")
    summary.add_metric("Time Window", "Last 7 days")
    summary.add_timestamps(tracker)
    summary.add_cost_summary(costs)
    summary.add_execution_logs('agent-a-execution.log')
    summary.write()


if __name__ == '__main__':
    main()
