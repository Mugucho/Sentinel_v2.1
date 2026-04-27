#!/usr/bin/env python3

# Test script para verificar que las nuevas funcionalidades funcionan
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from src.data_processing import process_data, calculate_support_resistance

    print("✅ data_processing importado correctamente")
except Exception as e:
    print(f"❌ Error en data_processing: {e}")

try:
    from src.pattern_recognition import find_complex_patterns

    print("✅ pattern_recognition importado correctamente")
except Exception as e:
    print(f"❌ Error en pattern_recognition: {e}")

try:
    from src.backtest import run_backtest, create_equity_curve_chart

    print("✅ backtest importado correctamente")
except Exception as e:
    print(f"❌ Error en backtest: {e}")

try:
    from src.macro_analysis import get_historical_macro_events, create_macro_chart

    print("✅ macro_analysis importado correctamente")
except Exception as e:
    print(f"❌ Error en macro_analysis: {e}")

try:
    from src.risk_management import drawdown_gate, exposure_gate, reconciliation_gate

    print("✅ risk_management importado correctamente")
except Exception as e:
    print(f"❌ Error en risk_management: {e}")

try:
    from src.styles import apply_futuristic_design

    print("✅ styles importado correctamente")
except Exception as e:
    print(f"❌ Error en styles: {e}")

try:
    from src.oracle import get_market_sentiment

    print("✅ oracle importado correctamente")
except Exception as e:
    print(f"❌ Error en oracle: {e}")

print("Test completado.")
