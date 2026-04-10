# 第一章：Prometheus 基础与指标类型

> **教程定位**：本系列从开发者视角出发，以 CloudMQ (`bookie` + `broker`) 的真实指标数据为例，讲解 Prometheus 指标体系、PromQL 查询、Grafana Dashboard 建设全链路。

---

## 1. 监控体系全景

```
┌─────────────────────────────────────────────────────────────────┐
│                         应用程序 (Go/Java/…)                     │
│                                                                  │
│   Counter / Gauge / Histogram / Summary                          │
│           │  在代码里注册、更新指标                               │
└───────────┼──────────────────────────────────────────────────────┘
            │  /metrics  HTTP endpoint
            ▼
┌─────────────────────────────┐
│   Prometheus Server         │  ← 定时拉取 (scrape)
│   时序数据库 (TSDB)         │
└────────────┬────────────────┘
             │  PromQL 查询
             ▼
┌─────────────────────────────┐
│   Grafana Dashboard         │  ← 可视化
└─────────────────────────────┘
```

CloudMQ 的 `broker.txt` 和 `bookie.txt` 就是 `/metrics` endpoint 返回的原始内容，  
即 **Prometheus 文本格式（Text Exposition Format）**。

---

## 2. Prometheus 文本格式解析

打开 `broker.txt`，你会看到两种行：

```
# TYPE cloudmq_rate_in gauge
cloudmq_rate_in{cluster="cluster-a-cloudmqcluster",namespace="cloudmq/__monitor",topic="persistent://..."} 0.0
```

| 组成部分 | 说明 |
|---------|------|
| `# TYPE <name> <type>` | 声明指标类型，是元数据注释 |
| `<metric_name>` | 指标名，唯一标识 |
| `{key="value", …}` | **标签（Labels）**，用于多维过滤 |
| `<value>` | 数值（float64） |

> **规律**：每个 `# TYPE` 行之后，紧跟该指标的所有时间序列（不同 labels 组合）。

### 2.1 标签的作用

同一个指标名 + 不同标签 = 不同的时间序列：

```
cloudmq_rate_in{cluster="cluster-a",namespace="cloudmq/__monitor",...} 0.0
cloudmq_rate_in{cluster="cluster-a",namespace="cloudmq/system",...}    0.0
```

这两条记录虽然指标名相同，但 `namespace` 不同，是两条独立的时间序列。

---

## 3. 四种指标类型详解

Prometheus 定义了 4 种核心指标类型，**选型决定了 PromQL 写法和 Grafana Panel 类型**。

### 3.1 Counter（计数器）

**特征**：
- 值只增不减（重启后归零）
- 代表"累计发生了多少次" 

**在 broker.txt 中的例子**：
```
# TYPE cloudmq_broker_lookup_answers counter
cloudmq_broker_lookup_answers_total{cluster="cluster-a-cloudmqcluster"} 6.0
cloudmq_broker_lookup_answers_created{cluster="cluster-a-cloudmqcluster"} 1.775735054435E9
```

> 注意：Prometheus 4.x 规范中 counter 会自动追加 `_total` 后缀（旧版不强制）。  
> `_created` 是 Counter 创建时间戳，用于支持 exemplar 等高级特性，一般忽略。

**典型用途**：
- 请求总数、错误次数、消息发布总数
- 需要配合 `rate()` / `irate()` 使用，转换为速率

```
# bookie.txt 中的例子
# TYPE bookkeeper_server_ADD_ENTRY_count counter（被 dashboard 用 irate 处理）
```

### 3.2 Gauge（仪表盘）

**特征**：
- 值可增可减，代表"当前状态"
- 无需速率转换，直接可用

**在 broker.txt 中的例子**：
```
# TYPE jvm_memory_bytes_used gauge
jvm_memory_bytes_used{cluster="cluster-a-cloudmqcluster",area="heap"} 1.44703488E8
jvm_memory_bytes_used{cluster="cluster-a-cloudmqcluster",area="nonheap"} 1.06328352E8

# TYPE cloudmq_topics_count gauge
cloudmq_topics_count{cluster="cluster-a-cloudmqcluster",namespace="cloudmq/__monitor"} 3

# TYPE jvm_threads_current gauge
jvm_threads_current{cluster="cluster-a-cloudmqcluster"} 168.0
```

**典型用途**：
- 内存使用量、线程数、连接数、队列深度、Backlog 大小
- 可以直接在 Grafana 展示当前值

### 3.3 Histogram（直方图）

**特征**：
- 对观测值（如延迟、大小）进行分桶统计
- 自动生成三种系列：`_bucket{le="..."}`, `_sum`, `_count`
- 可以计算百分位（p50/p99/p999）

