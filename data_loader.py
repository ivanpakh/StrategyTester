# data_loader.py
# Загружает CSV котировок MT5 в numpy-структуру (time -> int64 unix seconds)

import pandas as pd
import numpy as np
from pathlib import Path

DTYPE_QUOTES = np.dtype([('time', 'i8'), ('open', 'f8'), ('high', 'f8'), ('low', 'f8'), ('close', 'f8')])

def _to_unix_seconds(ts):
    # pd.Timestamp -> int (seconds)
    if pd.isna(ts):
        return np.int64(0)
    return np.int64(int(pd.Timestamp(ts).timestamp()))

def load_quotes_csv_to_numpy(csv_path, time_col='time', time_format=None):
    """
    Читает CSV и возвращает numpy-structured array dtype=DTYPE_QUOTES
    Ожидаются колонки: time, open, high, low, close (time может быть "YYYY-MM-DD HH:MM:SS" или др.)
    """
    p = Path(csv_path)
    if not p.exists():
        raise FileNotFoundError(f"{csv_path} not found")

    # Используем pandas для парсинга, затем переносим в numpy
    df = pd.read_csv(p, low_memory=False)
    # Try to detect combined datetime column: "time" or "date"+"time"
    if 'time' not in df.columns and 'datetime' in df.columns:
        df.rename(columns={'datetime': 'time'}, inplace=True)
    if 'time' not in df.columns and 'Date' in df.columns and 'Time' in df.columns:
        df['time'] = df['Date'].astype(str) + ' ' + df['Time'].astype(str)

    if 'time' not in df.columns:
        raise ValueError("No 'time' column found in CSV")

    # Parse datetime
    df['time'] = pd.to_datetime(df['time'], infer_datetime_format=True, errors='coerce')
    # Ensure numeric price columns
    for col in ['open', 'high', 'low', 'close']:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in CSV")
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce')

    df = df.dropna(subset=['time', 'open', 'high', 'low', 'close']).sort_values('time').reset_index(drop=True)

    arr = np.empty(len(df), dtype=DTYPE_QUOTES)
    arr['time'] = df['time'].apply(_to_unix_seconds).astype('i8')
    arr['open'] = df['open'].astype('f8').values
    arr['high'] = df['high'].astype('f8').values
    arr['low'] = df['low'].astype('f8').values
    arr['close'] = df['close'].astype('f8').values
    return arr
