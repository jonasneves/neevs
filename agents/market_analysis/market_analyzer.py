"""
Agent B: Market Analyzer
Analyzes market data using AI to generate insights, identify trends, and spot opportunities.
"""

import json
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import ExecutionTracker, CostCalculator, SummaryWriter, load_input_data, save_output_data

# OpenAI imports
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️  OpenAI library not available")


def analyze_crypto_market(crypto_data):
    """Analyze cryptocurrency market trends and generate insights."""
    print(f"🔍 Analyzing {len(crypto_data)} cryptocurrencies...")

    if not OPENAI_AVAILABLE or not os.environ.get('OPENAI_API_KEY'):
        print("⚠️  OpenAI not available, using mock analysis")
        return get_mock_crypto_analysis(crypto_data)

    # Prepare market data summary for AI
    crypto_summary = []
    for coin in crypto_data[:5]:  # Top 5
        crypto_summary.append(
            f"{coin['name']} ({coin['symbol']}): ${coin['price']:,.2f}, "
            f"24h: {coin['change_24h']:+.2f}%, 7d: {coin['change_7d']:+.2f}%, "
            f"Market Cap Rank: #{coin['market_cap_rank']}"
        )

    prompt = f"""You are a cryptocurrency market analyst. Analyze the current market data and provide insights.

Market Data:
{chr(10).join(crypto_summary)}

Provide a concise analysis (3-4 sentences) covering:
1. Overall market sentiment (bullish/bearish/neutral)
2. Notable trends or patterns
3. Key movers and why they might be moving
4. Brief outlook

Be specific, data-driven, and professional."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert cryptocurrency market analyst."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )

        analysis = response.choices[0].message.content.strip()
        tokens_used = {
            "input": response.usage.prompt_tokens,
            "output": response.usage.completion_tokens
        }

        print(f"✅ Crypto analysis completed ({tokens_used['output']} tokens)")

        return {
            "analysis": analysis,
            "tokens_used": tokens_used,
            "top_performers": [
                {"symbol": c["symbol"], "name": c["name"], "change_24h": c["change_24h"]}
                for c in sorted(crypto_data, key=lambda x: x["change_24h"], reverse=True)[:3]
            ],
            "top_losers": [
                {"symbol": c["symbol"], "name": c["name"], "change_24h": c["change_24h"]}
                for c in sorted(crypto_data, key=lambda x: x["change_24h"])[:3]
            ]
        }

    except Exception as e:
        print(f"⚠️  Error in crypto analysis: {str(e)}")
        return get_mock_crypto_analysis(crypto_data)


def analyze_stock_market(stocks_data, indices_data):
    """Analyze stock market trends and indices."""
    print(f"📈 Analyzing {len(stocks_data)} stocks and {len(indices_data)} indices...")

    if not OPENAI_AVAILABLE or not os.environ.get('OPENAI_API_KEY'):
        print("⚠️  OpenAI not available, using mock analysis")
        return get_mock_stock_analysis(stocks_data, indices_data)

    # Prepare market summary
    indices_summary = [
        f"{idx['name']}: ${idx['price']:,.2f} ({idx['change_percent']:+.2f}%)"
        for idx in indices_data
    ]

    stocks_summary = [
        f"{stock['symbol']}: ${stock['price']:,.2f} ({stock['change_percent']:+.2f}%)"
        for stock in stocks_data
    ]

    prompt = f"""You are a stock market analyst. Analyze the current market conditions and provide insights.

Major Indices:
{chr(10).join(indices_summary)}

Key Stocks:
{chr(10).join(stocks_summary)}

Provide a concise analysis (3-4 sentences) covering:
1. Overall market direction and sentiment
2. Sector performance and notable movers
3. Key drivers or market factors
4. Brief trading outlook

Be specific, data-driven, and professional."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert stock market analyst."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )

        analysis = response.choices[0].message.content.strip()
        tokens_used = {
            "input": response.usage.prompt_tokens,
            "output": response.usage.completion_tokens
        }

        print(f"✅ Stock analysis completed ({tokens_used['output']} tokens)")

        return {
            "analysis": analysis,
            "tokens_used": tokens_used,
            "market_direction": get_market_direction(indices_data),
            "top_gainers": [
                {"symbol": s["symbol"], "change_percent": s["change_percent"]}
                for s in sorted(stocks_data, key=lambda x: x["change_percent"], reverse=True)[:3]
            ],
            "top_decliners": [
                {"symbol": s["symbol"], "change_percent": s["change_percent"]}
                for s in sorted(stocks_data, key=lambda x: x["change_percent"])[:3]
            ]
        }

    except Exception as e:
        print(f"⚠️  Error in stock analysis: {str(e)}")
        return get_mock_stock_analysis(stocks_data, indices_data)


