# 🏛️ Sentinel v2.1: Market Architect Pro

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.25%2B-red?style=for-the-badge&logo=streamlit)
![Plotly](https://img.shields.io/badge/Plotly-5.10%2B-purple?style=for-the-badge&logo=plotly)

**Sentinel v2.1** es una plataforma de análisis cuantitativo y ejecución de trading de nivel institucional, diseñada para traders algorítmicos y analistas de mercado. Construida sobre Python y Streamlit, integra análisis técnico, macroeconómico, de sentimiento y gestión de riesgo en un único dashboard interactivo.

---

## ✨ Características Principales

Sentinel no es solo un visualizador de gráficos; es una estación de trabajo completa para el trading moderno.

*   **📊 Market Lab:** Entorno integrado para análisis profundo, simulación de estrategias y ejecución de órdenes a través de Alpaca.
*   **📋 Playbooks Tácticos:** Codifica, guarda y ejecuta planes de trading específicos para cada activo, incluyendo cálculos de riesgo y tamaño de posición.
*   **🛡️ Institutional Risk Gates:** Simula y monitoriza compuertas de riesgo como el drawdown máximo del portafolio y la exposición por activo.
*   **🤖 Oráculo AI:** Utiliza NLP (Procesamiento de Lenguaje Natural) para analizar el sentimiento de noticias del mercado en tiempo real y correlacionarlo con la acción del precio.
*   **🧭 Macro Top-Down:** Superpone eventos macroeconómicos clave (noticias de la FED, geopolítica, etc.) sobre los gráficos de precios para un análisis contextual.
*   **🪙 Radar de Volatilidad:** Visualiza la superficie de volatilidad implícita en 3D para identificar oportunidades en el mercado de opciones.
*   **🧲 Técnico & VSA:** Análisis intradiario con VWAP (Volume-Weighted Average Price) y VSA (Volume Spread Analysis) para seguir la huella institucional.
*   **📈 Quant Tear Sheet:** Genera hojas de resultados cuantitativos y realiza backtesting de estrategias de reversión a la media.
*   **🕸️ Análisis de Correlaciones:** Mide la correlación entre diferentes activos de tu cartera con mapas de calor interactivos.

---

## 🛠️ Tech Stack

*   **Framework Principal:** [Streamlit](https://streamlit.io/)
*   **Análisis de Datos:** [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
*   **Indicadores Técnicos:** [Pandas-TA](https://github.com/twopirllc/pandas-ta)
*   **Visualización:** [Plotly](https://plotly.com/python/)
*   **APIs de Datos y Trading:**
    *   [Alpaca Markets](https://alpaca.markets/) (Datos de alta fidelidad y ejecución)
    *   [Yahoo Finance](https://finance.yahoo.com/) (Motor de obtención de datos robusto y personalizado)
    *   [NewsAPI](https://newsapi.org/) (Análisis de sentimiento)
*   **Notificaciones:** [Telegram](https://telegram.org/)

---

## 🚀 Instalación y Puesta en Marcha

Sigue estos pasos para ejecutar Sentinel en tu máquina local.

**1. Clona el Repositorio**
```bash
git clone https://github.com/Mugucho/Sentinel_v2.1.git
cd Sentinel_v2.1
```

**2. Crea y Activa un Entorno Virtual**
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

**3. Instala las Dependencias**
Asegúrate de tener el archivo `requirements.txt` en la raíz del proyecto.
```bash
pip install -r requirements.txt
```

**4. Configura tus Credenciales**
Crea un archivo llamado `.env` en la raíz del proyecto. Este archivo guardará tus claves de API de forma segura. **Nunca subas este archivo a GitHub.** El archivo `.gitignore` ya está configurado para ignorarlo.

Copia y pega el siguiente contenido en tu archivo `.env`, reemplazando los valores con tus propias credenciales:

```env
# Clave de acceso para la propia aplicación
SENTINEL_PASSWORD="tu_clave_secreta_aqui"

# Credenciales de Alpaca Markets (para datos y trading)
ALPACA_API_KEY="TU_API_KEY_DE_ALPACA"
ALPACA_SECRET_KEY="TU_SECRET_KEY_DE_ALPACA"

# Credenciales de NewsAPI (para el Oráculo AI)
NEWS_API_KEY="TU_API_KEY_DE_NEWSAPI"

# Credenciales del Bot de Telegram (para notificaciones)
TELEGRAM_BOT_TOKEN="TU_TOKEN_DE_BOT_DE_TELEGRAM"
TELEGRAM_CHAT_ID="TU_CHAT_ID_DE_TELEGRAM"
```

**5. Ejecuta la Aplicación**
Una vez configurado, inicia Streamlit:
```bash
streamlit run dashboard.py
```

Abre tu navegador en `http://localhost:8501` y usa la contraseña que definiste en `SENTINEL_PASSWORD` para acceder.

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

---

## ✍️ Autor

*   **Mugucho** - GitHub

¡Siéntete libre de contactarme, contribuir o sugerir mejoras!