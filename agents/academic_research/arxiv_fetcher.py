"""
Agent A - arXiv Paper Fetcher

Fetches latest papers from arXiv API for specified categories.
"""

import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import os
from datetime import datetime, timedelta
from typing import List, Dict, Set

from agents.utils import ExecutionTracker, CostCalculator, SummaryWriter, save_output_data

# State file path
STATE_FILE = 'data/academic_research/fetch_state.json'


def load_fetch_state() -> Dict:
    """
    Load the fetch state containing last fetch time and recently seen paper IDs.

    Returns:
        Dictionary with 'last_fetch_time' and 'seen_paper_ids' (30-day rolling window)
    """
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
                print(f"✓ Loaded fetch state from {STATE_FILE}")
                print(f"  Last fetch: {state.get('last_fetch_time', 'Never')}")
                print(f"  Tracked papers: {len(state.get('seen_paper_ids', []))}")
                return state
        except Exception as e:
            print(f"⚠ Warning: Could not load fetch state: {e}")

    # Default state for first run
    print("ℹ No previous fetch state found - this is the first run")
    return {
        'last_fetch_time': None,
        'seen_paper_ids': []
    }


def save_fetch_state(last_fetch_time: str, paper_ids: Set[str], previous_ids: List[str]):
    """
    Save the fetch state with current timestamp and paper IDs.
    Maintains a 30-day rolling window of seen paper IDs.

    Args:
        last_fetch_time: ISO timestamp of current fetch
        paper_ids: Set of paper IDs from current fetch
        previous_ids: Previously seen paper IDs
    """
    # Combine current and previous IDs
    all_ids = list(paper_ids) + previous_ids

    # Remove duplicates while preserving order (most recent first)
    seen_ids = []
    for pid in all_ids:
        if pid not in seen_ids:
            seen_ids.append(pid)

    # Limit to reasonable size (last 500 papers ~30 days for 15 papers/day)
    seen_ids = seen_ids[:500]

    state = {
        'last_fetch_time': last_fetch_time,
        'seen_paper_ids': seen_ids,
        'updated_at': datetime.utcnow().isoformat()
    }

    # Ensure directory exists
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)

    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

    print(f"✓ Saved fetch state to {STATE_FILE}")
    print(f"  Tracking {len(seen_ids)} paper IDs")


def filter_duplicate_papers(papers: List[Dict], seen_ids: Set[str], last_fetch_time: str = None) -> List[Dict]:
    """
    Filter out papers that have already been seen or are too old.

    Args:
        papers: List of paper dictionaries from arXiv
        seen_ids: Set of previously seen paper IDs
        last_fetch_time: ISO timestamp of last fetch (optional)

    Returns:
        Filtered list of new papers only
    """
    filtered_papers = []
    duplicate_count = 0
    old_paper_count = 0

    # Parse last fetch time if provided
    cutoff_time = None
    if last_fetch_time:
        try:
            # Subtract 1 hour buffer to handle timezone/timing issues
            cutoff_time = datetime.fromisoformat(last_fetch_time.replace('Z', '+00:00')) - timedelta(hours=1)
        except Exception as e:
            print(f"⚠ Warning: Could not parse last_fetch_time: {e}")

    for paper in papers:
        paper_id = paper['id']

        # Check if already seen
        if paper_id in seen_ids:
            duplicate_count += 1
            continue

        # Check if published before last fetch (with buffer)
        if cutoff_time:
            try:
                published_time = datetime.fromisoformat(paper['published'].replace('Z', '+00:00'))
                if published_time < cutoff_time:
                    old_paper_count += 1
                    continue
            except Exception as e:
                # If we can't parse date, include the paper to be safe
                print(f"⚠ Warning: Could not parse published date for {paper_id}: {e}")

        filtered_papers.append(paper)

    print(f"🔍 Deduplication results:")
    print(f"  Total papers from arXiv: {len(papers)}")
    print(f"  Duplicates filtered: {duplicate_count}")
    if cutoff_time:
        print(f"  Old papers filtered: {old_paper_count}")
    print(f"  New papers to process: {len(filtered_papers)}")

    return filtered_papers


