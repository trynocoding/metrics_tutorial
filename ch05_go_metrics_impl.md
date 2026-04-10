# 第五章：Go 语言实现 Prometheus 指标——从代码到 Dashboard

> 本章用 Go 语言实现对应 Counter / Gauge / Histogram / Summary 四种类型，  
> 并展示如何将代码中定义的指标映射到 Grafana Panel。

---

## 1. 依赖准备

```bash
go mod init metrics-demo
go get github.com/prometheus/client_golang/prometheus
go get github.com/prometheus/client_golang/prometheus/promauto
go get github.com/prometheus/client_golang/prometheus/promhttp
```

核心包说明：
- `prometheus`：核心 API（注册、记录指标）
- `promauto`：自动注册的便捷包（省去手动 `Register`）
- `promhttp`：提供 `/metrics` HTTP handler

---

## 2. 最小化可运行示例

```go
// main.go
package main

import (
    "log"
    "net/http"
    "time"

    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promauto"
    "github.com/prometheus/client_golang/prometheus/promhttp"
)

// 定义指标（全局变量，包级别注册）
var (
    // Counter：消息发布总数
    messagesPublished = promauto.NewCounterVec(
        prometheus.CounterOpts{
            Name: "cloudmq_messages_published_total",
            Help: "Total number of messages published",
        },
        []string{"namespace", "topic", "cluster"},
    )

    // Gauge：当前在线 Producer 数量
    producersOnline = promauto.NewGaugeVec(
        prometheus.GaugeOpts{
            Name: "cloudmq_producers_count",
            Help: "Current number of online producers",
        },
        []string{"namespace", "cluster"},
    )
)

func main() {
    // 模拟业务产生指标
    go simulateMetrics()

    // 暴露 /metrics endpoint
    http.Handle("/metrics", promhttp.Handler())
    log.Println("Metrics server listening on :8080")
    log.Fatal(http.ListenAndServe(":8080", nil))
}

func simulateMetrics() {
    labels := prometheus.Labels{
        "namespace": "cloudmq/__monitor",
        "topic":     "persistent://cloudmq/__monitor/__change_events",
        "cluster":   "cluster-a",
    }
    for {
        messagesPublished.With(labels).Add(100)
        producersOnline.With(prometheus.Labels{
            "namespace": "cloudmq/__monitor",
            "cluster":   "cluster-a",
        }).Set(5)
        time.Sleep(time.Second)
    }
}
```

访问 `http://localhost:8080/metrics`，你会看到：
```
# HELP cloudmq_messages_published_total Total number of messages published
# TYPE cloudmq_messages_published_total counter
cloudmq_messages_published_total{cluster="cluster-a",namespace="cloudmq/__monitor",topic="..."} 300

# HELP cloudmq_producers_count Current number of online producers
# TYPE cloudmq_producers_count gauge
cloudmq_producers_count{cluster="cluster-a",namespace="cloudmq/__monitor"} 5
```

---

## 3. Counter 的完整实现

Counter 对应业务中的"累计发生了多少次"，结合 `rate()/irate()` 展示速率。

### 3.1 代码实现

```go
package metrics

import (
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promauto"
)

// ============================================================
// 消息发布 Counter
// 对应 broker 中的 cloudmq_rate_in（但那是 Gauge，这是更规范的设计）
// Dashboard PromQL: rate(cloudmq_messages_published_total[1m])
// ============================================================

var (
    // 发布消息总数（细粒度：按 namespace + topic）
    MessagesPublishedTotal = promauto.NewCounterVec(
        prometheus.CounterOpts{
            Namespace: "cloudmq",
            Name:      "messages_published_total",
            Help:      "Total number of messages successfully published",
        },
        []string{"cluster", "namespace", "topic"},
    )

    // 发布失败总数
    MessagesPublishedFailedTotal = promauto.NewCounterVec(
        prometheus.CounterOpts{
            Namespace: "cloudmq",
            Name:      "messages_published_failed_total",
            Help:      "Total number of messages that failed to publish",
        },
        []string{"cluster", "namespace", "topic", "error_type"},
    )

    // Lookup 请求总数（对应 cloudmq_broker_lookup_answers）
    BrokerLookupAnswers = promauto.NewCounterVec(
        prometheus.CounterOpts{
            Namespace: "cloudmq",
            Subsystem: "broker",
            Name:      "lookup_answers_total",
            Help:      "Total number of lookup requests answered",
        },
        []string{"cluster"},
    )
)
```

### 3.2 在业务中使用

