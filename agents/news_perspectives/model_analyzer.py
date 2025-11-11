"""
Shared Model Analyzer - Base class for AI model analysis

Provides common functionality for analyzing news with different AI models
using GitHub Models API via OpenAI SDK.
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional
from openai import OpenAI

from agents.utils import ExecutionTracker, CostCalculator, SummaryWriter, save_output_data, load_input_data


class ModelAnalyzer:
    """Base class for AI model analyzers"""

    def __init__(self, model_name: str, display_name: str, emoji: str = "🤖"):
        """
        Initialize the analyzer

        Args:
            model_name: Model identifier for the API (e.g., 'openai/gpt-4o', 'xai/grok-3')
            display_name: Human-readable model name (e.g., 'GPT-4o', 'Grok 3')
            emoji: Emoji for the model
        """
        self.model_name = model_name
        self.display_name = display_name
        self.emoji = emoji

        # GitHub Models API endpoint
        github_token = os.getenv('GH_MODELS_TOKEN') or os.getenv('GITHUB_TOKEN')
        if not github_token:
            raise ValueError("GH_MODELS_TOKEN or GITHUB_TOKEN environment variable required")

        print(f"  Initializing OpenAI client for {model_name}")
        print(f"  Token available: {'Yes' if github_token else 'No'}")
        print(f"  Token length: {len(github_token) if github_token else 0}")
        print(f"  Endpoint: https://models.github.ai/inference")

        try:
            self.client = OpenAI(
                base_url="https://models.github.ai/inference",
                api_key=github_token,
            )
            print(f"  ✓ OpenAI client initialized successfully")
        except Exception as e:
            print(f"  ✗ Error initializing client: {e}")
            raise

    def analyze_article(self, article: Dict) -> Dict:
        """
        Analyze a single article and generate AI perspective

        Args:
            article: Article dictionary with title, description, url, source

        Returns:
            Analysis dictionary with perspective, bias_indicators, sentiment, etc.
        """
        prompt = f"""Analyze this news article and provide your perspective. Be opinionated and show your analytical approach.

Title: {article['title']}
Source: {article['source']}
Description: {article['description']}

Provide a JSON response with:
1. "summary": A 2-3 sentence summary of the article from your perspective
2. "key_points": List of 3-5 key points or insights
3. "sentiment": Your overall sentiment (positive/negative/neutral/mixed)
4. "confidence": Your confidence in this analysis (high/medium/low)
5. "bias_check": What potential biases might exist in this story?
6. "missing_context": What important context or perspectives might be missing?
7. "implications": What are the broader implications of this story?

