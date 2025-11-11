"""
Shared utilities for AI agents
"""

import os
import time
from datetime import datetime
from typing import Dict, Optional, Any


class ExecutionTracker:
    """Track agent execution time and timestamps"""

    def __init__(self):
        self.start_time = time.time()
        self.start_timestamp = datetime.utcnow()
        self.end_time = None
        self.end_timestamp = None

    def finish(self):
        """Mark execution as finished"""
        self.end_time = time.time()
        self.end_timestamp = datetime.utcnow()

    def get_duration(self) -> float:
        """Get execution duration in seconds"""
        if self.end_time is None:
            return time.time() - self.start_time
        return self.end_time - self.start_time

    def get_duration_minutes(self) -> float:
        """Get execution duration in minutes"""
        return self.get_duration() / 60


class CostCalculator:
    """Calculate costs for agent execution"""

    # Pricing constants
    GITHUB_ACTIONS_COST_PER_MINUTE = 0.008  # For private repos
    OPENAI_INPUT_COST_PER_1M = 0.150  # GPT-4o-mini
    OPENAI_OUTPUT_COST_PER_1M = 0.600  # GPT-4o-mini

    @staticmethod
    def calculate_github_cost(execution_minutes: float) -> float:
        """Calculate GitHub Actions cost"""
        return execution_minutes * CostCalculator.GITHUB_ACTIONS_COST_PER_MINUTE

    @staticmethod
    def calculate_openai_cost(token_usage: Optional[Dict[str, int]] = None) -> Dict[str, float]:
        """Calculate OpenAI API costs"""
        if not token_usage:
            return {'input': 0, 'output': 0, 'total': 0}

        input_cost = (token_usage.get('prompt_tokens', 0) / 1_000_000) * CostCalculator.OPENAI_INPUT_COST_PER_1M
        output_cost = (token_usage.get('completion_tokens', 0) / 1_000_000) * CostCalculator.OPENAI_OUTPUT_COST_PER_1M

        return {
            'input': input_cost,
            'output': output_cost,
            'total': input_cost + output_cost
        }

    @staticmethod
    def calculate_total_cost(tracker: ExecutionTracker, token_usage: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
        """Calculate total costs for an agent run"""
        execution_minutes = tracker.get_duration_minutes()
        github_cost = CostCalculator.calculate_github_cost(execution_minutes)
        openai_costs = CostCalculator.calculate_openai_cost(token_usage)

        return {
            'execution_time': tracker.get_duration(),
            'execution_minutes': execution_minutes,
            'github_actions': github_cost,
            'openai': openai_costs,
            'total': github_cost + openai_costs['total'],
            'token_usage': token_usage or {}
        }


class SummaryWriter:
    """Write standardized GitHub Actions summaries"""

    def __init__(self, title: str, emoji: str = "🤖"):
        self.title = title
        self.emoji = emoji
        self.summary_lines = []

    def add_header(self):
        """Add header to summary"""
        self.summary_lines.append(f"## {self.emoji} {self.title}\n\n")

    def add_metric(self, label: str, value: Any):
        """Add a metric line"""
        self.summary_lines.append(f"**{label}:** {value}\n\n")

    def add_timestamps(self, tracker: ExecutionTracker):
        """Add start/end timestamps"""
        self.add_metric("Started", tracker.start_timestamp.strftime('%Y-%m-%d %H:%M:%S') + " UTC")
        if tracker.end_timestamp:
            self.add_metric("Ended", tracker.end_timestamp.strftime('%Y-%m-%d %H:%M:%S') + " UTC")

    def add_cost_summary(self, costs: Dict[str, Any]):
        """Add cost summary (total displayed, details collapsible)"""
        self.add_metric("Total Cost", f"${costs['total']:.6f}")

        # Cost breakdown (collapsible)
        self.summary_lines.append("<details>\n")
        self.summary_lines.append("<summary>💰 Cost Breakdown</summary>\n\n")
        self.summary_lines.append(f"**Execution Time:** {costs['execution_time']:.2f}s ({costs['execution_minutes']:.4f} minutes)\n\n")

        if costs['token_usage']:
            token_usage = costs['token_usage']
            self.summary_lines.append(f"**Token Usage:** {token_usage.get('total_tokens', 0):,} tokens\n")
            self.summary_lines.append(f"  - Input: {token_usage.get('prompt_tokens', 0):,} tokens\n")
            self.summary_lines.append(f"  - Output: {token_usage.get('completion_tokens', 0):,} tokens\n\n")

        self.summary_lines.append(f"**GitHub Actions:** ${costs['github_actions']:.6f}\n\n")

        if costs['openai']['total'] > 0:
            self.summary_lines.append(f"**OpenAI API:** ${costs['openai']['total']:.6f}\n")
            self.summary_lines.append(f"  - Input cost: ${costs['openai']['input']:.6f}\n")
            self.summary_lines.append(f"  - Output cost: ${costs['openai']['output']:.6f}\n\n")
            self.summary_lines.append("_Note: GitHub Actions is free for public repos. OpenAI pricing: $0.150/1M input tokens, $0.600/1M output tokens_\n\n")
        else:
            self.summary_lines.append("_Note: GitHub Actions is free for public repos, $0.008/min for private repos_\n\n")

        self.summary_lines.append("</details>\n\n")

    def add_execution_logs(self, log_file: str):
        """Add execution logs (collapsible)"""
        self.summary_lines.append("<details>\n")
        self.summary_lines.append("<summary>📋 Execution Logs</summary>\n\n")
        self.summary_lines.append("```\n")
        try:
            with open(log_file, 'r') as f:
                self.summary_lines.append(f.read())
        except FileNotFoundError:
            self.summary_lines.append("No execution logs available\n")
        self.summary_lines.append("\n```\n\n")
        self.summary_lines.append("</details>\n")

    def write(self):
        """Write summary to GitHub Actions"""
        summary_file = os.environ.get('GITHUB_STEP_SUMMARY')
        if summary_file:
            with open(summary_file, 'a') as f:
                f.writelines(self.summary_lines)
            print("✓ Successfully wrote summary to GitHub Actions")
        else:
            print("WARNING: GITHUB_STEP_SUMMARY not found, skipping summary")


def load_input_data(input_file: str) -> Dict[str, Any]:
    """Load input data from a JSON file"""
    import json

    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
        print(f"✓ Loaded input from {input_file}")
        return data
    except FileNotFoundError:
        print(f"✗ Input file not found: {input_file}")
        raise


def save_output_data(output_file: str, data: Dict[str, Any]):
    """Save output data to a JSON file"""
    import json
    import os

    # Ensure directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"✓ Saved output to {output_file}")
