# 第七章：进阶技巧——Recording Rules、自定义 Collector 与常见陷阱

> 本章讲解 Prometheus 高级使用模式，解决实际生产中遇到的性能问题、  
> 高基数问题和复杂查询问题，并给出 Go 实现的自定义 Collector 示例。

---

## 1. Recording Rules：预计算高频查询

### 1.1 问题背景

像这样的 PromQL 在 Dashboard 里每秒执行一次，计算量很大：

```promql
# 需要跨所有时间序列计算，在数据量大时很慢
histogram_quantile(0.99,
  sum(rate(cloudmq_publish_latency_seconds_bucket{cluster=~"$cluster"}[5m]))
  by (le, cluster)
)
```

如果有 100 个 Dashboard Panel 都在实时查这个，Prometheus 压力很大。

### 1.2 Recording Rule 解决方案

**在 Prometheus 配置文件中定义 Recording Rule**：

```yaml
# prometheus.yml 或单独的 rules/cloudmq_rules.yml
groups:
  - name: cloudmq_recording_rules
    interval: 30s    # 每 30 秒预计算一次
    rules:
      # 预计算各集群的消息发布速率（5分钟窗口）
      - record: cloudmq:rate_in:rate5m
        expr: |
          sum(rate(cloudmq_messages_published_total[5m]))
          by (cluster, namespace)

      # 预计算发布延迟 p99（按集群聚合）
      - record: cloudmq:publish_latency_seconds:p99:rate5m
        expr: |
          histogram_quantile(0.99,
            sum(rate(cloudmq_publish_latency_seconds_bucket[5m]))
            by (le, cluster)
          )

      # 预计算 Bookie 成功率（对应 bookie Dashboard 中的 Success Rate）
      - record: bookie:add_entry_success_rate:irate30s
        expr: |
          sum(irate(bookkeeper_server_ADD_ENTRY_count{success="true"}[30s]))
          by (cluster)
          /
          sum(irate(bookkeeper_server_ADD_ENTRY_count[30s]))
          by (cluster)
```

**Recording Rule 命名规范**：
```
<namespace>:<metric>:<aggregation>
                       ↑
             可加时间窗口后缀，如 rate5m, irate30s
```

### 1.3 在 Grafana 中使用预计算指标

```promql
# 原始查询（慢）
histogram_quantile(0.99, sum(rate(cloudmq_publish_latency_seconds_bucket[5m])) by (le, cluster))

# 使用 Recording Rule（快，直接查预计算结果）
cloudmq:publish_latency_seconds:p99:rate5m{cluster=~"$cluster"}
```

### 1.4 Recording Rules 的适用场景

| 场景 | 是否适用 |
|------|---------|
| Dashboard 中频繁使用的复杂查询 | ✅ |
| 用于告警的阈值判断 | ✅ |
| 需要跨大量时间序列聚合 | ✅ |
| 历史数据同比/环比分析 | ✅ |
| 偶尔查询的诊断性 PromQL | ❌ 不需要 |

---

## 2. 自定义 Collector：批量高效采集

### 2.1 问题背景

如果有 1000 个 topic，每个 topic 都需要采集多个指标，  
用 `GaugeVec.With(labels).Set(value)` 逐一更新的方式可能有性能问题。

**自定义 Collector 允许在 Prometheus 拉取时按需生成指标**，而不是维护内存状态。

### 2.2 Go 实现自定义 Collector