def fetch_arxiv_papers(categories: List[str] = None, max_results: int = 15) -> List[Dict]:
    """
    Fetch latest papers from arXiv API

    Args:
        categories: List of arXiv categories (e.g., ['cs.AI', 'cs.LG'])
        max_results: Maximum number of papers to fetch

    Returns:
        List of paper dictionaries
    """
    if categories is None:
        categories = ['cs.AI', 'cs.LG', 'cs.CL']

    # Build query for multiple categories
    query = ' OR '.join([f'cat:{cat}' for cat in categories])

    # arXiv API parameters
    params = {
        'search_query': query,
        'start': 0,
        'max_results': max_results,
        'sortBy': 'submittedDate',
        'sortOrder': 'descending'
    }

    url = 'http://export.arxiv.org/api/query?' + urllib.parse.urlencode(params)

    print(f"Fetching papers from arXiv: {query}")

    try:
        with urllib.request.urlopen(url) as response:
            data = response.read().decode('utf-8')

        # Parse XML response
        root = ET.fromstring(data)
        ns = {'atom': 'http://www.w3.org/2005/Atom',
              'arxiv': 'http://arxiv.org/schemas/atom'}

        papers = []
        for entry in root.findall('atom:entry', ns):
            paper_id = entry.find('atom:id', ns).text.split('/')[-1]

            # Extract authors
            authors = [author.find('atom:name', ns).text
                      for author in entry.findall('atom:author', ns)]

            # Extract categories
            cats = [cat.get('term')
                   for cat in entry.findall('atom:category', ns)]

            paper = {
                'id': paper_id,
                'title': entry.find('atom:title', ns).text.strip(),
                'authors': authors[:5],  # Limit to first 5 authors
                'abstract': entry.find('atom:summary', ns).text.strip()[:500] + '...',  # Truncate
                'published': entry.find('atom:published', ns).text,
                'updated': entry.find('atom:updated', ns).text,
                'pdf_url': f"https://arxiv.org/pdf/{paper_id}",
                'abs_url': f"https://arxiv.org/abs/{paper_id}",
                'categories': cats,
                'primary_category': cats[0] if cats else 'Unknown'
            }
            papers.append(paper)

        return papers

    except Exception as e:
        print(f"Error fetching from arXiv: {e}")
        return []


def main():
    """Main execution function"""
    # Track execution
    tracker = ExecutionTracker()

    # Get configuration from environment variables (for workflow_dispatch)
    max_papers = int(os.getenv('ARXIV_MAX_PAPERS', '15'))
    categories_str = os.getenv('ARXIV_CATEGORIES', 'cs.AI,cs.LG,cs.CL')
    categories = [c.strip() for c in categories_str.split(',')]

    print(f"\n📚 arXiv Paper Fetcher")
    print(f"  Configuration:")
    print(f"    Max papers: {max_papers}")
    print(f"    Categories: {', '.join(categories)}")
    print()

    # Load previous fetch state for deduplication
    state = load_fetch_state()
    seen_paper_ids = set(state.get('seen_paper_ids', []))
    last_fetch_time = state.get('last_fetch_time')

    print()

    # Fetch papers from arXiv
    all_papers = fetch_arxiv_papers(categories=categories, max_results=max_papers)

    print()

    # Filter out duplicates and old papers
    papers = filter_duplicate_papers(all_papers, seen_paper_ids, last_fetch_time)

    # If no new papers, we're done
    if len(papers) == 0:
        print("\n✓ No new papers to process")
        print("  All fetched papers were duplicates or already processed")
        print()
    else:
        print(f"\n✓ Agent A completed - {len(papers)} new papers to process")
        print(f"  Categories: {', '.join(categories)}")

    # Finish tracking
    tracker.finish()

    # Calculate costs
    costs = CostCalculator.calculate_total_cost(tracker)

    print(f"  Execution time: {costs['execution_time']:.2f}s")
    print(f"  Estimated cost: ${costs['total']:.6f}")

    # Get current timestamp
    current_timestamp = datetime.utcnow().isoformat()

    # Update fetch state with new papers
    new_paper_ids = {paper['id'] for paper in papers}
    save_fetch_state(current_timestamp, new_paper_ids, state.get('seen_paper_ids', []))

    # Create output
    output = {
        'agent': 'agent-a-paper-fetcher',
        'timestamp': current_timestamp,
        'status': 'completed',
        'data': {
            'papers': papers,
            'count': len(papers),
            'categories': categories,
            'fetch_date': datetime.utcnow().strftime('%Y-%m-%d')
        },
        'metadata': {
            'source': 'arXiv API',
            'query': ' OR '.join([f'cat:{cat}' for cat in categories]),
            'deduplication': {
                'total_fetched': len(all_papers),
                'new_papers': len(papers),
                'duplicates_filtered': len(all_papers) - len(papers),
                'last_fetch': last_fetch_time
            }
        },
        'costs': costs
    }

    # Save output
    save_output_data('data/academic_research/papers.json', output)

    # Write GitHub Actions summary
    summary = SummaryWriter("Agent A - Paper Fetcher", "📄")
    summary.add_header()
    summary.add_metric("Status", "Completed")
    summary.add_metric("New Papers", len(papers))
    summary.add_metric("Duplicates Filtered", len(all_papers) - len(papers))
    summary.add_metric("Categories", ', '.join(categories))
    summary.add_timestamps(tracker)
    summary.add_cost_summary(costs)
    summary.add_execution_logs('agent-a-execution.log')
    summary.write()


if __name__ == '__main__':
    main()
