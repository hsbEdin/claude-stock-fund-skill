#!/usr/bin/env python3
"""⭐ 新浪API数据获取（主力）+ 腾讯/天天基金备选。

新浪API是唯一经过验证的A股实时行情来源（2026-08-05验证）。
Tushare MCP stock_data 已弃用（返回2025年旧数据）。
东方财富 push2 API 已弃用（编码混乱）。

用法:
  python3 akshare_fetch.py stock 600309 20260501 20260604   # 日线+指标（腾讯备选）
  python3 akshare_fetch.py fund 016873 20260501             # 基金净值（天天基金）
  python3 akshare_fetch.py index 000300 20260501 20260604   # 指数（腾讯备选）
  python3 akshare_fetch.py spot 600309                      # ⭐ 实时快照（新浪API）
"""
import sys, json, time, re
import requests
import ssl
try:
    from urllib3 import PoolManager
except ImportError:
    pass

# --- 网络层 ---
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Referer": "https://finance.sina.com.cn",
}

def get(url, params=None, retry=2):
    """带重试的 GET"""
    for i in range(retry):
        try:
            r = requests.get(url, params=params, headers=HEADERS, timeout=10)
            if r.status_code == 200:
                return r
        except Exception:
            if i == retry - 1:
                raise
            time.sleep(1)

# --- 股票历史行情（腾讯） ---
def fetch_stock(code, start, end):
    """腾讯日K线 + 计算 MA/RSI/MACD"""
    symbol = code.split(".")[0]
    market = "sh" if code.endswith(".SH") else "sz"
    try:
        r = get("https://web.ifzq.gtimg.cn/appstock/app/fqkline/get",
                params={"param": f"{market}{symbol},day,{start},{end},300,qfq"})
        data = r.json()
        # data['data'] 是 dict: {'sh600309': {'qfqday': [[...]]}}
        stock_data = data.get("data")
        if not isinstance(stock_data, dict):
            return {"error": f"unexpected data type: {type(stock_data)}"}
        klines = None
        for k, v in stock_data.items():
            if isinstance(v, dict):
                klines = v.get("qfqday") or v.get("day")
                break
        if not klines:
            return {"error": "no klines found"}
        if not klines:
            return {"error": "no data from tencent"}
        rows = []
        for k in klines[-30:]:
            d = k[0]
            rows.append({
                "trade_date": d,
                "open": float(k[1]), "close": float(k[2]),
                "high": float(k[3]), "low": float(k[4]),
                "vol": float(k[5]), "amount": float(k[6]) if len(k) > 6 else 0
            })
        # 计算指标
        closes = [r["close"] for r in rows]
        for i in range(len(rows)):
            if i >= 4:
                rows[i]["MA5"] = round(sum(closes[i-4:i+1])/5, 2)
            if i >= 19:
                rows[i]["MA20"] = round(sum(closes[i-19:i+1])/20, 2)
            if i >= 59:
                rows[i]["MA60"] = round(sum(closes[i-59:i+1])/60, 2)
        # RSI(14)
        if len(closes) >= 15:
            deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
            gains = [max(d, 0) for d in deltas]
            losses = [max(-d, 0) for d in deltas]
            avg_gain = sum(gains[-14:]) / 14
            avg_loss = sum(losses[-14:]) / 14
            if avg_loss == 0:
                rsi_val = 100
            else:
                rs = avg_gain / avg_loss
                rsi_val = round(100 - 100/(1+rs), 2)
            rows[-1]["RSI"] = rsi_val
        # MACD(12,26,9)
        ema12 = closes[0]
        ema26 = closes[0]
        macd_dif = macd_dea = macd_val = 0
        for i, c in enumerate(closes):
            ema12 = c * 2/(12+1) + ema12 * (1 - 2/(12+1))
            ema26 = c * 2/(26+1) + ema26 * (1 - 2/(26+1))
            dif = ema12 - ema26
            dea_old = macd_dea
            macd_dea = dif * 2/(9+1) + macd_dea * (1 - 2/(9+1))
            macd_val = 2 * (dif - macd_dea)
            if i == len(closes) - 1:
                rows[-1]["MACD_DIF"] = round(dif, 4)
                rows[-1]["MACD_DEA"] = round(macd_dea, 4)
                rows[-1]["MACD"] = round(macd_val, 4)
        return rows
    except Exception as e:
        return {"error": str(e)}

