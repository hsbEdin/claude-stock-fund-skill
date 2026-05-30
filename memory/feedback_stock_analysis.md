---
name: stock-analysis-checklist
description: "When user says \"分析某个股票/基金\", automatically run full combo: fundamentals + market index + news + technical analysis."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 8766ff69-aece-4f5e-95af-36b15c86b7ef
---

When the user explicitly asks to "全面分析" a stock/fund, or invokes `/a-stock-debate` or `/fund-debate`, perform comprehensive multi-dimension analysis.

**For casual mentions like "分析XXX" or "XXX怎么样":** Give a brief 3-5 line summary only (latest price, PE, recent trend, 1 key risk). Do NOT pull full data or spawn agents.

**For explicit debate commands or "全面分析":** Run the full pipeline as defined in the respective command files.

**Why:** Full analysis pulls 10+ API calls and spawns 3 agents, consuming significant tokens. Casual mentions shouldn't trigger this unless the user explicitly wants depth.

**How to apply:** Match the user's intent. "看看XXX" or "XXX怎么样" → quick summary. "全面分析XXX" or "/a-stock-debate XXX" → full pipeline.

1. **Technical** — stock_data with macd(12,26,9) rsi(14) kdj(9,3,3) boll(20,2) ma(5) ma(10) ma(20) ma(60), money_flow, margin_trade
2. **Fundamentals** — company_performance (indicators + income_all + forecast), top10_holders, holder_number
3. **News** — finance_news for the stock
4. **Market** — index_data for 000001.SH, block_trade

**Why:** User went through a full analysis flow for 000063.SZ and 601231.SH and wants this as the default behavior — no need to ask which dimensions to pull each time.

**How to apply:** Whenever the user says "分析XX股票" or "分析XX基金", pull all four dimensions in parallel in a single batch, then deliver a beginner-friendly comprehensive report with multi-empty scoring and a final conclusion.
