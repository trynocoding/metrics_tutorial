# 第八章：Prometheus 告警规则实战

> **目标**：理解告警规则的语法结构，能读懂并编写针对 CloudMQ 各组件的 Prometheus AlertingRule，掌握告警阈值设计原则与生产环境调优方法。

---

## 8.1 为什么需要告警规则？

Grafana Dashboard 能让你**主动**看到问题——但前提是你得盯着屏幕。在生产环境中，更需要**告警**：当某个指标超出正常范围并持续一段时间时，系统主动通知运维人员。

Prometheus 的告警机制分两层：

```
Prometheus（评估规则，产生告警）
        ↓
Alertmanager（路由、分组、静默、发送通知）
        ↓
通知渠道（钉钉 / 企微 / PagerDuty / Slack ...）
```

本章聚焦第一层：如何编写让 Prometheus 正确触发告警的规则文件。

---

## 8.2 告警规则文件结构详解

告警规则以 YAML 编写，加载到 `prometheus.yml` 的 `rule_files` 字段：

```yaml
# prometheus.yml
rule_files:
  - "/etc/prometheus/rules/bookie_alerts.yml"
  - "/etc/prometheus/rules/broker_alerts.yml"
  - "/etc/prometheus/rules/dcs_alerts.yml"
```

每个规则文件的结构：

```yaml
groups:
  - name: cloudmq-bookie-alerts          # ① 告警组名称（全局唯一）
    rules:
      - alert: BookieLedgerDiskUsageHigh  # ② 告警名称（组内唯一）
        expr: |                           # ③ PromQL 表达式
          bookie_ledger_dir__cloudmq_data_bookkeeper_ledgers_usage > 85
        for: 5m                           # ④ 持续时间
        labels:
          severity: critical              # ⑤ 自定义标签
        annotations:
          summary: "Bookie 账本数据盘容量不足: {{ $labels.instance }}"  # ⑥ 模板
          description: "节点 {{ $labels.instance }} 的账本磁盘使用率超过 85%，磁盘若写满将转为只读模式。"
```

### 各字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `alert` | string | 告警名称，出现在 Prometheus UI 和通知消息中 |
| `expr` | PromQL | 表达式结果为非空（true）时进入 Pending 状态 |
| `for` | duration | 告警需持续此时长才从 **Pending → Firing**，用于过滤瞬时抖动 |
| `labels` | map | 附加到告警上的标签，可用于 Alertmanager 的路由匹配 |
| `annotations` | map | 可读性描述，支持 Go 模板语法 |

### 告警生命周期

```
表达式结果为 true
        ↓
    [Pending]  ← for 计时开始
        ↓  持续时间 >= for
    [Firing]   ← 此时 Alertmanager 才接收告警
        ↓  表达式结果变为 false
   [Inactive]
```

> **关键理解**：`for: 5m` 意味着"连续 5 分钟表达式都为 true"才触发——单次毛刺不会触发告警，这是生产环境防噪的核心机制。

### 模板变量

| 变量 | 说明 |
|------|------|
| `{{ $labels.instance }}` | 触发告警的实例地址（来自抓取目标的 `instance` 标签） |
| `{{ $labels.job }}` | 所属 job 名称 |
| `{{ $labels.component }}` | 自定义标签，如 `"bookie"` |
| `{{ $value }}` | 触发告警时，表达式的当前计算值 |

---

## 8.3 Bookie 告警规则解析（`bookie_alerts.yml`）

```yaml
groups:
  - name: cloudmq-bookie-alerts
    rules:
      - alert: BookieInstanceDown
        expr: up{job="cmq-bookie"} == 0 or bookie_SERVER_STATUS != 1
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Bookie 节点宕机或服务状态异常: {{ $labels.instance }}"
          description: "Bookie 节点 {{ $labels.instance }} 服务未就绪或进程宕机，将直接导致存储容量和副本可用率下降。"

      - alert: BookieHeapMemoryUsageHigh
        expr: jvm_memory_bytes_used{area="heap", component="bookie"} / jvm_memory_bytes_max{area="heap", component="bookie"} > 0.85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Bookie 节点 {{ $labels.instance }} 堆内存使用率高"
          description: "Bookie 节点 {{ $labels.instance }} 的堆内存使用率超过 85%，存在 OOM 风险。"

      - alert: BookieLedgerDiskUsageHigh
        expr: bookie_ledger_dir__cloudmq_data_bookkeeper_ledgers_usage > 85
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Bookie 账本数据盘容量不足: {{ $labels.instance }}"
          description: "节点 {{ $labels.instance }} 的账本(Ledger)磁盘空间使用率超过 85%，磁盘若写满将转为只读模式。"

      - alert: BookieIndexDiskUsageHigh
        expr: bookie_index_dir__cloudmq_data_bookkeeper_ledgers_usage > 85
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Bookie 索引盘容量不足: {{ $labels.instance }}"
          description: "节点 {{ $labels.instance }} 的索引(Index)磁盘空间使用率超过 85%。"

      - alert: BookieWriteRequestsRejected
        expr: rate(bookkeeper_server_ADD_ENTRY_REJECTED[5m]) > 0
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "Bookie 写入请求被拒绝: {{ $labels.instance }}"
          description: "节点 {{ $labels.instance }} 正在拒绝写入请求，可能是线程池队列已打满，写压力过载。"
```

