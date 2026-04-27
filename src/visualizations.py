import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# --- CONFIGURACIÓN VISUAL INSTITUCIONAL ---
PALETTE = {
    "bull": "#00CC96",  # Verde Sentinel
    "bear": "#FF4136",  # Rojo Alert
    "main": "#00B4D8",  # Azul Técnico
    "accent": "gold",  # Dorado Énfasis
    "background": "rgba(0,0,0,0)",
    "template": "plotly_dark",
}


def _apply_continuous_axis(fig):
    """Ajuste maestro para eliminar huecos de fines de semana y feriados."""
    fig.update_xaxes(type="category", nticks=20, tickformat="%b %d", showgrid=False)
    return fig


# === 1. GRÁFICOS PRINCIPALES (MARKET LAB) ===


def create_candlestick_chart(df, ticker):
    """Genera gráfico Candlestick con arquitectura de mercado (Soporte/Resistencia)."""
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df["Date"],
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                name=ticker,
            )
        ]
    )

    # Niveles de Soporte y Resistencia si existen
    if "Support_Level" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df["Date"],
                y=df["Support_Level"],
                name="Soporte",
                line=dict(color=PALETTE["bull"], width=1, dash="dot"),
            )
        )
    if "Resistance_Level" in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df["Date"],
                y=df["Resistance_Level"],
                name="Resistencia",
                line=dict(color=PALETTE["bear"], width=1, dash="dot"),
            )
        )

    fig.update_layout(
        title=f"Arquitectura de Mercado: {ticker}",
        template=PALETTE["template"],
        xaxis_rangeslider_visible=False,
        height=500,
        margin=dict(l=10, r=10, t=40, b=10),
    )
    return _apply_continuous_axis(fig)


def create_moving_average_chart(df, ticker, ma_window):
    """Gráfico de convergencia de precios y SMA."""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["Date"], y=df["Close"], name="Precio", line=dict(color=PALETTE["bull"])
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=df["MA"],
            name=f"SMA {ma_window}",
            line=dict(color=PALETTE["accent"], width=2, dash="dash"),
        )
    )

    fig.update_layout(
        title=f"Tendencia SMA {ma_window}: {ticker}",
        template=PALETTE["template"],
        height=400,
    )
    return _apply_continuous_axis(fig)


def create_rsi_chart(df):
    """Gráfico de RSI con zonas de sobrecompra/sobreventa."""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["Date"], y=df["RSI_14"], name="RSI 14", line=dict(color="#8884d8")
        )
    )
    fig.add_hline(y=70, line_dash="dash", line_color=PALETTE["bear"])
    fig.add_hline(y=30, line_dash="dash", line_color=PALETTE["bull"])

    fig.update_layout(
        title="RSI (14 Periods)",
        template=PALETTE["template"],
        height=250,
        yaxis=dict(range=[0, 100]),
    )
    return _apply_continuous_axis(fig)


def create_macd_chart(df):
    """Gráfico MACD con histograma de impulso."""
    # Si MACD no está calculado, se asume neutro
    macd = df.get("MACD", pd.Series([0] * len(df)))
    signal = df.get("MACD_Signal", pd.Series([0] * len(df)))
    hist = df.get("MACD_Hist", pd.Series([0] * len(df)))

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=df["Date"], y=macd, name="MACD", line=dict(color=PALETTE["main"]))
    )
    fig.add_trace(
        go.Scatter(
            x=df["Date"], y=signal, name="Signal", line=dict(color="white", width=1)
        )
    )
    fig.add_trace(
        go.Bar(
            x=df["Date"],
            y=hist,
            name="Histogram",
            marker_color=np.where(hist >= 0, PALETTE["bull"], PALETTE["bear"]),
        )
    )

    fig.update_layout(title="MACD Momentum", template=PALETTE["template"], height=300)
    return _apply_continuous_axis(fig)


# === 2. ANÁLISIS DE PATRONES Y VOLUMEN ===


