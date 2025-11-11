"""
Agent D: Market Editorial Digest Writer (John Oliver Style)

Synthesizes market data into an engaging, witty weekly digest.
Smart, accessible, opinionated writing style - John Oliver meets financial journalism.
"""

import json
import os
from datetime import datetime
from typing import Dict, Tuple

from agents.utils import (
    ExecutionTracker,
    CostCalculator,
    SummaryWriter,
    load_input_data,
    save_output_data
)


def generate_editorial_digest(digest_data: Dict) -> Tuple[Dict, Dict]:
    """
    Generate John Oliver-style editorial digest using OpenAI GPT-4o-mini

    Returns:
        Tuple of (editorial_dict, token_usage_dict)
    """
    api_key = os.environ.get('OPENAI_API_KEY')
    token_usage = {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}

    if not api_key:
        print("WARNING: OpenAI API key not found - using mock editorial digest")
        return mock_editorial_digest(digest_data), token_usage

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        # Build the editorial prompt
        prompt = build_editorial_prompt(digest_data)

        system_prompt = (
            "You're a market blogger with personality. Be smart, funny, and honest. "
            "Make finance accessible without dumbing it down. Channel John Oliver's wit applied to markets. "
            "Always respond with valid JSON only - no markdown, no code blocks, no extra text."
        )

        print("📝 Generating John Oliver-style market digest...")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.9,  # Higher for creativity and personality
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )

        raw_text = response.choices[0].message.content
        token_usage = {
            'prompt_tokens': response.usage.prompt_tokens,
            'completion_tokens': response.usage.completion_tokens,
            'total_tokens': response.usage.total_tokens
        }

        # Clean up the response - remove markdown code blocks if present
        cleaned_text = raw_text.strip()
        if cleaned_text.startswith("```"):
            # Remove markdown code blocks
            lines = cleaned_text.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            cleaned_text = "\n".join(lines).strip()

        # Parse JSON
        editorial_data = json.loads(cleaned_text)

        print(f"✅ Editorial digest generated")
        return editorial_data, token_usage

    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse AI response as JSON: {e}")
        print(f"Raw response: {raw_text[:500]}...")
        return mock_editorial_digest(digest_data), token_usage
    except Exception as e:
        print(f"❌ Error generating editorial digest: {e}")
        return mock_editorial_digest(digest_data), token_usage


def build_editorial_prompt(digest_data: Dict) -> str:
    """Build the prompt for the AI to generate the editorial digest."""
    prompt = "You're writing a WEEKLY MARKET DIGEST blog post for a broad audience.\n\n"

    prompt += "Your tone: Smart, witty, accessible. Strong opinions on market behavior. Make financial concepts understandable.\n"
    prompt += "Don't dumb things down, but don't gatekeep either.\n\n"

    prompt += "IMPORTANT OUTPUT RULES:\n"
    prompt += "- You MUST output ONLY valid JSON. No markdown, no code blocks, no extra text.\n"
    prompt += "- Start your response with { and end with }\n"
    prompt += "- Use proper JSON escaping for quotes and special characters\n\n"

    prompt += "MARKET DATA YOU'RE WORKING WITH:\n\n"

    # Add crypto section
    if "crypto_section" in digest_data and digest_data["crypto_section"].get("items"):
        prompt += "CRYPTOCURRENCY MARKETS:\n"
        for item in digest_data["crypto_section"]["items"]:
            prompt += f"- {item['name']} ({item['symbol']}): ${item['price']:,.2f} "
            prompt += f"({item['change_24h']:+.2f}%, {item['change_7d']:+.2f}% weekly)\n"
            prompt += f"  Market Cap: ${item['market_cap']:,.0f}, Volume: ${item['volume_24h']:,.0f}\n"
        prompt += f"\nCrypto Analysis: {digest_data['crypto_section'].get('analysis', 'No analysis')}\n\n"

    # Add stocks section
    if "stocks_section" in digest_data and digest_data["stocks_section"].get("items"):
        prompt += "STOCK MARKETS:\n"
        for item in digest_data["stocks_section"]["items"]:
            prompt += f"- {item['name']} ({item['symbol']}): ${item['price']:,.2f} "
            prompt += f"({item['change_percent']:+.2f}%)\n"
        prompt += f"\nStock Analysis: {digest_data['stocks_section'].get('analysis', 'No analysis')}\n\n"

    # Add highlights
    if "highlights" in digest_data:
        highlights = digest_data["highlights"]
        prompt += "KEY HIGHLIGHTS:\n"
        if "biggest_crypto_mover" in highlights:
            mover = highlights["biggest_crypto_mover"]
            prompt += f"- Biggest Crypto Mover: {mover['name']} ({mover['change']:+.2f}%)\n"
        if "biggest_stock_mover" in highlights:
            mover = highlights["biggest_stock_mover"]
            prompt += f"- Biggest Stock Mover: {mover['name']} ({mover['change']:+.2f}%)\n"
        if "market_leader" in highlights:
            leader = highlights["market_leader"]
            prompt += f"- Market Leader: {leader['name']} ({leader['category']})\n"
        prompt += "\n"

    # Add overall summary if available
    if "summary" in digest_data:
        summary = digest_data["summary"]
        if "headline" in summary:
            prompt += f"Overall Market Headline: {summary['headline']}\n"
        if "content" in summary:
            prompt += f"Summary: {summary['content']}\n"
        prompt += "\n"

    prompt += "YOUR TASK:\n"
    prompt += "Write an engaging, witty market digest that:\n"
    prompt += "1. Groups market movements into 2-4 thematic sections (e.g., 'Tech Takes a Hit', 'Crypto Does Its Thing', 'The Everything Rally')\n"
    prompt += "2. Connects the dots between different market movements\n"
    prompt += "3. Adds personality and hot takes on market behavior\n"
    prompt += "4. Makes financial jargon accessible without being condescending\n"
    prompt += "5. Comments on the irony, absurdity, or predictability of market movements\n\n"

    prompt += "OUTPUT FORMAT (VALID JSON ONLY):\n"
    prompt += "{\n"
    prompt += '  "title": "Catchy title with personality (e.g., \'This Week in Markets: Bitcoin Does Bitcoin Things\')",\n'
    prompt += '  "subtitle": "Witty one-liner about the week\'s theme",\n'
    prompt += '  "intro": "2-3 sentences setting the vibe and introducing the week\'s patterns",\n'
    prompt += '  "sections": [\n'
    prompt += "    {\n"
    prompt += '      "title": "Thematic section name with personality",\n'
    prompt += '      "assets": ["List", "of", "relevant", "assets", "in", "this", "theme"],\n'
    prompt += '      "commentary": "2-3 sentences with personality connecting these movements. Be witty but insightful."\n'
    prompt += "    }\n"
    prompt += "  ],\n"
    prompt += '  "editors_pick": {\n'
    prompt += '    "asset": "Name and symbol of most interesting movement",\n'
    prompt += '    "reason": "Why this is fascinating/absurd/predictable. 2-3 sentences with personality."\n'
    prompt += "  },\n"
    prompt += '  "parting_thoughts": "Closing thoughts on the week. What\'s the theme? What should we watch? 2-3 sentences."\n'
    prompt += "}\n\n"

    prompt += "Remember: Output ONLY the JSON. No markdown formatting. No code blocks. Just pure JSON starting with { and ending with }."

    return prompt


