# 第二章：PromQL 深度解析——基于真实 Dashboard 表达式

> 本章以 `broker.json` 和 `bookie.json` 中的真实 PromQL 表达式为例，  
> 从最基础的选择器讲到高级聚合，做到"每一行代码都能读懂"。

---

## 1. PromQL 核心概念：即时向量 vs 区间向量

### 1.1 即时向量（Instant Vector）

查询某一时刻的所有时间序列：

```promql
cloudmq_topics_count
```

返回每条时序最新的一个数据点，结果是 **一组样本**（每个标签组合一个）。

### 1.2 区间向量（Range Vector）

查询一段时间内的所有样本，`[5m]` 代表过去 5 分钟：

```promql
cloudmq_broker_lookup_answers_total[5m]
```

返回每条时序在过去 5 分钟内的所有数据点集合。  
区间向量**不能直接绘图**，必须经过函数处理（如 `rate()`）才能变为即时向量。

---

## 2. 标签选择器

### 2.1 精确匹配 `=`

```promql
jvm_memory_bytes_used{area="heap"}
```

只返回 `area` 标签等于 `"heap"` 的时间序列。

### 2.2 正则匹配 `=~`

```promql
# broker.json 中的真实表达式
sum(cloudmq_rate_in{cluster=~"$cluster", instance=~"$instance"}) by (instance)
```

`=~` 使用 RE2 正则语法，`$cluster` 和 `$instance` 是 Grafana 变量（后续章节详讲）。

### 2.3 排除匹配 `!=` 和 `!~`

```promql
jvm_threads_state{state!="RUNNABLE"}         # 不等于
jvm_threads_state{state!~"WAITING|BLOCKED"}  # 正则排除
```

### 2.4 选择器汇总

| 操作符 | 语义 |
|--------|------|
| `=` | 精确匹配 |
| `!=` | 不等于 |
| `=~` | 正则匹配 |
| `!~` | 正则排除 |

---

## 3. 速率函数：Counter 的正确打开方式

Counter 的原始值是单调递增的累计数，直接绘图没有意义。需要用速率函数转换：

### 3.1 `rate()` — 周期平均速率

```promql
# 计算过去 30 秒内，写入字节的平均速率（bytes/s）
rate(bookie_WRITE_BYTES{job=~"$job"}[30s])
```

`rate()` 会自动处理 Counter 重置（重启归零），对长时间窗口更稳定。

**来自 bookie.json 的真实例子**：
```promql
# panel "Throughput (MB/s)" 中的 query A
sum(rate(bookie_WRITE_BYTES{job=~"$job"}[30s]))
```

### 3.2 `irate()` — 瞬时速率

```promql
# 基于最近两个数据点计算速率
irate(bookkeeper_server_ADD_ENTRY_count{job=~"$job", instance=~"$instance", success="true"}[30s])
```

`irate()` 对**突刺**更敏感，适合检测短暂的流量峰值。  
`[30s]` 只是查找最近两个点的时间范围，不是平均窗口。

**broker.json 中的对比**：
```promql
# bookie.json panel "Entry Rate" 使用 irate，更灵敏
sum(irate(bookkeeper_server_READ_ENTRY_count{success="true"}[30s]))
```

### 3.3 rate vs irate 选择原则

| 场景 | 推荐函数 |
|------|---------|
| 长时间趋势图、告警规则 | `rate()` |
| 实时流量监控、峰值检测 | `irate()` |
| 采集间隔较长（>1min） | `rate()`（`irate` 可能丢精度）|

---

## 4. 聚合操作符

### 4.1 `sum()` — 求和

```promql
# broker.json panel "Publish rate (msg/s)"
sum(cloudmq_rate_in{cluster=~"$cluster", instance=~"$instance"}) by (instance)
```

`by (instance)` 表示按 `instance` 标签分组聚合，结果保留 `instance` 标签，其余丢弃。

等价关系：
```
原始时序：                       聚合后：
rate_in{topic="A", instance="i1"} 10   →  sum by(instance): {instance="i1"} 30
rate_in{topic="B", instance="i1"} 20   →
rate_in{topic="C", instance="i2"} 15   →  sum by(instance): {instance="i2"} 15
```

### 4.2 `without` 子句（与 `by` 相反）

```promql
sum(cloudmq_rate_in) without (topic, namespace)
# 等价于 sum by(cluster, instance)
```

### 4.3 常用聚合操作符列表

| 操作符 | 说明 |
|--------|------|
| `sum` | 求和 |
| `avg` | 均值 |
| `min` / `max` | 最小/最大值 |
| `count` | 计数（有多少条时间序列） |
| `count_values` | 统计某标签值出现次数 |
| `topk(n, expr)` | 取最大的 n 条 |
| `bottomk(n, expr)` | 取最小的 n 条 |

**bookie.json 中的 count 用法**：
```promql
# panel "Writable Bookies" — 统计 SERVER_STATUS==1 的 bookie 数量
count(bookie_SERVER_STATUS{job=~"$job"} == 1)
```

---

## 5. 比较运算符与过滤

```promql
# 只保留 SERVER_STATUS 为 1 的时间序列
bookie_SERVER_STATUS{job=~"$job"} == 1

# 只保留大于 0 的 backlog
cloudmq_msg_backlog{cluster=~"$cluster"} > 0
```

比较运算符返回满足条件的时间序列（不满足的被过滤掉）。

---

## 6. 算术运算

### 6.1 简单计算

```promql
# broker.json panel "Storage Write Latency" 中
# 将每分钟的计数换算为每秒
sum(cloudmq_storage_write_latency_le_0_5{cluster=~"$cluster"}) / 60.0
```