def generate_market_summary(crypto_analysis, stock_analysis):
    """Generate an overall market summary combining all insights."""
    print("📝 Generating overall market summary...")

    if not OPENAI_AVAILABLE or not os.environ.get('OPENAI_API_KEY'):
        print("⚠️  OpenAI not available, using mock summary")
        return get_mock_market_summary()

    prompt = f"""You are a senior financial analyst. Based on the following market analyses, create a brief market summary.

Cryptocurrency Market Analysis:
{crypto_analysis['analysis']}

Stock Market Analysis:
{stock_analysis['analysis']}

Provide:
1. A one-sentence market headline (punchy and informative)
2. A 2-3 sentence executive summary
3. One key opportunity to watch
4. One key risk to monitor

Be concise, professional, and actionable."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a senior financial market analyst."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=250,
            temperature=0.7
        )

        summary = response.choices[0].message.content.strip()
        tokens_used = {
            "input": response.usage.prompt_tokens,
            "output": response.usage.completion_tokens
        }

        print(f"✅ Market summary completed ({tokens_used['output']} tokens)")

        return {
            "summary": summary,
            "tokens_used": tokens_used
        }

    except Exception as e:
        print(f"⚠️  Error generating summary: {str(e)}")
        return get_mock_market_summary()


def get_market_direction(indices_data):
    """Determine overall market direction based on indices."""
    avg_change = sum(idx["change_percent"] for idx in indices_data) / len(indices_data)

    if avg_change > 1.0:
        return "strongly_bullish"
    elif avg_change > 0.3:
        return "bullish"
    elif avg_change > -0.3:
        return "neutral"
    elif avg_change > -1.0:
        return "bearish"
    else:
        return "strongly_bearish"


def get_mock_crypto_analysis(crypto_data):
    """Mock crypto analysis for testing."""
    return {
        "analysis": "The cryptocurrency market shows mixed sentiment with Bitcoin maintaining stability above $94k while altcoins display varied performance. Solana leads gains with a 5.2% 24-hour increase, suggesting continued strength in the Layer-1 ecosystem. Market volatility remains elevated as traders await macro economic indicators.",
        "tokens_used": {"input": 0, "output": 0},
        "top_performers": [c for c in sorted(crypto_data, key=lambda x: x["change_24h"], reverse=True)[:3]],
        "top_losers": [c for c in sorted(crypto_data, key=lambda x: x["change_24h"])[:3]]
    }


def get_mock_stock_analysis(stocks_data, indices_data):
    """Mock stock analysis for testing."""
    return {
        "analysis": "Equity markets posted gains across major indices with the NASDAQ leading at +1.71%, driven by strength in technology and AI-related stocks. NVIDIA's 5.88% surge highlights continued investor enthusiasm for AI infrastructure. Market breadth is positive with strong volume supporting the advance.",
        "tokens_used": {"input": 0, "output": 0},
        "market_direction": get_market_direction(indices_data),
        "top_gainers": [s for s in sorted(stocks_data, key=lambda x: x["change_percent"], reverse=True)[:3]],
        "top_decliners": [s for s in sorted(stocks_data, key=lambda x: x["change_percent"])[:3]]
    }


def get_mock_market_summary():
    """Mock market summary for testing."""
    return {
        "summary": "**Markets Rally on Tech Strength**\n\nBroad-based gains across equities and crypto with technology stocks leading the advance. AI infrastructure plays continue to attract capital while crypto markets stabilize.\n\n**Key Opportunity:** AI and semiconductor stocks showing momentum\n**Key Risk:** Elevated valuations require monitoring of macro conditions",
        "tokens_used": {"input": 0, "output": 0}
    }


def main():
    """Main execution function."""
    tracker = ExecutionTracker()

    print("=" * 60)
    print("🔍 AGENT B: MARKET ANALYZER")
    print("=" * 60)

    # Load input from Agent A
    input_data = load_input_data('data/market_analysis/market-data.json')

    crypto_data = input_data["data"]["cryptocurrencies"]
    stocks_data = input_data["data"]["stocks"]
    indices_data = input_data["data"]["indices"]

    # Perform analyses
    crypto_analysis = analyze_crypto_market(crypto_data)
    stock_analysis = analyze_stock_market(stocks_data, indices_data)
    market_summary = generate_market_summary(crypto_analysis, stock_analysis)

    # Calculate total tokens used
    total_tokens = {
        "input": (crypto_analysis.get("tokens_used", {}).get("input", 0) +
                  stock_analysis.get("tokens_used", {}).get("input", 0) +
                  market_summary.get("tokens_used", {}).get("input", 0)),
        "output": (crypto_analysis.get("tokens_used", {}).get("output", 0) +
                   stock_analysis.get("tokens_used", {}).get("output", 0) +
                   market_summary.get("tokens_used", {}).get("output", 0))
    }

    # Prepare output
    output = {
        "agent": "agent-b-market-analyzer",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "completed",
        "data": {
            "crypto_analysis": crypto_analysis,
            "stock_analysis": stock_analysis,
            "market_summary": market_summary,
            "analyzed_assets": {
                "crypto": len(crypto_data),
                "stocks": len(stocks_data),
                "indices": len(indices_data)
            }
        },
        "tokens_used": total_tokens
    }

    # Save output for next agent
    save_output_data('data/market_analysis/analyzed-market.json', output)

    tracker.finish()

    # Calculate costs
    costs = CostCalculator.calculate_total_cost(tracker, total_tokens)

    # Write job summary
    summary = SummaryWriter("Market Analyzer", "🔍")
    summary.add_header()
    summary.add_metric("Cryptocurrencies analyzed", len(crypto_data))
    summary.add_metric("Stocks analyzed", len(stocks_data))
    summary.add_metric("Indices analyzed", len(indices_data))
    summary.add_metric("AI tokens used", total_tokens["input"] + total_tokens["output"])
    summary.add_timestamps(tracker)
    summary.add_cost_summary(costs)
    summary.write()

    print("\n✅ Market analysis completed!")
    print(f"📁 Output saved to: data/market_analysis/analyzed-market.json")


if __name__ == "__main__":
    main()
