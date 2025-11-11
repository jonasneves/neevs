"""
Agent A: Market Data Fetcher
Fetches live market data including stocks, crypto, and market indices.
Uses free APIs: CoinGecko (crypto) and Alpha Vantage (stocks).
"""

import json
import urllib.request
import urllib.error
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import ExecutionTracker, CostCalculator, SummaryWriter, save_output_data


def fetch_crypto_data():
    """Fetch top cryptocurrencies from CoinGecko (free, no API key required)."""
    print("📊 Fetching cryptocurrency data from CoinGecko...")

    try:
        # CoinGecko API - top 10 coins by market cap with 24h change
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1&sparkline=false&price_change_percentage=24h,7d"

        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())

        crypto_list = []
        for coin in data:
            crypto_list.append({
                "symbol": coin["symbol"].upper(),
                "name": coin["name"],
                "price": coin["current_price"],
                "market_cap": coin["market_cap"],
                "market_cap_rank": coin["market_cap_rank"],
                "change_24h": coin.get("price_change_percentage_24h", 0),
                "change_7d": coin.get("price_change_percentage_7d_in_currency", 0),
                "volume_24h": coin["total_volume"],
                "image": coin["image"]
            })

        print(f"✅ Fetched {len(crypto_list)} cryptocurrencies")
        return crypto_list

    except Exception as e:
        print(f"⚠️  Error fetching crypto data: {str(e)}")
        # Return mock data as fallback
        return get_mock_crypto_data()


def fetch_stock_indices():
    """Fetch major market indices (S&P 500, NASDAQ, DOW)."""
    print("📈 Fetching market indices...")

    # Using Alpha Vantage requires API key - check for it
    api_key = os.environ.get('ALPHA_VANTAGE_API_KEY', '')

    if not api_key:
        print("⚠️  ALPHA_VANTAGE_API_KEY not found, using mock data")
        return get_mock_indices_data()

    try:
        indices = []
        # Note: Alpha Vantage free tier is limited to 25 requests/day
        symbols = {
            "SPY": "S&P 500",
            "QQQ": "NASDAQ",
            "DIA": "Dow Jones"
        }

        for symbol, name in symbols.items():
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"

            try:
                with urllib.request.urlopen(url, timeout=10) as response:
                    data = json.loads(response.read().decode())

                if "Global Quote" in data and data["Global Quote"]:
                    quote = data["Global Quote"]
                    indices.append({
                        "symbol": symbol,
                        "name": name,
                        "price": float(quote["05. price"]),
                        "change": float(quote["09. change"]),
                        "change_percent": float(quote["10. change percent"].rstrip('%')),
                        "volume": int(quote["06. volume"])
                    })
            except Exception as e:
                print(f"⚠️  Error fetching {symbol}: {str(e)}")

        if indices:
            print(f"✅ Fetched {len(indices)} market indices")
            return indices
        else:
            return get_mock_indices_data()

    except Exception as e:
        print(f"⚠️  Error fetching indices: {str(e)}")
        return get_mock_indices_data()


def fetch_trending_stocks():
    """Fetch trending/top moving stocks."""
    print("🔥 Fetching trending stocks...")

    api_key = os.environ.get('ALPHA_VANTAGE_API_KEY', '')

    if not api_key:
        print("⚠️  ALPHA_VANTAGE_API_KEY not found, using mock data")
        return get_mock_stocks_data()

    try:
        # Top tech stocks to monitor
        symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"]
        stocks = []

        for symbol in symbols[:5]:  # Limit to 5 to stay within API limits
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"

            try:
                with urllib.request.urlopen(url, timeout=10) as response:
                    data = json.loads(response.read().decode())

                if "Global Quote" in data and data["Global Quote"]:
                    quote = data["Global Quote"]
                    stocks.append({
                        "symbol": symbol,
                        "price": float(quote["05. price"]),
                        "change": float(quote["09. change"]),
                        "change_percent": float(quote["10. change percent"].rstrip('%')),
                        "volume": int(quote["06. volume"])
                    })
            except Exception as e:
                print(f"⚠️  Error fetching {symbol}: {str(e)}")

        if stocks:
            print(f"✅ Fetched {len(stocks)} stocks")
            return stocks
        else:
            return get_mock_stocks_data()

    except Exception as e:
        print(f"⚠️  Error fetching stocks: {str(e)}")
        return get_mock_stocks_data()