```go
package handler

import (
    "context"
    "fmt"
    "my-project/metrics"

    "github.com/prometheus/client_golang/prometheus"
)

type PublishHandler struct {
    cluster string
}

func (h *PublishHandler) Publish(ctx context.Context, namespace, topic string, msg []byte) error {
    labels := prometheus.Labels{
        "cluster":   h.cluster,
        "namespace": namespace,
        "topic":     topic,
    }

    err := doPublish(ctx, msg)
    if err != nil {
        // 失败计数：带 error_type 标签，方便分析失败原因
        metrics.MessagesPublishedFailedTotal.With(prometheus.Labels{
            "cluster":    h.cluster,
            "namespace":  namespace,
            "topic":      topic,
            "error_type": classifyError(err),
        }).Inc()
        return fmt.Errorf("publish failed: %w", err)
    }

    // 成功计数
    metrics.MessagesPublishedTotal.With(labels).Inc()
    return nil
}

func classifyError(err error) string {
    // 将 error 分类为有限的几种类型，避免高基数（cardinality）问题
    switch {
    case isTimeoutError(err):
        return "timeout"
    case isQuotaError(err):
        return "quota_exceeded"
    default:
        return "unknown"
    }
}
```

### 3.3 对应的 Grafana Panel 配置

```promql
# Panel: 发布速率（Time series）
rate(cloudmq_messages_published_total{cluster=~"$cluster", namespace=~"$namespace"}[1m])

# Panel: 失败率
rate(cloudmq_messages_published_failed_total{cluster=~"$cluster"}[1m])
  / rate(cloudmq_messages_published_total{cluster=~"$cluster"}[1m])

# Panel: 成功率百分比
100 * rate(cloudmq_messages_published_total{cluster=~"$cluster"}[1m])
    / (rate(cloudmq_messages_published_total{cluster=~"$cluster"}[1m])
     + rate(cloudmq_messages_published_failed_total{cluster=~"$cluster"}[1m]))
```

> ⚠️ **高基数陷阱**：不要将用户ID、消息ID等高唯一性字段作为 Label！  
> 每个唯一 Label 组合都是一条独立时间序列，高基数会导致 Prometheus 内存爆炸。  
> **规则**：一个 Label 的不同值不超过 1000 个。

---

## 4. Gauge 的完整实现

Gauge 对应"当前状态"，最适合直接展示当前值。

### 4.1 代码实现

```go
package metrics

import (
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promauto"
)

var (
    // 当前 Producer 数量（对应 cloudmq_producers_count）
    ProducersCount = promauto.NewGaugeVec(
        prometheus.GaugeOpts{
            Namespace: "cloudmq",
            Name:      "producers_count",
            Help:      "Current number of active producers",
        },
        []string{"cluster", "namespace"},
    )

    // 当前 Consumer 数量（对应 cloudmq_consumers_count）
    ConsumersCount = promauto.NewGaugeVec(
        prometheus.GaugeOpts{
            Namespace: "cloudmq",
            Name:      "consumers_count",
            Help:      "Current number of active consumers",
        },
        []string{"cluster", "namespace"},
    )

    // 消息积压量（对应 cloudmq_msg_backlog）
    MessageBacklog = promauto.NewGaugeVec(
        prometheus.GaugeOpts{
            Namespace: "cloudmq",
            Name:      "msg_backlog",
            Help:      "Current number of messages in the subscription backlog",
        },
        []string{"cluster", "namespace", "topic", "subscription"},
    )

    // 当前吞吐量（率类 Gauge，直接表示速率）
    // 注意：这是 Gauge 而非 Counter，因为值是当前速率，可增可减
    // 对应 cloudmq_rate_in（broker.txt 中就是 Gauge）
    MessageRateIn = promauto.NewGaugeVec(
        prometheus.GaugeOpts{
            Namespace: "cloudmq",
            Name:      "rate_in",
            Help:      "Current message publish rate (msg/s)",
        },
        []string{"cluster", "namespace", "topic"},
    )

    // JVM 式的线程池 Gauge 示例（对应 bookie/broker 中的线程池指标）
    ThreadPoolActiveWorkers = promauto.NewGaugeVec(
        prometheus.GaugeOpts{
            Name: "cloudmq_executor_active_threads",
            Help: "Number of currently active threads in the executor",
        },
        []string{"cluster", "executor_name"},
    )
)
```

### 4.2 Gauge 的三种更新方式

