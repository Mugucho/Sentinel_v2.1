import streamlit as st
from dotenv import load_dotenv
import os
import pandas as pd

# Importación de Módulos (Vistas)
from views.tab_premarket import render_premarket_tab
from views.tab_tecnico import render_tecnico_tab
from views.tab_patrones import render_patrones_tab
from views.tab_correlaciones import render_correlaciones_tab
from views.tab_risk_gates import render_risk_gates_tab
from views.tab_macro import render_macro_tab
from views.tab_tear_sheet import render_tear_sheet_tab
from views.tab_oracle import render_oracle_tab
from views.tab_volatilidad import render_volatilidad_tab
from views.tab_market_lab import render_market_lab_tab
from views.tab_journal import render_journal_tab
from views.tab_playbooks import render_playbooks_tab

# Importación de Motores (Lógica)
from src.notifier import send_telegram_alert
from src.data_fetcher import fetch_stock_data, fetch_watchlist_data
from src.data_processing import process_data
from src.styles import apply_futuristic_design

# Inicialización
load_dotenv()
st.set_page_config(page_title="Market Architect Pro", layout="wide")
apply_futuristic_design()

# Bloqueo de Seguridad Institucional
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False


def check_password():
    if not st.session_state["authenticated"]:
        pwd = st.text_input("Ingresa la clave de acceso al Búnker:", type="password")
        if pwd == os.getenv("SENTINEL_PASSWORD"):
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.stop()


check_password()

# --- PANEL LATERAL (SIDEBAR) ---
with st.sidebar:
    st.title("🏛️ Sentinel Control")
    st.caption("Market Architect Pro v2.1")
    st.divider()

    ticker = st.text_input("🎯 Ticker Principal", "XLE").upper()
    ma_window = st.number_input(
        "SMA Window", min_value=5, max_value=200, value=50, step=5
    )
    watchlist_input = st.text_input(
        "📌 Watchlist Tickers (separados por coma)", "AAPL,MSFT,AMZN,TSLA"
    )
    mis_tickers = [
        sym.strip().upper() for sym in watchlist_input.split(",") if sym.strip()
    ]

    env_api_key = os.getenv("ALPACA_API_KEY", "")
    env_secret_key = os.getenv("ALPACA_SECRET_KEY", "")

    st.divider()
    st.markdown("### 📡 Conexión Asíncrona")
    if st.button("🔔 Probar Enlace Telegram", width="stretch"):
        exito, respuesta = send_telegram_alert(
            "📡 Sistema Sentinel v2 en línea y transmitiendo desde el Búnker."
        )
        if exito:
            st.success("Mensaje entregado al móvil.")
        else:
            st.error(f"Fallo de transmisión: {respuesta}")

    st.sidebar.markdown("---")
    with st.sidebar.expander("🔑 Conexión Broker (Alpaca)"):
        api_key = st.text_input("API Key ID", value=env_api_key, type="password")
        secret_key = st.text_input("Secret Key", value=env_secret_key, type="password")
        paper_mode = st.checkbox("Modo Paper Trading", value=True)

# Título Principal
st.title(f"Dashboard de Análisis y Ejecución: {ticker}")
st.markdown("---")

# Sección de Watchlist (Variación Diaria)
with st.expander("📊 Resumen de Mi Cartera (Cambio Hoy)", expanded=True):
    with st.spinner("Sincronizando Watchlist..."):
        w_data = fetch_watchlist_data(mis_tickers)
        if not w_data.empty:
            cols = st.columns(len(w_data))
            for i, row in w_data.iterrows():
                cols[i].metric(
                    label=row["Ticker"],
                    value=f"${row['Precio']}",
                    delta=f"{row['Var %']}%",
                )
        else:
            st.info(
                "No hay datos de watchlist disponibles. Verifica tu conexión a la API."
            )

# Procesamiento Principal de Datos
if ticker:
    with st.spinner(f"Extrayendo datos institucionales de {ticker}..."):
        data = fetch_stock_data(ticker)

        if not data.empty:
            # Nuestro motor RAW ya devuelve el DataFrame limpio. Solo procesamos.
            data = process_data(data, ma_window)

            # KPIs
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Precio Cierre", f"${data['Close'].iloc[-1]:.2f}")
            m2.metric("Retorno Diario", f"{data['Daily Return'].iloc[-1]*100:.2f}%")

            # Búsqueda dinámica de la columna RSI para evitar KeyErrors
            rsi_val = data["RSI_14"].iloc[-1] if "RSI_14" in data.columns else 0.0
            m3.metric("RSI (14)", f"{rsi_val:.2f}")

            m4.metric("Volatilidad Anual", f"{data['Volatility'].iloc[-1]:.2%}")
        else:
            st.error(
                f"No se pudieron descargar los datos para {ticker}. Verifica el símbolo."
            )

# --- ENRUTAMIENTO DE PESTAÑAS ---
tabs = st.tabs(
    [
        "☀️ Pre-Market",
        "🧲 Técnico & VSA",
        "🧠 Patrones",
        "🕸️ Correlaciones",
        "🛡️ Risk Gates",
        "🧭 Macro Top-Down",
        "📈 Quant Tear Sheet",
        "📊 Market Lab",
        "🤖 Oráculo AI",
        "🪙 Radar Volatilidad",
        "📓 Journal",
        "📋 Playbooks",
    ]
)

with tabs[0]:
    render_premarket_tab(ticker)
with tabs[1]:
    render_tecnico_tab(ticker)
with tabs[2]:
    render_patrones_tab(ticker)
with tabs[3]:
    render_correlaciones_tab()
with tabs[4]:
    render_risk_gates_tab()
with tabs[5]:
    render_macro_tab(ticker)
with tabs[6]:
    render_tear_sheet_tab(ticker)
with tabs[7]:
    render_market_lab_tab(ticker)
with tabs[8]:
    render_oracle_tab(ticker)
with tabs[9]:
    render_volatilidad_tab(ticker)
with tabs[10]:
    render_journal_tab()
with tabs[11]:
    render_playbooks_tab(ticker)
