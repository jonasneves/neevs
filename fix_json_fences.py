#!/usr/bin/env python3
"""
Fix JSON responses that have markdown code fences
"""
import json
import sys

def strip_code_fences(content):
    """Strip markdown code fences from content and extract JSON only"""
    content = content.strip()

    # Find where the code fence starts
    lines = content.split('\n')
    start_idx = 0

    for i, line in enumerate(lines):
        if line.strip().startswith('```'):
            start_idx = i + 1  # Start after the opening fence
            break

    # Find the closing fence
    closing_fence_idx = -1
    for i in range(start_idx, len(lines)):
        if lines[i].strip() == '```':
            closing_fence_idx = i
            break

    if closing_fence_idx >= 0:
        lines = lines[start_idx:closing_fence_idx]  # Extract content between fences
    elif start_idx > 0:
        lines = lines[start_idx:]  # No closing fence found, take everything after opening

    content = '\n'.join(lines)
    return content

def fix_analysis_file(filepath):
    """Fix an analysis JSON file"""
    print(f"Processing {filepath}...")

    with open(filepath, 'r') as f:
        data = json.load(f)

    fixed_count = 0

    # Fix each analysis in the data
    if 'data' in data and 'analyses' in data['data']:
        for item in data['data']['analyses']:
            if 'analysis' in item:
                analysis = item['analysis']

                # Check if summary looks like raw JSON (truncated or with markdown)
                summary = analysis.get('summary', '').strip()
                if summary.startswith('```') or '```json' in summary[:100]:
                    # The full JSON is in key_points[0]
                    if 'key_points' in analysis and len(analysis['key_points']) > 0:
                        raw_json = strip_code_fences(analysis['key_points'][0])
                        try:
                            parsed = json.loads(raw_json)
                            # Update with parsed values
                            item['analysis'] = parsed
                            fixed_count += 1
                            print(f"  ✓ Fixed 1 analysis")
                        except json.JSONDecodeError as e:
                            print(f"  ✗ Failed to parse JSON: {e}")
                            print(f"    Content: {raw_json[:200]}")
                    else:
                        print(f"  ✗ No key_points found to extract from")

    if fixed_count > 0:
        # Write back
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"  💾 Saved {filepath} with {fixed_count} fixes\n")
    else:
        print(f"  ℹ️  No fixes needed\n")

if __name__ == '__main__':
    files = [
        'data/news_perspectives/gpt_mini_analysis.json',
        'data/news_perspectives/llama_small_analysis.json',
        'data/news_perspectives/phi_analysis.json',
        'data/news_perspectives/mistral_analysis.json',
    ]

    for filepath in files:
        try:
            fix_analysis_file(filepath)
        except Exception as e:
            print(f"  ✗ Error: {e}\n")
