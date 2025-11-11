"""
Agent C: Market Digest Writer
Creates a comprehensive, beautifully formatted market digest combining all analysis.
"""

import json
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import ExecutionTracker, CostCalculator, SummaryWriter, load_input_data, save_output_data


def format_currency(amount):
    """Format number as currency."""
    if amount >= 1_000_000_000_000:  # Trillions
        return f"${amount / 1_000_000_000_000:.2f}T"
    elif amount >= 1_000_000_000:  # Billions
        return f"${amount / 1_000_000_000:.2f}B"
    elif amount >= 1_000_000:  # Millions
        return f"${amount / 1_000_000:.2f}M"
    elif amount >= 1_000:  # Thousands
        return f"${amount / 1_000:.2f}K"
    else:
        return f"${amount:.2f}"


def format_percent(value):
    """Format percentage with color indicator."""
    return f"{value:+.2f}%"


def create_crypto_section(crypto_data, crypto_analysis):
    """Create cryptocurrency section of the digest."""
    print("📊 Creating crypto section...")

    crypto_items = []
    for coin in crypto_data[:5]:  # Top 5
        crypto_items.append({
            "symbol": coin["symbol"],
            "name": coin["name"],
            "price": coin["price"],
            "price_formatted": f"${coin['price']:,.2f}" if coin['price'] >= 1 else f"${coin['price']:.4f}",
            "market_cap": coin["market_cap"],
            "market_cap_formatted": format_currency(coin["market_cap"]),
            "change_24h": coin["change_24h"],
            "change_24h_formatted": format_percent(coin["change_24h"]),
            "change_7d": coin["change_7d"],
            "change_7d_formatted": format_percent(coin["change_7d"]),
            "rank": coin["market_cap_rank"],
            "image": coin.get("image", ""),
            "is_gaining": coin["change_24h"] > 0
        })

    return {
        "title": "💎 Cryptocurrency Market",
        "items": crypto_items,
        "analysis": crypto_analysis["analysis"],
        "top_performers": crypto_analysis.get("top_performers", []),
        "top_losers": crypto_analysis.get("top_losers", [])
    }


def create_stocks_section(stocks_data, indices_data, stock_analysis):
    """Create stocks and indices section of the digest."""
    print("📈 Creating stocks section...")

    # Format indices
    indices_items = []
    for idx in indices_data:
        indices_items.append({
            "symbol": idx["symbol"],
            "name": idx["name"],
            "price": idx["price"],
            "price_formatted": f"${idx['price']:,.2f}",
            "change": idx["change"],
            "change_formatted": f"{idx['change']:+.2f}",
            "change_percent": idx["change_percent"],
            "change_percent_formatted": format_percent(idx["change_percent"]),
            "is_gaining": idx["change_percent"] > 0
        })

    # Format stocks
    stock_items = []
    for stock in stocks_data:
        stock_items.append({
            "symbol": stock["symbol"],
            "price": stock["price"],
            "price_formatted": f"${stock['price']:,.2f}",
            "change": stock["change"],
            "change_formatted": f"{stock['change']:+.2f}",
            "change_percent": stock["change_percent"],
            "change_percent_formatted": format_percent(stock["change_percent"]),
            "volume": stock["volume"],
            "volume_formatted": format_currency(stock["volume"]),
            "is_gaining": stock["change_percent"] > 0
        })

    return {
        "title": "📊 Stock Market",
        "indices": indices_items,
        "stocks": stock_items,
        "analysis": stock_analysis["analysis"],
        "market_direction": stock_analysis.get("market_direction", "neutral"),
        "top_gainers": stock_analysis.get("top_gainers", []),
        "top_decliners": stock_analysis.get("top_decliners", [])
    }


def create_digest(market_data, analyzed_data, market_summary):
    """Create the complete market digest."""
    print("📝 Assembling market digest...")

    # Extract data
    crypto_data = market_data["cryptocurrencies"]
    stocks_data = market_data["stocks"]
    indices_data = market_data["indices"]

    crypto_analysis = analyzed_data["crypto_analysis"]
    stock_analysis = analyzed_data["stock_analysis"]

    # Calculate market stats
    total_crypto_market_cap = sum(c["market_cap"] for c in crypto_data)
    avg_crypto_change_24h = sum(c["change_24h"] for c in crypto_data) / len(crypto_data)
    avg_indices_change = sum(i["change_percent"] for i in indices_data) / len(indices_data)

    # Create digest structure
    digest = {
        "title": "Market Analysis Digest",
        "subtitle": f"Market Update • {datetime.utcnow().strftime('%B %d, %Y')}",
        "generated_at": datetime.utcnow().isoformat(),
        "summary": {
            "headline": "Daily Market Snapshot",
            "content": market_summary["summary"],
            "stats": {
                "total_crypto_market_cap": format_currency(total_crypto_market_cap),
                "crypto_24h_avg_change": format_percent(avg_crypto_change_24h),
                "indices_avg_change": format_percent(avg_indices_change),
                "market_sentiment": get_market_sentiment(avg_crypto_change_24h, avg_indices_change)
            }
        },
        "crypto_section": create_crypto_section(crypto_data, crypto_analysis),
        "stocks_section": create_stocks_section(stocks_data, indices_data, stock_analysis),
        "highlights": {
            "biggest_crypto_mover": get_biggest_mover(crypto_data, "crypto"),
            "biggest_stock_mover": get_biggest_mover(stocks_data, "stock"),
            "market_leader": get_market_leader(indices_data)
        },
        "metadata": {
            "assets_tracked": len(crypto_data) + len(stocks_data),
            "indices_tracked": len(indices_data),
            "last_updated": datetime.utcnow().isoformat()
        }
    }

    return digest


