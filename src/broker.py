import os
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from alpaca.trading.client import TradingClient
import pandas as pd
from datetime import datetime, timedelta

load_dotenv()


class AlpacaProvider:
    def __init__(self):
        """Inicializa los clientes de Alpaca usando las llaves del Búnker."""
        self.api_key = os.getenv("ALPACA_API_KEY")
        self.secret_key = os.getenv("ALPACA_SECRET_KEY")

        if not self.api_key or not self.secret_key:
            raise ValueError("Credenciales de Alpaca no encontradas en .env")

        # Cliente para Datos de Mercado (Velas, Tick data)
        self.data_client = StockHistoricalDataClient(self.api_key, self.secret_key)

        # Cliente para Ejecución y Cuenta (Fijado en Paper Trading = True)
        self.trading_client = TradingClient(self.api_key, self.secret_key, paper=True)

    def get_account_capital(self):
        """Obtiene el capital actual de la cuenta para alimentar el Kill Switch."""
        try:
            account = self.trading_client.get_account()
            return float(account.equity)
        except Exception as e:
            print(f"Error de conexión con la cuenta Alpaca: {e}")
            return None

    def get_historical_bars(self, ticker, days_back=5, timeframe=TimeFrame.Minute):
        """
        Descarga velas de micro-estructura directamente del exchange.
        Reemplaza la dependencia de yfinance.
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        # Parámetros estrictos para la API de Alpaca
        request_params = StockBarsRequest(
            symbol_or_symbols=ticker,
            timeframe=timeframe,
            start=start_date,
            end=end_date,
        )

        try:
            bars = self.data_client.get_stock_bars(request_params)
            df = bars.df

            # Formateo de datos: Alpaca devuelve un MultiIndex (symbol, timestamp).
            # Lo aplanamos para que Sentinel y pandas_ta lo puedan procesar.
            if isinstance(df.index, pd.MultiIndex):
                df = df.reset_index(level=0, drop=True)

            # Estandarización de columnas (Capitalizadas como las espera Sentinel)
            df = df.rename(
                columns={
                    "open": "Open",
                    "high": "High",
                    "low": "Low",
                    "close": "Close",
                    "volume": "Volume",
                }
            )

            return df
        except Exception as e:
            print(f"Error descargando micro-estructura de {ticker}: {e}")
            return (
                pd.DataFrame()
            )  # Devuelve un DataFrame vacío si falla para no romper la app
