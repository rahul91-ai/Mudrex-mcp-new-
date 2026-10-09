
import os
import requests
from fastmcp import FastMCP

mcp = FastMCP("Mudrex Futures Market Data")

BASE_URL = "https://trade.mudrex.com/fapi/v1/price"
TIMEOUT = 20


def mudrex_get(endpoint, params=None):
    """Fetch public, read-only Mudrex futures market data."""
    response = requests.get(
        f"{BASE_URL}/{endpoint}",
        params=params,
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


@mcp.tool()
def get_futures_klines(
    symbol: str,
    interval: str = "1h",
    limit: int = 500,
):
    """Get historical OHLCV candles for a Mudrex futures symbol."""
    symbol = symbol.upper().strip()

    if "/" not in symbol:
        if symbol.endswith("USDT"):
            symbol = symbol[:-4] + "/USDT"
        else:
            return {
                "error": "Use a symbol such as BTCUSDT or BTC/USDT."
            }

    allowed_intervals = {
        "1s", "1m", "3m", "5m", "15m", "30m",
        "1h", "2h", "4h", "6h", "8h", "12h",
        "1d", "1w", "1M",
    }

    if interval not in allowed_intervals:
        return {"error": "Unsupported interval."}

    if not 1 <= limit <= 1440:
        return {"error": "Limit must be between 1 and 1440."}

    return mudrex_get(
        "kline",
        {
            "symbol": symbol,
            "interval": interval,
            "limit": limit,
        },
    )


@mcp.tool()
def get_mark_price_klines(
    symbol: str,
    interval: str = "1h",
    limit: int = 500,
):
    """Get historical mark-price candles for a futures symbol."""
    symbol = symbol.upper().strip()

    if "/" not in symbol:
        if symbol.endswith("USDT"):
            symbol = symbol[:-4] + "/USDT"
        else:
            return {"error": "Use a symbol such as BTCUSDT or BTC/USDT."}

    if not 1 <= limit <= 1440:
        return {"error": "Limit must be between 1 and 1440."}

    return mudrex_get(
        "mark-kline",
        {
            "symbol": symbol,
            "interval": interval,
            "limit": limit,
        },
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=port,
        path="/mcp",
    )
