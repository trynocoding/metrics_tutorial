# 第三章：Grafana Panel 类型与指标类型的映射关系

> 本章从 `bookie.json` 和 `broker.json` 两个真实 Dashboard 入手，  
> 讲清楚"为什么这个指标用这种 Panel"——这不是随意选择，而是有规律可循。

---

## 1. Panel 类型总览

在你的两个 Dashboard 文件中，出现了以下 Panel 类型：

| Panel 类型 | 在 JSON 中的标识 | 典型用途 |
|-----------|----------------|---------|
| **Graph** (老版) / **Time series** (新版) | `"type": "graph"` | 时间维度的折线图 |
| **Singlestat** (老版) / **Stat** (新版) | `"type": "singlestat"` | 单一数值大字展示 |
| **Row** | `"type": "row"` | 分组折叠 |
| **Gauge** | `"gauge": {"show": true, ...}` | 嵌在 Singlestat 里的仪表盘 |

> 注意：你的 dashboard 使用的是 Grafana 5.x/7.x 时代的旧组件（`graph`, `singlestat`）。  
> Grafana 8+ 推荐用 `timeseries`, `stat`, `gauge` 等新组件，功能更强。

---

## 2. 指标类型 → Panel 类型 的决策树

```
你有什么样的指标？
│
├── Gauge（当前状态值）
│   ├── 需要看趋势变化  → Time series（折线图）
│   └── 只看当前值      → Stat / Singlestat
│
├── Counter（累计次数）
│   ├── 主要看速率趋势  → Time series (配合 rate/irate PromQL)
│   └── 需要看总量      → Stat（显示当前累计值）
│
├── Histogram（分布）
│   ├── 看延迟分位数趋势 → Time series（p50/p99/p999各一条线）
│   └── 看分布形状       → 堆积折线图（Stacked Graph，各桶为一条线）
│
└── Summary（预计算分位数）
    └── 看延迟趋势       → Time series（直接用 quantile 标签）
```

---

## 3. 逐 Panel 拆解：bookie Dashboard

### 3.1 Singlestat：Writable Bookies

```json
{
    "type": "singlestat",
    "title": "Writable Bookies",
    "targets": [{
        "expr": "count(bookie_SERVER_STATUS{job=~\"$job\"} == 1)"
    }]
}
```

**为什么用 Singlestat？**
- `bookie_SERVER_STATUS` 是 **Gauge**，值为 0（只读）或 1（可写）
- `count(...==1)` 得到的是一个**即时数值**（当前可写 bookie 数）
- 运维人员第一眼需要看到的是"现在有几台 bookie 可写"，不需要历史趋势
- 📌 **规律**：表达"当前状态/数量"的关键健康指标 → Singlestat / Stat

**JSON 关键字段解析**：

```json
{
    "colorBackground": false,  // 是否根据阈值改变背景色
    "colorValue": false,       // 是否根据阈值改变数值颜色
    "thresholds": "",          // 阈值（格式: "80,90"）
    "gauge": {                 // 是否显示仪表盘样式
        "show": false
    },
    "valueName": "avg"         // 取查询结果的哪个值：avg/current/min/max/total
}
```

### 3.2 Singlestat + Gauge：Writable Bookies (percentage)

```json
{
    "type": "singlestat",
    "title": "writable bookies (percentage)",
    "format": "percent",
    "gauge": {
        "show": true,           // 显示仪表盘圆弧
        "maxValue": 100,
        "minValue": 0
    },
    "thresholds": "80,90",     // < 80% 红色, 80-90% 黄色, > 90% 绿色
    "colors": ["#d44a3a", "rgba(237, 129, 40, 0.89)", "#299c46"],
    "targets": [{
        "expr": "100 * count(bookie_SERVER_STATUS==1) / count(bookie_SERVER_STATUS)"
    }],
    "valueName": "current"
}
```

**为什么 Singlestat 不是 Graph？**
- 百分比是结果指标（outcome metric），运维更关心"现在是否达标"
- 配合颜色阈值，一眼看出红/黄/绿状态
- 📌 **规律**：百分比健康指标 + 阈值告警 → Singlestat with Gauge enabled

**阈值颜色映射**：

```
colors: ["#d44a3a", "rgba(237, 129, 40, 0.89)", "#299c46"]
         ↑ 红色           ↑ 橙色                   ↑ 绿色
thresholds: "80,90"
         ↑ 第一阈值 80    ↑ 第二阈值 90
```

映射关系：
- 值 < 80  → 红色（严重）
- 80 ≤ 值 < 90 → 橙色（警告）
- 值 ≥ 90  → 绿色（健康）

