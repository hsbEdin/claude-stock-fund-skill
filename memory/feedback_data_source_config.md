---
name: data-source-config
description: "A股实时行情必须用新浪API（唯一准确来源），Tushare/东方财富/雪球均不可靠 — 2026-08-05 验证"
metadata: 
  node_type: memory
  type: feedback
  updated: 2026-08-05
  originSessionId: e566810b-1e20-4289-9eac-a8e904bc9b15
---

## ⭐ 实时行情：新浪API（唯一准确，必须优先）

**经过2026-08-05严格验证：新浪API是唯一返回正确实时价格的来源。**

### Bash 直接调用（无依赖）

```bash
curl -s -H 'Referer: https://finance.sina.com.cn' \
     -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36' \
     'https://hq.sinajs.cn/list=sz300502,sz300308,sz300394' | iconv -f gbk -t utf-8
```

代码规则：上海 `sh`+代码，深圳 `sz`+代码。多个代码逗号分隔。

解析格式：`名称,今开,昨收,现价,最高,最低,买价,卖价,成交股数,成交金额,...,日期,时间`

### Python 脚本（AKShare备选）

```bash
python3 scripts/akshare_fetch.py spot 600309  # 单只实时快照
```

内部使用相同的 Referer + User-Agent 策略调用新浪API。

## ⚠️ 已弃用的数据源

| 数据源 | 问题 | 验证日期 |
|--------|------|----------|
| **Tushare MCP stock_data** | 返回旧数据（2025年而非2026年），价格完全错误 | 2026-08-05 |
| **东方财富 push2 API** | JSON编码单位不透明（分/厘混用），易解析错误 | 2026-08-05 |
| **东方财富网页** | JS动态渲染，WebFetch无法获取 | 2026-08-05 |
| **雪球 API** | 需登录认证，被封 | 2026-08-05 |

## Tushare MCP 保留用途（仅基本面/资金面）

`stock_data` 已弃用，但以下接口仍可用于非实时数据：
- `money_flow` — 资金流向
- `margin_trade` — 融资融券
- `finance_news` — 财经新闻
- `index_data` — 指数K线（但建议交叉验证）
- `company_performance` — 财务指标（如可用）

## 基金数据

- 天天基金API (`fundgz.1234567.com.cn`) — 经常被封，不优先
- `fund_data` MCP — 如返回数据可用，否则用新浪API交叉验证
- 基金代码通过东方财富搜索获取

## 已安装插件

- `stock-deep-analyzer@uzi-skill`: 深度分析（22维+51评委）
- `baostock@baostock-skill`: BaoStock 基本面数据
- `trading-agents-plugin@lucemia-trading-agents-plugin`: 美股辩论