### 逐条解析

**1. `BookieInstanceDown` — 双重检测，更可靠**

```yaml
expr: up{job="cmq-bookie"} == 0 or bookie_SERVER_STATUS != 1
```

这条规则用了 `or` 联合两个判断：
- `up == 0`：Prometheus 抓取失败（进程宕机、网络不通）
- `bookie_SERVER_STATUS != 1`：进程活着但服务未就绪（如正在启动、GC Stop-The-World 过长）

两种情况都应触发告警，这比单纯检测 `up` 更能捕捉"**灰色状态**"。

**2. `BookieHeapMemoryUsageHigh` — 比率计算**

```yaml
expr: jvm_memory_bytes_used{area="heap", component="bookie"}
    / jvm_memory_bytes_max{area="heap", component="bookie"} > 0.85
```

两个同类型 Gauge 做除法得到使用率，标签过滤确保只匹配 `bookie` 组件的堆内存。注意：`for: 5m` 过滤了短暂的 GC 压力导致的瞬时高峰。

**3. `BookieLedgerDiskUsageHigh` / `BookieIndexDiskUsageHigh` — 磁盘告警**

阈值设为 **85%** 而非 95%，原因：
- Bookie 磁盘写满后会自动切换为**只读模式**，拒绝所有写入请求
- 磁盘使用率从 85% 增长到 100% 的速度往往比想象的快
- 留出 15% 的窗口期给运维人员扩容或清理数据

**4. `BookieWriteRequestsRejected` — Counter 的速率检测**

```yaml
expr: rate(bookkeeper_server_ADD_ENTRY_REJECTED[5m]) > 0
```

`ADD_ENTRY_REJECTED` 是 Counter 类型，必须用 `rate()` 求速率。`> 0` 意味着只要有拒绝发生就告警——这类错误在正常情况下绝对不应该出现，因此零容忍是合理的。

---

## 8.4 Broker 告警规则解析（`broker_alerts.yml`）

```yaml
groups:
  - name: cloudmq-broker-alerts
    rules:
      - alert: BrokerInstanceDown
        expr: up{job="cmq-broker"} == 0
        for: 1m
        labels:
          severity: critical

      - alert: BrokerHeapMemoryUsageHigh
        expr: jvm_memory_bytes_used{area="heap", component="broker"} / jvm_memory_bytes_max{area="heap", component="broker"} > 0.85
        for: 5m
        labels:
          severity: warning

      - alert: BrokerMessageBacklogTooHigh
        expr: cloudmq_broker_msg_backlog > 500000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Broker 集群消息积压严重: {{ $value }} 条"
          description: "Broker 全局消息积压超过 50 万条，可能意味着消费者处理慢或已经停止消费。"

      - alert: BrokerTopicLoadFailed
        expr: rate(cloudmq_topic_load_failed[5m]) > 0
        for: 1m
        labels:
          severity: warning

      - alert: BrokerStorageWriteErrors
        expr: rate(cloudmq_ml_AddEntryErrors[5m]) > 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Broker 存储层写入 Ledger 失败"
          description: "节点 {{ $labels.instance }} 向 Bookie 写入数据发生错误，可能导致丢失数据或生产者严重受阻。"
```

### 重点解析

**`BrokerMessageBacklogTooHigh` — 注意 `$value` 的用法**

```yaml
summary: "Broker 集群消息积压严重: {{ $value }} 条"
```

`$value` 在此处会渲染为触发告警时 `cloudmq_broker_msg_backlog` 的实际值（如 "782341 条"），让运维人员在告警通知中直接看到严重程度，无需再去查 Dashboard。

**`BrokerStorageWriteErrors` — 为什么是 critical？**

向 Bookie 写入失败意味着消息数据无法被持久化，直接触发数据可靠性风险。该指标为 Counter，任何非零速率都是立即响应信号。其触发往往预示 Bookie 集群出了故障，需要同步检查 `BookieInstanceDown` 是否同时触发。

