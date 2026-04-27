import pandas as pd
import pandas_ta as ta
import numpy as np


def detect_ihs_pattern(df):
    """
    Detecta el patrón Hombro-Cabeza-Hombro Invertido (IHS).
    Es un patrón de reversión de tendencia bajista a alcista.
    Estructura: Hombro Izq (bajo) -> Cabeza (menor) -> Hombro Der (bajo similar)
    """
    ihs_detections = []
    prices = df["Close"].values
    min_window = 10  # Ventana mínima para detectar el patrón

    if len(prices) < min_window:
        return ihs_detections

    # Buscar patrones IHS en ventanas deslizantes
    for i in range(min_window, len(prices)):
        window = prices[max(0, i - min_window) : i + 1]

        if len(window) < 5:
            continue

        # Encontrar mínimos y máximos en la ventana
        left_shoulder_idx = np.argmin(window[: len(window) // 2])
        head_idx = np.argmin(window)
        right_shoulder_idx = np.argmin(window[len(window) // 2 :]) + len(window) // 2

        if left_shoulder_idx == head_idx or head_idx == right_shoulder_idx:
            continue

        left_shoulder = window[left_shoulder_idx]
        head = window[head_idx]
        right_shoulder = window[right_shoulder_idx]

        # Validar estructura: cabeza debe ser el menor, hombros similares
        if head < left_shoulder and head < right_shoulder:
            # Permitir variación de ±5% en los hombros
            shoulder_tolerance = np.mean([left_shoulder, right_shoulder]) * 0.05

            if abs(left_shoulder - right_shoulder) <= shoulder_tolerance:
                ihs_detections.append(
                    {
                        "index": i,
                        "left_shoulder": left_shoulder,
                        "head": head,
                        "right_shoulder": right_shoulder,
                        "depth": (np.mean([left_shoulder, right_shoulder]) - head)
                        / head
                        * 100,
                    }
                )

    return ihs_detections


def detect_head_and_shoulders_pattern(df):
    """
    Detecta el patrón Hombro-Cabeza-Hombro (HS).
    Es un patrón de reversión de tendencia alcista a bajista.
    Estructura: Hombro Izq (alto) -> Cabeza (mayor) -> Hombro Der (alto similar)
    """
    hs_detections = []
    prices = df["Close"].values
    min_window = 10

    if len(prices) < min_window:
        return hs_detections

    for i in range(min_window, len(prices)):
        window = prices[max(0, i - min_window) : i + 1]

        if len(window) < 5:
            continue

        # Encontrar máximos en la ventana
        left_shoulder_idx = np.argmax(window[: len(window) // 2])
        head_idx = np.argmax(window)
        right_shoulder_idx = np.argmax(window[len(window) // 2 :]) + len(window) // 2

        if left_shoulder_idx == head_idx or head_idx == right_shoulder_idx:
            continue

        left_shoulder = window[left_shoulder_idx]
        head = window[head_idx]
        right_shoulder = window[right_shoulder_idx]

        # Validar estructura: cabeza debe ser el mayor, hombros similares
        if head > left_shoulder and head > right_shoulder:
            shoulder_tolerance = np.mean([left_shoulder, right_shoulder]) * 0.05

            if abs(left_shoulder - right_shoulder) <= shoulder_tolerance:
                hs_detections.append(
                    {
                        "index": i,
                        "left_shoulder": left_shoulder,
                        "head": head,
                        "right_shoulder": right_shoulder,
                        "height": (head - np.mean([left_shoulder, right_shoulder]))
                        / np.mean([left_shoulder, right_shoulder])
                        * 100,
                    }
                )

    return hs_detections


def find_complex_patterns(df):
    """
    Detecta patrones complejos usando:
    1. Patrones de velas (pandas_ta)
    2. Patrones geométricos (IHS, HS)
    """
    if "Pattern_Detected" not in df.columns:
        df["Pattern_Detected"] = ""

    signals = {}
    df = df.copy()  # Evitar advertencias de SettingWithCopyWarning

    # 1. Detección de patrones de velas vía pandas_ta
    try:
        patterns_df = df.ta.cdl_pattern(
            name=["doji", "hammer", "engulfing", "shootingstar"], talib=False
        )

        if patterns_df is not None:
            for col in patterns_df.columns:
                name = col.replace("CDL_", "").upper()
                hits = patterns_df[patterns_df[col] != 0]
                for idx in hits.index:
                    current = df.at[idx, "Pattern_Detected"]
                    df.at[idx, "Pattern_Detected"] = (
                        name if current == "" else f"{current}+{name}"
                    )
                    if name not in signals:
                        signals[name] = f"Patrón de vela {name} detectado"
    except Exception as e:
        print(f"Error detectando patrones de velas: {e}")

    # 2. Detectar IHS (Inverted Head and Shoulders)
    ihs_detections = detect_ihs_pattern(df)
    if ihs_detections:
        # Marcar el índice más reciente del patrón
        latest_ihs = ihs_detections[-1]
        signals["IHS"] = (
            f"Inverted Head and Shoulders detectado (profundidad: {latest_ihs['depth']:.2f}%)"
        )
        df.at[df.index[min(latest_ihs["index"], len(df) - 1)], "Pattern_Detected"] = (
            "IHS"
        )

    # 3. Detectar HS (Head and Shoulders)
    hs_detections = detect_head_and_shoulders_pattern(df)
    if hs_detections:
        latest_hs = hs_detections[-1]
        signals["HS"] = (
            f"Head and Shoulders detectado (altura: {latest_hs['height']:.2f}%)"
        )
        df.at[df.index[min(latest_hs["index"], len(df) - 1)], "Pattern_Detected"] = "HS"

    return df, signals
