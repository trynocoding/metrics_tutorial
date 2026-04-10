# CloudMQ Broker 组件指标说明

Broker 是 CloudMQ 的消息路由与协议处理节点，支持Kafka、AMQP、MQTT 多协议接入。

---

## 一、JVM 内存指标

| 指标名 | 含义说明 |
|--------|----------|
| `jvm_memory_bytes_used` | JVM 各内存区域（heap/nonheap）当前使用量，单位字节 |
| `jvm_memory_bytes_committed` | JVM 各内存区域已提交大小，单位字节 |
| `jvm_memory_bytes_max` | JVM 各内存区域最大容量，单位字节 |
| `jvm_memory_bytes_init` | JVM 各内存区域初始大小，单位字节 |
| `jvm_memory_pool_bytes_used` | JVM 各内存池（ZHeap/Metaspace/CodeHeap 等）当前使用量，单位字节 |
| `jvm_memory_pool_bytes_committed` | JVM 各内存池已提交大小，单位字节 |
| `jvm_memory_pool_bytes_max` | JVM 各内存池最大容量，单位字节 |
| `jvm_memory_pool_bytes_init` | JVM 各内存池初始大小，单位字节 |
| `jvm_memory_pool_collection_used_bytes` | GC 后各内存池的使用量，单位字节 |
| `jvm_memory_pool_collection_committed_bytes` | GC 后各内存池已提交大小，单位字节 |
| `jvm_memory_pool_collection_max_bytes` | GC 后各内存池最大值，单位字节 |
| `jvm_memory_pool_collection_init_bytes` | GC 后各内存池初始值，单位字节 |
| `jvm_memory_pool_allocated_bytes` | JVM 各内存池累计分配字节数 |
| `jvm_memory_direct_bytes_used` | JVM 堆外直接内存已使用量，单位字节 |
| `jvm_memory_direct_bytes_max` | JVM 堆外直接内存最大可用量，单位字节 |
| `jvm_memory_objects_pending_finalization` | 等待 GC 终结的对象数量 |

---

## 二、JVM 线程与类指标

| 指标名 | 含义说明 |
|--------|----------|
| `jvm_threads_current` | 当前 JVM 线程总数 |
| `jvm_threads_daemon` | 当前守护线程数 |
| `jvm_threads_peak` | JVM 启动以来线程数峰值 |
| `jvm_threads_started` | JVM 启动以来累计创建的线程总数 |
| `jvm_threads_deadlocked` | 当前处于死锁状态的线程数 |
| `jvm_threads_deadlocked_monitor` | 因监视器（monitor）死锁的线程数 |
| `jvm_threads_state` | 各状态下的线程数（RUNNABLE/BLOCKED/WAITING/TIMED_WAITING 等） |
| `jvm_classes_currently_loaded` | 当前 JVM 已加载的类数量 |
| `jvm_classes_loaded` | JVM 启动以来累计加载的类总数 |
| `jvm_classes_unloaded` | JVM 启动以来累计卸载的类总数 |

---

## 三、JVM GC 与 Buffer 指标

| 指标名 | 含义说明 |
|--------|----------|
| `jvm_gc_collection_seconds` | GC 周期耗时（count：GC 次数，sum：总耗时），支持 ZGC Cycles/Pauses |
| `jvm_info` | JVM 基础信息（运行时、厂商、版本） |
| `jvm_buffer_pool_used_bytes` | JVM Buffer 池（direct/mapped）当前使用字节数 |
| `jvm_buffer_pool_capacity_bytes` | JVM Buffer 池容量，单位字节 |
| `jvm_buffer_pool_used_buffers` | JVM Buffer 池当前使用的 Buffer 数量 |

---

## 四、进程指标

| 指标名 | 含义说明 |
|--------|----------|
| `process_cpu_seconds` | 进程累计 CPU 使用时间，单位秒 |
| `process_start_time_seconds` | 进程启动时间（Unix 时间戳） |
| `process_open_fds` | 当前已打开的文件描述符数量 |
| `process_max_fds` | 系统允许的最大文件描述符数量 |
| `process_virtual_memory_bytes` | 进程虚拟内存大小，单位字节 |
| `process_resident_memory_bytes` | 进程常驻物理内存大小，单位字节 |

---

## 五、日志指标

| 指标名 | 含义说明 |
|--------|----------|
| `log4j2_appender` | 各日志级别（debug/info/warn/error/fatal/trace）的累计日志输出条数 |

---

## 六、版本与认证指标