```go
// 方式一：Set（直接设置当前值，最常用）
ProducersCount.With(prometheus.Labels{
    "cluster":   "cluster-a",
    "namespace": "tenant/namespace",
}).Set(float64(len(activeProducers)))

// 方式二：Inc/Dec（递增/递减1）
ProducersCount.With(labels).Inc()  // 新 producer 连接
ProducersCount.With(labels).Dec()  // producer 断开

// 方式三：Add/Sub（加减任意值）
MessageBacklog.With(labels).Add(float64(newMessages))
MessageBacklog.With(labels).Sub(float64(consumedMessages))
```

### 4.3 定期采集 Gauge 的最佳实践

```go
// 对于需要轮询计算的 Gauge（如 backlog），使用定时任务更新
func StartMetricsCollector(ctx context.Context, store Store, interval time.Duration) {
    ticker := time.NewTicker(interval)
    defer ticker.Stop()

    for {
        select {
        case <-ctx.Done():
            return
        case <-ticker.C:
            collectSubscriptionMetrics(store)
        }
    }
}

func collectSubscriptionMetrics(store Store) {
    subscriptions := store.ListSubscriptions()
    for _, sub := range subscriptions {
        labels := prometheus.Labels{
            "cluster":      sub.Cluster,
            "namespace":    sub.Namespace,
            "topic":        sub.Topic,
            "subscription": sub.Name,
        }
        backlog, _ := store.GetBacklog(sub)
        MessageBacklog.With(labels).Set(float64(backlog))
    }
}
```

> 💡 **注意**：这种定时采集模式要小心"幽灵标签"问题：  
> 如果一个 subscription 被删除，它的 Gauge 仍然存在于 Prometheus 中，  
> 直到下次程序重启或手动 `Delete(labels)` / `Reset()`。

```go
// 删除一个 Gauge 的标签组合
MessageBacklog.Delete(prometheus.Labels{
    "cluster":      "cluster-a",
    "namespace":    "tenant/ns",
    "topic":        "topic-name",
    "subscription": "sub-name",
})
```

---

## 5. Histogram 的完整实现

Histogram 是最复杂但最强大的类型，适合延迟、大小等分布统计。

### 5.1 代码实现

```go
package metrics

import (
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promauto"
)

var (
    // 发布延迟 Histogram（对应 bookie 中 bookkeeper_server_ADD_ENTRY_REQUEST）
    PublishLatency = promauto.NewHistogramVec(
        prometheus.HistogramOpts{
            Namespace: "cloudmq",
            Name:      "publish_latency_seconds",
            Help:      "Publish operation latency distribution",
            // 桶设计：覆盖 0.1ms ~ 10s 的延迟范围
            // 在常见 SLA 阈值处加密（10ms/100ms/1s）
            Buckets: []float64{
                0.0001, // 0.1ms
                0.0005, // 0.5ms
                0.001,  // 1ms
                0.005,  // 5ms
                0.01,   // 10ms  ← SLA 阈值附近
                0.025,  // 25ms
                0.05,   // 50ms
                0.1,    // 100ms ← SLA 阈值附近
                0.25,   // 250ms
                0.5,    // 500ms
                1.0,    // 1s    ← SLA 阈值附近
                2.5,    // 2.5s
                10.0,   // 10s
            },
        },
        []string{"cluster", "namespace", "topic"},
    )

    // 消息大小 Histogram
    MessageSizeBytes = promauto.NewHistogramVec(
        prometheus.HistogramOpts{
            Namespace: "cloudmq",
            Name:      "message_size_bytes",
            Help:      "Message payload size distribution",
            Buckets:   prometheus.ExponentialBuckets(256, 2, 12), // 256B ~ 512KB
        },
        []string{"cluster", "namespace"},
    )

    // 元数据存储操作延迟（对应 cloudmq_metadata_store_ops_latency_ms）
    MetadataStoreLatency = promauto.NewHistogramVec(
        prometheus.HistogramOpts{
            Namespace: "cloudmq",
            Subsystem: "metadata_store",
            Name:      "ops_latency_ms",
            Help:      "Metadata store operation latency in milliseconds",
            Buckets:   []float64{1, 3, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000},
        },
        []string{"cluster", "name", "type", "status"},
    )
)
```

### 5.2 在业务中使用

