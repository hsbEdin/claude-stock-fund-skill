---
name: stock-analysis-checklist
description: "All analysis commands are manual on-demand only. Only /thesis has auto-reminder."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 8766ff69-aece-4f5e-95af-36b15c86b7ef
---

**For casual mentions like "分析XXX" or "XXX怎么样":** Pull a brief summary — latest price, PE, recent trend, 1 key risk (3-5 lines). Pull stock_data + company_performance(indicators) only. Do NOT spawn debate agents.

**For "/a-stock-debate XXX" or "/fund-debate XXX":** Run the full pipeline as defined in the respective command files.

**All other commands (/portfolio, /morning-brief, /fund-debate) are manual/on-demand only.** User must explicitly type the slash command to trigger them.

**Exception — /thesis reminder:** Once a week, if the user hasn't run `/thesis review`, display a prominent reminder. Format:

```
┌──────────────────────────────────────────────────────────────┐
│  ⚠️ /thesis review 已 X 天未运行                               │
│                                                              │
│  当前活跃论文：N 条                                             │
│  需检查：证伪条件是否触发？论文评分是否衰减？                     │
│                                                              │
│  输入 /thesis review 开始巡检                                  │
└──────────────────────────────────────────────────────────────┘
```

Do NOT bury this in a paragraph. Use the box format above to make it unmissable.

**Why:** Quick summaries for casual mentions are useful and cheap. Full pipelines and agents should be explicit.
