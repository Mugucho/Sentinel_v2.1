import streamlit as st


def render_playbooks_tab(ticker):
    st.subheader("📋 Playbooks Tácticos (Libro de Jugadas)")
    st.markdown(
        "Protocolos de ejecución predefinidos para sectores específicos y regímenes de mercado."
    )

    # Definición de playbooks por ticker
    playbooks = {
        "XLE": {
            "name": "Sector Energía: XLE Geo-Reversion",
            "emoji": "🛢️",
            "macro": """
            **🌍 Contexto Macro & Sentimiento:**
            * **Corto Plazo:** Alcista / Volátil (Prima de guerra).
            * **Medio Plazo:** Bajista (Destrucción de demanda por inflación).
            * **Veredicto:** Evitar rupturas (Breakouts). Operar rebotes en sobreventa extrema usando niveles de liquidez.
            """,
            "rules": """
            **⚙️ Reglas de Ejecución (Long/Compra):**
            1. Precio > SMA 200 días.
            2. Perforación de Banda Bollinger Inferior.
            3. RSI 14 < 30 (Sobreventa intradiaria).
            4. VSA: Pico de volumen confirmando absorción institucional.
            """,
            "checklist": [
                "08:00 AM - Escaneo Macro: Revisar titulares de geopolítica y petróleo.",
                "08:15 AM - Futuros: Auditar comportamiento del Brent/WTI pre-mercado.",
                "08:30 AM - Niveles: Anotar PDH, PDL y POC del día anterior.",
                "09:45 AM - 11:00 AM - Ventana Táctica: Confirmar reglas de entrada y ejecutar si aplica.",
                "12:00 PM - Cierre de Pantalla: Activar modo manos libres.",
                "04:15 PM - Journaling: Registrar la sesión y apagar motores.",
            ],
        },
        "QQQ": {
            "name": "Sector Tecnología: QQQ Momentum",
            "emoji": "💻",
            "macro": """
            **🌍 Contexto Macro & Sentimiento:**
            * **Corto Plazo:** Alcista en rotación de crecimiento.
            * **Medio Plazo:** Dependiente de tasas y earnings.
            * **Veredicto:** Operar pulsos de liquidez en zonas de resistencia. Momentum puro.
            """,
            "rules": """
            **⚙️ Reglas de Ejecución (Long/Compra):**
            1. Precio > SMA 50 días (Impulso corto plazo).
            2. MACD positivo y cruce alcista.
            3. Volume > SMA 20 días (Confirmación institucional).
            4. Extensión máxima: 2% del cierre anterior (Profit-taking dinámico).
            """,
            "checklist": [
                "08:00 AM - FOMC Watch: Revisar comunicados de tasas de interés.",
                "08:15 AM - Earnings Calendar: Auditar earnings pre-market.",
                "08:30 AM - Técnico: Anotar pivot points y zonas de retracción Fib.",
                "09:45 AM - 11:30 AM - Ventana Principal: Entrada en breakouts de sesión.",
                "12:00 PM - Gestión de Riesgo: Ajustar stops dinámicos.",
                "03:45 PM - Preparar Salida: Cierre antes de últimos 15 minutos.",
            ],
        },
        "GLD": {
            "name": "Sector Oro: GLD Safe Haven",
            "emoji": "🏆",
            "macro": """
            **🌍 Contexto Macro & Sentimiento:**
            * **Corto Plazo:** Defensivo en crisis de riesgo.
            * **Medio Plazo:** Inverso al dólar fuerte.
            * **Veredicto:** Operar rotaciones de riesgo-aversión. Mean reversion en extremos.
            """,
            "rules": """
            **⚙️ Reglas de Ejecución (Long/Compra):**
            1. DXY (Dólar) > 105 (Correlación inversa débil).
            2. Real Rates en zona negativa.
            3. VIX > 20 (Sesgo defensivo).
            4. Soporte en SMA 200 días confirmado.
            """,
            "checklist": [
                "08:00 AM - DXY Scan: Monitorear fortaleza del dólar.",
                "08:15 AM - Central Bank Watch: Revisar comunicados de bancos centrales.",
                "08:30 AM - VIX Level: Auditar nivel de volatilidad del mercado.",
                "10:00 AM - Entrada: Comprar en quiebres defensivos.",
                "12:00 PM - Gestión: Mantener sin ajustes hasta señal de cierre.",
                "03:30 PM - Salida: Cerrar en recuperación de riesgo.",
            ],
        },
    }

    # Selector de Playbooks
    ticker_upper = ticker.upper()
    if ticker_upper not in playbooks:
        st.warning(
            f"El ticker {ticker_upper} aún no tiene un playbook configurado. Próximamente disponible."
        )
        return

    pb = playbooks[ticker_upper]

    st.divider()
    st.markdown(f"### {pb['emoji']} Protocolo {ticker_upper}: {pb['name']}")

    col_macro, col_rules = st.columns(2)

    with col_macro:
        st.info(pb["macro"])

    with col_rules:
        st.success(pb["rules"])

    st.divider()

    # Calculadora Institucional de Riesgo
    st.markdown("### 🛡️ Calculadora de Riesgo y Position Sizing")
    st.caption("Arquitectura para Capital Base de $1,000 | Riesgo Máximo: 1% ($10)")

    c1, c2, c3 = st.columns(3)
    with c1:
        entry_price = st.number_input(
            "Precio de Entrada ($)",
            min_value=0.01,
            value=100.00,
            step=0.10,
            key=f"entry_{ticker_upper}",
        )
    with c2:
        atr_val = st.number_input(
            "Valor ATR Actual ($)",
            min_value=0.01,
            value=2.00,
            step=0.10,
            key=f"atr_{ticker_upper}",
        )
    with c3:
        st.markdown(" ")  # Espaciador
        calcular = st.button(
            "Calcular Parámetros", width="stretch", key=f"calc_{ticker_upper}"
        )

    if calcular:
        sl_distance = atr_val * 1.5
        stop_loss = entry_price - sl_distance
        take_profit = entry_price + (sl_distance * 3)  # Ratio 1:3

        risk_amount = 10.00  # 1% de $1000
        shares = int(risk_amount / sl_distance)
        capital_required = shares * entry_price

        m1, m2, m3, m4 = st.columns(4)
        m1.metric(
            "Stop Loss Físico", f"${stop_loss:.2f}", "-1.5x ATR", delta_color="inverse"
        )
        m2.metric("Take Profit Fijo", f"${take_profit:.2f}", "Ratio 1:3")
        m3.metric("Acciones a Comprar", f"{shares} shares")
        m4.metric("Capital a Invertir", f"${capital_required:.2f}", "Riesgo real: $10")

    st.divider()

    # El Checklist Operativo
    st.markdown(f"### ⏱️ Checklist de Ejecución EST ({ticker_upper})")

    for item in pb["checklist"]:
        st.checkbox(item, key=f"cb_{ticker_upper}_{item}")
