# 第六章：指标分类实战——黄金信号与 Dashboard 架构

> 本章解答一个核心问题：**面对几百个指标，如何知道该监控什么、怎么组织 Dashboard？**  
> 以 CloudMQ 的 broker 和 bookie 为真实案例，系统化地讲解指标分类方法论。

---

## 1. Google SRE 的"黄金信号"

Google SRE 书中提出四个黄金信号（Four Golden Signals），是监控任何服务的通用框架：

```
┌─────────────────────────────────────────────────────────────────────┐
│                     四个黄金信号                                      │
│                                                                     │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────────┐  │
│  │  延迟     │  │  流量     │  │  错误率   │  │   饱和度      │  │
│  │ Latency  │  │  Traffic  │  │  Errors   │  │  Saturation  │  │
│  │          │  │          │  │           │  │              │  │
│  │p50/p99   │  │ msg/s    │  │ 失败率    │  │ CPU/内存/    │  │
│  │延迟分布  │  │ bytes/s  │  │ 错误计数  │  │ 队列深度/    │  │
│  │          │  │ 请求数   │  │           │  │ 线程池饱和度 │  │
│  └───────────┘  └───────────┘  └───────────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. CloudMQ Broker 指标的黄金信号映射

### 2.1 延迟（Latency）

| 指标 | 类型 | PromQL 示例 | Panel |
|------|------|------------|-------|
| `cloudmq_instance_publish_latency` | Summary | `{quantile="0.99"}` | Graph（多分位数） |
| `cloudmq_broker_publish_latency` | Summary | `{quantile="0.99"}` | Graph |
| `cloudmq_storage_write_latency_le_*` | Gauge（分桶） | `sum(...)/60` | Stacked Graph |
| `cloudmq_metadata_store_ops_latency_ms` | Histogram | `histogram_quantile(0.99, ...)` | Graph |
| `cloudmq_topic_load_times` | Summary | `{quantile="0.99"}` | Graph |

**broker.json 里的延迟 Panel 布局**：
```
y=27: Publish Latency - 50pct | Publish Latency - 99pct | ...
y=20: Messages Backlog        | Storage Write Latency
```

### 2.2 流量（Traffic）

| 指标 | 类型 | PromQL 示例 | Panel |
|------|------|------------|-------|
| `cloudmq_rate_in` | Gauge | `sum(...) by (instance)` | Graph |
| `cloudmq_rate_out` | Gauge | `sum(...) by (instance)` | Graph |
| `cloudmq_throughput_in` | Gauge | `sum(...) by (instance)` | Graph（Y轴 Bps） |
| `cloudmq_throughput_out` | Gauge | `sum(...) by (instance)` | Graph（Y轴 Bps） |
| `cloudmq_producers_count` | Gauge | `sum(...)` | Graph |
| `cloudmq_consumers_count` | Gauge | `sum(...)` | Graph |
| `cloudmq_topics_count` | Gauge | `sum(...)` | Graph |

**broker.json 的流量 Panel 布局（前两行）**：
```
y=0:  Publish rate (msg/s)     | Dispatch rate (msg/s)
y=7:  Publish throughput (MB/s)| Dispatch throughput (MB/s)
y=14: Topics count | Producers count | Consumers count
```

### 2.3 错误率（Errors）

broker.json 中没有独立的错误率 Panel，但常见的错误指标有：

| 指标 | 类型 | 说明 |
|------|------|------|
| `cloudmq_broker_lookup_failures` | Counter | Lookup 失败次数 |
| `cloudmq_authentication_failures` | Counter | 认证失败次数 |
| `log4j2_appender_total{level="error"}` | Counter | 错误日志数量 |
| `bes_servlet_errorcount` | Counter | HTTP 错误请求数 |

**示例 PromQL（错误率）**：
```promql
# Lookup 失败率
rate(cloudmq_broker_lookup_failures_total[5m])
/ (rate(cloudmq_broker_lookup_failures_total[5m]) + rate(cloudmq_broker_lookup_answers_total[5m]))