| 指标名 | 含义说明 |
|--------|----------|
| `cloudmq_version_info` | CloudMQ 版本信息（版本号、commit） |
| `cloudmq_authentication_success` | 认证成功次数（按认证方式分组） |
| `cloudmq_authentication_failures` | 认证失败次数（按认证方式及失败原因分组） |
| `cloudmq_expired_token` | 已过期 Token 的累计数量 |
| `cloudmq_expiring_token_minutes` | 即将过期 Token 的剩余有效分钟分布 |

---

## 七、元数据存储指标

| 指标名 | 含义说明 |
|--------|----------|
| `cloudmq_metadata_store_ops_latency_ms` | 元数据存储操作延迟分布（按操作类型 get/put/del 及成功/失败分组），单位毫秒 |
| `cloudmq_metadata_store_put_bytes` | 元数据存储累计写入字节数 |
| `cloudmq_batch_metadata_store_executor_queue_size` | 批量元数据写入执行器的当前队列长度 |
| `cloudmq_batch_metadata_store_queue_wait_time_ms` | 批量元数据写入任务在队列中的等待时间分布，单位毫秒 |
| `cloudmq_batch_metadata_store_batch_size` | 批量元数据写入每批次操作数量分布 |
| `cloudmq_batch_metadata_store_batch_execute_time_ms` | 批量元数据写入每批次执行耗时分布，单位毫秒 |

---

## 八、Broker 服务核心指标

| 指标名 | 含义说明 |
|--------|----------|
| `cloudmq_broker_rate_in` | Broker 当前消息入流速率（条/秒） |
| `cloudmq_broker_rate_out` | Broker 当前消息出流速率（条/秒） |
| `cloudmq_broker_throughput_in` | Broker 当前入流吞吐量（字节/秒） |
| `cloudmq_broker_throughput_out` | Broker 当前出流吞吐量（字节/秒） |
| `cloudmq_broker_topics_count` | Broker 上当前加载的 Topic 总数 |
| `cloudmq_broker_producers_count` | Broker 上当前连接的 Producer 总数 |
| `cloudmq_broker_consumers_count` | Broker 上当前连接的 Consumer 总数 |
| `cloudmq_broker_subscriptions_count` | Broker 上当前存在的 Subscription 总数 |
| `cloudmq_broker_msg_backlog` | Broker 全局消息积压总数 |
| `cloudmq_broker_pending_bytes_to_dispatch` | Broker 待下发（pending dispatch）的字节数 |
| `cloudmq_broker_throttled_connections` | 当前被限速的连接数 |
| `cloudmq_broker_throttled_connections_global_limit` | 全局限速连接数的阈值 |
| `cloudmq_broker_publish_latency` | Broker 消息发布端到端延迟分布，单位毫秒 |
| `cloudmq_broker_storage_size` | Broker 存储数据总大小，单位字节 |
| `cloudmq_broker_storage_logical_size` | Broker 存储逻辑大小（未压缩），单位字节 |
| `cloudmq_broker_storage_write_rate` | Broker 存储写入速率（字节/秒） |
| `cloudmq_broker_storage_read_rate` | Broker 存储读取速率（字节/秒） |
| `cloudmq_broker_storage_read_cache_misses_rate` | Broker 存储读缓存未命中速率 |

---

## 九、Broker Topic 加载指标

| 指标名 | 含义说明 |
|--------|----------|
| `cloudmq_broker_topic_load_pending_requests` | 当前待处理的 Topic 加载请求数 |
| `cloudmq_topic_load_times` | Topic 加载耗时分布，单位毫秒 |
| `topic_load_times` | Topic 加载耗时分布（兼容旧名称） |
| `topic_load_failed` | Topic 加载失败的累计次数 |

---

## 十、Broker Lookup 指标

| 指标名 | 含义说明 |
|--------|----------|
| `cloudmq_broker_lookup` | Broker Lookup 操作延迟分布，单位毫秒 |
| `cloudmq_broker_lookup_answers` | Broker 直接响应 Lookup 请求的次数 |
| `cloudmq_broker_lookup_redirects` | Broker 重定向 Lookup 请求的次数 |
| `cloudmq_broker_lookup_failures` | Broker Lookup 操作失败的次数 |
| `cloudmq_broker_lookup_pending_requests` | 当前待处理的 Lookup 请求数 |
| `cloudmq_broker_load_manager_bundle_assigment` | Bundle 分配操作的延迟分布，单位毫秒 |

---

## 十一、Topic 级别指标