```go
// collector/topic_collector.go
package collector

import (
    "github.com/prometheus/client_golang/prometheus"
)

// TopicStore 提供 Topic 数据（业务逻辑接口）
type TopicStore interface {
    ListTopics() []TopicInfo
}

type TopicInfo struct {
    Cluster      string
    Namespace    string
    Topic        string
    RateIn       float64
    RateOut      float64
    MsgBacklog   int64
    ProducerCount int
    ConsumerCount int
}

// TopicCollector 实现 prometheus.Collector 接口
type TopicCollector struct {
    store TopicStore

    // 描述符（Desc 预先创建好，提升性能）
    rateInDesc      *prometheus.Desc
    rateOutDesc     *prometheus.Desc
    msgBacklogDesc  *prometheus.Desc
    producerCount   *prometheus.Desc
    consumerCount   *prometheus.Desc
}

// NewTopicCollector 创建 Collector 实例
func NewTopicCollector(store TopicStore) *TopicCollector {
    labels := []string{"cluster", "namespace", "topic"}
    
    return &TopicCollector{
        store: store,
        
        rateInDesc: prometheus.NewDesc(
            "cloudmq_rate_in",
            "Message publish rate in messages per second",
            labels, nil,
        ),
        rateOutDesc: prometheus.NewDesc(
            "cloudmq_rate_out",
            "Message dispatch rate in messages per second",
            labels, nil,
        ),
        msgBacklogDesc: prometheus.NewDesc(
            "cloudmq_msg_backlog",
            "Number of messages in the subscription backlog",
            labels, nil,
        ),
        producerCount: prometheus.NewDesc(
            "cloudmq_producers_count",
            "Number of active producers",
            []string{"cluster", "namespace"}, nil,
        ),
        consumerCount: prometheus.NewDesc(
            "cloudmq_consumers_count",
            "Number of active consumers",
            []string{"cluster", "namespace"}, nil,
        ),
    }
}

// Describe 实现 prometheus.Collector 接口
// 向 Prometheus 注册表声明本 Collector 会产生哪些指标
func (c *TopicCollector) Describe(ch chan<- *prometheus.Desc) {
    ch <- c.rateInDesc
    ch <- c.rateOutDesc
    ch <- c.msgBacklogDesc
    ch <- c.producerCount
    ch <- c.consumerCount
}

// Collect 实现 prometheus.Collector 接口
// 在 Prometheus 抓取时被调用，实时生成指标样本
func (c *TopicCollector) Collect(ch chan<- prometheus.Metric) {
    topics := c.store.ListTopics()
    
    // namespace 层面的聚合（用于 producerCount/consumerCount）
    nsProducers := make(map[string]int)
    nsConsumers := make(map[string]int)
    
    for _, t := range topics {
        labelValues := []string{t.Cluster, t.Namespace, t.Topic}
        nsKey := t.Cluster + "/" + t.Namespace
        
        // Topic 级别的 Gauge
        ch <- prometheus.MustNewConstMetric(
            c.rateInDesc,
            prometheus.GaugeValue,
            t.RateIn,
            labelValues...,
        )
        ch <- prometheus.MustNewConstMetric(
            c.rateOutDesc,
            prometheus.GaugeValue,
            t.RateOut,
            labelValues...,
        )
        ch <- prometheus.MustNewConstMetric(
            c.msgBacklogDesc,
            prometheus.GaugeValue,
            float64(t.MsgBacklog),
            labelValues...,
        )
        
        // 聚合到 namespace 级别
        nsProducers[nsKey] += t.ProducerCount
        nsConsumers[nsKey] += t.ConsumerCount
    }
    
    // 输出 namespace 级别聚合指标
    for nsKey, count := range nsProducers {
        cluster, namespace := splitNsKey(nsKey)
        ch <- prometheus.MustNewConstMetric(
            c.producerCount,
            prometheus.GaugeValue,
            float64(count),
            cluster, namespace,
        )
    }
    for nsKey, count := range nsConsumers {
        cluster, namespace := splitNsKey(nsKey)
        ch <- prometheus.MustNewConstMetric(
            c.consumerCount,
            prometheus.GaugeValue,
            float64(count),
            cluster, namespace,
        )
    }
}

func splitNsKey(key string) (string, string) {
    // 简单分隔，实际可用 strings.SplitN
    parts := strings.SplitN(key, "/", 2)
    return parts[0], parts[1]
}
```

### 2.3 注册自定义 Collector

```go
func main() {
    store := NewTopicStore(db)
    
    // 注册自定义 Collector
    collector := collector.NewTopicCollector(store)
    prometheus.MustRegister(collector)
    
    http.Handle("/metrics", promhttp.Handler())
    http.ListenAndServe(":8080", nil)
}
```

### 2.4 自定义 Collector vs GaugeVec 比较

| 维度 | GaugeVec | 自定义 Collector |
|------|---------|----------------|
| 使用复杂度 | 简单 | 中等 |
| 数据时效性 | 定时后台更新 | 抓取时即时计算 |
| 内存占用 | 所有指标常驻内存 | 抓取时临时分配 |
| 过期标签处理 | 需手动 Delete | 天然解决（每次重新生成） |
| 适用场景 | 少量指标，频繁更新 | 大量指标（如 1000+ topic） |

