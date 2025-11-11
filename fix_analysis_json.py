#!/usr/bin/env python3
"""
Fix analysis JSON files where the proper JSON is stuffed into key_points[0]
"""

import json
import os

def extract_json_from_string(content):
    """Extract JSON object from a string that may have extra text"""
    # Strip markdown code fences and **JSON Response** prefix
    content = content.strip()

    # Remove **JSON Response** prefix if present
    if content.startswith('**JSON Response'):
        lines = content.split('\n')
        # Skip lines until we hit code fence or JSON
        start_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('```') or line.strip().startswith('{'):
                start_idx = i
                break
        content = '\n'.join(lines[start_idx:])

    # Remove code fences
    if content.startswith('```'):
        lines = content.split('\n')
        if lines[0].startswith('```'):
            lines = lines[1:]
        if lines and lines[-1].strip() == '```':
            lines = lines[:-1]
        content = '\n'.join(lines)

    # Find the first { and matching }
    json_start = content.find('{')
    if json_start >= 0:
        brace_count = 0
        json_end = -1
        for i in range(json_start, len(content)):
            if content[i] == '{':
                brace_count += 1
            elif content[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    json_end = i + 1
                    break

        if json_end > json_start:
            json_content = content[json_start:json_end]
            try:
                return json.loads(json_content)
            except json.JSONDecodeError:
                pass

    return None

def fix_analysis_file(filepath):
    """Fix an analysis JSON file"""
    print(f"Processing {filepath}...")

    with open(filepath, 'r') as f:
        data = json.load(f)

    fixed_count = 0
    for item in data['data']['analyses']:
        if 'analysis' in item:
            analysis = item['analysis']

            # Check if this looks like a broken analysis
            # (summary starts with { or **JSON Response, key_points has the full JSON)
            summary_start = analysis.get('summary', '').strip()
            if ('summary' in analysis and
                (summary_start.startswith('{') or summary_start.startswith('**JSON Response')) and
                'key_points' in analysis and
                len(analysis['key_points']) > 0):

                # Try to extract proper JSON from key_points[0]
                raw_content = analysis['key_points'][0]
                parsed = extract_json_from_string(raw_content)

                if parsed and 'summary' in parsed:
                    # Replace with properly parsed fields
                    item['analysis'] = {
                        'summary': parsed.get('summary', ''),
                        'key_points': parsed.get('key_points', []),
                        'sentiment': parsed.get('sentiment', 'neutral'),
                        'confidence': parsed.get('confidence', 'medium'),
                        'bias_check': parsed.get('bias_check', ''),
                        'missing_context': parsed.get('missing_context', ''),
                        'implications': parsed.get('implications', ''),
                        # Preserve metadata
                        'model': analysis.get('model', ''),
                        'model_id': analysis.get('model_id', ''),
                        'analyzed_at': analysis.get('analyzed_at', ''),
                    }

                    # Preserve token_usage if present
                    if 'token_usage' in analysis:
                        item['analysis']['token_usage'] = analysis['token_usage']

                    fixed_count += 1
                    print(f"  ✓ Fixed article: {item['article']['title'][:60]}...")

    if fixed_count > 0:
        # Write back the fixed data
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"  Saved {fixed_count} fixes to {filepath}")
    else:
        print(f"  No fixes needed for {filepath}")

    return fixed_count

def main():
    data_dir = 'data/news_perspectives'

    files_to_fix = [
        f'{data_dir}/gpt_mini_analysis.json',
        f'{data_dir}/llama_small_analysis.json',
        f'{data_dir}/phi_analysis.json',
        f'{data_dir}/mistral_analysis.json',
    ]

    total_fixed = 0
    for filepath in files_to_fix:
        if os.path.exists(filepath):
            total_fixed += fix_analysis_file(filepath)
        else:
            print(f"Skipping {filepath} (not found)")

    print(f"\n✅ Total articles fixed: {total_fixed}")

if __name__ == '__main__':
    main()
