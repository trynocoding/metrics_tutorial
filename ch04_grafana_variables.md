# 第四章：Grafana 模板变量系统——动态过滤的来龙去脉

> 本章深入解析 `$cluster`、`$instance`、`$job` 等变量，  
> 从 broker.json/bookie.json 的真实配置出发，彻底搞清楚变量的工作原理。

---

## 1. 变量的作用

你在 Panel 的 PromQL 里经常看到：

```promql
sum(cloudmq_rate_in{cluster=~"$cluster", instance=~"$instance"}) by (instance)
```

`$cluster` 和 `$instance` 不是写死的字符串，而是 Dashboard 级别的变量。  
它们在 Dashboard 顶部显示为下拉框，用户选择后，所有 Panel 的 PromQL 自动更新。

```
┌─────────────────────────────────────────────────────┐
│  Dashboard: Broker Metrics                          │
│                                                     │
│  [Cluster: cluster-a ▼]  [Instance: broker-0 ▼]   │← 变量下拉框
│                                                     │
│  ┌──────────────────┐  ┌──────────────────────┐   │
│  │ Publish Rate      │  │ Dispatch Rate        │   │
│  │ (过滤 cluster-a, │  │ (自动同步变量)       │   │
│  │  broker-0 数据)  │  │                      │   │
│  └──────────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

---

## 2. 变量定义：broker.json 完整解析

broker Dashboard 定义了 3 个变量（在 JSON 的 `templating.list` 数组中）：

### 2.1 变量一：cluster

```json
{
    "name": "cluster",
    "label": "Cluster",
    "type": "query",
    "datasource": "cloudmq-cluster",
    "query": {
        "query": "{cluster=~\".+\"}"
    },
    "regex": "/.*[^_]cluster=\\\"([^\\\"]+)\\\".*/",
    "refresh": 2,
    "includeAll": true,
    "multi": false,
    "sort": 1
}
```

**逐字段解读**：

| 字段 | 值 | 含义 |
|------|-----|------|
| `type` | `"query"` | 变量值通过 PromQL 查询获取 |
| `query.query` | `{cluster=~".+"}` | 查找所有有 `cluster` 标签的时间序列 |
| `regex` | `/.*cluster=\"([^\"]+)\".*/` | 从查询结果中提取 cluster 标签的值 |
| `refresh` | `2` | 每次页面刷新时重新加载（2=on dashboard load） |
| `includeAll` | `true` | 包含"All"选项（选All=不过滤） |
| `multi` | `false` | 单选（不能同时选多个） |
| `sort` | `1` | 按字母升序排列 |

**工作流程**：
```
1. Grafana 执行查询：{cluster=~".+"}
   → 返回所有含 cluster 标签的时间序列的元数据

2. 对每条元数据，用 regex 提取 cluster 标签值：
   regex: /.*cluster="([^"]+)".*/
   从 'cloudmq_rate_in{cluster="cluster-a-cloudmqcluster",...}'
   提取到   "cluster-a-cloudmqcluster"

3. 去重后填充到下拉框
   选项: [All, cluster-a-cloudmqcluster, cluster-b-cloudmqcluster, ...]
```

### 2.2 变量二：instance（依赖 cluster 变量）

```json
{
    "name": "instance",
    "label": "instance",
    "type": "query",
    "query": {
        "query": "cloudmq_rate_in{cluster=~\"$cluster\", instance=~\".+\"}"
    },
    "regex": "/.*[^_]instance=\\\"([^\\\"]+)\\\".*/",
    "multi": true,         // 多选！
    "refresh": 2,
    "includeAll": true
}
```

**关键差异**：
- `query` 里引用了 `$cluster` 变量 → **级联变量**（先选 cluster，再选 instance）
- `multi: true` → 允许同时选多个 instance

**级联关系**：
```
$cluster 变化  →  $instance 的查询重新执行
              →  $instance 的选项列表更新
              →  所有 Panel 的 PromQL 更新
```

### 2.3 变量三：cache（隐藏变量）

