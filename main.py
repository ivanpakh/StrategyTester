# main.py
import numpy as np
from data_loader import load_quotes_csv_to_numpy
from intervals_loader import load_intervals_csv
from tester_hybrid import evaluate_strategy

# Параметры — подстрой под свои пути
M1_file = "quotes_data/XAUUSD_M1_2016-01-01_to_2025-10-01.csv"
TF_file = "quotes_data/XAUUSD_M5_2016-01-01_to_2025-10-01.csv"
approved_shorts_csv = "data/ApprovedShorts.csv"
approved_longs_csv = "data/ApprovedLongs.csv"

# 1) Загружаем котировки M1 (для всех вычислений по ценам)
quotes_m1 = load_quotes_csv_to_numpy(M1_file)

# 2) Загружаем approved intervals
approved_shorts = load_intervals_csv(approved_shorts_csv)
approved_longs = load_intervals_csv(approved_longs_csv)

# 3) Подготовим сигнальный массив (пример)
# в реальном сценарии сигналы генерирует твоя стратегия; здесь — пример
dtype_signals = np.dtype([('time','i8'), ('price','f8'), ('type','i4')])
signals = np.array([
    (int( (np.datetime64('2016-01-04T01:00:00').astype('datetime64[s]')).astype('int') ), 1065.69, 1),
    (int( (np.datetime64('2016-01-04T02:00:00').astype('datetime64[s]')).astype('int') ), 1064.38, 1),
], dtype=dtype_signals)

# 4) Запуск тестера (xa, yb — те же веса, что в MQL)
opt_result, info = evaluate_strategy(signals, approved_shorts, approved_longs, quotes_m1, xa=1.0, yb=4.0)
print("OptResult:", opt_result)
print("Details:", info)