---

## 8.5 DCS 告警规则解析（`dcs_alerts.yml`）

```yaml
groups:
  - name: cloudmq-dcs-alerts
    rules:
      - alert: DcsInstanceDown
        expr: up{job="cmq-dcs"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "DCS 节点宕机: {{ $labels.instance }}"
          description: "DCS 节点 {{ $labels.instance }} 宕机。如果过半节点宕机可能导致整个 CloudMQ 集群由于无法访问元数据而瘫痪。"

      - alert: DcsHeapMemoryUsageHigh
        expr: jvm_memory_bytes_used{area="heap", component="dcs"} / jvm_memory_bytes_max{area="heap", component="dcs"} > 0.85
        for: 5m
        labels:
          severity: warning

      - alert: DcsFdExhaustion
        expr: process_open_fds{component="dcs"} / process_max_fds{component="dcs"} > 0.85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "DCS 节点 {{ $labels.instance }} 文件描述符快耗尽"
          description: "节点 {{ $labels.instance }} 已使用的文件描述符比例超过了 85%，可能导致无法建立新的请求连接。"

      - alert: DcsOutstandingRequestsHigh
        expr: outstanding_requests > 1000
        for: 3m
        labels:
          severity: warning
        annotations:
          summary: "DCS 节点排队请求过多: {{ $labels.instance }}"
          description: "节点 {{ $labels.instance }} 当前挂起(尚未处理完成)的请求数量超过 1000，可能是磁盘 IO 过慢导致事务提交受到阻塞。"

      - alert: DcsWriteThrottle
        expr: rate(throttled_ops[5m]) > 0
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "DCS 触发写入限流: {{ $labels.instance }}"
          description: "节点 {{ $labels.instance }} 操作被限流，DCS 正在承受短暂时段内的较大元数据修改压力。"
```

### DCS 告警的特殊性

DCS（ZooKeeper 兼容协调服务）是 CloudMQ 的**元数据大脑**，所有组件启动、Topic 发现、负载均衡都依赖它。其告警优先级天然高于 Broker/Bookie。

**`DcsInstanceDown` — Quorum 机制决定了它的危险边界**

DCS 基于 ZAB 协议需要 Quorum（多数派）存活：

| 集群规模 | 最多可宕机节点数 | 宕机超过此数 |
|---------|----------------|------------|
| 3 节点  | 1 个           | 集群不可用  |
| 5 节点  | 2 个           | 集群不可用  |

因此在三节点 DCS 集群中，**第一个节点宕机**就必须立即响应，不能等第二个宕机再处理。

**`DcsFdExhaustion` — 文件描述符的连锁反应**

```yaml
expr: process_open_fds{component="dcs"} / process_max_fds{component="dcs"} > 0.85
```

文件描述符耗尽会导致 DCS 无法接受新的客户端连接。由于 Broker 和 Bookie 在启动或故障恢复时会向 DCS 建立大量短连接，FD 耗尽会导致整个 CloudMQ 集群的元数据访问雪崩。

**`DcsOutstandingRequestsHigh` — `for: 3m` 而非 5m**

```yaml
for: 3m
```

相比内存类告警的 5 分钟，请求积压告警选择了 3 分钟。因为积压 1000 个请求说明 DCS 的事务提交链路已经严重阻塞，这类问题不会自行恢复，应更快触发。而磁盘使用率可能因 GC 等因素短暂波动，所以容忍时间更长。

---

## 8.6 告警的三种状态

在 `http://<prometheus-ip>:9090/alerts` 页面可以看到：

```
Inactive  →  Pending  →  Firing
 正常         观察中      已触发
```

| 状态 | 含义 | 是否通知 Alertmanager |
|------|------|----------------------|
| **Inactive** | 表达式结果为 false，系统正常 | ❌ |
| **Pending** | 表达式为 true 但未超过 `for` 时长 | ❌ |
| **Firing** | 超过 `for` 时长，告警正式激活 | ✅ |

> **调试技巧**：如果规则一直 Pending 不变 Firing，检查 `for` 配置；如果 Inactive 但你认为应该触发，在 Prometheus Expression Browser 直接执行 `expr` 看返回值。

---

## 8.7 告警阈值设计原则

好的告警阈值需要满足两点：**不漏报**（真正的故障必须触发）、**不误报**（正常波动不能触发）。结合 CloudMQ 的这批规则，总结几条实用原则：

### 原则一：Counter 类告警用 `rate()`，且往往零容忍

