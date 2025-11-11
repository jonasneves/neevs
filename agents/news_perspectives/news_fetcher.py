"""
News Fetcher - Fetches latest news from Google News RSS

Uses Google News RSS feed to get top headlines without requiring an API key.
"""

import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict
import html
import re

from agents.utils import ExecutionTracker, CostCalculator, SummaryWriter, save_output_data


def clean_html(text: str) -> str:
    """Remove HTML tags and decode entities"""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Decode HTML entities
    text = html.unescape(text)
    return text.strip()


def fetch_google_news(topic: str = 'WORLD', max_results: int = 10) -> List[Dict]:
    """
    Fetch latest news from Google News RSS feed

    Args:
        topic: News topic (WORLD, NATION, BUSINESS, TECHNOLOGY, ENTERTAINMENT, SPORTS, SCIENCE, HEALTH)
        max_results: Maximum number of articles to fetch

    Returns:
        List of news article dictionaries
    """
    # Google News RSS URL
    base_url = 'https://news.google.com/rss'

    # Topic mapping
    topic_map = {
        'WORLD': '/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnVHZ0pWVXlnQVAB',
        'NATION': '/topics/CAAqIQgKIhtDQkFTRGdvSUwyMHZNRGs1TVdvaUFtVnVLQUFQAQ',
        'BUSINESS': '/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB',
        'TECHNOLOGY': '/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB',
        'ENTERTAINMENT': '/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNREpxYW5RU0FtVnVHZ0pWVXlnQVAB',
        'SPORTS': '/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp1ZEdvU0FtVnVHZ0pWVXlnQVAB',
        'SCIENCE': '/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp0Y1RjU0FtVnVHZ0pWVXlnQVAB',
        'HEALTH': '/topics/CAAqIQgKIhtDQkFTRGdvSUwyMHZNR3QwTlRFU0FtVnVLQUFQAQ',
    }

    # Use top stories if no topic or use topic-specific feed
    if topic and topic.upper() in topic_map:
        url = base_url + topic_map[topic.upper()] + '?hl=en-US&gl=US&ceid=US:en'
    else:
        url = base_url + '?hl=en-US&gl=US&ceid=US:en'

    print(f"Fetching news from Google News (topic: {topic})")
    print(f"URL: {url}")

    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )

        with urllib.request.urlopen(req) as response:
            data = response.read().decode('utf-8')

        # Parse XML RSS feed
        root = ET.fromstring(data)

        articles = []
        for item in root.findall('.//item')[:max_results]:
            title_elem = item.find('title')
            link_elem = item.find('link')
            pub_date_elem = item.find('pubDate')
            description_elem = item.find('description')
            source_elem = item.find('source')

            # Extract article data
            title = title_elem.text if title_elem is not None else 'Unknown Title'
            link = link_elem.text if link_elem is not None else ''
            pub_date = pub_date_elem.text if pub_date_elem is not None else ''
            description = clean_html(description_elem.text) if description_elem is not None else ''
            source = source_elem.text if source_elem is not None else 'Unknown Source'

            article = {
                'id': f"news_{len(articles)}_{int(datetime.utcnow().timestamp())}",
                'title': clean_html(title),
                'description': description[:500] if description else title,  # Fallback to title
                'url': link,
                'source': source,
                'published': pub_date,
                'topic': topic,
                'fetched_at': datetime.utcnow().isoformat(),
            }
            articles.append(article)

        print(f"✓ Fetched {len(articles)} articles from Google News")
        return articles

    except Exception as e:
        print(f"✗ Error fetching from Google News: {e}")
        import traceback
        traceback.print_exc()
        return []


def main():
    """Main execution function"""
    # Track execution
    tracker = ExecutionTracker()

    # Get configuration from environment variables (for workflow_dispatch)
    import os
    max_articles_per_topic = int(os.getenv('NEWS_MAX_ARTICLES_PER_TOPIC', '5'))
    topics_str = os.getenv('NEWS_TOPICS', 'TECHNOLOGY,WORLD,BUSINESS')
    topics = [t.strip().upper() for t in topics_str.split(',')]

    print(f"\n📰 News Fetcher")
    print(f"  Configuration:")
    print(f"    Max articles per topic: {max_articles_per_topic}")
    print(f"    Topics: {', '.join(topics)}")
    print()

    # Fetch news from configured topics
    all_articles = []
    for topic in topics:
        articles = fetch_google_news(topic=topic, max_results=max_articles_per_topic)
        all_articles.extend(articles)

    # Remove duplicates based on title similarity
    seen_titles = set()
    unique_articles = []
    for article in all_articles:
        # Simple deduplication by first 50 chars of title
        title_key = article['title'][:50].lower()
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            unique_articles.append(article)

    print(f"\n✓ News Fetcher completed - Fetched {len(unique_articles)} unique articles")
    print(f"  Topics: {', '.join(topics)}")

    # Finish tracking
    tracker.finish()

    # Calculate costs (no API costs for RSS feed)
    costs = CostCalculator.calculate_total_cost(tracker)

    print(f"  Execution time: {costs['execution_time']:.2f}s")
    print(f"  Estimated cost: ${costs['total']:.6f}")

    # Create output
    output = {
        'agent': 'news-fetcher',
        'timestamp': datetime.utcnow().isoformat(),
        'status': 'completed',
        'data': {
            'articles': unique_articles,
            'count': len(unique_articles),
            'topics': topics,
            'fetch_date': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        },
        'metadata': {
            'source': 'Google News RSS',
            'topics_queried': topics,
        },
        'costs': costs
    }

    # Save output
    save_output_data('data/news_perspectives/news.json', output)

    # Write GitHub Actions summary
    summary = SummaryWriter("News Fetcher", "📰")
    summary.add_header()
    summary.add_metric("Status", "Completed")
    summary.add_metric("Articles Fetched", len(unique_articles))
    summary.add_metric("Topics", ', '.join(topics))
    summary.add_timestamps(tracker)
    summary.add_cost_summary(costs)
    summary.write()


if __name__ == '__main__':
    main()
