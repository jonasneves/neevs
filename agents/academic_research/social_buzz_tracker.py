"""
Agent D - Social Buzz Tracker

Tracks social media buzz for research papers across HN, Reddit, and Twitter.
Identifies which papers people are actually talking about.
Uses FREE APIs only - no auth required.
"""

import json
import os
import re
import time
from datetime import datetime
from typing import List, Dict, Tuple
import urllib.request
import urllib.parse

from agents.utils import (
    ExecutionTracker,
    CostCalculator,
    SummaryWriter,
    load_input_data,
    save_output_data
)


def search_hackernews(paper_id: str, title: str) -> Dict:
    """
    Search Hacker News for mentions of this paper
    Uses free Algolia HN API
    """
    try:
        # Search for arXiv ID
        query = f"arxiv {paper_id.split('v')[0]}"  # Remove version
        url = f"https://hn.algolia.com/api/v1/search?query={urllib.parse.quote(query)}&tags=story"

        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())

        hits = data.get('hits', [])

        if not hits:
            # Try searching by title keywords (first 5 words)
            title_words = ' '.join(title.split()[:5])
            url = f"https://hn.algolia.com/api/v1/search?query={urllib.parse.quote(title_words)}&tags=story"

            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())

            hits = data.get('hits', [])

        if hits:
            top_hit = hits[0]
            return {
                'found': True,
                'discussions': len(hits),
                'points': top_hit.get('points', 0),
                'comments': top_hit.get('num_comments', 0),
                'url': f"https://news.ycombinator.com/item?id={top_hit.get('objectID')}",
                'title': top_hit.get('title', '')
            }

        return {'found': False}

    except Exception as e:
        print(f"  HN search error: {e}")
        return {'found': False, 'error': str(e)}


def search_reddit(paper_id: str, title: str) -> Dict:
    """
    Search Reddit for mentions of this paper
    Uses free Reddit JSON API (no auth needed for search)
    """
    try:
        # Search for arXiv ID
        query = f"arxiv {paper_id.split('v')[0]}"
        url = f"https://www.reddit.com/search.json?q={urllib.parse.quote(query)}&limit=10"

        # Reddit requires a user agent
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'ResearchBlogBot/1.0')

        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())

        posts = data.get('data', {}).get('children', [])

        if not posts:
            # Try title search
            title_words = ' '.join(title.split()[:5])
            url = f"https://www.reddit.com/search.json?q={urllib.parse.quote(title_words)}&limit=10"

            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'ResearchBlogBot/1.0')

            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())

            posts = data.get('data', {}).get('children', [])

        if posts:
            total_upvotes = sum(p['data'].get('ups', 0) for p in posts)
            total_comments = sum(p['data'].get('num_comments', 0) for p in posts)
            top_post = max(posts, key=lambda p: p['data'].get('ups', 0))

            return {
                'found': True,
                'posts': len(posts),
                'upvotes': total_upvotes,
                'comments': total_comments,
                'top_subreddit': top_post['data'].get('subreddit', ''),
                'top_url': f"https://reddit.com{top_post['data'].get('permalink', '')}"
            }

        return {'found': False}

    except Exception as e:
        print(f"  Reddit search error: {e}")
        return {'found': False, 'error': str(e)}


def calculate_buzz_score(hn_data: Dict, reddit_data: Dict) -> int:
    """
    Calculate a 0-100 buzz score based on social media metrics
    """
    score = 0

    # Hacker News signals (max 60 points)
    if hn_data.get('found'):
        score += min(hn_data.get('points', 0) / 5, 30)  # Up to 30 points (150+ HN points = max)
        score += min(hn_data.get('comments', 0) / 2, 20)  # Up to 20 points (40+ comments = max)
        score += hn_data.get('discussions', 0) * 5  # 5 points per discussion

    # Reddit signals (max 40 points)
    if reddit_data.get('found'):
        score += min(reddit_data.get('upvotes', 0) / 10, 20)  # Up to 20 points (200+ upvotes = max)
        score += min(reddit_data.get('comments', 0) / 3, 10)  # Up to 10 points (30+ comments = max)
        score += reddit_data.get('posts', 0) * 5  # 5 points per post

    return min(int(score), 100)


def is_trending(buzz_score: int, hn_data: Dict, reddit_data: Dict) -> bool:
    """
    Determine if a paper is "trending" based on recent activity
    """
    if buzz_score >= 50:
        return True

    # Recent HN activity
    if hn_data.get('found') and hn_data.get('points', 0) >= 50:
        return True

    # Recent Reddit activity
    if reddit_data.get('found') and reddit_data.get('upvotes', 0) >= 100:
        return True

    return False


