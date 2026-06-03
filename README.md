# Claude Stock & Fund Investment Toolkit

A股 + 基金 全链路 AI 投资工具链：选股 → 盯盘 → 纪律 → 校准。

## 安装

```bash
# 1. 添加市场
claude plugin marketplace add hsbEdin/claude-stock-fund-skill

# 2. 安装插件
claude plugin install claude-stock-fund-skill@claude-stock-fund-skill

# 3. 安装 Python 依赖
pip install baostock pandas

# 4. 初始化数据文件
cp data/portfolio.json ~/.claude/portfolio.json
cp data/thesis_ledger.json ~/.claude/thesis_ledger.json
cp data/ai_track_record.json ~/.claude/ai_track_record.json
# 编辑 portfolio.json 填入你自己的持仓
```

## 命令

### `/a-stock-debate <代码>` — 选股

7 智能体多空辩论 + 行业适配模块 + Grill-Me 压力测试 + AI 建议跟踪。

**v2.0 新增：**
- 行业适配模块：化工/半导体/通信/电力/消费电子，每类问最关键的问题
- Grill-Me 集成：辩论结束后提示第三方压力测试
- AI 建议自动写入 `ai_track_record.json`

### `/fund-debate <代码>` — 选基

7 智能体基金辩论 + 净值/经理/持仓/基准四维数据。

**v2.0 新增：**
- Phase 2.5 持仓穿透：风格漂移检测、费率分析、规模预警
- AI 建议自动跟踪

### `/portfolio` — 盯盘 (新)

组合仪表盘：实时行情、浮动盈亏、行业集中度、基准对比。

**功能：**
- 股票实时行情 + 基金净值（≥5 万且有代码的自动拉取）
- 组合 vs 沪深 300 基准对比
- 科技/周期/海外/均衡 集中度热力图
- 单票 PE > 50x、日跌幅 > 5% 自动预警

### `/thesis` — 纪律 (新)

第一性原理投资纪律 + 论文账本。

**子命令：**
- `/thesis open <代码>` — 创建可证伪论文（概率分布 + EV + 证伪条件）
- `/thesis review` — 自动巡检所有论文，计算健康评分
- `/thesis close <ID>` — 按逻辑（非盈亏）判定 PASSED/FAILED
- `/thesis stats` — 累计胜率、盈亏比、AI 正确率

**论文评分公式：** `评分 = 初始 EV% × 时间衰减系数 × 条件存活率`

## 数据文件

| 文件 | 位置 | 用途 |
|------|------|------|
| `portfolio.json` | `~/.claude/` | 持仓数据（股票代码/股数/成本，基金代码/金额/成本） |
| `thesis_ledger.json` | `~/.claude/` | 论文账本（每笔交易的证伪条件和验证记录） |
| `ai_track_record.json` | `~/.claude/` | AI 建议跟踪（每条建议的结果和正确率统计） |

## 架构

```
选股层    /a-stock-debate (辩论+行业+压力测试)
         /fund-debate    (辩论+持仓穿透)

盯盘层    /portfolio      (组合仪表盘+基准对比+风控)

纪律层    /thesis open     (可证伪论文→EV→证伪条件)
         /thesis review   (时间衰减评分+自动巡检)
         /thesis close    (逻辑判定+联动AI追踪)

校准层    ai_track_record.json (AI命中率统计)
```

## 数据源

| 数据维度 | 数据源 | 频率限制 |
|---------|--------|---------|
| 技术指标/行情 | Tushare MCP (finance-data-server) | 宽松 |
| 资金流向/融资融券 | Tushare MCP | 宽松 |
| 财经新闻 | Tushare MCP | 无限制 |
| 基本面/估值 | **BaoStock**（免费无限制） | 无限制 |
| 基金净值/持仓 | Tushare MCP | 1次/分钟 |

## 依赖

- Claude Code CLI
- Python 3.9+ (baostock, pandas)
- finance-data-server MCP (Tushare 数据)
- macOS / Linux

## 许可证

MIT