| 指标名 | 含义说明 |
|--------|----------|
| `cloudmq_topics_count` | 各命名空间下的 Topic 数量 |
| `cloudmq_producers_count` | 各 Topic 当前连接的 Producer 数量 |
| `cloudmq_consumers_count` | 各 Topic 当前连接的 Consumer 数量 |
| `cloudmq_subscriptions_count` | 各 Topic 当前的 Subscription 数量 |
| `cloudmq_rate_in` | 各 Topic 当前消息入流速率（条/秒） |
| `cloudmq_rate_out` | 各 Topic 当前消息出流速率（条/秒） |
| `cloudmq_throughput_in` | 各 Topic 当前入流吞吐量（字节/秒） |
| `cloudmq_throughput_out` | 各 Topic 当前出流吞吐量（字节/秒） |
| `cloudmq_in_bytes_total` | 各 Topic 累计接收字节数 |
| `cloudmq_in_messages_total` | 各 Topic 累计接收消息数 |
| `cloudmq_out_bytes_total` | 各 Topic 累计发送字节数（含订阅维度） |
| `cloudmq_out_messages_total` | 各 Topic 累计发送消息数（含订阅维度） |
| `cloudmq_average_msg_size` | 各 Topic 消息平均大小，单位字节 |
| `cloudmq_msg_backlog` | 各 Topic 当前消息积压数量 |
| `cloudmq_publish_rate_limit_times` | 各 Topic 触发发布速率限制的次数 |
| `cloudmq_delayed_message_index_size_bytes` | 各 Topic 延迟消息索引占用大小，单位字节 |

---

## 十二、Topic 存储延迟指标

> 这组指标记录消息写入存储的延迟分布，分为「Entry 写入」（storage_write）和「Ledger 写入」（storage_ledger_write）两个维度。

| 指标名 | 含义说明 |
|--------|----------|
| `cloudmq_storage_write_latency_le_0_5` | 写入延迟 ≤0.5ms 的消息数 |
| `cloudmq_storage_write_latency_le_1` | 写入延迟 ≤1ms 的消息数 |
| `cloudmq_storage_write_latency_le_5` | 写入延迟 ≤5ms 的消息数 |
| `cloudmq_storage_write_latency_le_10` | 写入延迟 ≤10ms 的消息数 |
| `cloudmq_storage_write_latency_le_20` | 写入延迟 ≤20ms 的消息数 |
| `cloudmq_storage_write_latency_le_50` | 写入延迟 ≤50ms 的消息数 |
| `cloudmq_storage_write_latency_le_100` | 写入延迟 ≤100ms 的消息数 |
| `cloudmq_storage_write_latency_le_200` | 写入延迟 ≤200ms 的消息数 |
| `cloudmq_storage_write_latency_le_1000` | 写入延迟 ≤1000ms 的消息数 |
| `cloudmq_storage_write_latency_overflow` | 写入延迟 >1000ms 的消息数 |
| `cloudmq_storage_write_latency_count` | 写入操作的总次数 |
| `cloudmq_storage_write_latency_sum` | 写入操作总延迟之和 |
| `cloudmq_storage_ledger_write_latency_le_0_5` | Ledger 写入延迟 ≤0.5ms 的次数 |
| `cloudmq_storage_ledger_write_latency_le_1` | Ledger 写入延迟 ≤1ms 的次数 |
| `cloudmq_storage_ledger_write_latency_le_5` | Ledger 写入延迟 ≤5ms 的次数 |
| `cloudmq_storage_ledger_write_latency_le_10` | Ledger 写入延迟 ≤10ms 的次数 |
| `cloudmq_storage_ledger_write_latency_le_20` | Ledger 写入延迟 ≤20ms 的次数 |
| `cloudmq_storage_ledger_write_latency_le_50` | Ledger 写入延迟 ≤50ms 的次数 |
| `cloudmq_storage_ledger_write_latency_le_100` | Ledger 写入延迟 ≤100ms 的次数 |
| `cloudmq_storage_ledger_write_latency_le_200` | Ledger 写入延迟 ≤200ms 的次数 |
| `cloudmq_storage_ledger_write_latency_le_1000` | Ledger 写入延迟 ≤1000ms 的次数 |
| `cloudmq_storage_ledger_write_latency_overflow` | Ledger 写入延迟 >1000ms 的次数 |
| `cloudmq_storage_ledger_write_latency_count` | Ledger 写入操作的总次数 |
| `cloudmq_storage_ledger_write_latency_sum` | Ledger 写入操作总延迟之和 |

---

## 十三、Topic 存储大小与积压指标