```go
func (h *PublishHandler) PublishWithLatency(ctx context.Context, namespace, topic string, msg []byte) error {
    startTime := time.Now()

    err := doPublish(ctx, msg)

    // 无论成功失败都记录延迟
    duration := time.Since(startTime)
    labels := prometheus.Labels{
        "cluster":   h.cluster,
        "namespace": namespace,
        "topic":     topic,
    }
    metrics.PublishLatency.With(labels).Observe(duration.Seconds())

    // 记录消息大小
    metrics.MessageSizeBytes.With(prometheus.Labels{
        "cluster":   h.cluster,
        "namespace": namespace,
    }).Observe(float64(len(msg)))

    return err
}

// 元数据存储操作示例
func (s *MetadataStore) Get(ctx context.Context, key string) ([]byte, error) {
    startTime := time.Now()
    
    val, err := s.backend.Get(ctx, key)
    
    latencyMs := float64(time.Since(startTime)) / float64(time.Millisecond)
    
    status := "success"
    if err != nil {
        status = "fail"
    }
    
    metrics.MetadataStoreLatency.With(prometheus.Labels{
        "cluster": s.cluster,
        "name":    "metadata-store",
        "type":    "get",
        "status":  status,
    }).Observe(latencyMs)
    
    return val, err
}
```

### 5.3 Bucket 设计指南

```go
// 方式一：手动指定（精准控制）
Buckets: []float64{0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0}

// 方式二：线性等距（prometheus.LinearBuckets）
// 从 5 开始，步长 5，共 10 个桶: 5, 10, 15, 20, ..., 50
Buckets: prometheus.LinearBuckets(5, 5, 10)

// 方式三：指数增长（最常用，适合跨越多个数量级的延迟）
// 从 1ms 开始，每次乘以 2，共 10 个桶: 1, 2, 4, 8, 16, 32, 64, 128, 256, 512
Buckets: prometheus.ExponentialBuckets(1, 2, 10)

// 方式四：指数递减桶（prometheus.ExponentialBucketsRange）
// 在 start 到 end 之间均匀分布 count 个桶（指数间隔）
Buckets: prometheus.ExponentialBucketsRange(0.1, 100, 10)
```

### 5.4 对应的 PromQL

```promql
# p99 延迟（用 histogram_quantile）
histogram_quantile(0.99,
  rate(cloudmq_publish_latency_seconds_bucket{cluster=~"$cluster"}[$__rate_interval])
)

# p50, p95, p99 同图展示（三个 target）
histogram_quantile(0.50, rate(cloudmq_publish_latency_seconds_bucket[$__rate_interval]))
histogram_quantile(0.95, rate(cloudmq_publish_latency_seconds_bucket[$__rate_interval]))
histogram_quantile(0.99, rate(cloudmq_publish_latency_seconds_bucket[$__rate_interval]))

# 平均延迟（sum/count）
rate(cloudmq_publish_latency_seconds_sum[$__rate_interval])
/ rate(cloudmq_publish_latency_seconds_count[$__rate_interval])
```

---

## 6. Summary 的实现与适用场景

### 6.1 代码实现

```go
var (
    // 发布延迟 Summary（提前在客户端计算分位数）
    // 注意：MaxAge + AgeBuckets 控制滑动窗口
    PublishLatencySummary = promauto.NewSummaryVec(
        prometheus.SummaryOpts{
            Namespace: "cloudmq",
            Name:      "broker_publish_latency",
            Help:      "Publish latency with pre-computed quantiles",
            // 分位数及误差目标（误差越小，内存越大）
            Objectives: map[float64]float64{
                0.5:   0.05,  // p50, 误差 ±5%
                0.9:   0.01,  // p90, 误差 ±1%
                0.99:  0.001, // p99, 误差 ±0.1%
                0.999: 0.001, // p999
            },
            // 滑动窗口设置（避免历史数据污染）
            MaxAge:     10 * time.Minute, // 只保留最近 10 分钟的样本
            AgeBuckets: 5,               // 将窗口分为 5 个子桶滚动
        },
        []string{"cluster"},
    )
)
```

### 6.2 Summary vs Histogram 选择原则

| 场景 | 选择 | 原因 |
|------|------|------|
| 需要跨多实例聚合 p99 | **Histogram** | `histogram_quantile()` 支持聚合 |
| 单实例即可，追求精度 | **Summary** | 客户端精确计算 |
| 采集点很多（> 1000/s） | **Histogram** | 采样计算更高效 |
| 对存储敏感，桶数量少 | **Summary** | 只输出分位数，体积小 |
| Java 应用（Micrometer 默认）| **Summary** | Java 库默认 Summary |
| Go 应用（新项目）| **Histogram** | 更灵活 |

---

## 7. 完整的 metrics 包结构

经过上面的分析，给出一个生产级别的 Go metrics 包设计：

