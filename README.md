# Claude Stock & Fund Debate Skills

A股股票 + 基金多智能体辩论分析工具。让 Claude Code 化身你的7人投资研究团队。

## 安装

### 1. 安装插件

```bash
# 添加市场
claude plugin marketplace add hsbEdin/claude-stock-fund-skill

# 安装插件
claude plugin install claude-stock-fund-skill@claude-stock-fund-skill
```

### 2. 安装 Python 依赖

```bash
pip install baostock pandas
```

### 3. 配置 MCP 数据源

需要 `finance-data-server` MCP 服务（提供 Tushare 行情/资金/新闻数据）。在 `~/.claude/settings.json` 的 `mcpServers` 中添加：

```json
{
  "mcpServers": {
    "finance-data-server": {
      "url": "http://<你的Tushare API服务地址>/sse",
      "type": "sse",
      "timeout": 600
    }
  }
}
```

## 使用

### 股票多空辩论

```
/a-stock-debate 600309
/a-stock-debate 000063
```

**工作流：** 并行拉取技术面/资金面/基本面/消息面数据 → 多方分析师 → 空方逐条反驳 → 风控挖隐藏风险 → 研究主管裁决 → BUY/SELL/HOLD

### 基金多空辩论

```
/fund-debate 166002
/fund-debate 016873
```

**工作流：** 并行拉取净值/经理/持仓/基准数据 → 多方论证 → 空方反驳 → 风控评估 → 申购/持有/赎回

## 数据源架构

| 数据维度 | 数据源 | 频率限制 |
|---------|--------|---------|
| 技术指标(MACD/RSI/KDJ/BOLL/MA) | Tushare MCP | 宽松 |
| 资金流向 + 融资融券 | Tushare MCP | 宽松 |
| 财经新闻 | Tushare MCP | 无限制 |
| 公司基本信息/行业 | **BaoStock** | **无限制** |
| 利润/成长/偿债指标 | **BaoStock** | **无限制** |
| PE/PB估值 | **BaoStock** | **无限制** |
| 大盘指数 | **BaoStock** | **无限制** |

双数据源确保基本面数据不受 Tushare 频率限制影响。

## 优化特性

- **Token 节省：** Agent 只接收数据摘要而非原始表格，每场辩论节省 ~20K tokens
- **智能触发：** "分析XXX"只给5行摘要，"全面分析XXX"或 `/a-stock-debate` 才触发完整辩论
- **独立脚本：** BaoStock 数据拉取独立为可复用脚本

## 依赖

- Claude Code CLI
- Python 3.9+ (baostock, pandas)
- finance-data-server MCP (Tushare 数据)
- macOS / Linux

## 许可证

MIT