| 指标名 | 含义说明 |
|--------|----------|
| `cloudmq_storage_size` | 各 Topic 存储占用大小（原始字节） |
| `cloudmq_storage_logical_size` | 各 Topic 存储逻辑大小（未压缩） |
| `cloudmq_storage_offloaded_size` | 各 Topic 已卸载到对象存储的数据大小 |
| `cloudmq_storage_backlog_size` | 各 Topic 消息积压的存储大小 |
| `cloudmq_storage_backlog_quota_limit` | 各 Topic 消息积压大小限制（-1 表示无限制） |
| `cloudmq_storage_backlog_quota_limit_time` | 各 Topic 消息积压时间限制，单位秒（-1 表示无限制） |
| `cloudmq_storage_read_rate` | 各 Topic 存储读取速率（字节/秒） |
| `cloudmq_storage_write_rate` | 各 Topic 存储写入速率（字节/秒） |
| `cloudmq_storage_read_cache_misses_rate` | 各 Topic 存储读缓存未命中速率 |

---

## 十四、Entry 大小分布指标

| 指标名 | 含义说明 |
|--------|----------|
| `cloudmq_entry_size_le_128` | 消息大小 ≤128 字节的 Entry 数量 |
| `cloudmq_entry_size_le_512` | 消息大小 ≤512 字节的 Entry 数量 |
| `cloudmq_entry_size_le_1_kb` | 消息大小 ≤1KB 的 Entry 数量 |
| `cloudmq_entry_size_le_2_kb` | 消息大小 ≤2KB 的 Entry 数量 |
| `cloudmq_entry_size_le_4_kb` | 消息大小 ≤4KB 的 Entry 数量 |
| `cloudmq_entry_size_le_16_kb` | 消息大小 ≤16KB 的 Entry 数量 |
| `cloudmq_entry_size_le_100_kb` | 消息大小 ≤100KB 的 Entry 数量 |
| `cloudmq_entry_size_le_1_mb` | 消息大小 ≤1MB 的 Entry 数量 |
| `cloudmq_entry_size_le_overflow` | 消息大小超出最大分桶的 Entry 数量 |
| `cloudmq_entry_size_count` | 各 Topic Entry 总数量（含大小统计） |
| `cloudmq_entry_size_sum` | 各 Topic Entry 总字节数 |

---

## 十五、Subscription 指标

| 指标名 | 含义说明 |
|--------|----------|
| `cloudmq_subscription_consumers_count` | 各 Subscription 当前 Consumer 数量 |
| `cloudmq_subscription_back_log` | 各 Subscription 消息积压数量 |
| `cloudmq_subscription_back_log_no_delayed` | 各 Subscription 不含延迟消息的积压数量 |
| `cloudmq_subscription_delayed` | 各 Subscription 当前延迟消息数量 |
| `cloudmq_subscription_unacked_messages` | 各 Subscription 当前未确认（Unacked）消息数量 |
| `cloudmq_subscription_blocked_on_unacked_messages` | 各 Subscription 因未确认消息过多而被阻塞的状态（1/0） |
| `cloudmq_subscription_total_msg_expired` | 各 Subscription 累计已过期消息数量 |
| `cloudmq_subscription_msg_rate_out` | 各 Subscription 当前消息出流速率（条/秒） |
| `cloudmq_subscription_msg_throughput_out` | 各 Subscription 当前出流吞吐量（字节/秒） |
| `cloudmq_subscription_msg_rate_expired` | 各 Subscription 消息过期速率（条/秒） |
| `cloudmq_subscription_msg_rate_redeliver` | 各 Subscription 消息重新投递速率（条/秒） |
| `cloudmq_subscription_msg_drop_rate` | 各 Subscription 消息丢弃速率（条/秒） |
| `cloudmq_subscription_msg_ack_rate` | 各 Subscription 消息确认速率（条/秒） |
| `cloudmq_subscription_filter_processed_msg_count` | 各 Subscription 过滤器处理的消息总数 |
| `cloudmq_subscription_filter_accepted_msg_count` | 各 Subscription 过滤器接受的消息数量 |
| `cloudmq_subscription_filter_rejected_msg_count` | 各 Subscription 过滤器拒绝的消息数量 |
| `cloudmq_subscription_filter_rescheduled_msg_count` | 各 Subscription 过滤器重新调度的消息数量 |
| `cloudmq_subscription_last_expire_timestamp` | 各 Subscription 最近一次消息过期时间戳（毫秒） |
| `cloudmq_subscription_last_acked_timestamp` | 各 Subscription 最近一次消息确认时间戳（毫秒） |
| `cloudmq_subscription_last_consumed_timestamp` | 各 Subscription 最近一次消息消费时间戳（毫秒） |
| `cloudmq_subscription_last_consumed_flow_timestamp` | 各 Subscription 最近一次流量触发时间戳（毫秒） |
| `cloudmq_subscription_last_mark_delete_advanced_timestamp` | 各 Subscription 最近一次标记删除推进时间戳（毫秒） |