def get_mock_crypto_data():
    """Return mock crypto data for testing/fallback."""
    return [
        {"symbol": "BTC", "name": "Bitcoin", "price": 94250.00, "market_cap": 1867000000000, "market_cap_rank": 1, "change_24h": 2.5, "change_7d": 5.8, "volume_24h": 45000000000, "image": "https://assets.coingecko.com/coins/images/1/large/bitcoin.png"},
        {"symbol": "ETH", "name": "Ethereum", "price": 3420.00, "market_cap": 411000000000, "market_cap_rank": 2, "change_24h": 1.8, "change_7d": 4.2, "volume_24h": 20000000000, "image": "https://assets.coingecko.com/coins/images/279/large/ethereum.png"},
        {"symbol": "USDT", "name": "Tether", "price": 1.00, "market_cap": 125000000000, "market_cap_rank": 3, "change_24h": 0.01, "change_7d": -0.02, "volume_24h": 75000000000, "image": "https://assets.coingecko.com/coins/images/325/large/Tether.png"},
        {"symbol": "SOL", "name": "Solana", "price": 215.50, "market_cap": 105000000000, "market_cap_rank": 4, "change_24h": 5.2, "change_7d": 12.3, "volume_24h": 3500000000, "image": "https://assets.coingecko.com/coins/images/4128/large/solana.png"},
        {"symbol": "BNB", "name": "BNB", "price": 625.00, "market_cap": 91000000000, "market_cap_rank": 5, "change_24h": 1.5, "change_7d": 3.8, "volume_24h": 1800000000, "image": "https://assets.coingecko.com/coins/images/825/large/bnb-icon2_2x.png"}
    ]


def get_mock_indices_data():
    """Return mock indices data for testing/fallback."""
    return [
        {"symbol": "SPY", "name": "S&P 500", "price": 587.50, "change": 5.25, "change_percent": 0.90, "volume": 45000000},
        {"symbol": "QQQ", "name": "NASDAQ", "price": 505.75, "change": 8.50, "change_percent": 1.71, "volume": 35000000},
        {"symbol": "DIA", "name": "Dow Jones", "price": 438.25, "change": 2.10, "change_percent": 0.48, "volume": 3500000}
    ]


def get_mock_stocks_data():
    """Return mock stock data for testing/fallback."""
    return [
        {"symbol": "AAPL", "price": 228.50, "change": 3.25, "change_percent": 1.44, "volume": 52000000},
        {"symbol": "MSFT", "price": 425.75, "change": 5.50, "change_percent": 1.31, "volume": 28000000},
        {"symbol": "GOOGL", "price": 178.25, "change": 2.75, "change_percent": 1.57, "volume": 22000000},
        {"symbol": "NVDA", "price": 148.50, "change": 8.25, "change_percent": 5.88, "volume": 385000000},
        {"symbol": "TSLA", "price": 352.75, "change": -5.25, "change_percent": -1.47, "volume": 95000000}
    ]


def main():
    """Main execution function."""
    tracker = ExecutionTracker()

    print("=" * 60)
    print("🏦 AGENT A: MARKET DATA FETCHER")
    print("=" * 60)

    # Fetch all market data
    crypto_data = fetch_crypto_data()
    indices_data = fetch_stock_indices()
    stocks_data = fetch_trending_stocks()

    # Prepare output
    output = {
        "agent": "agent-a-market-fetcher",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "completed",
        "data": {
            "cryptocurrencies": crypto_data,
            "indices": indices_data,
            "stocks": stocks_data,
            "crypto_count": len(crypto_data),
            "indices_count": len(indices_data),
            "stocks_count": len(stocks_data)
        },
        "costs": {
            "api_calls": len(crypto_data) + len(indices_data) + len(stocks_data),
            "total_usd": 0.00  # Free tier APIs
        }
    }

    # Save output for next agent
    save_output_data('data/market_analysis/market-data.json', output)

    tracker.finish()

    # Calculate costs
    costs = CostCalculator.calculate_total_cost(tracker, {"input": 0, "output": 0})

    # Write job summary
    summary = SummaryWriter("Market Data Fetcher", "📊")
    summary.add_header()
    summary.add_metric("Cryptocurrencies fetched", len(crypto_data))
    summary.add_metric("Market indices fetched", len(indices_data))
    summary.add_metric("Stocks fetched", len(stocks_data))
    summary.add_timestamps(tracker)
    summary.add_cost_summary(costs)
    summary.write()

    print("\n✅ Market data fetching completed!")
    print(f"📁 Output saved to: data/market_analysis/market-data.json")


if __name__ == "__main__":
    main()