---

## 3. 常见 PromQL 陷阱与反模式

### 3.1 陷阱一：用 `=` 匹配多选变量

```promql
# ❌ 错误：multi=true 的变量无法用 = 匹配
cloudmq_rate_in{instance="$instance"}

# ✅ 正确：用 =~ 支持多值
cloudmq_rate_in{instance=~"$instance"}
```

### 3.2 陷阱二：忘记 `by (le)` 导致 histogram_quantile 失效

```promql
# ❌ 错误：sum 后丢失了 le 标签，histogram_quantile 无法计算
histogram_quantile(0.99, sum(rate(my_histogram_bucket[5m])))

# ✅ 正确：保留 le 标签
histogram_quantile(0.99, sum(rate(my_histogram_bucket[5m])) by (le))

# ✅ 更完整：按需保留其他维度标签
histogram_quantile(0.99, sum(rate(my_histogram_bucket[5m])) by (le, cluster))
```

### 3.3 陷阱三：对 Gauge 使用 rate()

```promql
# ❌ 错误：cloudmq_rate_in 是 Gauge，不应该用 rate()
rate(cloudmq_rate_in[5m])

# ✅ 正确：直接使用
cloudmq_rate_in

# 若需要平滑：用 avg_over_time
avg_over_time(cloudmq_rate_in[5m])
```

### 3.4 陷阱四：Summary 跨实例聚合

```promql
# ❌ 错误：对 Summary 的 quantile 标签做 avg，结果没有意义
avg(cloudmq_instance_publish_latency{quantile="0.99"})
# 得到的是"各实例各自 p99 的算术平均"，不是全局 p99

# ✅ 如果确实需要全局 p99，应该用 Histogram：
histogram_quantile(0.99, sum(rate(publish_latency_bucket[5m])) by (le))
```

### 3.5 陷阱五：Counter 重置未处理

```promql
# 如果使用 delta() 处理 Counter，重启后归零会导致负值
delta(cloudmq_messages_published_total[5m])  # ❌ 可能出现负值

# ✅ 用 increase() 或 rate()，它们会自动处理 Counter 重置
increase(cloudmq_messages_published_total[5m])  # 区间内增量
rate(cloudmq_messages_published_total[5m])       # 每秒速率
```

### 3.6 陷阱六：高基数 Label

```promql
# ❌ 错误：将 message_id 或 trace_id 作为 Label
cloudmq_publish_latency{message_id="abc-123-def-456", ...}

# 问题：每个 message_id 都是一条独立时间序列，百万级 topic 
# 会导致 Prometheus 内存溢出（OOM）

# ✅ 正确：用有限枚举值的 Label
cloudmq_publish_latency{error_type="timeout", ...}  # 枚举错误类型
cloudmq_publish_latency{priority="high", ...}       # 枚举优先级
```

**黄金法则**：一个 Label 的不同值数量（基数）不超过 **1000**。

---

## 4. 自定义 Histogram（非标准分桶）的 PromQL 处理

CloudMQ 使用了将 Histogram 展平为多个 Gauge 的实现方式（`cloudmq_storage_write_latency_le_*`），  
这在 Java 的 Pulsar/CloudMQ 中很常见。

### 4.1 问题：无法用 histogram_quantile

由于这些 Gauge 不具备 Prometheus Histogram 的标准格式（没有 `le` 标签），  
无法使用 `histogram_quantile()`。

### 4.2 解决方案：计算桶比率

```promql
# 查看各延迟桶的消息数占比
# 如：≤1ms 的消息占总数的比例
sum(cloudmq_storage_write_latency_le_1{cluster=~"$cluster"})
/ sum(cloudmq_storage_write_latency_le_1000{cluster=~"$cluster"})
# ≤1000ms 约等于总数（如果 overflow 很小）
```

### 4.3 用 Go 将自定义分桶转为标准 Histogram

如果你有权修改暴露端，可以将这些 Gauge 转为标准 Prometheus Histogram：

