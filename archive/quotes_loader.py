import os
import pandas as pd
import chardet
from pathlib import Path

DATA_FOLDER = Path("../quotes_data")  # папка с CSV


def load_quotes(symbol: str, timeframe: str) -> pd.DataFrame:
    """
    Загружает котировки из CSV для заданного инструмента и таймфрейма.

    :param symbol: например "XAUUSD"
    :param timeframe: например "H1", "M5", "D1"
    :return: pandas DataFrame с котировками
    """
    # Ищем файл в папке
    files = list(DATA_FOLDER.glob(f"{symbol}_{timeframe}_*.csv"))
    if not files:
        raise FileNotFoundError(f"Файл для {symbol} {timeframe} не найден в {DATA_FOLDER}")

    file_path = files[0]
    print(f"Загружаем: {file_path}")

    # Определяем кодировку автоматически
    with open(file_path, 'rb') as f:
        enc = chardet.detect(f.read(10000))['encoding']

    df = pd.read_csv(file_path, encoding=enc, sep=',')

    # Преобразуем колонку времени
    if 'time' in df.columns:
        df['time'] = pd.to_datetime(df['time'], errors='coerce')

    # Сортируем по времени и ставим индекс
    df = df.sort_values('time').reset_index(drop=True)
    return df