### 3.3 Graph：Success Rate

```json
{
    "type": "graph",
    "title": "Success Rate",
    "lines": true,
    "fill": 0,              // 折线下方不填充
    "targets": [
        {
            "expr": "100 * sum(irate(bookkeeper_server_ADD_ENTRY_count{success=\"true\"}[30s])) / sum(irate(bookkeeper_server_ADD_ENTRY_count[30s]))",
            "legendFormat": "add_entry"
        },
        {
            "expr": "...",  // read_entry 成功率
            "legendFormat": "read_entry"
        }
    ],
    "yaxes": [{"format": "short", "min": "0"}]
}
```

**为什么用 Graph？**
- 成功率随时间变化才是有意义的（突然下降说明有问题）
- 两条线（add/read）方便对比
- 📌 **规律**：基于 Counter 计算的速率/百分比趋势 → Graph/Time series

### 3.4 Graph：Latency（多分位数）

```json
{
    "type": "graph",
    "title": "Latency",
    "yaxes": [{"format": "ms", "min": "0"}],
    "targets": [
        {"expr": "avg(bookkeeper_server_ADD_ENTRY_REQUEST{quantile=\"0.99\"})",  "legendFormat": "add (p99)"},
        {"expr": "avg(bookkeeper_server_ADD_ENTRY_REQUEST{quantile=\"0.999\"})", "legendFormat": "add (p999)"},
        {"expr": "avg(bookkeeper_server_ADD_ENTRY_REQUEST{quantile=\"0.5\"})",   "legendFormat": "add (p50)"},
        {"expr": "avg(bookkeeper_server_READ_ENTRY_REQUEST{quantile=\"0.99\"})", "legendFormat": "read (p99)"},
        // ...
    ]
}
```

**为什么用 Graph + 多条线？**
- Summary 指标直接输出分位数，每个 quantile 是一条独立的时间序列
- 同时展示 p50(中位数)/p99/p999，可以判断延迟的分布形态：
  - 若 p50 低、p999 高 → 有偶发的尖刺
  - 若三者都高 → 系统整体有问题
- 📌 **规律**：延迟分位数 → Graph（多条线，Y轴单位ms）

**Y轴格式选择**：
```json
"format": "ms"   // 毫秒
"format": "Bps"  // bytes per second（自动换算为 KB/MB/GB）
"format": "short" // 纯数字
"format": "none" // 纯数字，不加单位
"format": "percent" // 百分比
```

---

## 4. 逐 Panel 拆解：broker Dashboard

### 4.1 Graph：Storage Write Latency（堆积图）

```json
{
    "type": "graph",
    "title": "Storage Write Latency",
    "fill": 5,            // 填充折线下方区域（5/10是填充强度）
    "stack": true,        // 堆积模式！
    "linewidth": 0,       // 线宽为0，全部用面积表示
    "aliasColors": {
        "0 - 0.5 ms": "#2F575E",
        "0.5 - 1 ms": "#3F6833",
        // 每个桶一个颜色
    },
    "targets": [
        {"expr": "sum(cloudmq_storage_write_latency_le_0_5{...}) / 60.0", "legendFormat": "0 - 0.5 ms"},
        {"expr": "sum(cloudmq_storage_write_latency_le_1{...}) / 60.0",   "legendFormat": "0.5 - 1 ms"},
        // ...每个延迟桶一个 target
    ]
}
```

**为什么用 Stacked Graph？**
- `cloudmq_storage_write_latency_le_*` 是 CloudMQ 自定义的分桶 Gauge。
- 堆积图可以通过切片直观展示各延迟区间的占比分布。

> ⚠️ **实战避坑指南：双重计数的陷阱！**  
> 必须指出，虽然这个旧版 Dashboard 强行使用了 Stacked 堆积模式，但**这是一个反直觉的陷阱设计**！  
> 在 Prometheus 规范中，带有 `le` (Less than or Equal) 前缀的分桶数据是**累积的 (Cumulative)**。这意味着 `le_10` 已经默默包含了 `le_5` 里的所有数据。如果在 Grafana 中直接用折线图叠加 (stack) 它们，会导致图表的绝对高度发生严重的数值膨胀（例如 `le_0_5` 会在上面每一个区域里被重复加盖）。  
> 
> **正确的解决思路**：
> 1. **标准解法**：在 PromQL 中手动做减法计算**独立桶**（例如：`le_1` 减去 `le_0_5`），然后再进行堆积。
> 2. **新版面板（推荐）**：使用 Grafana 新版的 `Heatmap` (热力图) 面板，它支持原生将 Cumulative Bucket 转换为常规 Bucket 来完美展示准确的直方分布。
> 3. **妥协查看**：如果一定要看当前这种有瑕疵的叠图，请只看“色块的相对厚度”，不要去看 Y 轴汇总的总高度。