**在 broker.txt 中的例子**：
```
# TYPE cloudmq_metadata_store_ops_latency_ms histogram
cloudmq_metadata_store_ops_latency_ms_bucket{...,le="1.0"}   7.0
cloudmq_metadata_store_ops_latency_ms_bucket{...,le="3.0"}   37.0
cloudmq_metadata_store_ops_latency_ms_bucket{...,le="5.0"}   76.0
...
cloudmq_metadata_store_ops_latency_ms_bucket{...,le="+Inf"} 144.0
cloudmq_metadata_store_ops_latency_ms_count{...}            144.0
cloudmq_metadata_store_ops_latency_ms_sum{...}           430315.0
```

解读：`le="5.0"` 代表"≤5ms 的请求有 76 个"。

**桶（Bucket）的设计原则**：
- 覆盖你关心的延迟范围
- 在关键阈值附近加密（如 SLA 是 10ms，则在 5/10/20 各设一个桶）

**PromQL 计算 p99**：
```promql
histogram_quantile(0.99, rate(cloudmq_metadata_store_ops_latency_ms_bucket[5m]))
```

### 3.4 Summary（摘要）

**特征**：
- 在**客户端**计算分位数，直接输出 `{quantile="0.99"}` 标签
- 无需服务端计算，但**不能跨实例聚合**

**在 broker.txt 中的例子**：
```
# TYPE cloudmq_broker_publish_latency summary
cloudmq_broker_publish_latency{cluster="...",quantile="0.5"}   NaN
cloudmq_broker_publish_latency{cluster="...",quantile="0.99"}  NaN
cloudmq_broker_publish_latency_count{cluster="..."} 0.0
cloudmq_broker_publish_latency_sum{cluster="..."}   0.0
```

**bookie dashboard 中的例子**（Java Summary）：
```
# bookie.json panel "Latency" 的 PromQL：
avg(bookkeeper_server_ADD_ENTRY_REQUEST{success="true", quantile="0.99"})
```

---

## 4. 四种类型对比速查表

| 类型 | 值变化 | 是否可聚合 | 典型 PromQL 函数 | 典型 Grafana Panel |
|------|--------|-----------|------------------|--------------------|
| **Counter** | 只增 | ✅ | `rate()`, `irate()` | Time series (折线) |
| **Gauge** | 任意 | ✅ | 直接使用, `avg()` | Time series / Stat |
| **Histogram** | 只增(累计) | ✅ | `histogram_quantile()`, `rate(_bucket)` | Time series (折线/堆积) |
| **Summary** | 只增(累计) | ⚠️ 有限 | 直接使用 quantile 标签 | Time series (折线) |

> ⚠️ **Summary 跨实例聚合的陷阱**：  
> 如果有 3 个 broker 实例，`avg(cloudmq_broker_publish_latency{quantile="0.99"})`  
> 得到的是"三个实例各自 p99 的平均值"，而不是"所有请求的 p99"。  
> 真正想要全局 p99，应该使用 Histogram + `histogram_quantile()`。

---

## 5. CloudMQ 指标命名规律

观察 `broker.txt` 中的指标前缀，可以识别其来源：

| 前缀 | 来源 | 示例 |
|------|------|------|
| `cloudmq_` | CloudMQ 业务指标 | `cloudmq_rate_in`, `cloudmq_topics_count` |
| `jvm_` | JVM 运行时（Java） | `jvm_memory_bytes_used`, `jvm_gc_collection_seconds` |
| `bookie_` | BookKeeper 服务器状态 | `bookie_SERVER_STATUS`, `bookie_WRITE_BYTES` |
| `bookkeeper_server_` | BookKeeper 服务层 | `bookkeeper_server_ADD_ENTRY_count` |
| `caffeine_cache_` | Caffeine 缓存库 | `caffeine_cache_hit_total` |
| `bes_` | 嵌入式 HTTP 服务器 | `bes_threadpool_currentthreadcount` |
| `log4j2_` | 日志框架 | `log4j2_appender_total` |
| `process_` | 进程级别 | `process_cpu_seconds_total`, `process_open_fds` |

---

## 6. 本章小结

| 关键概念 | 要点 |
|---------|------|
| 指标名+标签 | 确定一条唯一的时间序列 |
| Counter | 累计值，需用 `rate()`/`irate()` 转速率 |
| Gauge | 当前值，直接展示 |
| Histogram | 分桶，支持服务端聚合计算分位数 |
| Summary | 客户端分位，不能跨实例聚合 |

**下一章**：将深入 PromQL 查询语言——过滤、聚合、速率计算，结合真实 dashboard 中的表达式逐一拆解。
