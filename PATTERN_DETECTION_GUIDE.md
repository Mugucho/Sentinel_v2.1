# Integración de Detección de Patrones Complejos

## 📋 Resumen

Se ha integrado con éxito la detección automática de patrones complejos (chartismo) en la pestaña "Patrones" del Market Lab. El sistema ahora detecta:

1. **Patrones de Velas** (DOJI, HAMMER, ENGULFING, SHOOTINGSTAR)
2. **Patrones Geométricos**:
   - **IHS** (Inverted Head and Shoulders) - Reversión de tendencia bajista a alcista
   - **HS** (Head and Shoulders) - Reversión de tendencia alcista a bajista

---

## 🔍 Patrones Detectados

### 1. **IHS - Hombro-Cabeza-Hombro Invertido** ⭐
**Tipo:** Patrón de reversión alcista (Bullish)

**Estructura:**
```
    Hombro Izq
    /         \
   /           Cabeza (más bajo)
  /           / 
Soporte -----/-------Hombro Der (similar al izq)
         Línea de cuello
```

**Características:**
- Ocurre en tendencias bajistas
- La cabeza es el punto más bajo
- Los hombros tienen alturas similares (tolerancia ±5%)
- Profundidad: diferencia porcentual entre hombros y cabeza
- Señal de compra al romper la línea de cuello hacia arriba

**Ejemplo en código:**
```
Se detectó un patrón IHS con profundidad de 8.5%
Potencial de reversión alcista significativo
```

### 2. **HS - Hombro-Cabeza-Hombro** ⚠️
**Tipo:** Patrón de reversión bajista (Bearish)

**Estructura:**
```
Hombro Izq     Cabeza      Hombro Der
      \       /  \       /
       \     /    \     /
        \   /      \   /
---------\ /--------\ /--------
       Línea de cuello
```

**Características:**
- Ocurre en tendencias alcistas
- La cabeza es el punto más alto
- Los hombros tienen alturas similares
- Altura: diferencia porcentual entre cabeza y hombros
- Señal de venta al romper la línea de cuello hacia abajo

### 3. **Patrones de Velas**
- **DOJI**: Indecisión del mercado
- **HAMMER**: Reversión alcista potencial
- **ENGULFING**: Cambio de sentimiento fuerte
- **SHOOTINGSTAR**: Rechazo a precios altos

---

## 📍 Ubicación en el Software

### Archivo Principal: `views/tab_market_lab.py`

**Sección:** Pestaña "🕯️ Patrones" (t2)

```python
with t2:
    st.subheader("🕯️ Detección de Patrones Complejos (Chartismo)")
    
    # Detectar patrones geométricos complejos
    processed_chart_data, complex_signals = find_complex_patterns(processed_chart_data)
    
    # Mostrar alertas
    if complex_signals:
        st.markdown("### 📊 Patrones Detectados:")
        # ... (mostrar alertas)
    
    # Visualización
    st.plotly_chart(
        create_patterns_only_chart(processed_chart_data, ticker_input),
        use_container_width=True,
    )
```

---

## 🛠️ Funciones Principales

### `find_complex_patterns(df)` 
**Ubicación:** `src/pattern_recognition.py`

**Parámetros:**
- `df` (DataFrame): DataFrame con columnas OHLCV

**Retorna:**
- `df` (DataFrame): DataFrame actualizado con columna `Pattern_Detected`
- `signals` (dict): Diccionario con patrones detectados y descripción

**Ejemplo de uso:**
```python
from src.pattern_recognition import find_complex_patterns

data, signals = find_complex_patterns(data)

# signals puede contener:
# {'IHS': 'Inverted Head and Shoulders detectado (profundidad: 8.5%)'}
# {'HS': 'Head and Shoulders detectado (altura: 6.2%)'}
# {'DOJI': 'Patrón de vela DOJI detectado'}
```

### `detect_ihs_pattern(df)` 
Detecta específicamente patrones IHS.

**Retorna:** Lista de diccionarios con detalles de detecciones
```python
[
    {
        'index': 45,
        'left_shoulder': 150.25,
        'head': 145.30,
        'right_shoulder': 150.10,
        'depth': 8.5
    }
]
```

### `detect_head_and_shoulders_pattern(df)`
Detecta específicamente patrones HS.

**Retorna:** Lista de diccionarios con detalles de detecciones
```python
[
    {
        'index': 45,
        'left_shoulder': 150.25,
        'head': 155.30,
        'right_shoulder': 150.10,
        'height': 6.2
    }
]
```