---

## 十六、事务（Transaction）指标

| 指标名 | 含义说明 |
|--------|----------|
| `cloudmq_txn_tb_active_total` | 各 Topic 当前活跃事务数量 |
| `cloudmq_txn_tb_committed_total` | 各 Topic 累计已提交事务数量 |
| `cloudmq_txn_tb_aborted_total` | 各 Topic 累计已回滚事务数量 |

---

## 十七、Schema 指标

| 指标名 | 含义说明 |
|--------|----------|
| `cloudmq_schema_get_ops_latency` | Schema 获取操作的延迟分布，单位毫秒 |
| `cloudmq_schema_get_ops_failed` | Schema 获取操作失败的累计次数 |
| `cloudmq_schema_put_ops_latency` | Schema 写入操作的延迟分布，单位毫秒 |
| `cloudmq_schema_put_ops_failed` | Schema 写入操作失败的累计次数 |
| `cloudmq_schema_del_ops_latency` | Schema 删除操作的延迟分布，单位毫秒 |
| `cloudmq_schema_del_ops_failed` | Schema 删除操作失败的累计次数 |
| `cloudmq_schema_compatible` | Schema 兼容性校验通过的累计次数 |
| `cloudmq_schema_incompatible` | Schema 兼容性校验不通过的累计次数 |

---

## 十八、ManagedLedger（ML）缓存指标

| 指标名 | 含义说明 |
|--------|----------|
| `cloudmq_ml_cache_entries` | ML 读缓存当前 Entry 数量 |
| `cloudmq_ml_cache_evicted_entries_total` | ML 读缓存累计驱逐 Entry 数量 |
| `cloudmq_ml_cache_evictions` | ML 读缓存发生驱逐的次数 |
| `cloudmq_ml_cache_inserted_entries_total` | ML 读缓存累计插入 Entry 数量 |
| `cloudmq_ml_cache_hits_rate` | ML 读缓存命中速率（次/秒） |
| `cloudmq_ml_cache_hits_throughput` | ML 读缓存命中吞吐量（字节/秒） |
| `cloudmq_ml_cache_misses_rate` | ML 读缓存未命中速率（次/秒） |
| `cloudmq_ml_cache_misses_throughput` | ML 读缓存未命中吞吐量（字节/秒） |
| `cloudmq_ml_cache_used_size` | ML 读缓存已使用内存大小，单位字节 |
| `cloudmq_ml_cache_pool_allocated` | ML 读缓存内存池已分配大小，单位字节 |
| `cloudmq_ml_cache_pool_used` | ML 读缓存内存池已使用大小，单位字节 |
| `cloudmq_ml_cache_pool_active_allocations` | ML 读缓存内存池当前活跃分配数量 |
| `cloudmq_ml_cache_pool_active_allocations_huge` | ML 读缓存内存池大型分配数量 |
| `cloudmq_ml_cache_pool_active_allocations_normal` | ML 读缓存内存池普通分配数量 |
| `cloudmq_ml_cache_pool_active_allocations_small` | ML 读缓存内存池小型分配数量 |
| `cloudmq_ml_reads_inflight_bytes` | ML 当前飞行中（正在读取）的字节数（-1 表示无限制） |
| `cloudmq_ml_reads_available_inflight_bytes` | ML 可用的飞行中读取字节配额（-1 表示无限制） |
| `cloudmq_ml_cache_pendingreads_matched` | ML 读缓存 pending 读请求命中的次数 |
| `cloudmq_ml_cache_pendingreads_matched_included` | ML 读缓存 pending 读请求完全覆盖命中的次数 |
| `cloudmq_ml_cache_pendingreads_matched_overlapping_miss_left` | ML 读缓存 pending 读请求左部分缺失的次数 |
| `cloudmq_ml_cache_pendingreads_matched_overlapping_miss_right` | ML 读缓存 pending 读请求右部分缺失的次数 |
| `cloudmq_ml_cache_pendingreads_matched_overlapping_miss_both` | ML 读缓存 pending 读请求两端均缺失的次数 |
| `cloudmq_ml_cache_pendingreads_missed` | ML 读缓存 pending 读请求完全未命中的次数 |
| `cloudmq_ml_cache_pendingreads_entries_read` | ML 读缓存 pending 读请求实际读取的 Entry 数量 |
| `cloudmq_ml_cache_pendingreads_entries_notread` | ML 读缓存 pending 读请求未能读取的 Entry 数量 |

---

## 十九、ManagedLedger（ML）写入与读取指标

