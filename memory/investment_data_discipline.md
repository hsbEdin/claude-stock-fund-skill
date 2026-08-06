---
name: investment-data-discipline
description: 投资分析前必须校验时间、数据、指标，不可凭记忆或近似值
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 6dc93982-c6cf-44f8-80e2-9ff34cd1805b
---

## 投资分析数据纪律

每次回答投资相关问题（行情、走势、个股分析、辩论、portfolio），必须按以下顺序检查：

### 强制验证流程

1. **先确认当前时间**：调用 current_timestamp(format="datetime") 获取北京时间，标注在回复开头
2. **美股数据必须标注日期**：明确是「X月X日收盘」还是「盘前/盘中」，不能混用。美股收盘 = 北京时间凌晨 4:00，当晚 21:30 开盘
3. **A股实时行情只用新浪API**：`curl -s -H 'Referer: https://finance.sina.com.cn' 'https://hq.sinajs.cn/list=szXXXXXX' | iconv -f gbk -t utf-8`。**禁止使用 Tushare MCP stock_data**（已验证返回2025年旧数据），禁止使用东方财富 push2 API（编码混乱）。详见 [[data-source-config]]
4. **A股数据必须标注实时性**：明确是「今日盘中 14:30」还是「X月X日收盘」，截取API返回的时间戳
5. **所有数字必须有来源**：现价 = 新浪API实时拉取，不能凭记忆或估算
6. **百分比必须同级对比**：单日涨跌和累计涨跌不能混在同一段，累计数据必须标注起止日期
7. **预测必须先检查外生变量**：周末/节后必查地缘政治、美伊局势、油价、重大政策

**Why:** 7/10 预测失误因漏掉地缘事件。7/14 把盘前当收盘。7/15 时间尺度混用。2026-08-05 发现Tushare MCP stock_data返回的是2025年旧数据（新易盛183 vs 实际417），东方财富API编码混乱。**已验证只有新浪API返回正确价格。**

**How to apply:** 每次回答投资问题前先跑 current_timestamp，在第一行标注时间。A股现价只信新浪API。美股数据标注日期。预测走势前先搜「周末/隔夜重大事件」。