---

## 🎨 Visualización

### Interfaz de Usuario en Market Lab

```
🕯️ Detección de Patrones Complejos (Chartismo)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Patrones Detectados:

🚀 ALERTA: Se detectó un patrón IHS (Hombro-Cabeza-Hombro Invertido) en AAPL
💡 Este patrón sugiere un cambio de tendencia de bajista a alcista. 
   Señal potencial de compra.

📈 Visualización de Patrones:
[Gráfico Plotly con patrones marcados]
```

---

## 📈 Ejemplo en el Dashboard

Cuando ejecutas Market Lab en AAPL y se detecta un IHS:

```
Terminal Market Lab (AAPL)

⚙️ Parámetros de Análisis
├─ Ticker: AAPL
├─ SMA Window: 50
└─ Stop Loss: 5%

[Tabs: Análisis Técnico | 🕯️ Patrones | Vol y Riesgo | Simulación | ...]

🕯️ Patrones
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 ALERTA: Se detectó un patrón IHS (Hombro-Cabeza-Hombro Invertido) en AAPL
💡 Este patrón sugiere un cambio de tendencia de bajista a alcista. Señal potencial de compra.

📈 Visualización de Patrones:
[Gráfico interactivo con velas y patrones marcados]
```

---

## 🔧 Configuración y Tolerancia

### Parámetros de Detección

1. **Ventana mínima:** 10 barras (para evitar falsos positivos en datasets pequeños)
2. **Tolerancia de hombros:** ±5% de variación entre hombro izquierdo y derecho
3. **Métrica de profundidad (IHS):** `(promedio hombros - cabeza) / cabeza * 100`
4. **Métrica de altura (HS):** `(cabeza - promedio hombros) / promedio hombros * 100`

### Para ajustar la sensibilidad:

Editar en `src/pattern_recognition.py`:

```python
def detect_ihs_pattern(df):
    # Cambiar tolerancia de ±5% a ±3% para mayor precisión
    shoulder_tolerance = np.mean([left_shoulder, right_shoulder]) * 0.03  # Era 0.05
```

---

## ⚠️ Advertencias y Limitaciones

1. **Falsos positivos:** Los patrones geométricos pueden ocurrir en pequeñas escalas sin significancia
2. **Confirmación requerida:** Un patrón IHS o HS debe confirmarse con volumen y otros indicadores
3. **Timeframe importante:** Los patrones funcionan mejor en timeframes más altos (diarios, semanales)
4. **No es predictor:** Los patrones son análisis técnico, no garantizan movimientos futuros

### Uso Recomendado:

```python
# Combinar con otros indicadores para mayor confianza
score, signals = score_stock(data, fundamentals)

# Buscar confirmación de patrones:
# 1. Patrón IHS detectado
# 2. RSI < 30 (sobreventa)
# 3. MACD cruzando positivamente
# 4. Volumen aumentando en ruptura
```

---

## 📊 Integración en Streamlit

### Uso en otras vistas:

```python
from src.pattern_recognition import find_complex_patterns
from src.visualizations import create_patterns_only_chart

# En cualquier vista
data, signals = find_complex_patterns(data)

if signals:
    for pattern_name, signal_msg in signals.items():
        if pattern_name == "IHS":
            st.success(f"🚀 {signal_msg}")
        elif pattern_name == "HS":
            st.warning(f"⚠️ {signal_msg}")
        else:
            st.info(f"📍 {signal_msg}")

# Mostrar gráfico
st.plotly_chart(create_patterns_only_chart(data, ticker))
```

---

## 📝 Notas de Implementación

- ✅ Totalmente integrado en Market Lab
- ✅ Sin cambios requeridos en código existente
- ✅ Compatible con todos los timeframes
- ✅ Detecta múltiples patrones simultáneamente
- ✅ Bajo overhead computacional

---

## 🚀 Próximas Mejoras Opcionales

1. **Patrones Adicionales:**
   - Triángulos (simétricos, ascendentes, descendentes)
   - Banderas y astas
   - Cuñas

2. **Machine Learning:**
   - Entrenar modelo para detectar patrones con mayor precisión
   - Validación histórica de patrones

3. **Alertas Automáticas:**
   - Notificaciones cuando se forma un patrón
   - Seguimiento de validaciones de patrones

---

**Última actualización:** 2026-04-25
**Versión:** 2.1
**Estado:** ✅ Operativo