| 指标名 | 含义说明 |
|--------|----------|
| `cloudmq_ml_count` | 当前活跃的 ManagedLedger 数量 |
| `cloudmq_ml_AddEntryBytesRate` | ML 写入 Entry 的字节速率（字节/秒） |
| `cloudmq_ml_AddEntryMessagesRate` | ML 写入 Entry 的消息速率（条/秒） |
| `cloudmq_ml_AddEntrySucceed` | ML 写入 Entry 成功的累计次数 |
| `cloudmq_ml_AddEntryErrors` | ML 写入 Entry 失败的累计次数 |
| `cloudmq_ml_AddEntryWithReplicasBytesRate` | ML 含副本写入 Entry 的字节速率（字节/秒） |
| `cloudmq_ml_AddEntryLatencyBuckets` | ML 写入 Entry 延迟分布（按时间区间分桶） |
| `cloudmq_ml_AddEntryLatencyBuckets_OVERFLOW` | ML 写入 Entry 延迟超出最大分桶的次数 |
| `cloudmq_ml_LedgerAddEntryLatencyBuckets` | ML Ledger 层写入 Entry 延迟分布（按时间区间分桶） |
| `cloudmq_ml_LedgerAddEntryLatencyBuckets_OVERFLOW` | ML Ledger 层写入 Entry 延迟超出最大分桶的次数 |
| `cloudmq_ml_LedgerSwitchLatencyBuckets` | ML Ledger 切换（滚动）延迟分布（按时间区间分桶） |
| `cloudmq_ml_LedgerSwitchLatencyBuckets_OVERFLOW` | ML Ledger 切换延迟超出最大分桶的次数 |
| `cloudmq_ml_ReadEntriesRate` | ML 读取 Entry 的速率（次/秒） |
| `cloudmq_ml_ReadEntriesBytesRate` | ML 读取 Entry 的字节速率（字节/秒） |
| `cloudmq_ml_ReadEntriesSucceeded` | ML 读取 Entry 成功的累计次数 |
| `cloudmq_ml_ReadEntriesErrors` | ML 读取 Entry 失败的累计次数 |
| `cloudmq_ml_ReadEntriesOpsCacheMissesRate` | ML 读取 Entry 时缓存未命中速率 |
| `cloudmq_ml_MarkDeleteRate` | ML 标记删除（Mark Delete）的速率（次/秒） |
| `cloudmq_ml_NumberOfMessagesInBacklog` | ML 当前积压消息数量 |
| `cloudmq_ml_StoredMessagesSize` | ML 存储的消息总字节数 |
| `cloudmq_ml_EntrySizeBuckets` | ML Entry 大小分布（按字节区间分桶） |
| `cloudmq_ml_EntrySizeBuckets_OVERFLOW` | ML Entry 大小超出最大分桶的次数 |

---

## 二十、连接管理指标

| 指标名 | 含义说明 |
|--------|----------|
| `cloudmq_active_connections` | 当前活跃连接数 |
| `cloudmq_connection_created_total_count` | 累计创建的连接总数 |
| `cloudmq_connection_create_success_count` | 累计成功建立的连接数 |
| `cloudmq_connection_create_fail_count` | 累计建立失败的连接数 |
| `cloudmq_connection_closed_total_count` | 累计已关闭的连接数 |

---

## 二十一、负载均衡指标

| 指标名 | 含义说明 |
|--------|----------|
| `cloudmq_lb_cpu_usage` | 负载均衡视角下的 Broker CPU 使用率（百分比） |
| `cloudmq_lb_memory_usage` | 负载均衡视角下的 Broker 内存使用率（百分比） |
| `cloudmq_lb_directMemory_usage` | 负载均衡视角下的 Broker 直接内存使用率（百分比） |
| `cloudmq_lb_bandwidth_in_usage` | 负载均衡视角下的 Broker 入带宽使用率（百分比） |
| `cloudmq_lb_bandwidth_out_usage` | 负载均衡视角下的 Broker 出带宽使用率（百分比） |
| `cloudmq_lb_unload_broker_total` | Bundle 卸载时涉及的 Broker 累计数量 |
| `cloudmq_lb_unload_bundle_total` | 累计卸载的 Bundle 数量 |
| `cloudmq_lb_bundles_split_total` | 累计发生分裂的 Bundle 数量 |

---

## 二十二、资源组指标