def track_social_buzz(papers: List[Dict]) -> Tuple[List[Dict], Dict]:
    """
    Track social media buzz for all papers

    Returns:
        Tuple of (papers_with_buzz, stats_dict)
    """
    papers_with_buzz = []
    stats = {
        'total_papers': len(papers),
        'papers_with_buzz': 0,
        'trending_papers': 0,
        'total_hn_discussions': 0,
        'total_reddit_posts': 0
    }

    for i, paper in enumerate(papers[:10], 1):  # Limit to 10 to be nice to APIs
        print(f"Checking social buzz ({i}/{min(len(papers), 10)}): {paper['title'][:50]}...")

        # Search Hacker News
        hn_data = search_hackernews(paper['id'], paper['title'])
        time.sleep(0.5)  # Be nice to HN API

        # Search Reddit
        reddit_data = search_reddit(paper['id'], paper['title'])
        time.sleep(0.5)  # Be nice to Reddit API

        # Calculate buzz score
        buzz_score = calculate_buzz_score(hn_data, reddit_data)
        trending = is_trending(buzz_score, hn_data, reddit_data)

        # Update stats
        if hn_data.get('found') or reddit_data.get('found'):
            stats['papers_with_buzz'] += 1

        if trending:
            stats['trending_papers'] += 1

        if hn_data.get('found'):
            stats['total_hn_discussions'] += hn_data.get('discussions', 0)

        if reddit_data.get('found'):
            stats['total_reddit_posts'] += reddit_data.get('posts', 0)

        # Add buzz data to paper
        papers_with_buzz.append({
            **paper,
            'social_buzz': {
                'hacker_news': hn_data,
                'reddit': reddit_data,
                'buzz_score': buzz_score,
                'trending': trending,
                'has_buzz': hn_data.get('found') or reddit_data.get('found')
            }
        })

    return papers_with_buzz, stats


def main():
    """Main execution function"""
    # Track execution
    tracker = ExecutionTracker()

    # Load input data from Agent A
    agent_a_data = load_input_data('data/academic_research/papers.json')
    papers = agent_a_data['data']['papers']

    print(f"🔍 Tracking social buzz for {len(papers)} papers...")

    # Track social buzz
    papers_with_buzz, stats = track_social_buzz(papers)

    print(f"✓ Agent D completed - Tracked social buzz for {stats['total_papers']} papers")
    print(f"  Papers with buzz: {stats['papers_with_buzz']}")
    print(f"  Trending papers: {stats['trending_papers']}")
    print(f"  HN discussions: {stats['total_hn_discussions']}")
    print(f"  Reddit posts: {stats['total_reddit_posts']}")

    # Finish tracking
    tracker.finish()

    # Calculate costs (no API costs - all free!)
    costs = CostCalculator.calculate_total_cost(tracker, {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0})

    print(f"  Execution time: {costs['execution_time']:.2f}s")
    print(f"  API cost: $0.00 (all free APIs!)")

    # Create output
    output = {
        'agent': 'agent-d-social-buzz-tracker',
        'timestamp': datetime.utcnow().isoformat(),
        'status': 'completed',
        'input_from': 'agent-a-paper-fetcher',
        'data': {
            'papers_with_buzz': papers_with_buzz,
            'stats': stats,
            'trending_papers': [p for p in papers_with_buzz if p['social_buzz']['trending']],
        },
        'metadata': {
            'sources': ['Hacker News', 'Reddit'],
            'apis_used': ['hn.algolia.com', 'reddit.com/search.json'],
            'cost': 'FREE'
        },
        'costs': costs
    }

    # Save output
    save_output_data('data/academic_research/social-buzz.json', output)

    # Write GitHub Actions summary
    summary = SummaryWriter("Agent D - Social Buzz Tracker", "🔥")
    summary.add_header()
    summary.add_metric("Status", "Completed")
    summary.add_metric("Papers Tracked", stats['total_papers'])
    summary.add_metric("Papers with Buzz", stats['papers_with_buzz'])
    summary.add_metric("Trending Papers", stats['trending_papers'])
    summary.add_metric("HN Discussions", stats['total_hn_discussions'])
    summary.add_metric("Reddit Posts", stats['total_reddit_posts'])
    summary.add_metric("API Cost", "$0.00 (FREE)")
    summary.add_timestamps(tracker)
    summary.add_cost_summary(costs)
    summary.add_execution_logs('agent-d-execution.log')
    summary.write()


if __name__ == '__main__':
    main()
