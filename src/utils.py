import pandas as pd


def vsa_validator(df):
    if df is None or len(df) < 24:
        return False, "Datos insuficientes."

    vol_sma = df["Volume"].rolling(window=24).mean().iloc[-1]
    current_vol = df["Volume"].iloc[-1]

    if vol_sma == 0:
        vol_sma = 1
    volume_ratio = current_vol / vol_sma

    current_close, current_open = df["Close"].iloc[-1], df["Open"].iloc[-1]
    spread = abs(current_close - current_open)
    avg_spread = abs(df["Close"] - df["Open"]).rolling(window=24).mean().iloc[-1]

    if volume_ratio >= 2.0 and spread > avg_spread:
        return True, f"🟢 VSA VALIDADO (Vol: {volume_ratio:.1f}x)"
    elif volume_ratio >= 2.0 and spread < avg_spread:
        return False, f"🟡 VSA ADVERTENCIA: Absorción (Vol: {volume_ratio:.1f}x)"
    else:
        return False, f"🔴 VSA TRAMPA: Bajo Volumen (Vol: {volume_ratio:.1f}x)"
