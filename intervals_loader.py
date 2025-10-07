# intervals_loader.py
# Загружает ApprovedLongs/ApprovedShorts в numpy-структуру
# Ожидаемый CSV формат: date1,date2,openDate1,openDate2,closeDate1,closeDate2,price1,price2
# Даты могут быть в формате 'YYYY-MM-DD HH:MM:SS'

import pandas as pd
import numpy as np
from pathlib import Path

DTYPE_INTERVAL = np.dtype([
    ('date1','i8'), ('date2','i8'),
    ('opendate1','i8'), ('opendate2','i8'),
    ('closedate1','i8'), ('closedate2','i8'),
    ('price1','f8'), ('price2','f8')
])

def _to_unix_seconds(ts):
    if pd.isna(ts):
        return np.int64(0)
    return np.int64(int(pd.Timestamp(ts).timestamp()))

def load_intervals_csv(path):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)

    df = pd.read_csv(p, low_memory=False)
    # Ensure required columns
    required = ['date1','date2','openDate1','openDate2','closeDate1','closeDate2','price1','price2']
    cols_lower = {c.lower(): c for c in df.columns}
    # Normalize names: allow case-insensitive
    mapping = {}
    for r in required:
        rl = r.lower()
        if rl in cols_lower:
            mapping[cols_lower[rl]] = r
        else:
            raise ValueError(f"Required column '{r}' not found in {path}")

    df = df.rename(columns=mapping)
    # parse datetimes
    for dtcol in ['date1','date2','openDate1','openDate2','closeDate1','closeDate2']:
        df[dtcol] = pd.to_datetime(df[dtcol], infer_datetime_format=True, errors='coerce')

    for pcol in ['price1','price2']:
        df[pcol] = pd.to_numeric(df[pcol].astype(str).str.replace(',','.'), errors='coerce')

    df = df.dropna(subset=['date1','date2','openDate1','openDate2','closeDate1','closeDate2','price1','price2']).reset_index(drop=True)

    arr = np.empty(len(df), dtype=DTYPE_INTERVAL)
    arr['date1'] = df['date1'].apply(_to_unix_seconds).astype('i8')
    arr['date2'] = df['date2'].apply(_to_unix_seconds).astype('i8')
    arr['opendate1'] = df['openDate1'].apply(_to_unix_seconds).astype('i8')
    arr['opendate2'] = df['openDate2'].apply(_to_unix_seconds).astype('i8')
    arr['closedate1'] = df['closeDate1'].apply(_to_unix_seconds).astype('i8')
    arr['closedate2'] = df['closeDate2'].apply(_to_unix_seconds).astype('i8')
    arr['price1'] = df['price1'].astype('f8').values
    arr['price2'] = df['price2'].astype('f8').values
    return arr