def create_patterns_only_chart(df, ticker):
    """Resalta visualmente los patrones detectados en el gráfico de velas."""
    fig = create_candlestick_chart(df, ticker)
    hits = df[df["Pattern_Detected"] != "NEUTRAL"]

    for _, row in hits.iterrows():
        fig.add_annotation(
            x=row["Date"],
            y=row["Low"],
            text=f"<b>{row['Pattern_Detected']}</b>",
            showarrow=True,
            arrowhead=1,
            bgcolor=PALETTE["accent"],
            font=dict(color="black"),
        )
    return fig


def create_volume_analysis_chart(df):
    """Análisis de volumen con colorización dinámica según el cierre."""
    colors = [PALETTE["bear"] if r < 0 else PALETTE["bull"] for r in df["Daily Return"]]
    fig = go.Figure(
        data=[go.Bar(x=df["Date"], y=df["Volume"], marker_color=colors, name="Volumen")]
    )
    fig.update_layout(
        title="Análisis de Volumen Institucional",
        template=PALETTE["template"],
        height=300,
    )
    return _apply_continuous_axis(fig)


# === 3. MÉTRICAS DE PERFORMANCE Y SCORING ===


def score_stock(df):
    """Calcula un score técnico de 0 a 8 basado en confluencias."""
    latest = df.iloc[-1]
    signals = []
    score = 0

    # Reglas de Scoring
    if latest["Close"] > latest["MA"]:
        score += 1
        signals.append("Precio sobre MA")
    if latest["RSI_14"] < 35:
        score += 2
        signals.append("Sobrevendido (RSI < 35)")
    elif latest["RSI_14"] > 65:
        score -= 1
        signals.append("Sobrecomprado (RSI > 65)")
    if latest["Rel_Vol"] > 1.5:
        score += 2
        signals.append("Volumen Inusual (Acumulación)")
    if latest["Pattern_Detected"] in ["BULL", "HAMMER", "IHS"]:
        score += 3
        signals.append(f"Patrón Alcista: {latest['Pattern_Detected']}")

    return max(0, score), signals


def create_stock_scoring_chart(scores_list):
    """Gráfico comparativo de calidad de activos (Screening)."""
    tickers = [s[0] for s in scores_list]
    scores = [s[1] for s in scores_list]
    colors = [
        PALETTE["bull"] if s >= 6 else PALETTE["accent"] if s >= 4 else PALETTE["bear"]
        for s in scores
    ]

    fig = go.Figure(
        go.Bar(
            x=tickers, y=scores, marker_color=colors, text=scores, textposition="auto"
        )
    )
    fig.update_layout(
        title="Screening de Calidad (Sentinel Score)",
        template=PALETTE["template"],
        yaxis_range=[0, 8],
    )
    return fig


def create_correlation_heatmap(data_dict):
    """Matriz de correlación entre múltiples activos."""
    close_prices = pd.DataFrame(
        {ticker: df["Close"] for ticker, df in data_dict.items()}
    )
    corr_matrix = close_prices.corr()

    fig = px.imshow(
        corr_matrix,
        text_auto=True,
        color_continuous_scale="RdYlGn",
        title="Matriz de Correlación de Riesgo",
    )
    fig.update_layout(template=PALETTE["template"])
    return fig


def create_daily_returns_histogram(df):
    """Distribución estadística de retornos."""
    fig = go.Figure(
        data=[
            go.Histogram(x=df["Daily Return"], marker_color=PALETTE["main"], nbinsx=50)
        ]
    )
    fig.update_layout(
        title="Distribución de Retornos", template=PALETTE["template"], height=350
    )
    return fig


def create_volume_vs_close_scatter(df):
    """Relación de dispersión entre volumen y precio."""
    fig = go.Figure(
        data=[
            go.Scatter(
                x=df["Volume"],
                y=df["Close"],
                mode="markers",
                marker=dict(
                    color=df["Daily Return"], colorscale="RdYlGn", showscale=True
                ),
            )
        ]
    )
    fig.update_layout(
        title="Dispersión: Volumen vs Precio", template=PALETTE["template"], height=400
    )
    return fig
