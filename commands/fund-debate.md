---
name: fund-debate
description: 基金多空辩论 — 净值/经理/持仓/基准四维数据，7智能体对抗，输出申赎决策
argument-hint: <6位基金代码>
---

从 $ARGUMENTS 提取6位代码，补全后缀(ETF:15/16/18→.SZ, 50/51→.SH; 场外→.OF)。调用 current_timestamp(format="date") 获取 TODAY。

---

## Phase 1 — 并行拉取

用 finance-data-server MCP 一次性并行：
1. fund_data(ts_code="XXX.XX", data_type="basic", start_date=TODAY, end_date=TODAY)
2. fund_data(ts_code="XXX.XX", data_type="nav", start_date=1年前, end_date=TODAY)
3. fund_data(ts_code="XXX.XX", data_type="manager", start_date=TODAY, end_date=TODAY)
4. fund_data(ts_code="XXX.XX", data_type="portfolio", start_date=TODAY, end_date=TODAY)
5. fund_data(ts_code="XXX.XX", data_type="dividend", start_date=2年前, end_date=TODAY)
6. finance_news(query="代码+名称")
7. index_data(code="000300.SH", start_date=3月前, end_date=TODAY)

如basic失败，尝试将后缀改为.OF重试一次。

---

## Phase 2 — 数据摘要（节省Agent Token）

从原始数据提取精简摘要（≤400字）：

```
【基本信息】名称/类型/成立日/规模/费率
【净值走势】1年前净值→最新净值，1年涨幅%，近3月涨跌幅，近期最大回撤%
【经理】姓名/从业年限/管理本基金时长/同时管理几只
【持仓】前3大重仓股/行业集中度判断
【基准对比】是否跑赢沪深300，超额收益%
```

---

## Phase 2.5 — 持仓穿透 & 风格漂移检测

如果 fund_data(ts_code="XXX.OF", data_type="portfolio") 返回了持仓数据：

1. **当前持仓 vs 历史持仓对比**：列出 top 5 重仓股的变化。如果过去 2 期 top 5 中换了 3 只以上 → 🟡「持仓换手率高，策略漂移风险」
2. **费率影响计算**：年费率 × 持有金额 = 年持有成本。如果费后跑不赢 ETF，提示换指数基金
3. **持仓 vs 基准重合度**：与基金名称暗示的投资方向对比。例如：
   - 「永赢科技智选」top 5 应该 > 60% 科技
   - 如果 top 5 里出现银行/白酒 → 🔴「风格漂移警报」
4. **规模预警**：如果规模 < 5000 万 → 清盘风险。规模 > 100 亿 → 灵活性下降

---

## Phase 3 — 多空辩论（仅传摘要+关键数据，≤600字/Agent）

依次运行3个 Agent（subagent_type="general-purpose"）：

### Agent 1 — 多方
```
你是基金多方分析师。基于数据论证申购/持有。

[插入 Phase 2 摘要]

150字以内。以"多方论点：申购/持有。理由：..."开头，以"信心度：高/中/低"结尾。
```

### Agent 2 — 空方（拿多方报告）
```
你是基金空方分析师。逐条反驳多方。

[插入 Phase 2 摘要]
多方报告：[插入]

150字以内。以"空方：谨慎/赎回。理由：..."开头，以"信心度：高/中/低"结尾。
```

### Agent 3 — 风控（拿双方报告）
```
你是基金风控分析师。找双方忽略的风险。

[插入 Phase 2 摘要]
多方：[插入] 空方：[插入]

100字以内。以"风控：风险高/中/低。关注：..."开头。
```

---

## Phase 4 — 裁决

```
## 基金辩论 — XXXXXX

| | 多方 | 空方 | 风控 |
|---|---|---|---|
| 观点 | 各一句 | | |
| 信心 | 高/中/低 | 高/中/低 | 风险 高/中/低 |

**结论：** [申购/定投/持有观望/减仓/赎回]
**理由：** [2-3句，引用关键数据]

**速览：** 1年回报% | 最大回撤% | 经理X年 | 规模X亿

**操作：** [金额/方式/期限]

> ⚠️ AI辩论，不构成投资建议。
```

## 规则
- Phase 1 所有调用一次性并行发出
- Tushare频率超限时用网络搜索补充
- Agent输入≤600字，只用摘要不传原始数据
- **AI 建议跟踪：** 辩论结束后，向 `~/.claude/ai_track_record.json` 追加一条记录，type="fund"，recommendation 为申/赎/持，status="pending"。
- 接口失败标注后继续
