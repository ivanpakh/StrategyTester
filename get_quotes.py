import MetaTrader5 as mt5
import pandas as pd
import os
import subprocess
import time
from datetime import datetime

# -----------------------------------------------------------
# Пользовательские параметры
# -----------------------------------------------------------
symbol = input("Введите символ (например XAUUSD): ").strip().upper()
date_from = input("Дата начала (в формате YYYY-MM-DD): ").strip()
date_to = input("Дата конца (в формате YYYY-MM-DD): ").strip()

# -----------------------------------------------------------
# Все доступные таймфреймы от 1M до 1D
# -----------------------------------------------------------
TIMEFRAMES = {
    "M1": mt5.TIMEFRAME_M1,
    "M2": mt5.TIMEFRAME_M2,
    "M3": mt5.TIMEFRAME_M3,
    "M4": mt5.TIMEFRAME_M4,
    "M5": mt5.TIMEFRAME_M5,
    "M6": mt5.TIMEFRAME_M6,
    "M10": mt5.TIMEFRAME_M10,
    "M12": mt5.TIMEFRAME_M12,
    "M15": mt5.TIMEFRAME_M15,
    "M20": mt5.TIMEFRAME_M20,
    "M30": mt5.TIMEFRAME_M30,
    "H1": mt5.TIMEFRAME_H1,
    "H2": mt5.TIMEFRAME_H2,
    "H3": mt5.TIMEFRAME_H3,
    "H4": mt5.TIMEFRAME_H4,
    "H6": mt5.TIMEFRAME_H6,
    "H8": mt5.TIMEFRAME_H8,
    "H12": mt5.TIMEFRAME_H12,
    "D1": mt5.TIMEFRAME_D1
}

# -----------------------------------------------------------
# Путь к терминалу (укажи, если MT5 установлен в другом месте)
# -----------------------------------------------------------
MT5_PATH = r"C:\Program Files\MetaTrader 5\terminal64.exe"

# -----------------------------------------------------------
# Проверка и запуск MT5 при необходимости
# -----------------------------------------------------------
def ensure_mt5_running():
    if not mt5.initialize():
        print("⚠️ MT5 не запущен. Пробую запустить вручную...")
        subprocess.Popen([MT5_PATH])
        time.sleep(7)  # даём MT5 время на загрузку
        if not mt5.initialize():
            raise ConnectionError("❌ Не удалось подключиться к MetaTrader 5.")
    print("✅ MetaTrader 5 подключен.")

# -----------------------------------------------------------
# Основная функция выгрузки
# -----------------------------------------------------------
def export_quotes(symbol: str, date_from: str, date_to: str):
    from_date = pd.Timestamp(date_from)
    to_date = pd.Timestamp(date_to)

    quotes_folder = os.path.join(os.path.dirname(__file__), "quotes_data")
    os.makedirs(quotes_folder, exist_ok=True)

    total_frames = len(TIMEFRAMES)
    done = 0

    for tf_name, tf_const in TIMEFRAMES.items():
        done += 1
        print(f"\n[{done}/{total_frames}] 📈 {symbol} {tf_name}")

        rates = mt5.copy_rates_range(symbol, tf_const, from_date, to_date)
        if rates is None or len(rates) == 0:
            print(f"⚠️ Нет данных для {symbol} {tf_name}")
            continue

        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s")

        file_name = f"{symbol}_{tf_name}_{date_from}_to_{date_to}.csv"
        file_path = os.path.join(quotes_folder, file_name)
        df.to_csv(file_path, index=False)

        print(f"✅ {len(df)} строк сохранено в {file_path}")

# -----------------------------------------------------------
# Точка входа
# -----------------------------------------------------------
def main():
    ensure_mt5_running()
    try:
        export_quotes(symbol, date_from, date_to)
    finally:
        mt5.shutdown()
        print("\n🏁 Завершено.")

if __name__ == "__main__":
    main()
