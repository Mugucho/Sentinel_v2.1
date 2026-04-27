import requests
import time
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv

# Cargar credenciales del Búnker [cite: 1]
load_dotenv()


@st.cache_data(ttl=600)  # Cache por 10 minutos
def fetch_stock_data(ticker, period_days=365, interval="1d"):
    """
    Motor RAW para Yahoo Finance (v8 Chart API).
    Extrae OHLCV mediante peticiones HTTP directas con paginación temporal.
    """
    end_dt = datetime.now(timezone.utc)
    start_dt = end_dt - timedelta(days=period_days)

    # Ajuste de ventanas según el intervalo para evitar bloqueos
    step_days = 7 if interval == "1m" else 59 if interval in ["5m", "15m"] else 360

    all_chunks = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Sentinel/2.1"}

    curr_end = end_dt
    curr_start = max(start_dt, curr_end - timedelta(days=step_days))

    while curr_end > start_dt:
        url = f"https://query2.finance.yahoo.com/v8/finance/chart/{ticker}"
        params = {
            "period1": int(curr_start.timestamp()),
            "period2": int(curr_end.timestamp()),
            "interval": interval,
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code != 200:
                break

            json_data = response.json()
            result = json_data.get("chart", {}).get("result", [])

            if not result or "timestamp" not in result[0]:
                break

            res = result[0]
            quote = res["indicators"]["quote"][0]

            chunk = pd.DataFrame(
                {
                    "Date": [
                        datetime.fromtimestamp(t, tz=timezone.utc)
                        for t in res["timestamp"]
                    ],
                    "Open": quote.get("open", []),
                    "High": quote.get("high", []),
                    "Low": quote.get("low", []),
                    "Close": quote.get("close", []),
                    "Volume": quote.get("volume", []),
                }
            )
            all_chunks.append(chunk)

            # Paginación hacia atrás
            curr_end = curr_start
            curr_start = max(start_dt, curr_end - timedelta(days=step_days))
            time.sleep(0.5)  # Anti-ban delay

        except Exception:
            break

    if not all_chunks:
        return pd.DataFrame()

    df = pd.concat(all_chunks).drop_duplicates("Date").dropna()
    df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None)
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        df[col] = df[col].astype(float)

    return df.sort_values("Date").reset_index(drop=True)


@st.cache_data(ttl=600)  # Cache por 10 minutos
def fetch_trading_data_alpaca(ticker, days_back=365, interval="1Day"):
    """
    Motor RAW para Alpaca Markets (v2 Bars API).
    Utiliza paginación manual mediante 'next_page_token'.
    """
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")

    url = f"https://data.alpaca.markets/v2/stocks/{ticker}/bars"
    headers = {
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": secret_key,
        "Accept": "application/json",
    }

    end_dt = datetime.now(timezone.utc)
    start_dt = end_dt - timedelta(days=days_back)

    all_bars = []
    page_token = None

    while True:
        params = {
            "timeframe": interval,
            "start": start_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end": end_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "limit": 1000,
            "adjustment": "all",
        }
        if page_token:
            params["page_token"] = page_token

        try:
            response = requests.get(url, headers=headers, params=params, timeout=15)
            if response.status_code != 200:
                break

            data = response.json()
            bars = data.get("bars", [])
            if not bars:
                break

            all_bars.extend(bars)
            page_token = data.get("next_page_token")

            if not page_token:
                break
            time.sleep(0.2)  # Rate limit management

        except Exception:
            break

    if not all_bars:
        return pd.DataFrame()

    df = pd.DataFrame(all_bars)
    df.rename(
        columns={
            "t": "Date",
            "o": "Open",
            "h": "High",
            "l": "Low",
            "c": "Close",
            "v": "Volume",
        },
        inplace=True,
    )
    df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None)

    for col in ["Open", "High", "Low", "Close", "Volume"]:
        df[col] = df[col].astype(float)

    return df.sort_values("Date").reset_index(drop=True)


@st.cache_data(ttl=300)  # Cache por 5 minutos
def fetch_watchlist_data(tickers):
    """Obtiene precios rápidos para la visualización de la Watchlist."""
    summary = []
    for symbol in tickers:
        df = fetch_stock_data(symbol, period_days=5)
        if not df.empty:
            last = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else last
            summary.append(
                {
                    "Ticker": symbol,
                    "Precio": round(last["Close"], 2),
                    "Var %": round(((last["Close"] / prev["Close"]) - 1) * 100, 2),
                }
            )
    return pd.DataFrame(summary)