```go
// 自定义累计桶转标准 Histogram
type CustomBucketHistogram struct {
    desc    *prometheus.Desc
    store   BucketStore
}

func (h *CustomBucketHistogram) Collect(ch chan<- prometheus.Metric) {
    buckets := h.store.GetBuckets() // 返回 map[float64]uint64
    
    ch <- prometheus.MustNewConstHistogram(
        h.desc,
        buckets.Count,         // 总数
        buckets.Sum,           // 总和（毫秒）
        map[float64]uint64{
            0.5:  buckets.Le0_5ms,
            1.0:  buckets.Le1ms,
            5.0:  buckets.Le5ms,
            10.0: buckets.Le10ms,
            // ...
        },
        "cluster-a", "namespace/topic", // label values
    )
}
```

---

## 5. Exemplars：将 Trace 和 Metrics 关联

Exemplars 允许在 Histogram 的桶上附加 Trace ID，实现从监控图表直接跳转到链路追踪。

```go
// 支持 Exemplar 的 Observer（需要 OpenMetrics 格式）
import (
    "github.com/prometheus/client_golang/prometheus"
)

// 记录带 Exemplar 的延迟
func recordWithExemplar(h prometheus.ExemplarObserver, duration float64, traceID string) {
    h.(prometheus.ExemplarObserver).ObserveWithExemplar(
        duration,
        prometheus.Labels{
            "trace_id": traceID, // 关联到分布式追踪系统
        },
    )
}
```

在 Grafana 中开启 Exemplar 支持后，Histogram 图表上会显示散点，  
点击散点可以跳转到对应的 Trace。

---

## 6. 最佳实践总结

### 6.1 命名规范

```
# 格式：[namespace_][subsystem_]name[_unit]
cloudmq_broker_publish_latency_seconds     ✅
cloudmq_broker_publish_lat                 ❌ (缩写)
cloudmq_broker_publish_latency_milliseconds ❌ (应用 _seconds，Prometheus 约定)

# 单位规范
_seconds  (时间)
_bytes    (字节)
_total    (counter 后缀)
_ratio    (比率, 0.0-1.0)
_info     (info 指标)
```

### 6.2 标签设计规范

```go
// ✅ 好的标签：有限枚举值，有业务意义
Labels: []string{"cluster", "namespace", "status", "method"}

// ❌ 坏的标签：高基数，运行时生成
Labels: []string{"request_id", "user_id", "message_id", "error_message"}
```

### 6.3 Go 指标组织推荐结构

```
myservice/
├── main.go
├── metrics/
│   ├── registry.go     # 自定义 Registry，统一注册
│   ├── broker.go       # Broker 业务指标
│   ├── storage.go      # 存储层指标
│   ├── jvm.go          # JVM/运行时指标（如需）
│   └── collector/
│       └── topic_collector.go  # 自定义 Collector（大量动态指标）
└── ...
```

---

## 7. 本章小结

| 技术 | 适用场景 | 关键要点 |
|------|---------|---------|
| Recording Rules | 复杂查询预计算 | 命名规范 `ns:metric:aggregation` |
| 自定义 Collector | 大量动态指标（1000+ topic） | 实现 `Describe` 和 `Collect` 接口 |
| `by (le)` 保留 | Histogram 聚合 | 不然 histogram_quantile 报错 |
| `=~` 匹配 | 多选变量 | 永远比 `=` 更安全 |
| 高基数控制 | Label 设计 | 单 Label 值 < 1000 |
| Exemplars | Metrics+Tracing 联动 | 需要 OpenMetrics 格式支持 |

---

## 附录：快速参考卡

**指标类型选择**：
```
只增不减？→ Counter（配合 rate/irate）
可增可减？→ Gauge（直接展示或设置）
需要分位数且多实例聚合？→ Histogram（bucket + histogram_quantile）
单实例精确分位数？→ Summary（Objectives + MaxAge）
```

**Panel 类型选择**：
```
当前单一数值/状态？→ Stat/Singlestat
趋势折线？→ Time series/Graph
分布堆积？→ Stacked Graph（stack:true）
仪表盘圆弧？→ Gauge（Singlestat + gauge.show:true）
```

**PromQL 常用模式**：
```
速率：rate(counter[5m]) 或 irate(counter[30s])
分位数：histogram_quantile(0.99, sum(rate(histogram_bucket[5m])) by (le))
百分比：100 * numerator / denominator
成功率：100 * rate(success[5m]) / rate(total[5m])
资源使用率：used / max * 100
```
