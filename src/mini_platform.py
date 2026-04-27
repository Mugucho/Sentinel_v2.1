import os
from dataclasses import dataclass
from typing import List, Optional

try:
    from alpaca.trading.client import TradingClient

    ALPACA_AVAILABLE = True
except ImportError:
    TradingClient = None
    ALPACA_AVAILABLE = False


@dataclass
class TradeRecord:
    timestamp: object
    symbol: str
    side: str
    qty: int
    price: float
    pnl: float


class TradingEngine:
    def __init__(self, stop_loss_pct: float = 0.05):
        self.stop_loss_pct = stop_loss_pct

    def strategy(self, close: float, ma: float, pattern_detected: str) -> str:
        if pattern_detected == "BULL" and close > ma:
            return "BUY"
        if pattern_detected == "BEAR" and close < ma:
            return "SELL"
        return "HOLD"


def run_simulation(data, sl_input: float = 0.05):
    cash = 10000.0
    position_qty = 0
    entry_price = 0.0
    ledger: List[TradeRecord] = []
    engine = TradingEngine(stop_loss_pct=sl_input)

    for _, row in data.iterrows():
        signal = engine.strategy(row["Close"], row["MA"], row["Pattern_Detected"])

        if position_qty == 0 and signal == "BUY":
            position_qty = 1
            entry_price = float(row["Close"])
            cash -= entry_price
            ledger.append(
                TradeRecord(
                    timestamp=row["Date"],
                    symbol=row.get("Ticker", ""),
                    side="BUY",
                    qty=position_qty,
                    price=entry_price,
                    pnl=0.0,
                )
            )

        if position_qty > 0:
            stop_price = entry_price * (1 - sl_input)
            if row["Close"] <= stop_price or signal == "SELL":
                exit_price = float(row["Close"])
                pnl = (exit_price - entry_price) * position_qty
                cash += exit_price * position_qty
                ledger.append(
                    TradeRecord(
                        timestamp=row["Date"],
                        symbol=row.get("Ticker", ""),
                        side="SELL",
                        qty=position_qty,
                        price=exit_price,
                        pnl=pnl,
                    )
                )
                position_qty = 0
                entry_price = 0.0

    return ledger, position_qty, cash


class AlpacaExecutor:
    def __init__(self, api_key: str, secret_key: str, paper_mode: bool = True):
        if not ALPACA_AVAILABLE:
            raise ImportError("alpaca-py no está disponible en el entorno.")
        self.client = TradingClient(api_key, secret_key, paper=paper_mode)

    def place_order(self, symbol: str, qty: int, side: str):
        return self.client.submit_order(
            symbol=symbol,
            qty=qty,
            side=side.lower(),
            type="market",
            time_in_force="gtc",
        )