**堆积图关键配置**：
```json
"stack": true,        // 开启堆积
"fill": 5,            // 填充透明度（1-10）
"linewidth": 0,       // 边框线宽（0=无边框，只有面积）
"bars": false,        // 不用柱状图
"lines": true         // 基于折线堆积
```

### 4.2 Graph：Publish Latency - 50pct / 99pct

```json
{
    "type": "graph",
    "title": "Publish Latency - 50pct",
    "yaxes": [{"format": "ms", "min": "0"}],
    "targets": [{
        "expr": "sum(cloudmq_instance_publish_latency{cluster=~\"$cluster\", instance=~\"$instance\", quantile=\"0.5\"}) by (instance)",
        "legendFormat": "{{ instance }}"
    }]
}
```

**这是 Summary 指标的 Grafana 用法**：
- `cloudmq_instance_publish_latency` 是 Summary，有 `quantile` 标签
- 每个 `quantile` 值单独出一个 panel（p50 一个，p99 一个）
- `legendFormat: "{{ instance }}"` 使用 labels 的值作为图例名称

**legendFormat 模板语法**：
```
"{{ instance }}"           → 使用 instance 标签值，如 "broker-0:8080"
"add (p{{ quantile }})"   → "add (p0.99)"（混合字符串+标签）
"add_entry"               → 固定字符串
```

---

## 5. Panel 类型选择完整规则

| 指标类型 | 分析维度 | 推荐 Panel | 配置要点 |
|---------|---------|-----------|---------|
| Gauge | 当前值（单一标量） | **Stat/Singlestat** | `valueName: "current"` |
| Gauge | 配比/健康度 | **Stat + Gauge圆弧** | 设置 `thresholds`, `format: "percent"` |
| Gauge | 趋势 | **Time series** | fill=0, lines=true |
| Counter | 速率趋势 | **Time series** | PromQL 加 `rate()`/`irate()` |
| Counter | 当前总量 | **Stat** | 直接展示累计值 |
| Histogram | 分位数趋势 | **Time series（多条线）** | 每个 quantile 一个 target |
| Summary | 分位数趋势 | **Time series（多条线）** | 每个 quantile 一个 target 或按标签过滤 |
| 分桶分布 | 比例分布 | **Stacked Graph** | `stack: true`, `fill: 5` |
| 二元状态 | 数量统计 | **Stat + count() PromQL** | 配合比较运算符过滤 |

---

## 6. Row Panel：Dashboard 分组

bookie Dashboard 中使用了 Row 将 Panel 分组：

```json
{
    "type": "row",
    "title": "Healthy",
    "collapsed": false
}
```

Row 的作用：
- 视觉上将 Dashboard 分成若干区域（如 Healthy / IO / Cache / JVM）
- `collapsed: false` 展开状态，`true` 折叠
- Row 本身不承载数据，只是布局容器

---

## 7. gridPos：Panel 布局系统

Grafana 使用 12 列的网格系统：

```json
"gridPos": {
    "h": 7,   // 高度（单位格）
    "w": 12,  // 宽度（1-24，满行=24）
    "x": 0,   // X 坐标（从左边起）
    "y": 0    // Y 坐标（从上往下累加）
}
```

常见布局：
- `"w": 24`：全宽（占满一行）
- `"w": 12`：半宽（一行两个）
- `"w": 8`：三等分（一行三个）
- `"w": 6`：四等分（一行四个）

broker Dashboard 第一行（y=0）就是两个 `w:12` 的 Graph Panel，各占半宽。

---

## 8. 本章小结

| 关键映射 | 规律 |
|---------|------|
| `count()` → 健康状态数量 | Singlestat/Stat |
| 百分比 + 阈值 | Singlestat + Gauge圆弧 + colors |
| `rate(Counter)` 趋势 | Time series（折线） |
| Summary/Histogram 分位数 | Time series（多条线，Y轴 ms） |
| 分桶 Gauge 分布 | Stacked Graph（`stack:true`） |
| `legendFormat: "{{ label }}"` | 动态图例 |
| gridPos | 12列网格布局 |

**下一章**：Grafana 变量系统——`$cluster`、`$instance` 是如何工作的，  
以及如何通过 PromQL 动态查询标签值来填充下拉框。