```json
{
    "name": "cache",
    "label": "Cache Name",
    "type": "query",
    "hide": 1,             // 隐藏！不在 UI 显示
    "query": {
        "query": "caffeine_cache_hit_total{cluster=~\"$cluster\", instance=~\"$instance\"}"
    },
    "regex": "/.*[^_]cache=\\\"([^\\\"]+)\\\".*/",
    "multi": true,
    "includeAll": true
}
```

`hide: 1` 的变量不在下拉框中显示，但可以在 PromQL 里引用 `$cache`。  
这个变量被 Cache 相关的 Panel 使用，默认选 All（所有缓存）。

---

## 3. 变量类型总览

| 类型 | 说明 | 典型用法 |
|------|------|---------|
| `query` | PromQL 查询动态获取 | 从标签值填充选项 |
| `custom` | 手动填写选项列表 | `"value1,value2,value3"` |
| `constant` | 固定值（隐藏） | 数据源名称等 |
| `datasource` | 选择数据源 | 多集群场景 |
| `interval` | 时间间隔 | `$__interval` |
| `textbox` | 自由输入文本框 | 正则过滤 |
| `adhoc` | 即席标签过滤器 | 动态添加过滤条件 |

---

## 4. 变量在 PromQL 中的使用模式

### 4.1 单值变量：精确匹配或正则匹配

```promql
# 精确匹配（multi=false，单选）
cloudmq_rate_in{cluster="$cluster"}

# 正则匹配（推荐方式，兼容 multi=true）
cloudmq_rate_in{cluster=~"$cluster"}
```

为什么推荐 `=~` 而不是 `=`？

| 场景 | `=` 行为 | `=~` 行为 |
|------|---------|----------|
| 选择单个值 "cluster-a" | 精确匹配，正常 | 正则匹配，正常 |
| 选择 All（`$__all`） | **语法错误！** | 自动展开为 `.+` 匹配所有 |
| 多选 "a,b,c"（`multi=true`）| **无法工作** | 自动展开为 `a\|b\|c` |

Grafana 会将多选变量的值用 `|` 连接，正则匹配天然支持：
```
$instance = "broker-0|broker-1|broker-2"
instance=~"$instance"  →  instance=~"broker-0|broker-1|broker-2"
```

### 4.2 dashboard.json 中的转义

JSON 文件中需要对引号转义，实际 PromQL 是：
```promql
cloudmq_rate_in{cluster=~"$cluster", instance=~"$instance"}
```

JSON 中写作：
```json
"expr": "sum(cloudmq_rate_in{cluster=~\\\"$cluster\\\", instance=~\\\"$instance\\\"}) by (instance)"
```

### 4.3 bookie Dashboard 中的 $job 变量

bookie Dashboard 使用 `$job` 而不是 `$instance`，因为 bookie 的指标通过 Prometheus Job 标签区分：

```promql
# bookie.json 中的 PromQL
count(bookie_SERVER_STATUS{job=~"$job"} == 1)
bookie_WRITE_BYTES{job=~"$job"}
bookkeeper_server_ADD_ENTRY_count{job=~"$job", instance=~"$instance", success="true"}
```

`job` 是 Prometheus 的保留标签，在 scrape_config 中定义：
```yaml
scrape_configs:
  - job_name: "bookie-cluster-a"    # 这就是 job 标签的值
    static_configs:
      - targets: ["bookie-0:8000", "bookie-1:8000"]
```

---

## 5. Regex 提取机制详解

变量定义中的 `regex` 字段非常重要，控制如何从查询结果中提取变量值：

### 5.1 cluster 变量的 regex

```
/.*[^_]cluster=\"([^\"]+)\".*/
   |    |         |        |
   |    |         └──── 捕获组：提取引号内的内容
   |    └──── 前一个字符不是下划线（避免匹配 _cluster=）
   └──── 匹配任意前缀
```

为什么需要 `[^_]`？  
防止匹配到如 `host_cluster` 这样的标签名中的 `cluster`。

### 5.2 instance 变量的 regex