Be honest about uncertainties and limitations. Your response will be compared with other AI models to show different perspectives."""

        try:
            print(f"    Calling API for model {self.model_name}...", flush=True)
            print(f"    Request parameters:", flush=True)
            print(f"      - temperature: 0.7", flush=True)
            print(f"      - max_tokens: 1000", flush=True)
            print(f"      - model: {self.model_name}", flush=True)
            print(f"    Making OpenAI API request...", flush=True)

            import time
            from openai import RateLimitError

            start_time = time.time()
            max_retries = 3
            base_delay = 2

            for attempt in range(max_retries):
                try:
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=[
                            {"role": "system", "content": "You are an analytical AI assistant helping users understand news from multiple perspectives. Be thorough, honest about limitations, and highlight your unique analytical approach."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=1000,
                    )
                    break  # Success, exit retry loop

                except RateLimitError as e:
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)  # Exponential backoff
                        print(f"    ⚠ Rate limit hit, retrying in {delay}s... (attempt {attempt + 1}/{max_retries})", flush=True)
                        time.sleep(delay)
                    else:
                        raise  # Re-raise on final attempt

            elapsed = time.time() - start_time
            print(f"    ✓ API call completed in {elapsed:.2f}s", flush=True)

            content = response.choices[0].message.content

            # Strip markdown code fences if present
            if content.strip().startswith('```'):
                # Remove code fences
                lines = content.strip().split('\n')
                if lines[0].startswith('```'):
                    lines = lines[1:]  # Remove opening fence
                if lines and lines[-1].strip() == '```':
                    lines = lines[:-1]  # Remove closing fence
                content = '\n'.join(lines)

            # Try to parse as JSON, fallback to text
            try:
                analysis = json.loads(content)
            except json.JSONDecodeError:
                # Try to extract just the JSON object if there's extra text after it
                try:
                    # Find the first { and try to parse from there
                    json_start = content.find('{')
                    if json_start >= 0:
                        # Find the matching closing brace by counting braces
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
                            analysis = json.loads(json_content)
                        else:
                            raise json.JSONDecodeError("Could not find complete JSON object", content, 0)
                    else:
                        raise json.JSONDecodeError("No JSON object found", content, 0)
                except json.JSONDecodeError:
                    # If still can't parse, structure the text response
                    analysis = {
                        "summary": content[:300],
                        "key_points": [content],
                        "sentiment": "neutral",
                        "confidence": "medium",
                        "bias_check": "Unable to parse structured response",
                        "missing_context": "",
                        "implications": ""
                    }

            # Add metadata
            analysis['model'] = self.display_name
            analysis['model_id'] = self.model_name
            analysis['analyzed_at'] = datetime.utcnow().isoformat()

            # Token usage
            if hasattr(response, 'usage'):
                analysis['token_usage'] = {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens,
                }

            return analysis

        except Exception as e:
            error_msg = str(e)
            print(f"✗ Error analyzing with {self.display_name}: {error_msg}", flush=True)
            print(f"   Error type: {type(e).__name__}", flush=True)
            if hasattr(e, 'status_code'):
                print(f"   Status code: {e.status_code}", flush=True)
            if hasattr(e, 'message'):
                print(f"   Message: {e.message}", flush=True)

            return {
                'model': self.display_name,
                'model_id': self.model_name,
                'error': error_msg,
                'error_type': type(e).__name__,
                'analyzed_at': datetime.utcnow().isoformat(),
                'summary': f"Analysis failed: {error_msg}",
                'sentiment': 'unknown',
            }

    def analyze_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Analyze multiple articles

        Args:
            articles: List of article dictionaries

        Returns:
            List of analyzed articles with perspectives
        """
        analyzed = []
        total_tokens = {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}

        for i, article in enumerate(articles):
            print(f"  Analyzing article {i+1}/{len(articles)}: {article['title'][:60]}...")
            analysis = self.analyze_article(article)

            # Track token usage
            if 'token_usage' in analysis:
                for key in total_tokens:
                    total_tokens[key] += analysis['token_usage'].get(key, 0)

            analyzed.append({
                'article': article,
                'analysis': analysis,
            })

            # Small delay between articles to avoid rate limits
            if i < len(articles) - 1:  # Don't delay after the last article
                import time
                time.sleep(1)

        return analyzed, total_tokens

    def run(self, input_file: str, output_file: str, agent_id: str):
        """
        Main execution function

        Args:
            input_file: Path to input JSON file with articles
            output_file: Path to output JSON file
            agent_id: Agent identifier for tracking
        """
        print(f"\n{self.emoji} {self.display_name} Analyzer - Starting...")
        print(f"  Input file: {input_file}")
        print(f"  Output file: {output_file}")
        print(f"  Model ID: {self.model_name}")

        # Track execution
        tracker = ExecutionTracker()

        # Load input data
        print(f"  Loading input data from {input_file}...")
        try:
            input_data = load_input_data(input_file)
            articles = input_data.get('data', {}).get('articles', [])
            print(f"  ✓ Loaded {len(articles)} articles")
        except Exception as e:
            print(f"  ✗ Error loading input data: {e}")
            raise

        print(f"\n{self.emoji} {self.display_name} Analyzer")
        print(f"  Articles to analyze: {len(articles)}")

        # Analyze articles
        print(f"  Starting analysis...")
        analyzed, token_usage = self.analyze_articles(articles)

        print(f"\n✓ {self.display_name} Analyzer completed - Analyzed {len(analyzed)} articles")

        # Finish tracking
        tracker.finish()

        # Calculate costs
        costs = CostCalculator.calculate_total_cost(tracker, token_usage)

        print(f"  Execution time: {costs['execution_time']:.2f}s")
        print(f"  Tokens used: {token_usage['total_tokens']:,}")
        print(f"  Estimated cost: ${costs['total']:.6f}")

        # Create output
        output = {
            'agent': agent_id,
            'model': self.display_name,
            'model_id': self.model_name,
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'completed',
            'data': {
                'analyses': analyzed,
                'count': len(analyzed),
            },
            'metadata': {
                'model': self.display_name,
                'articles_analyzed': len(analyzed),
            },
            'costs': costs
        }

        # Save output
        save_output_data(output_file, output)

        # Write GitHub Actions summary
        summary = SummaryWriter(f"{self.display_name} Analyzer", self.emoji)
        summary.add_header()
        summary.add_metric("Status", "Completed")
        summary.add_metric("Model", self.display_name)
        summary.add_metric("Articles Analyzed", len(analyzed))
        summary.add_timestamps(tracker)
        summary.add_cost_summary(costs)
        summary.write()