### 6.2 百分比计算

```promql
# bookie.json panel "writable bookies (percentage)"
100 
* count(bookie_SERVER_STATUS{job=~"$job", instance=~"$instance"} == 1)
/ count(bookie_SERVER_STATUS{job=~"$job", instance=~"$instance"})
```

计算逻辑：
1. 分子：`STATUS==1` 的 bookie 数
2. 分母：全部 bookie 数
3. `* 100`：转为百分比

### 6.3 成功率计算

```promql
# bookie.json panel "Success Rate"
100 * sum(irate(bookkeeper_server_ADD_ENTRY_count{success="true"}[30s]))
    / sum(irate(bookkeeper_server_ADD_ENTRY_count[30s]))
```

注意：分母不过滤 `success="true"`，包含所有请求（成功+失败）。

---

## 7. Histogram 的 PromQL 模式

### 7.1 计算分位数

```promql
# 基本语法
histogram_quantile(0.99, rate(my_histogram_bucket[5m]))

# bookie.json panel "Latency" 中（Summary，不需要 histogram_quantile）
avg(bookkeeper_server_ADD_ENTRY_REQUEST{success="true", quantile="0.99"})
```

### 7.2 CloudMQ 自定义 Histogram（分桶存为 Gauge）

CloudMQ 不使用标准 Prometheus Histogram 格式，  
而是将每个桶存为独立的 Gauge 指标（命名如 `cloudmq_storage_write_latency_le_5`）：

```
cloudmq_storage_write_latency_le_0_5   → ≤ 0.5ms 的写入次数
cloudmq_storage_write_latency_le_1     → ≤ 1ms
cloudmq_storage_write_latency_le_5     → ≤ 5ms
cloudmq_storage_write_latency_le_10    → ≤ 10ms
...
cloudmq_storage_write_latency_overflow → > 1000ms
```

对应的 PromQL（broker.json Storage Write Latency panel）：
```promql
# "1 - 5 ms" 这个桶的每秒消息数 = (≤5ms总数 / 60秒窗口)
sum(cloudmq_storage_write_latency_le_5{cluster=~"$cluster"}) / 60.0
```

> 💡 **开发者视角**：这种实现方式是将 Histogram 的桶「拍扁」为多个 Gauge，  
> 优点是在不支持 Histogram 的场景下也能工作，缺点是无法使用 `histogram_quantile()`，  
> 只能看桶分布。

---

## 8. 常用函数速查

### 8.1 时间相关

| 函数 | 说明 |
|------|------|
| `rate(v[d])` | 区间内每秒平均速率 |
| `irate(v[d])` | 基于最近两点的瞬时速率 |
| `increase(v[d])` | 区间内总增量 (`rate * 时间`) |
| `delta(v[d])` | Gauge 在区间内的变化量 |
| `deriv(v[d])` | 线性回归导数（Gauge 趋势） |

### 8.2 聚合时间序列

| 函数 | 说明 |
|------|------|
| `avg_over_time(v[d])` | 区间内均值 |
| `max_over_time(v[d])` | 区间内最大值 |
| `min_over_time(v[d])` | 区间内最小值 |
| `last_over_time(v[d])` | 区间内最后一个值 |

### 8.3 数学

| 函数 | 说明 |
|------|------|
| `abs(v)` | 绝对值 |
| `ceil(v)` / `floor(v)` | 向上/向下取整 |
| `round(v)` | 四舍五入 |
| `clamp(v, min, max)` | 截断到 [min, max] |
| `sqrt(v)` | 平方根 |

---

## 9. 真实 Dashboard 表达式全解析

### 9.1 broker Publish Rate

```promql
sum(cloudmq_rate_in{cluster=~"$cluster", instance=~"$instance"}) by (instance)
```

- `cloudmq_rate_in`：Gauge，单位 msg/s（已是速率，无需 `rate()`）
- `sum ... by (instance)`：按实例分组汇总各 namespace/topic 的速率
- `$cluster`, `$instance`：Grafana 模板变量（正则匹配）

### 9.2 broker JVM GC 时间

```promql
# 未在 dashboard 展示，但常见写法：
rate(jvm_gc_collection_seconds_sum{gc="ZGC Cycles"}[1m])
```

- 这是一个 Summary 指标，`_sum` 是 GC 总耗时
- `rate()` 得到每秒 GC 的平均耗时

### 9.3 bookie 成功率

```promql
100 * sum(irate(bookkeeper_server_ADD_ENTRY_count{success="true"}[30s]))
    / sum(irate(bookkeeper_server_ADD_ENTRY_count[30s]))
```

完整解读：
1. `irate(...{success="true"}[30s])`：成功写入的瞬时速率
2. `irate(...[30s])`：所有写入的瞬时速率（包含失败）
3. 两个 `sum()` 分别跨实例聚合
4. 相除得到 0~1 的比率，乘 100 得到百分比

---

## 10. 本章小结

| 知识点 | 要点 |
|-------|------|
| 即时向量 | 某时刻的当前值 |
| 区间向量 | `[5m]`，需函数处理 |
| `rate()` vs `irate()` | 长期趋势 vs 瞬时峰值 |
| `sum by (label)` | 分组聚合，保留指定标签 |
| 算术运算 | 除法做占比，乘法做换算 |
| Histogram | `histogram_quantile(0.99, rate(_bucket[5m]))` |

**下一章**：深入 Grafana Dashboard 的 Panel 类型，理解每种指标在Grafana中的最佳可视化方式。
