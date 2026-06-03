---
name: a-stock-debate
description: A股多空辩论 — 双数据源(Tushare+BaoStock)，7智能体对抗，输出买卖决策
argument-hint: <6位股票代码>
---

从 $ARGUMENTS 提取6位代码，补全后缀(60xxx→.SH, 00/30xxx→.SZ)。调用 current_timestamp(format="date") 获取 TODAY。

---

## Phase 1 — 并行拉取（Tushare + BaoStock 同时发出）

### Tushare MCP（技术/资金/新闻）
1. stock_data(code="XXX.XX", market_type="cn", start_date=3月前, end_date=TODAY, indicators="macd(12,26,9) rsi(14) kdj(9,3,3) boll(20,2) ma(5) ma(10) ma(20) ma(60)")
2. money_flow(ts_code="XXX.XX", start_date=3月前, end_date=TODAY)
3. margin_trade(data_type="margin_detail", ts_code="XXX.XX", start_date=1月前, end_date=TODAY)
4. finance_news(query="代码+名称")

### BaoStock Python（基本面/估值/指数，免费无限制）
```bash
python3 /Users/bytedance/.claude/scripts/baostock_fetch.py sh.600xxx 三个月前 TODAY 2>/dev/null | sed '1d'
```
（代码格式：60xxx→sh.60xxxx, 00/30xxx→sz.xxxxxx）

---

## Phase 2 — 数据摘要（关键！节省Agent Token）

收集 Phase 1 所有数据后，提取以下**精简摘要**（不超过500字），只包含关键数字：

```
【技术面摘要】最新收盘价/涨跌幅、RSI/MACD状态(金叉/死叉)、均线排列、布林位置、近3月涨跌幅
【资金面摘要】近5日主力净流入/流出、60日累计净流向、融资余额趋势、近3日融资买入额
【基本面摘要】Q1营收/净利/毛利率、同比增速、ROE、PE/PB、资产负债率、行业
【大盘摘要】上证指数近1月涨跌幅
【新闻摘要】最重要的1-2条新闻标题
```

---

## Phase 3 — 多空对抗（仅传摘要+关键原始数据给Agent）

依次运行3个 Agent（subagent_type="general-purpose"），**每个Agent只给摘要+最近10日技术数据表+最新一期财务数据，不超过800字输入。**

### Agent 1 — 多方（先跑）
```
你是A股多方分析师。基于以下数据，用3个做多信号论证买入。

[插入 Phase 2 摘要]
[插入最近10日 stock_data 表]

要求：150字以内。以"多方论点：买入。理由：..."开头，以"信心度：高/中/低"结尾。
```

### Agent 2 — 空方（拿多方报告后跑）
```
你是A股空方分析师。逐条反驳多方，提出未提及的风险。

[插入 Phase 2 摘要]
多方报告：[插入多方报告]

要求：150字以内。以"空方反驳：谨慎/卖出。理由：..."开头，以"信心度：高/中/低"结尾。
```

### Agent 3 — 风控（拿双方报告后跑）
```
你是风控分析师。找出双方都忽略的隐藏风险。

[插入 Phase 2 摘要]
多方：[插入多方报告]  空方：[插入空方报告]

要求：100字以内。以"风控：风险高/中/低。关注：..."开头。
```

---

## Phase 4 — 研究主管裁决

```
## 多空辩论 — XXXXXX（股票名+行业）

| | 多方 | 空方 | 风控 |
|---|---|---|---|
| 观点 | 各一句 | | |
| 信心 | 高/中/低 | 高/中/低 | 风险 高/中/低 |

**结论：** [买入/增持/持有/减持/卖出]
**理由：** [2-3句，引用最关键数据点]

**行业适配模块：** [根据公司主业选择，最多3条最关键的问自己的问题]
- 化工/周期：MDI/产品价差趋势？产能利用率？下游开工率？
- 半导体/封测：订单可见度几个季度？客户集中度（苹果占比）？SiP/先进封装渗透率？
- 通信设备：5G/6G 资本开支周期？运营商集采份额？海外收入占比？
- 电力/能源：电价政策方向？煤价/天然气成本？新能源补贴变动？
- 消费电子：大客户新品周期？备货节奏？竞争格局？

**关键指标：** ROE=XX% | PE=XXx | 净利润增速=XX% | 毛利率=XX%

**价位：** 入场¥XX-XX | 止损¥XX | 阻力¥XX
**仓位：** [X%仓位，分X批]

**⚡ Grill-Me 压力测试：** 如果你打算按上述结论操作，先运行 `/grill-me "我要[买入/卖出]XX股票，理由是..."` ，让 AI 从五个角度挑刺：①逻辑漏洞 ②忽略的反面证据 ③仓位是否合理 ④退出条件是否清晰 ⑤如果判断错了，最大损失是多少。

> ⚠️ AI辩论，不构成投资建议。
```

---

## 规则
- Phase 1 所有调用一次性并行发出
- Phase 2 摘要必须自己从原始数据中提取关键数字，不能省略
- Agent 输入控制在800字以内，用摘要替代原始数据
- 接口失败标注后继续，不中断流程
- **AI 建议跟踪：** 辩论结束后，向 `~/.claude/ai_track_record.json` 追加一条记录：`{"date": "TODAY", "type": "stock", "ticker": "XXX.XX", "name": "股票名", "recommendation": "BUY/SELL/HOLD", "price": 当前价, "source_command": "/a-stock-debate", "verdict": "一句结论"}`。status 为 "pending"，待后续验证更新。
