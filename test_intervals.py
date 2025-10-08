import os
print("Текущая рабочая директория:", os.getcwd())

from Tintervals_loader import load_approved_intervals

approved_longs, approved_shorts = load_approved_intervals(
    "ApprovedTrades/ApprovedLongs.csv",
    "ApprovedTrades/ApprovedShorts.csv"
)

print("ApprovedLongs:", len(approved_longs))
print("ApprovedShorts:", len(approved_shorts))
print("Пример записи:")
print(approved_longs[0])