# 认证失败率
rate(cloudmq_authentication_failures_total[5m])
```

### 2.4 饱和度（Saturation）

| 指标 | 类型 | 说明 |
|------|------|------|
| `jvm_memory_bytes_used` | Gauge | JVM 内存使用 |
| `jvm_memory_bytes_max` | Gauge | JVM 内存上限 |
| `jvm_threads_current` | Gauge | 当前线程数 |
| `cloudmq_msg_backlog` | Gauge | 消息积压（饱和度最直接体现） |
| `bes_threadpool_currentthreadsbusy` | Gauge | HTTP 线程池繁忙线程数 |
| `process_open_fds` | Gauge | 打开文件描述符数 |

**JVM 内存使用率 PromQL**：
```promql
jvm_memory_bytes_used{area="heap"} / jvm_memory_bytes_max{area="heap"} * 100
```

---

## 3. CloudMQ Bookie 指标的黄金信号映射

### 3.1 延迟

| 指标 | 类型 | Panel |
|------|------|-------|
| `bookkeeper_server_ADD_ENTRY_REQUEST` | Summary(Java) | Graph（多分位数） |
| `bookkeeper_server_READ_ENTRY_REQUEST` | Summary(Java) | Graph（多分位数） |

**bookie.json Latency Panel 中的 6 条线**：
```
add (p50)   add (p99)   add (p999)
read (p50)  read (p99)  read (p999)
```

### 3.2 流量

| 指标 | 类型 | PromQL |
|------|------|--------|
| `bookie_WRITE_BYTES` | Counter | `sum(rate(...[30s]))` |
| `bookie_READ_BYTES` | Counter | `sum(rate(...[30s]))` |
| `bookkeeper_server_ADD_ENTRY_count` | Counter | `sum(irate(...{success="true"}[30s]))` |
| `bookkeeper_server_READ_ENTRY_count` | Counter | `sum(irate(...{success="true"}[30s]))` |

### 3.3 错误率 / 健康度

| 指标 | Panel 类型 | 说明 |
|------|-----------|------|
| `bookie_SERVER_STATUS==1` count | Singlestat | 可写 bookie 数（健康度） |
| `bookie_SERVER_STATUS==0` count | Singlestat | 只读 bookie 数（异常指标） |
| ADD_ENTRY 成功率 | Graph | Counter 成功率计算 |

---

## 4. 指标的第二种分类方式：层次分类

除了黄金信号横向切分，还可以按**系统层次**纵向分类：

```
┌──────────────────────────────────────────────────────┐
│  Layer 7: 业务指标（消息、Topic、Producer/Consumer）   │
│  cloudmq_rate_in, cloudmq_msg_backlog, ...           │
├──────────────────────────────────────────────────────┤
│  Layer 6: 存储指标（写延迟、读延迟、写量）             │
│  cloudmq_storage_write_latency_*, bookie_WRITE_BYTES │
├──────────────────────────────────────────────────────┤
│  Layer 5: 应用服务器指标（BES/Tomcat 线程池）          │
│  bes_threadpool_*, bes_servlet_*                     │
├──────────────────────────────────────────────────────┤
│  Layer 4: 缓存指标（Caffeine）                        │
│  caffeine_cache_hit_total, caffeine_cache_miss_total  │
├──────────────────────────────────────────────────────┤
│  Layer 3: JVM 指标（GC、内存、线程）                  │
│  jvm_memory_bytes_*, jvm_gc_*, jvm_threads_*        │
├──────────────────────────────────────────────────────┤
│  Layer 2: 进程指标（CPU、FD、内存）                   │
│  process_cpu_seconds_total, process_open_fds         │
└──────────────────────────────────────────────────────┘
```

---

## 5. Dashboard Row 组织实践

### 5.1 bookie Dashboard Row 结构

```json
Row 1: "Healthy"
  - Singlestat: Writable Bookies
  - Singlestat: ReadOnly Bookies  
  - Singlestat: writable bookies (percentage) [with Gauge 圆弧]
  - Graph: Success Rate
  - Graph: Latency

Row 2: "IO"
  - Graph: Throughput (MB/s)
  - Graph: Entry Rate

Row 3 (collapsed): "Per Bookie"
  - Graph: Write Bytes (by instance)
  - ... 按实例细分的指标

Row 4 (collapsed): "Cache"
  - Graph: Read Cache Hit Rate
  - ...

Row 5 (collapsed): "JVM"
  - Graph: JVM Memory
  - Graph: GC Time
  - ...
```

**设计原则**：
- 第一行：最重要的单值健康指标（Singlestat）
- 第二行：最重要的趋势指标（Graph）
- 往下：越来越细节的诊断指标（默认折叠）

### 5.2 broker Dashboard 没有 Row，直接平铺

broker.json 所有 Panel 都在同一层级，按 `y` 坐标从上到下排：

```
y=0:   Publish Rate | Dispatch Rate
y=7:   Publish Throughput | Dispatch Throughput
y=14:  Topics Count | Producers Count | Consumers Count
y=20:  Messages Backlog | Storage Write Latency
y=27:  Publish Latency p50 | p75 | p99 | p999
y=34:  JVM Memory | GC | Threads | ...
```

**规律**：从业务指标（顶部）→ 到系统指标（底部），重要性递减。

---

## 6. 指标类型与 Dashboard 分类的完整映射

```
黄金信号维度 × 系统层次 → Dashboard 结构
─────────────────────────────────────────────────────

Row: 总览（Overview）
  ├── Singlestat: 集群状态（Gauge：可写节点数）
  ├── Stat: 今日消息量（Counter：同比/环比）
  └── Stat: 当前告警数（计数）

