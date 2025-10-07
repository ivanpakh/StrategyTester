# tester_hybrid.py
# Быстрый тестер: CPU-реализация с numba (parallel),
# опционально здесь можно добавить GPU-реализацию позднее.

import numpy as np
from numba import njit, prange

# сигнальные типы: 1 = SHORT, 2 = LONG (как в твоем MQL)
# Подготовь signals как numpy structured array:
# dtype_signals = np.dtype([('time','i8'), ('price','f8'), ('type','i4')])

@njit
def _compute_max_lengths_cpu(approved_shorts, approved_longs, quotes_time, quotes_high, quotes_low):
    max_shorts = 0.0
    max_longs = 0.0
    # approved_shorts/longs have fields in order of DTYPE_INTERVAL
    for i in range(approved_shorts.shape[0]):
        d1 = approved_shorts[i]['date1']
        d2 = approved_shorts[i]['date2']
        idx1 = np.searchsorted(quotes_time, d1)
        idx2 = np.searchsorted(quotes_time, d2)
        # safety bounds
        if idx1 >= quotes_high.shape[0]: idx1 = quotes_high.shape[0]-1
        if idx2 >= quotes_low.shape[0]: idx2 = quotes_low.shape[0]-1
        max_shorts += (quotes_high[idx1] - quotes_low[idx2])

    for i in range(approved_longs.shape[0]):
        d1 = approved_longs[i]['date1']
        d2 = approved_longs[i]['date2']
        idx1 = np.searchsorted(quotes_time, d1)
        idx2 = np.searchsorted(quotes_time, d2)
        if idx1 >= quotes_low.shape[0]: idx1 = quotes_low.shape[0]-1
        if idx2 >= quotes_high.shape[0]: idx2 = quotes_high.shape[0]-1
        max_longs += (quotes_high[idx2] - quotes_low[idx1])

    return max_shorts, max_longs

@njit(parallel=True)
def _compute_sums_cpu(signals, approved_shorts, approved_longs, quotes_time, quotes_high, quotes_low):
    n_sig = signals.shape[0]
    summ_shorts_arr = np.zeros(n_sig, dtype=np.float64)
    summ_longs_arr = np.zeros(n_sig, dtype=np.float64)

    # For each signal (parallel)
    for i in prange(n_sig):
        t = signals[i]['time']
        typ = signals[i]['type']

        if typ == 1:  # SHORT
            for j in range(approved_shorts.shape[0]):
                sh = approved_shorts[j]
                if sh['opendate1'] <= t <= sh['opendate2']:
                    idx1 = np.searchsorted(quotes_time, sh['date1'])
                    idx2 = np.searchsorted(quotes_time, sh['date2'])
                    if idx1 >= quotes_high.shape[0]: idx1 = quotes_high.shape[0]-1
                    if idx2 >= quotes_low.shape[0]: idx2 = quotes_low.shape[0]-1
                    summ_shorts_arr[i] += (quotes_high[idx1] - quotes_low[idx2])
                    break  # signal matched this approved interval (MQL logic uses first match)
                elif sh['opendate2'] < t <= sh['closedate2']:
                    idx = np.searchsorted(quotes_time, t)
                    if idx >= quotes_high.shape[0]: idx = quotes_high.shape[0]-1
                    # linear proportion: (price_at_signal - price2) / (price1 - price2) * (price1 - price2)
                    # simplifies to price_at_signal - price2
                    summ_shorts_arr[i] += (quotes_high[idx] - sh['price2'])
                    break

        elif typ == 2:  # LONG
            for j in range(approved_longs.shape[0]):
                lo = approved_longs[j]
                if lo['opendate1'] <= t <= lo['closedate1']:
                    idx = np.searchsorted(quotes_time, t)
                    if idx >= quotes_low.shape[0]: idx = quotes_low.shape[0]-1
                    # linear proportion simplifies to price2 - price_at_signal
                    summ_longs_arr[i] += (lo['price2'] - quotes_low[idx])
                    break
                elif lo['closedate1'] < t <= lo['date2']:
                    # contributes 0
                    break

    total_summ_shorts = 0.0
    total_summ_longs = 0.0
    for i in range(n_sig):
        total_summ_shorts += summ_shorts_arr[i]
        total_summ_longs += summ_longs_arr[i]

    return total_summ_shorts, total_summ_longs

def evaluate_strategy(signals, approved_shorts, approved_longs, quotes_m1,
                      xa=1.0, yb=4.0, backend='auto'):
    """
    signals: numpy structured array dtype = [('time','i8'),('price','f8'),('type','i4')]
    approved_shorts/approved_longs: numpy structured arrays dtype DTYPE_INTERVAL
    quotes_m1: numpy structured array dtype [('time','i8'),('open','f8'),('high','f8'),('low','f8'),('close','f8')]
    backend: 'auto'|'cpu'|'gpu'  (gpu not implemented here; fallback to cpu)
    """
    # prepare plain arrays for numba
    quotes_time = quotes_m1['time']
    quotes_high = quotes_m1['high']
    quotes_low = quotes_m1['low']

    # compute max lengths (CPU, cheap)
    max_shorts, max_longs = _compute_max_lengths_cpu(approved_shorts, approved_longs, quotes_time, quotes_high, quotes_low)

    # compute sums per signals (parallel CPU)
    summ_shorts, summ_longs = _compute_sums_cpu(signals, approved_shorts, approved_longs, quotes_time, quotes_high, quotes_low)

    # compute percentages and OptResult
    x = 100.0 * summ_shorts / max_shorts if max_shorts != 0.0 else 0.0
    y = 100.0 * summ_longs / max_longs if max_longs != 0.0 else 0.0

    opt_result = 10000.0 * (x / 100.0) ** xa * (1.0 - y / 100.0) ** yb
    return opt_result, {'x': x, 'y': y, 'summ_shorts': summ_shorts, 'max_shorts': max_shorts,
                        'summ_longs': summ_longs, 'max_longs': max_longs}
