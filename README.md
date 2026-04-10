# Prometheus & Grafana 从开发者视角入门教程

> **目标读者**：有一定编程基础（Go 为主），想从 0 到 1 理解监控指标全链路的开发者  
> **参考资料**：本教程基于 CloudMQ（bookie + broker）的真实 Grafana Dashboard 和 Prometheus 指标数据

---

## 教程结构

| 章节 | 主题 | 核心内容 |
|------|------|---------|
| [第一章](./ch01_prometheus_fundamentals.md) | **Prometheus 基础与指标类型** | 文本格式解析、Counter/Gauge/Histogram/Summary 四种类型详解 |
| [第二章](./ch02_promql_deep_dive.md) | **PromQL 深度解析** | 选择器、速率函数、聚合操作符，基于真实 Dashboard 表达式拆解 |
| [第三章](./ch03_grafana_panel_types.md) | **Grafana Panel 类型与指标类型映射** | 为什么这种指标用这种 Panel，逐 Panel 拆解 bookie/broker Dashboard |
| [第四章](./ch04_grafana_variables.md) | **Grafana 模板变量系统** | `$cluster`/`$instance` 的工作原理，级联变量，Regex 提取机制 |
| [第五章](./ch05_go_metrics_impl.md) | **Go 语言实现 Prometheus 指标** | 四种类型的完整 Go 代码示例，中间件模式，高基数陷阱 |
| [第六章](./ch06_metrics_classification.md) | **指标分类实战** | 黄金信号框架，Dashboard Row 组织，代码→文本→PromQL→Panel 全链路 |
| [第七章](./ch07_advanced_techniques.md) | **进阶技巧** | Recording Rules，自定义 Collector，常见 PromQL 陷阱，快速参考卡 |

---

## 学习路径建议

```
新手路径（2~3小时）：
  第一章 → 第二章 → 第三章 → 快速参考卡（第七章附录）

开发路径（4~5小时）：
  第一章 → 第二章 → 第五章 → 第六章 → 第七章

Dashboard 搭建路径（3~4小时）：
  第一章 → 第三章 → 第四章 → 第六章 → 第七章
```

---

## 关键概念速查

### 指标类型 → Panel 类型 → PromQL 模式

| 指标类型 | 典型 Grafana Panel | 典型 PromQL |
|---------|-------------------|------------|
| **Counter** | Time series（折线） | `rate(metric_total[5m])` |
| **Gauge** | Time series 或 Stat | 直接使用 `metric` |
| **Gauge（分桶）** | Stacked Graph | `sum(cloudmq_storage_write_latency_le_X) / 60` |
| **Histogram** | Time series（多分位线）| `histogram_quantile(0.99, sum(rate(metric_bucket[5m])) by (le))` |
| **Summary** | Time series（多分位线）| `metric{quantile="0.99"}` |
| **计数（健康）** | Stat / Singlestat | `count(metric == 1)` |
| **百分比** | Stat + Gauge圆弧 | `100 * count(healthy) / count(total)` |

### Dashboard 变量 → PromQL 使用规则

```promql
# 单/多选变量，永远用 =~
{cluster=~"$cluster", instance=~"$instance"}

# 级联变量：子变量 query 引用父变量
"query": "metric{cluster=~\"$cluster\", instance=~\".+\"}"

# 内置时间变量（优于硬编码）
rate(metric[$__rate_interval])
```

---

## 参考资料与支撑文件

- **Grafana Dashboards**:
  - [broker.json](./dashboards/broker.json) — CloudMQ Broker 指标 Dashboard
  - [bookie.json](./dashboards/bookie.json) — CloudMQ Bookie（BookKeeper）指标 Dashboard
- **Prometheus 原始指标数据**:
  - [broker.txt](./raw_data/broker.txt) — Broker 原始指标文本快照
  - [bookie.txt](./raw_data/bookie.txt) — Bookie 原始指标文本快照
- **详细指标字典与文档**:
  - [broker_metrics.md](./docs/broker_metrics.md) — Broker 指标全量中英文字典与解释
  - [bookie_metrics.md](./docs/bookie_metrics.md) — Bookie 指标全量中英文字典与解释