Row: 流量（Traffic）
  ├── Graph [Counter→rate]: 发布速率 msg/s
  ├── Graph [Counter→rate]: 消费速率 msg/s
  ├── Graph [Gauge]: 积压消息数（msg_backlog）
  └── Graph [Gauge]: 在线 Producer/Consumer 数

Row: 延迟（Latency）
  ├── Graph [Summary/Histogram]: 发布延迟 p50/p99
  ├── Graph [Summary]: 消费延迟 p50/p99
  └── Stacked Graph [Gauge 分桶]: 存储写入延迟分布

Row: 错误（Errors）
  ├── Graph [Counter→rate]: 认证失败率
  ├── Graph [Counter→rate]: Lookup 失败率
  └── Graph [Counter→rate]: 错误日志

Row: 资源饱和度（Saturation）
  ├── Graph [Gauge]: JVM 堆内存使用率
  ├── Graph [Gauge]: 文件描述符使用率
  ├── Graph [Gauge]: 线程池活跃线程数
  └── Graph [Gauge]: CPU 使用率
```

---

## 7. 从代码到 Dashboard 的完整链路示例

以"消息发布延迟"这一指标为例，追踪全链路：

**Step 1：代码中定义 Histogram**
```go
var PublishLatency = promauto.NewHistogramVec(
    prometheus.HistogramOpts{
        Name:    "cloudmq_publish_latency_seconds",
        Buckets: prometheus.ExponentialBucketsRange(0.0001, 10, 15),
    },
    []string{"cluster", "namespace", "topic"},
)
```

**Step 2：业务代码中记录**
```go
start := time.Now()
err := publishMessage(ctx, msg)
PublishLatency.With(labels).Observe(time.Since(start).Seconds())
```

**Step 3：Prometheus 抓取后的文本格式**
```
# TYPE cloudmq_publish_latency_seconds histogram
cloudmq_publish_latency_seconds_bucket{cluster="c1",le="0.0001"} 1234
cloudmq_publish_latency_seconds_bucket{cluster="c1",le="0.000215"} 4567
...
cloudmq_publish_latency_seconds_bucket{cluster="c1",le="+Inf"} 10000
cloudmq_publish_latency_seconds_count{cluster="c1"} 10000
cloudmq_publish_latency_seconds_sum{cluster="c1"} 4.523
```

**Step 4：PromQL 计算 p99**
```promql
histogram_quantile(0.99,
  sum(rate(cloudmq_publish_latency_seconds_bucket{cluster=~"$cluster"}[$__rate_interval]))
  by (le)
)
```

注意 `by (le)`：`histogram_quantile` 要求保留 `le` 标签，  
同时用 `sum by (le)` 跨 namespace/topic 聚合。

**Step 5：Grafana Panel JSON**
```json
{
    "type": "timeseries",
    "title": "Publish Latency p99",
    "fieldConfig": {
        "defaults": {
            "unit": "s",           // 秒
            "custom": {
                "lineWidth": 2,
                "fillOpacity": 10
            }
        }
    },
    "targets": [
        {
            "expr": "histogram_quantile(0.99, sum(rate(cloudmq_publish_latency_seconds_bucket{cluster=~\"$cluster\"}[$__rate_interval])) by (le))",
            "legendFormat": "p99"
        },
        {
            "expr": "histogram_quantile(0.50, ...)",
            "legendFormat": "p50"
        }
    ]
}
```

---

## 8. 告警规则的指标类型偏好

告警规则（Alerting Rules）与指标类型也有对应关系：

| 场景 | 推荐指标类型 | 示例规则 |
|------|------------|---------|
| 速率异常（突增/骤降） | Counter + rate() | `rate(errors[5m]) > 100` |
| 当前值超阈值 | Gauge | `msg_backlog > 1000000` |
| 延迟 SLA 违规 | Histogram + quantile | `histogram_quantile(0.99, ...) > 0.1` |
| 节点宕机 | Gauge（健康状态） | `up == 0` |
| 资源耗尽 | Gauge（饱和度） | `memory_used / memory_max > 0.95` |

---

## 9. 本章小结

| 分类维度 | 方法 | CloudMQ 示例 |
|---------|------|------------|
| 黄金信号 | 延迟/流量/错误/饱和度 | 覆盖4个层面 |
| 系统层次 | 业务→缓存→JVM→进程 | Row 组织方式 |
| 指标类型映射 | Counter→速率, Gauge→状态, Histogram→分布 | Panel 类型选择依据 |
| 高基数控制 | Label 值类别 < 1000 | error_type 而非 error_message |

**下一章**：进阶技巧——Recording Rules（预计算）、Exemplars（链路追踪集成）、自定义 Collector（批量高效采集），以及常见的 PromQL 反模式与陷阱。
