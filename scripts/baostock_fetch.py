#!/usr/bin/env python3
"""BaoStock fundamentals fetcher. Usage: python3 baostock_fetch.py sh.600309 2025-02-28 2026-05-29"""
import sys, os
from datetime import date

# Suppress baostock stdout noise
import contextlib, io
import json
with contextlib.redirect_stdout(io.StringIO()):
    import baostock as bs
    import pandas as pd
    bs.login()

code_bs = sys.argv[1]       # sh.600309 or sz.000063
start_date = sys.argv[2]    # 3 months ago
end_date = sys.argv[3]      # today

bs.login()  # suppress stdout
r = {}

# Basic info + industry
for fn, args in [
    ('basic', lambda: bs.query_stock_basic(code=code_bs)),
    ('industry', lambda: bs.query_stock_industry(code=code_bs)),
]:
    try:
        rs = args()
        rows = [rs.get_row_data() for _ in range(100) if rs.next() and rs.error_code == '0']
        r[fn] = dict(cols=rs.fields, data=rows)
    except Exception as e:
        r[fn] = dict(error=str(e))

# Financials: last 4 quarters
for yr, q in [(2026,1),(2025,4),(2025,3),(2025,2)]:
    for tag, fn in [
        ('profit', bs.query_profit_data),
        ('growth', bs.query_growth_data),
        ('balance', bs.query_balance_data),
    ]:
        if tag == 'balance' and q not in (1,4):  # Only annual/Q4 for balance sheet
            continue
        try:
            rs = fn(code=code_bs, year=yr, quarter=q)
            rows = [rs.get_row_data() for _ in range(100) if rs.next() and rs.error_code == '0']
            r[f'{tag}_{yr}Q{q}'] = dict(cols=rs.fields, data=rows)
        except Exception as e:
            r[f'{tag}_{yr}Q{q}'] = dict(error=str(e))

# Index K-line (last 30 days)
try:
    rs = bs.query_history_k_data_plus(
        'sh.000001', 'date,close,pctChg', start_date, end_date, frequency='d', adjustflag='3'
    )
    rows = [rs.get_row_data() for _ in range(500) if rs.next() and rs.error_code == '0']
    r['index'] = dict(cols=rs.fields, data=rows[-30:])
except Exception as e:
    r['index'] = dict(error=str(e))

# Forecast
try:
    rs = bs.query_forecast_report(code=code_bs, year=2026, quarter=2)
    rows = [rs.get_row_data() for _ in range(100) if rs.next() and rs.error_code == '0']
    r['forecast'] = dict(cols=rs.fields, data=rows)
except:
    r['forecast'] = dict(data=[])

with contextlib.redirect_stdout(io.StringIO()):
    bs.logout()
print(json.dumps(r, indent=2, default=str))
