import pandas as pd
import numpy as np

def load_approved_intervals(long_path: str, short_path: str):
    """
    Загружает данные ApprovedLongs и ApprovedShorts из CSV
    и преобразует их в numpy-структуры для быстрой работы.
    """

    # читаем лонги
    longs = pd.read_csv(long_path, parse_dates=["openDate1", "openDate2", "closeDate1", "closeDate2"])
    shorts = pd.read_csv(short_path, parse_dates=["openDate1", "openDate2", "closeDate1", "closeDate2"])

    # проверяем, что нужные столбцы присутствуют
    required_cols = {"openDate1", "openDate2", "closeDate1", "closeDate2", "price1", "price2"}
    if not required_cols.issubset(longs.columns) or not required_cols.issubset(shorts.columns):
        raise ValueError(f"Ожидались столбцы {required_cols}")

    # преобразуем в numpy-структуры
    approved_longs = longs.to_dict(orient="records")
    approved_shorts = shorts.to_dict(orient="records")

    return np.array(approved_longs, dtype=object), np.array(approved_shorts, dtype=object)