def mock_editorial_digest(digest_data: Dict) -> Dict:
    """Generate a mock editorial digest when OpenAI is not available."""
    return {
        "title": "This Week in Markets: A Tale of Two Volatilities",
        "subtitle": "Crypto gonna crypto, stocks gonna stock",
        "intro": "This week, the markets decided to remind us all that predictability is for the weak. Cryptocurrencies did their usual chaotic dance while traditional stocks played it relatively cool, proving once again that we live in the weirdest financial timeline.",
        "sections": [
            {
                "title": "Crypto's Usual Chaos",
                "assets": ["Bitcoin", "Ethereum", "Top Cryptocurrencies"],
                "commentary": "Cryptocurrencies continued their time-honored tradition of moving in ways that make absolutely no sense to anyone outside (and let's be honest, inside) the crypto space. Whether it's up, down, or sideways, there's always someone on Twitter claiming they predicted it all along."
            },
            {
                "title": "Traditional Markets Play It Cool(ish)",
                "assets": ["S&P 500", "NASDAQ", "Major Indices"],
                "commentary": "Meanwhile, in the land of grown-up money, traditional stocks had a relatively normal week. Sure, there were fluctuations, but nothing that made Jim Cramer cry on TV, so we're calling it a win."
            }
        ],
        "editors_pick": {
            "asset": "Bitcoin (BTC)",
            "reason": "Because it's Bitcoin. It's always Bitcoin. Whether it's mooning or tanking, BTC remains the honey badger of financial assets—it doesn't care what you think, and it's definitely not taking questions."
        },
        "parting_thoughts": "The markets continue to remind us that they're equal parts economic indicator and chaos engine. Keep your portfolios diversified, your expectations measured, and your sense of humor intact. We'll be back next week with more financial absurdity."
    }


def main():
    """Main execution flow."""
    tracker = ExecutionTracker()

    print("\n" + "="*60)
    print("🎭 Market Editorial Digest Writer (John Oliver Style)")
    print("="*60)

    try:
        # Load market digest
        digest_data = load_input_data('data/market_analysis/digest.json')

        if not digest_data:
            print("❌ Cannot proceed without market digest data")
            return

        # Generate editorial digest
        editorial_data, token_usage = generate_editorial_digest(digest_data)

        # Add metadata
        editorial_data["metadata"] = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "style": "john-oliver-markets",
            "model": "gpt-4o-mini",
            "token_usage": token_usage
        }

        # Save editorial digest
        save_output_data('data/market_analysis/editorial_digest.json', editorial_data)

        # Calculate costs
        tracker.finish()
        costs = CostCalculator.calculate_total_cost(tracker, token_usage)

        # Write summary
        summary = SummaryWriter("Market Editorial Digest Writer", "🎭")
        summary.add_header()
        summary.add_metric("Status", "Completed")
        summary.add_metric("Title", editorial_data.get('title', 'N/A'))
        summary.add_metric("Sections", len(editorial_data.get('sections', [])))
        summary.add_metric("Editor's Pick", editorial_data.get('editors_pick', {}).get('asset', 'N/A'))
        summary.add_metric("Model", "GPT-4o-mini (OpenAI)")
        summary.add_timestamps(tracker)
        summary.add_cost_summary(costs)
        summary.write()

        print("\n✅ Market editorial digest generation complete!")
        print(f"📊 Title: {editorial_data.get('title', 'N/A')}")
        print(f"📝 Sections: {len(editorial_data.get('sections', []))}")
        print(f"⭐ Editor's Pick: {editorial_data.get('editors_pick', {}).get('asset', 'N/A')}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
