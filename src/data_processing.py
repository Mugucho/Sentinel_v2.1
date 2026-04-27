import numpy as np
import pandas as pd
import pandas_ta as ta
import streamlit as st


@st.cache_data
def process_data(data: pd.DataFrame, ma_window: int = 50) -> pd.DataFrame:
    """
    Procesa datos de OHLCV con indicadores técnicos y corrección de huecos visuales.
    """
    if data.empty:
        return data

    # 1. Limpieza de Fechas y Ordenamiento para evitar gráficos entrecortados
    if "Date" not in data.columns:
        data = data.reset_index()

    # Eliminamos zonas horarias para compatibilidad total
    data["Date"] = pd.to_datetime(data["Date"]).dt.tz_localize(None)
    data = data.sort_values("Date").reset_index(drop=True)

    # 2. Indicadores Básicos (min_periods=1 evita que la línea desaparezca al inicio)
    data["SMA"] = data["Close"].rolling(window=ma_window, min_periods=1).mean()
    data["MA"] = data["SMA"]
    data["Daily Return"] = data["Close"].pct_change().fillna(0)
    data["Volatility"] = data["Daily Return"].rolling(
        window=20, min_periods=1
    ).std() * np.sqrt(252)

    # 3. RSI y Volumen Relativo
    if "RSI_14" not in data.columns:
        data["RSI_14"] = ta.rsi(data["Close"], length=14).fillna(0)

    data["Vol_Avg"] = ta.sma(data["Volume"], length=20).fillna(0)
    data["Rel_Vol"] = (data["Volume"] / data["Vol_Avg"]).fillna(1)

    # 4. Detección de Patrones (talib=False para evitar errores de instalación)
    try:
        cdl_patterns = data.ta.cdl_pattern(
            name=["doji", "hammer", "engulfing", "shootingstar"], talib=False
        )
        if cdl_patterns is not None:
            # AQUÍ ESTABA EL ERROR. Ya se eliminó el [cite:2]
            data = pd.concat([data, cdl_patterns.fillna(0)], axis=1)
    except Exception as e:
        print(f"Advertencia: No se pudieron detectar patrones de velas: {e}")

    # 5. Columna Simplificada de Patrones
    data["Pattern_Detected"] = np.where(
        (data["Close"] > data["Open"]) & (data["Close"] > data["MA"]),
        "BULL",
        np.where(
            (data["Close"] < data["Open"]) & (data["Close"] < data["MA"]),
            "BEAR",
            "NEUTRAL",
        ),
    )

    # Conectamos las columnas de pandas_ta con nuestra columna principal
    if "CDL_HAMMER" in data.columns:
        data["Pattern_Detected"] = np.where(
            data["CDL_HAMMER"] != 0, "HAMMER", data["Pattern_Detected"]
        )
    if "CDL_ENGULFING" in data.columns:
        data["Pattern_Detected"] = np.where(
            data["CDL_ENGULFING"] != 0, "ENGULFING", data["Pattern_Detected"]
        )
    if "CDL_DOJI" in data.columns:
        data["Pattern_Detected"] = np.where(
            data["CDL_DOJI"] != 0, "DOJI", data["Pattern_Detected"]
        )
    if "CDL_SHOOTINGSTAR" in data.columns:
        data["Pattern_Detected"] = np.where(
            data["CDL_SHOOTINGSTAR"] != 0, "SHOOTINGSTAR", data["Pattern_Detected"]
        )

    # Rellenar cualquier hueco restante para suavizar la visualización
    return data.ffill().fillna(0)


def calculate_support_resistance(df, window=50):
    """
    Cálculo de niveles dinámicos de soporte y resistencia.
    Esta función es requerida por tab_market_lab.py.
    """
    df = df.copy()
    # Usamos min_periods=1 para que los niveles aparezcan desde la primera vela
    df["Support_Level"] = df["Low"].rolling(window=window, min_periods=1).min()
    df["Resistance_Level"] = df["High"].rolling(window=window, min_periods=1).max()
    return df