def get_market_sentiment(crypto_change, stock_change):
    """Determine overall market sentiment."""
    avg_change = (crypto_change + stock_change) / 2

    if avg_change > 2.0:
        return {"label": "Very Bullish", "emoji": "🚀", "color": "green"}
    elif avg_change > 0.5:
        return {"label": "Bullish", "emoji": "📈", "color": "lightgreen"}
    elif avg_change > -0.5:
        return {"label": "Neutral", "emoji": "➡️", "color": "gray"}
    elif avg_change > -2.0:
        return {"label": "Bearish", "emoji": "📉", "color": "orange"}
    else:
        return {"label": "Very Bearish", "emoji": "🔻", "color": "red"}


def get_biggest_mover(data, asset_type):
    """Get the biggest mover (positive or negative)."""
    if asset_type == "crypto":
        sorted_data = sorted(data, key=lambda x: abs(x["change_24h"]), reverse=True)
        if sorted_data:
            top = sorted_data[0]
            return {
                "symbol": top["symbol"],
                "name": top["name"],
                "change": top["change_24h"],
                "change_formatted": format_percent(top["change_24h"]),
                "direction": "up" if top["change_24h"] > 0 else "down"
            }
    else:  # stock
        sorted_data = sorted(data, key=lambda x: abs(x["change_percent"]), reverse=True)
        if sorted_data:
            top = sorted_data[0]
            return {
                "symbol": top["symbol"],
                "change": top["change_percent"],
                "change_formatted": format_percent(top["change_percent"]),
                "direction": "up" if top["change_percent"] > 0 else "down"
            }

    return None


def get_market_leader(indices_data):
    """Get the leading market index."""
    if indices_data:
        leader = max(indices_data, key=lambda x: x["change_percent"])
        return {
            "name": leader["name"],
            "symbol": leader["symbol"],
            "change": leader["change_percent"],
            "change_formatted": format_percent(leader["change_percent"])
        }
    return None


def main():
    """Main execution function."""
    tracker = ExecutionTracker()

    print("=" * 60)
    print("📝 AGENT C: MARKET DIGEST WRITER")
    print("=" * 60)

    # Load inputs
    market_data_raw = load_input_data('data/market_analysis/market-data.json')
    analyzed_data_raw = load_input_data('data/market_analysis/analyzed-market.json')

    market_data = market_data_raw["data"]
    analyzed_data = analyzed_data_raw["data"]
    market_summary = analyzed_data["market_summary"]

    # Create digest
    digest = create_digest(market_data, analyzed_data, market_summary)

    # Prepare output
    output = {
        "agent": "agent-c-digest-writer",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "completed",
        "data": {
            "digest": digest
        },
        "costs": {
            "total_usd": 0.00  # No AI calls in this agent
        }
    }

    # Save outputs
    save_output_data('data/market_analysis/digest.json', output)

    # Also save to public directory for web access
    public_digest = {
        "generated_at": digest["generated_at"],
        "digest": digest
    }
    save_output_data('public/market-analysis.json', public_digest)

    tracker.finish()

    # Calculate costs
    costs = CostCalculator.calculate_total_cost(tracker, {"input": 0, "output": 0})

    # Write job summary
    summary = SummaryWriter("Market Digest Writer", "📝")
    summary.add_header()
    summary.add_metric("Assets in digest", digest["metadata"]["assets_tracked"])
    summary.add_metric("Indices tracked", digest["metadata"]["indices_tracked"])
    summary.add_metric("Market sentiment", digest["summary"]["stats"]["market_sentiment"]["label"])
    summary.add_timestamps(tracker)
    summary.add_cost_summary(costs)
    summary.write()

    print("\n✅ Market digest created successfully!")
    print(f"📁 Output saved to: data/market_analysis/digest.json")
    print(f"🌐 Public digest: public/market-analysis.json")


if __name__ == "__main__":
    main()
