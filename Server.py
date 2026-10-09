
import os
import time
import requests
from fastmcp import FastMCP

mcp = FastMCP("Mudrex Futures Market Data")

BASE_URL = "https://trade.mudrex.com/fapi/v1/price"
TIMEOUT = 30

INTERVAL_SECONDS = {
    "1s": 1,
    "1m": 60,
    "3m": 180,
    "5m": 300,
    "15m": 900,
    "30m": 1800,
    "1h": 3600,
    "2h": 7200,
    "4h": 14400,
    "6h": 21600,
    "8h": 28800,
    "12h": 43200,
    "1d": 86400,
    "1w": 604800,
    "1M": 2592000,
}


def normalize_asset(symbol: str) -> str:
    symbol = symbol.strip().upper().replace(" ", "")
    if "/" not in symbol and symbol.endswith("USDT"):
        symbol = symbol[:-4] + "/USDT"
    if "/" not in symbol:
        raise ValueError("Use a symbol such as BTCUSDT or BTC/USDT.")
    return symbol


def fetch_klines(endpoint, symbol, aggregation, limit):
    if aggregation not in INTERVAL_SECONDS:
        return {"error": "Unsupported aggregation interval."}

    if not 1 <= limit <= 1440:
        return {"error": "Limit must be between 1 and 1440."}

    try:
        asset = normalize_asset(symbol)
        end_time = int(time.time())
        start_time = end_time - (
            INTERVAL_SECONDS[aggregation] * limit
        )

        params = {
            "assets": asset,
            "aggregation": aggregation,
            "start_time": start_time,
            "end_time": end_time,
        }

        response = requests.get(
            f"{BASE_URL}/{endpoint}",
            params=params,
            timeout=TIMEOUT,
        )

        if not response.ok:
            return {
                "error": "Mudrex API request failed",
                "status_code": response.status_code,
                "details": response.text[:1500],
                "request_url": response.url,
            }

        return response.json()

    except (requests.RequestException, ValueError) as exc:
        return {"error": str(exc)}


@mcp.tool()
def get_futures_klines(
    symbol: str,
    interval: str = "1h",
    limit: int = 500,
):
    """Get historical Mudrex futures OHLCV candles."""
    return fetch_klines(
        "kline", symbol, interval, limit
    )


@mcp.tool()
def get_mark_price_klines(
    symbol: str,
    interval: str = "1h",
    limit: int = 500,
):
    """Get historical Mudrex futures mark-price candles."""
    return fetch_klines(
        "mark-kline", symbol, interval, limit
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=port,
        path="/mcp",
    )
    