| 指标名 | 含义说明 |
|--------|----------|
| `cloudmq_resource_group_aggregate_usage_secs` | 资源组聚合使用统计的耗时分布，单位秒 |
| `cloudmq_resource_group_calculate_quota_secs` | 资源组配额计算的耗时分布，单位秒 |
| `cloudmq_resource_group_bytes_used` | 各资源组当前已使用的字节数 |
| `cloudmq_resource_group_messages_used` | 各资源组当前已使用的消息数 |
| `cloudmq_resource_group_calculated_bytes_quota` | 各资源组计算得出的字节配额 |
| `cloudmq_resource_group_calculated_messages_quota` | 各资源组计算得出的消息配额 |
| `cloudmq_resource_group_updates` | 各资源组配额更新的累计次数 |
| `cloudmq_resource_group_tenant_registers` | 各资源组注册的 Tenant 累计次数 |
| `cloudmq_resource_group_tenant_unregisters` | 各资源组注销的 Tenant 累计次数 |
| `cloudmq_resource_group_namespace_registers` | 各资源组注册的 Namespace 累计次数 |
| `cloudmq_resource_group_namespace_unregisters` | 各资源组注销的 Namespace 累计次数 |

---

## 二十三、缓存（Caffeine）指标

| 指标名 | 含义说明 |
|--------|----------|
| `caffeine_cache_hit` | 各缓存（owned-bundles/bundles 等）命中次数 |
| `caffeine_cache_miss` | 各缓存未命中次数 |
| `caffeine_cache_requests` | 各缓存请求总次数（命中 + 未命中） |
| `caffeine_cache_eviction` | 各缓存发生驱逐的次数 |
| `caffeine_cache_eviction_weight` | 各缓存驱逐的数据权重大小 |
| `caffeine_cache_loads` | 各缓存触发实际加载的次数 |
| `caffeine_cache_load_failure` | 各缓存加载失败的次数 |
| `caffeine_cache_load_duration_seconds` | 各缓存加载操作的耗时分布，单位秒 |
| `caffeine_cache_estimated_size` | 各缓存当前估计的条目数量 |

---

## 二十四、Web 服务（BES）指标

> BES 是 Broker 内嵌的 HTTP/Admin REST 服务。

| 指标名 | 含义说明 |
|--------|----------|
| `bes_bytesreceived_total` | Web 服务累计接收字节数 |
| `bes_bytessent_total` | Web 服务累计发送字节数 |
| `bes_processingtime_total` | Web 服务累计请求处理时间，单位毫秒 |
| `bes_maxtime_total` | Web 服务单次请求最大处理时间，单位毫秒 |
| `bes_errorcount` | Web 服务累计错误请求数 |
| `bes_requestcount` | Web 服务累计请求总数 |
| `bes_threadpool_maxthreads` | Web 线程池最大线程数 |
| `bes_threadpool_minsparethreads` | Web 线程池最小备用线程数 |
| `bes_threadpool_currentthreadcount` | Web 线程池当前线程总数（按监听端口） |
| `bes_threadpool_currentthreadsbusy` | Web 线程池当前忙碌线程数（按监听端口） |
| `bes_threadpool_acceptcount` | Web 线程池等待队列最大长度 |
| `bes_threadpool_keepalivecount` | Web 线程池当前 Keep-Alive 连接数 |
| `bes_threadpool_pollerthreadcount` | Web 线程池 Poller 线程数 |
| `bes_threadpool_connectioncount` | Web 线程池当前连接数 |
| `bes_session_activesessions_total` | 当前活跃 HTTP 会话数 |
| `bes_session_rejectedsessions_total` | 被拒绝的 HTTP 会话数 |
| `bes_session_sessioncounter_total` | 累计创建的 HTTP 会话数 |
| `bes_session_expiredsessions_total` | 已过期的 HTTP 会话数 |
| `bes_session_processingtime_total` | HTTP 会话累计处理时间 |
| `bes_servlet_requestcount` | 各 Servlet 的累计请求数 |
| `bes_servlet_errorcount` | 各 Servlet 的累计错误请求数 |
| `bes_servlet_processingtime_total` | 各 Servlet 的累计处理时间 |
| `bes_servlet_maxtime_total` | 各 Servlet 单次请求最大处理时间 |

---

## 二十五、Web Executor 指标

| 指标名 | 含义说明 |
|--------|----------|
| `cloudmq_web_executor_current_threads` | Web 异步执行器当前线程总数 |
| `cloudmq_web_executor_active_threads` | Web 异步执行器当前活跃线程数 |
| `cloudmq_web_executor_idle_threads` | Web 异步执行器当前空闲线程数 |
| `cloudmq_web_executor_min_threads` | Web 异步执行器的最小线程数配置 |
| `cloudmq_web_executor_max_threads` | Web 异步执行器的最大线程数配置 |

---

## 二十六、Kafka 协议（KOC）指标