```yaml
# 正确：检测速率
expr: rate(cloudmq_ml_AddEntryErrors[5m]) > 0

# 错误：直接比较累计值（永远为 true）
expr: cloudmq_ml_AddEntryErrors > 0
```

对于错误类 Counter，如果业务语义是"一次都不该发生"，阈值就设 `> 0`，`for` 设 1m 过滤瞬时噪声。

### 原则二：资源类告警预留窗口期

磁盘、内存等资源从警戒线到真正耗尽有一个过程，阈值不要设太高：

```
推荐阈值梯度：
  80% → warning（提前预警，计划处理）
  90% → critical（立即处理）
  95% → SEVERE（可能已有影响）
```

CloudMQ 将磁盘告警设在 85% 是合理的：留出约 15% 的数据量给运维操作窗口。

### 原则三：`for` 时长要匹配业务恢复速度

| 类型 | 推荐 `for` | 理由 |
|------|-----------|------|
| 实例宕机 | 1m | 通常不会自恢复，越快越好 |
| 内存使用率高 | 5m | GC 可能导致短暂高峰，需过滤 |
| 请求积压 | 3m | 积压通常不会自行消散，但要排除启动期 |
| 磁盘使用率高 | 5m | 短时间写入爆发不应触发，磁盘是慢变量 |

### 原则四：severity 标签要有后续路由意义

```yaml
labels:
  severity: critical  # Alertmanager 可据此路由到不同渠道
```

`critical` 和 `warning` 不只是视觉上的区分，在 Alertmanager 中可以配置 `critical` 发送电话/短信，`warning` 只发群消息。

---

## 8.8 热加载与调整阈值

修改规则文件后，无需重启 Prometheus，可用 API 热加载（需启动时开启 `--web.enable-lifecycle`）：

```bash
curl -X POST http://localhost:9090/-/reload
```

**调整示例：**

```yaml
# 场景：DCS 集群规模扩大，请求数正常值已接近 1000，需放宽阈值
- alert: DcsOutstandingRequestsHigh
  expr: outstanding_requests > 2000   # 原来是 1000
  for: 3m

# 场景：某 Bookie 节点磁盘扩容了，但告警太频繁，放宽到 90%
- alert: BookieLedgerDiskUsageHigh
  expr: bookie_ledger_dir__cloudmq_data_bookkeeper_ledgers_usage > 90
  for: 5m
```

---

## 8.9 完整规则文件汇总

| 文件 | 告警组 | 规则数 |
|------|--------|--------|
| [`alert/bookie_alerts.yml`](./alert/bookie_alerts.yml) | `cloudmq-bookie-alerts` | 5 条 |
| [`alert/broker_alerts.yml`](./alert/broker_alerts.yml) | `cloudmq-broker-alerts` | 5 条 |
| [`alert/dcs_alerts.yml`](./alert/dcs_alerts.yml) | `cloudmq-dcs-alerts` | 5 条 |

### 各组件告警覆盖维度

| 维度 | Bookie | Broker | DCS |
|------|--------|--------|-----|
| 实例存活 | ✅（含业务状态） | ✅ | ✅ |
| 堆内存 | ✅ | ✅ | ✅ |
| 磁盘 | ✅（Ledger+Index） | ❌ | ❌ |
| 文件描述符 | ❌ | ❌ | ✅ |
| 请求积压 | ❌ | ❌ | ✅ |
| 写入限流/拒绝 | ✅ | ✅（存储层） | ✅ |
| 业务积压 | ❌ | ✅（消息积压） | ❌ |
| Topic/元数据 | ❌ | ✅（Topic 加载） | ❌ |

---

## 小结

本章要点：

1. **告警 = PromQL 表达式 + 持续时间 + 标签**，三者缺一不可
2. **`for` 是防噪核心**：短暂抖动不触发，避免告警风暴
3. **Counter 必须用 `rate()`**，直接比较累计值无意义
4. **DCS 告警优先级最高**：它是 CloudMQ 集群的元数据基础设施，任何节点宕机都应立即响应
5. **Bookie 磁盘是 critical 告警**：磁盘写满后整条写链路中断，影响全局
6. **阈值需根据实际环境调整**：不同集群规模、硬件配置的正常值范围不同

---

*参考文件：[`alert/`](./alert/) 目录下的三份规则文件，以及 [`docs/dcs_metrics.md`](./docs/dcs_metrics.md)、[`docs/bookie_metrics.md`](./docs/bookie_metrics.md)、[`docs/broker_metrics.md`](./docs/broker_metrics.md) 中对应指标的详细说明。*