# --- 实时快照（新浪） ---
def fetch_spot(code):
    """新浪实时行情，已测试通过"""
    symbol = code.split(".")[0]
    prefix = "sh" if code.endswith(".SH") else "sz"
    try:
        r = get(f"https://hq.sinajs.cn/list={prefix}{symbol}")
        text = r.text
        # 解析: var hq_str_sh600309="名称,今开,昨收,现价,最高,最低,..."
        match = re.search(r'"([^"]+)"', text)
        if not match:
            return {"error": "parse failed"}
        parts = match.group(1).split(",")
        if len(parts) < 32:
            return {"error": f"too few fields: {len(parts)}"}
        return {
            "name": parts[0],
            "open": float(parts[1]),
            "close_yesterday": float(parts[2]),
            "price": float(parts[3]),
            "high": float(parts[4]),
            "low": float(parts[5]),
            "volume": int(float(parts[8])),
            "amount": float(parts[9]),
            "change_pct": round((float(parts[3]) - float(parts[2])) / float(parts[2]) * 100, 2),
            "pe": float(parts[38]) if len(parts) > 38 and parts[38] else None,
        }
    except Exception as e:
        return {"error": str(e)}

# --- 指数（腾讯） ---
def fetch_index(code, start, end):
    """腾讯指数行情"""
    idx_map = {"000001": "sh000001", "000300": "sh000300", "399001": "sz399001", "399006": "sz399006"}
    key = idx_map.get(code, f"sh{code}")
    raw_start, raw_end = start.replace("-", ""), end.replace("-", "")
    try:
        url = f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
        r = get(url, params={"param": f"{key},day,{raw_start},{raw_end},30,qfq"})
        data = r.json()
        klines = data.get("data", {}).get(key, {}).get("day", [])
        if not klines:
            return {"error": "no index data from tencent"}
        return [{"trade_date": k[0], "open": float(k[1]), "close": float(k[2]), "high": float(k[3]), "low": float(k[4]), "vol": float(k[5])} for k in klines]
    except Exception as e:
        return {"error": str(e)}

# --- 基金净值（天天基金） ---
def fetch_fund(code, start):
    """天天基金净值"""
    raw_start = start.replace("-", "")
    try:
        url = f"https://api.fund.eastmoney.com/f10/lsjz"
        params = {"fundCode": code, "pageIndex": 1, "pageSize": 10, "startDate": raw_start, "endDate": ""}
        headers = {**HEADERS, "Referer": "https://fundf10.eastmoney.com/"}
        r = requests.get(url, params=params, headers=headers, timeout=10)
        data = r.json()
        items = data.get("Data", {}).get("LSJZList", [])
        if not items:
            return {"error": "no fund data"}
        return [{"nav_date": it["FSRQ"], "nav": float(it["DWJZ"]), "accumulated_nav": float(it.get("LJJZ", 0))} for it in items]
    except Exception as e:
        return {"error": str(e)}

# --- main ---
if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    try:
        if cmd == "stock":
            result = fetch_stock(sys.argv[2], sys.argv[3], sys.argv[4])
        elif cmd == "fund":
            result = fetch_fund(sys.argv[2], sys.argv[3])
        elif cmd == "index":
            result = fetch_index(sys.argv[2], sys.argv[3], sys.argv[4])
        elif cmd == "spot":
            result = fetch_spot(sys.argv[2])
        else:
            result = {"error": f"unknown cmd: {cmd}", "usage": "stock/fund/index/spot"}
    except Exception as e:
        result = {"error": str(e)}
    print(json.dumps(result, ensure_ascii=False, default=str))
