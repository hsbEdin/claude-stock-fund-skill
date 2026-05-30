---
name: data-source-config
description: "Dual data source strategy for a-stock-debate: Tushare MCP for technical/money flow, BaoStock for fundamentals/valuation/index — installed 2026-05-29"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 7f59d603-dcc0-4cde-bdeb-ac1c24c12db2
---

**Why:** Tushare fundamental APIs (fina_indicator, income, top10_holders, company_basic, index_daily) frequently hit rate limits (5次/天 or 1次/小时), causing ~40-60% of Phase 1 calls to fail during debates.

**How to apply:** In `/a-stock-debate`, Phase 1 now uses:
- **Tushare MCP** (unchanged): stock_data + indicators, money_flow, margin_trade, finance_news
- **BaoStock Python** (new, free, no rate limits): company basic info, industry, profit/growth/balance financials, index K-line (上证指数), performance forecast, PE/PB valuation from K-line data
- Both groups fired in parallel during Phase 1

BaoStock code format: `sh.600309` (Shanghai), `sz.000063` (Shenzhen).

**Installed plugins for extended analysis:**
- `stock-deep-analyzer@uzi-skill` (UZI-Skill v3.5.0): 22-dimension analysis, DCF valuation, comps, earnings, scan-trap, quick-scan
- `baostock@baostock-skill`: BaoStock API reference and skill documentation
- `trading-agents-plugin@lucemia-trading-agents-plugin`: US stock multi-agent debate (yfinance-based)

[[portfolio-thesis-20260529]]