> KOC（Kafka-on-CloudMQ）是 Broker 内置的 Kafka 协议适配层，允许 Kafka 客户端直接连接 CloudMQ。

| 指标名 | 含义说明 |
|--------|----------|
| `koc_server_ALIVE_CHANNEL_COUNT` | 当前存活（建立中或已建立）的 Kafka 通道数 |
| `koc_server_ACTIVE_CHANNEL_COUNT` | 当前活跃（正在处理请求）的 Kafka 通道数 |
| `koc_server_REQUEST_QUEUE_SIZE` | Kafka 请求处理队列当前长度 |
| `koc_server_KOC_EVENT_QUEUE_SIZE` | KOC 内部事件队列当前长度 |
| `koc_server_BATCH_COUNT_PER_MEMORYRECORDS` | 每次 MemoryRecords 处理包含的批次数量 |
| `koc_server_NETWORK_TOTAL_BYTES_IN` | Kafka 协议累计接收字节数 |
| `koc_server_NETWORK_TOTAL_BYTES_OUT` | Kafka 协议累计发送字节数 |
| `koc_server_RESPONSE_BLOCKED_TIMES` | 响应被阻塞的累计次数 |
| `koc_server_WAITING_FETCHES_TRIGGERED` | 触发等待 Fetch 的累计次数 |
| `koc_server_RESPONSE_BLOCKED_LATENCY` | 响应被阻塞的延迟分布（按成功/失败分组） |
| `koc_server_REQUEST_PARSE_LATENCY` | Kafka 请求解析耗时分布（按成功/失败分组） |
| `koc_server_PRODUCE_ENCODE` | Kafka Produce 消息编码耗时分布（按成功/失败分组） |
| `koc_server_FETCH_DECODE` | Kafka Fetch 消息解码耗时分布（按成功/失败分组） |
| `koc_server_MESSAGE_READ` | Kafka 消息读取耗时分布（按成功/失败分组） |
| `koc_server_MESSAGE_PUBLISH` | Kafka 消息发布耗时分布（按成功/失败分组） |
| `koc_server_MESSAGE_QUEUED_LATENCY` | Kafka 消息在队列中等待的延迟分布（按成功/失败分组） |
| `koc_server_PENDING_TOPIC_LATENCY` | Kafka 请求等待 Topic 就绪的延迟分布（按成功/失败分组） |
| `koc_server_PREPARE_METADATA` | Kafka Metadata 请求准备耗时分布（按成功/失败分组） |

---

## 二十七、MQTT 协议（MOP）指标

> MOP（MQTT-on-CloudMQ）是 Broker 内置的 MQTT 协议适配层。

| 指标名 | 含义说明 |
|--------|----------|
| `mop_active_client_count` | 当前活跃的 MQTT 客户端连接数 |
| `mop_maximum_client_count` | 历史最大 MQTT 客户端连接数 |
| `mop_total_client_count` | 累计连接过的 MQTT 客户端总数 |
| `mop_sub_count` | 累计 MQTT 订阅数量 |
| `mop_received_count` | 累计接收的 MQTT 消息数量 |
| `mop_received_bytes` | 累计接收的 MQTT 消息字节数 |
| `mop_send_count` | 累计发送的 MQTT 消息数量 |
| `mop_send_bytes` | 累计发送的 MQTT 消息字节数 |

---

## 二十八、Ledger Offloader（分层存储）指标

> Ledger Offloader 负责将冷数据从 BookKeeper 卸载到对象存储（如 S3），以下指标反映卸载与回读性能。

| 指标名 | 含义说明 |
|--------|----------|
| `brk_ledgeroffloader_offload_rate` | 数据卸载到对象存储的速率（字节/秒） |
| `brk_ledgeroffloader_offload_error` | 卸载操作失败的累计次数 |
| `brk_ledgeroffloader_read_bytes` | 从对象存储累计回读的字节数 |
| `brk_ledgeroffloader_read_offload_rate` | 从对象存储回读数据的速率（字节/秒） |
| `brk_ledgeroffloader_read_offload_error` | 从对象存储回读失败的累计次数 |
| `brk_ledgeroffloader_read_ledger_latency` | 从 BookKeeper Ledger 读取数据的延迟分布，单位毫秒 |
| `brk_ledgeroffloader_read_offload_data_latency` | 从对象存储读取数据的延迟分布，单位毫秒 |
| `brk_ledgeroffloader_read_offload_index_latency` | 从对象存储读取索引的延迟分布，单位毫秒 |
| `brk_ledgeroffloader_write_storage_error` | 写入对象存储时发生错误的累计次数 |
| `brk_ledgeroffloader_delete_offload_ops` | 删除已卸载数据的操作累计次数 |