```go
// metrics/metrics.go
package metrics

import (
    "net/http"

    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promhttp"
)

// Registry 自定义注册表（避免污染默认全局注册表）
var Registry = prometheus.NewRegistry()

// 初始化所有指标
func init() {
    // 注册默认的 Go 运行时指标（对应 jvm_ 指标）
    Registry.MustRegister(
        prometheus.NewGoCollector(),          // Go 运行时指标
        prometheus.NewProcessCollector(
            prometheus.ProcessCollectorOpts{},
        ),
    )
}

// Handler 返回 HTTP 处理器
func Handler() http.Handler {
    return promhttp.HandlerFor(Registry, promhttp.HandlerOpts{
        EnableOpenMetrics: true, // 支持 OpenMetrics 格式
    })
}
```

```go
// metrics/broker.go
package metrics

import (
    "github.com/prometheus/client_golang/prometheus"
)

var (
    RateIn = prometheus.NewGaugeVec(
        prometheus.GaugeOpts{Name: "cloudmq_rate_in", Help: "Message publish rate (msg/s)"},
        []string{"cluster", "namespace", "topic"},
    )

    TopicsCount = prometheus.NewGaugeVec(
        prometheus.GaugeOpts{Name: "cloudmq_topics_count", Help: "Number of topics"},
        []string{"cluster", "namespace"},
    )

    PublishLatency = prometheus.NewHistogramVec(
        prometheus.HistogramOpts{
            Name:    "cloudmq_instance_publish_latency",
            Help:    "Per-instance publish latency",
            Buckets: prometheus.ExponentialBucketsRange(0.5, 1000, 12),
        },
        []string{"cluster", "instance"},
    )
)

func init() {
    // 在自定义 Registry 中注册
    Registry.MustRegister(RateIn, TopicsCount, PublishLatency)
}
```

---

## 8. 中间件模式：HTTP 请求自动计量

```go
// middleware/metrics.go
package middleware

import (
    "net/http"
    "strconv"
    "time"

    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promauto"
)

var (
    httpRequestDuration = promauto.NewHistogramVec(
        prometheus.HistogramOpts{
            Name:    "http_request_duration_seconds",
            Help:    "HTTP request duration distribution",
            Buckets: prometheus.DefBuckets, // 默认桶：.005, .01, .025, .05, .1, .25, .5, 1, 2.5, 5, 10
        },
        []string{"method", "path", "status_code"},
    )
    
    httpRequestsTotal = promauto.NewCounterVec(
        prometheus.CounterOpts{
            Name: "http_requests_total",
            Help: "Total HTTP requests",
        },
        []string{"method", "path", "status_code"},
    )
)

// MetricsMiddleware 自动记录所有 HTTP 请求指标
func MetricsMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        
        // 包装 ResponseWriter 以捕获状态码
        wrapped := &responseWriter{ResponseWriter: w, statusCode: http.StatusOK}
        next.ServeHTTP(wrapped, r)
        
        duration := time.Since(start)
        labels := prometheus.Labels{
            "method":      r.Method,
            "path":        normalizePath(r.URL.Path), // 归一化路径，避免高基数
            "status_code": strconv.Itoa(wrapped.statusCode),
        }
        
        httpRequestDuration.With(labels).Observe(duration.Seconds())
        httpRequestsTotal.With(labels).Inc()
    })
}

type responseWriter struct {
    http.ResponseWriter
    statusCode int
}

func (rw *responseWriter) WriteHeader(code int) {
    rw.statusCode = code
    rw.ResponseWriter.WriteHeader(code)
}

func normalizePath(path string) string {
    // 将 /api/users/12345 → /api/users/:id
    // 避免每个 user ID 都创建一条时间序列
    // 实际项目中用路由库提供的路径模板
    return path
}
```

---

## 9. 本章小结

| 指标类型 | Go API | 业务场景 | 关键注意点 |
|---------|--------|---------|-----------|
| Counter | `NewCounterVec` + `.Inc()/.Add()` | 请求数、错误数、消息数 | label 基数控制；避免 error message 做 label |
| Gauge | `NewGaugeVec` + `.Set()/.Inc()/.Dec()` | 连接数、队列深度、内存 | 删除不再使用的标签组合 |
| Histogram | `NewHistogramVec` + `.Observe()` | 延迟、大小分布 | 桶设计很关键；`_seconds` 为标准单位 |
| Summary | `NewSummaryVec` + `.Observe()` | 单实例精确分位数 | 不能跨实例聚合；设置 MaxAge |

**下一章**：指标分类实战——如何将业务指标按"黄金信号"（延迟、流量、错误、饱和度）分类，以及如何组织 Dashboard 的 Row 结构，做到监控覆盖无死角。
