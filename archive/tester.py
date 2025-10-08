# tester.py
import numpy as np
from numba import njit

@njit
def evaluate_strategy(signals, approved_longs, approved_shorts, quotes_m1, max_shorts, max_longs, xa=1.0, yb=4.0):
    summ_shorts = 0.0
    summ_longs = 0.0

    for signal in signals:
        t = signal['time']
        if signal['type'] == 'SHORT':
            for interval in approved_shorts:
                if interval['opendate1'] <= t <= interval['opendate2']:
                    summ_shorts += interval['price1'] - interval['price2']
                elif interval['opendate2'] < t <= interval['closedate2']:
                    price_signal = quotes_m1[np.searchsorted(quotes_m1['time'], t)]['high']
                    summ_shorts += (price_signal - interval['price2']) / (interval['price1'] - interval['price2']) * (interval['price1'] - interval['price2'])
        else:  # LONG
            for interval in approved_longs:
                if interval['opendate1'] <= t <= interval['closedate1']:
                    price_signal = quotes_m1[np.searchsorted(quotes_m1['time'], t)]['low']
                    summ_longs += (interval['price2'] - price_signal)
                elif interval['closedate1'] < t <= interval['date2']:
                    summ_longs += 0.0

    x = 100.0 * summ_shorts / max_shorts if max_shorts != 0 else 0.0
    y = 100.0 * summ_longs / max_longs if max_longs != 0 else 0.0

    opt_result = 10000.0 * (x / 100.0) ** xa * (1.0 - y / 100.0) ** yb
    return opt_result