```
/.*[^_]instance=\"([^\"]+)\".*/
```

同理，确保提取的是 `instance` 标签，而不是 `job_instance` 等组合。

### 5.3 regex 的完整语法

- 不加 regex：直接使用查询结果的时间序列名
- 加 regex但无捕获组：过滤匹配的结果
- 加 regex+捕获组 `()`：提取捕获组内容作为变量值

---

## 6. 内置变量（Grafana 全局变量）

除了自定义变量，Grafana 还内置了一些时间相关变量：

| 变量 | 说明 | 示例值 |
|------|------|-------|
| `$__interval` | 当前时间范围的适当步长 | `15s`, `1m`, `5m` |
| `$__interval_ms` | 以毫秒为单位的步长 | `15000` |
| `$__range` | 时间范围总长度 | `1h`, `6h` |
| `$__rate_interval` | 适合 rate() 的最小可靠区间 | `1m0s` |
| `$__from` | 时间范围起点（Unix ms） | `1712000000000` |
| `$__to` | 时间范围终点（Unix ms） | `1712003600000` |
| `$__all` | All 选项的内部值 | `.+` |

**最佳实践**：PromQL 中尽量使用 `[$__rate_interval]` 替代硬编码的 `[30s]`：

```promql
# 硬编码方式（broker.json 中的做法，老式）
irate(bookkeeper_server_ADD_ENTRY_count[30s])

# 推荐方式（动态适应时间范围）
rate(bookkeeper_server_ADD_ENTRY_count[$__rate_interval])
```

---

## 7. refresh 策略

```json
"refresh": 2
```

| 值 | 含义 |
|----|------|
| `0` | 不自动刷新（只在启动时加载一次） |
| `1` | 页面刷新时重新加载 |
| `2` | 时间范围变化时重新加载（推荐） |

---

## 8. 数据源变量

broker.json 的 `__inputs` 部分定义了数据源：

```json
"__inputs": [
    {
        "name": "DS_TEST-CLUSTER",
        "label": "cloudmq-cluster",
        "type": "datasource",
        "pluginId": "prometheus"
    }
]
```

每个 Panel 引用：
```json
"datasource": "cloudmq-cluster"
```

这允许导入 Dashboard 时，将数据源映射到不同的 Prometheus 实例。

---

## 9. 变量注入全链路总结

```
Grafana 启动/刷新
        │
        ▼
1. 执行变量查询：{cluster=~".+"}
   拉取所有含 cluster 标签的时间序列元数据
        │
        ▼
2. 应用 regex 提取标签值
   "/.*cluster=\"([^\"]+)\".*/" → ["cluster-a", "cluster-b"]
        │
        ▼
3. 填充下拉框
   用户选择 "cluster-a"
        │
        ▼
4. 触发 instance 变量重新查询（级联）
   cloudmq_rate_in{cluster=~"cluster-a", instance=~".+"}
   提取 instance 值 → ["broker-0:8080", "broker-1:8080"]
        │
        ▼
5. 所有 Panel 的 PromQL 中 $cluster/$instance 被替换
   {cluster=~"cluster-a", instance=~"broker-0:8080"}
        │
        ▼
6. 向 Prometheus 发送查询，渲染图表
```

---

## 10. 本章小结

| 概念 | 要点 |
|------|------|
| `type: "query"` | 通过 PromQL 动态获取变量值 |
| `regex` 捕获组 | 从时间序列名中提取标签值 |
| `=~` vs `=` | 多选变量必须用 `=~` |
| `multi: true` | 允许多选，值用 `\|` 连接 |
| `includeAll: true` | 包含 "All" 选项 |
| 级联变量 | 子变量 query 引用父变量 |
| `$__rate_interval` | 动态时间窗口，优于硬编码 |
| `hide: 1` | 隐藏变量，仍可在 PromQL 使用 |

**下一章**：从开发者角度用 Go 语言实现各类指标的完整代码示例，深入理解 Counter/Gauge/Histogram/Summary 在业务代码中的最佳实践。
