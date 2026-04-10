# CloudMQ Bookie 组件指标说明

Bookie 是 CloudMQ 的存储节点，负责消息的持久化存储。

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
| `jvm_memory_pool_collection_committed_bytes` | GC 后各内存池的已提交大小，单位字节 |
| `jvm_memory_pool_collection_max_bytes` | GC 后各内存池的最大值，单位字节 |
| `jvm_memory_pool_collection_init_bytes` | GC 后各内存池的初始值，单位字节 |
| `jvm_memory_direct_bytes_used` | JVM 堆外直接内存已使用量，单位字节 |
| `jvm_memory_direct_bytes_max` | JVM 堆外直接内存最大可用量，单位字节 |
| `jvm_memory_objects_pending_finalization` | 等待 GC 终结的对象数量 |

---

## 二、JVM 线程指标

| 指标名 | 含义说明 |
|--------|----------|
| `jvm_threads_current` | 当前 JVM 线程总数 |
| `jvm_threads_daemon` | 当前守护线程数 |
| `jvm_threads_peak` | JVM 启动以来线程数峰值 |
| `jvm_threads_started` | JVM 启动以来累计创建的线程总数 |
| `jvm_threads_deadlocked` | 当前处于死锁状态的线程数 |
| `jvm_threads_deadlocked_monitor` | 因监视器（monitor）死锁的线程数 |
| `jvm_threads_state` | 各状态下的线程数（RUNNABLE/BLOCKED/WAITING/TIMED_WAITING 等） |

---

## 三、JVM GC 指标

| 指标名 | 含义说明 |
|--------|----------|
| `jvm_gc_collection_seconds` | GC 周期耗时（count：GC 次数，sum：总耗时），支持 ZGC Cycles/Pauses |

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

## 六、元数据存储指标

| 指标名 | 含义说明 |
|--------|----------|
| `cloudmq_metadata_store_ops_latency_ms` | 元数据存储操作延迟分布（按操作类型 get/put/del 及成功/失败分组），单位毫秒 |
| `cloudmq_metadata_store_put_bytes` | 元数据存储累计写入字节数 |
| `cloudmq_batch_metadata_store_executor_queue_size` | 批量元数据写入执行器的当前队列长度 |
| `cloudmq_batch_metadata_store_queue_wait_time_ms` | 批量元数据写入任务在队列中的等待时间分布，单位毫秒 |
| `cloudmq_batch_metadata_store_batch_size` | 批量元数据写入每批次操作数量分布 |
| `cloudmq_batch_metadata_store_batch_execute_time_ms` | 批量元数据写入每批次执行耗时分布，单位毫秒 |

---

## 七、Bookie 服务核心指标

| 指标名 | 含义说明 |
|--------|----------|
| `bookie_SERVER_STATUS` | Bookie 节点服务状态（1 表示正常运行） |
| `bookie_WRITE_BYTES` | Bookie 累计写入字节数 |
| `bookie_READ_BYTES` | Bookie 累计读取字节数 |
| `bookie_THREAD_RUNTIME` | Bookie 线程实际运行时长分布 |
| `bookie_throttled_write` | Bookie 写入被限速的次数 |
| `bookie_BOOKIE_ADD_ENTRY` | Bookie 处理写入请求的端到端延迟分布，单位毫秒 |
| `bookie_BOOKIE_ADD_ENTRY_BYTES` | Bookie 累计处理写入请求的字节数 |
| `bookie_BOOKIE_READ_ENTRY` | Bookie 处理读取请求的端到端延迟分布，单位毫秒 |
| `bookie_BOOKIE_READ_ENTRY_BYTES` | Bookie 累计处理读取请求的字节数 |
| `bookie_BOOKIE_RECOVERY_ADD_ENTRY` | Bookie 处理账本恢复写入请求的延迟分布，单位毫秒 |
| `bookie_BOOKIE_FORCE_LEDGER` | Bookie 处理强制刷盘请求的延迟分布 |
| `bookie_BOOKIE_GET_LIST_OF_ENTRIES_OF_LEDGER` | Bookie 返回账本 Entry 列表请求的延迟分布 |
| `bookie_read_entry` | Bookie 读取 Entry 耗时分布（内部统计） |

---

## 八、Bookie 账本（Ledger）指标

| 指标名 | 含义说明 |
|--------|----------|
| `bookie_ledgers_count` | 当前 Bookie 节点上的账本（Ledger）总数 |
| `bookie_ACTIVE_LEDGER_TOTAL` | 当前活跃账本数量 |
| `bookie_DELETED_LEDGER_TOTAL` | 累计已删除账本数量 |
| `bookie_entries_count` | 当前 Bookie 存储的 Entry 总数 |
| `bookie_ledger_writable_dirs` | 可写账本目录数量 |
| `bookie_ledger_num_dirs` | 账本目录总数 |
| `bookie_ledger_dir__cloudmq_data_bookkeeper_ledgers_usage` | 账本数据目录的磁盘使用率 |
| `bookie_index_writable_dirs` | 可写索引目录数量 |
| `bookie_index_num_dirs` | 索引目录总数 |
| `bookie_index_dir__cloudmq_data_bookkeeper_ledgers_usage` | 索引目录的磁盘使用率 |
| `bookie_ACTIVE_ENTRY_LOG_SPACE_BYTES` | 当前活跃 Entry Log 文件已占用的字节数 |
| `bookie_ACTIVE_ENTRY_LOG_TOTAL` | 当前活跃的 Entry Log 文件的总数 |
| `bookie_RECLAIMED_COMPACTION_SPACE_BYTES` | 通过压缩回收的磁盘空间，单位字节 |
| `bookie_RECLAIMED_DELETION_SPACE_BYTES` | 通过账本删除回收的磁盘空间，单位字节 |
| `bookie_MAJOR_COMPACTION_TOTAL` | 大型压缩（Major Compaction）累计执行次数 |
| `bookie_MINOR_COMPACTION_TOTAL` | 小型压缩（Minor Compaction）累计执行次数 |

---

## 九、Bookie Journal（预写日志）指标

| 指标名 | 含义说明 |
|--------|----------|
| `bookie_JOURNAL_QUEUE_MAX_SIZE` | Journal 队列的最大容量 |
| `bookie_JOURNAL_DIRS` | Journal 目录数量 |
| `bookie_journal_JOURNAL_QUEUE_SIZE` | Journal 队列当前积压的请求数 |
| `bookie_journal_JOURNAL_MEMORY_USED` | Journal 使用的内存量，单位字节 |
| `bookie_journal_JOURNAL_MEMORY_MAX` | Journal 可使用的最大内存，单位字节 |
| `bookie_journal_JOURNAL_WRITE_BYTES` | Journal 累计写入字节数 |
| `bookie_journal_JOURNAL_ADD_ENTRY` | Journal 写入单条 Entry 的延迟分布，单位毫秒 |
| `bookie_journal_JOURNAL_CREATION_LATENCY` | 创建新 Journal 文件的延迟分布，单位毫秒 |
| `bookie_journal_JOURNAL_FLUSH_LATENCY` | Journal 数据强制刷入磁盘的延迟分布 |
| `bookie_journal_JOURNAL_FORCE_WRITE_QUEUE_SIZE` | Journal 强制写入队列中当前等待执行的任务数 |
| `bookie_journal_JOURNAL_FORCE_LEDGER` | Journal 强制刷盘（Force Ledger）操作延迟分布 |
| `bookie_journal_JOURNAL_FORCE_WRITE_BATCH_BYTES` | Journal 强制写批次的字节数分布 |
| `bookie_journal_JOURNAL_FORCE_WRITE_BATCH_ENTRIES` | Journal 强制写批次包含的 Entry 数量分布 |
| `bookie_journal_JOURNAL_FORCE_WRITE_ENQUEUE` | Journal 强制写入队列等待时间分布 |
| `bookie_journal_JOURNAL_FORCE_WRITE_GROUPING_TOTAL` | Journal 强制写分组操作的累计总数 |
| `bookie_journal_JOURNAL_NUM_FLUSH_MAX_WAIT` | Journal 因达到最大等待时间而触发刷盘的次数 |
| `bookie_journal_JOURNAL_NUM_FLUSH_MAX_OUTSTANDING_BYTES` | Journal 因超出最大未落盘字节阈值而触发刷盘的次数 |
| `bookie_journal_JOURNAL_NUM_FLUSH_EMPTY_QUEUE` | Journal 因队列为空而触发刷盘的次数 |
| `bookie_journal_JOURNAL_QUEUE_LATENCY` | Entry 在 Journal 队列中等待的延迟分布，单位毫秒 |
| `bookie_journal_JOURNAL_PROCESS_TIME_LATENCY` | Journal 处理时间延迟分布，单位毫秒 |
| `bookie_journal_JOURNAL_SYNC` | Journal 同步操作的延迟分布 |
| `bookie_journal_callback_time` | Journal 写入回调执行的时间分布，单位毫秒 |

---

## 十、Bookie 缓存指标

| 指标名 | 含义说明 |
|--------|----------|
| `bookie_write_cache_size` | 写缓存当前占用大小，单位字节 |
| `bookie_write_cache_max_size` | 写缓存最大容量，单位字节 |
| `bookie_write_cache_count` | 写缓存中的 Entry 数量 |
| `bookie_write_cache_hits` | 写缓存命中次数 |
| `bookie_write_cache_misses` | 写缓存未命中次数 |
| `bookie_read_cache_size` | 读缓存当前占用大小，单位字节 |
| `bookie_read_cache_count` | 读缓存中的 Entry 数量 |
| `bookie_read_cache_hits` | 读缓存命中次数 |
| `bookie_read_cache_misses` | 读缓存未命中次数 |

---

## 十一、Bookie 存储读写线程池指标

| 指标名 | 含义说明 |
|--------|----------|
| `bookkeeper_server_BookieReadThreadPool_threads` | 读线程池的当前线程数 |
| `bookkeeper_server_BookieReadThreadPool_max_queue_size` | 读线程池的最大队列长度 |
| `bookkeeper_server_BookieHighPriorityThread_threads` | 高优先级写线程池的线程数 |
| `bookkeeper_server_BookieHighPriorityThread_max_queue_size` | 高优先级写线程池的最大队列长度 |
| `bookkeeper_server_thread_executor_queue` | 各线程的当前任务队列长度 |
| `bookie_db_storage_thread_time` | DbLedgerStorage 后台清理及刷盘线程的运行耗时分布 |
| `bookkeeper_server_thread_executor_completed` | 各线程累计完成的任务数 |
| `bookkeeper_server_thread_executor_tasks_completed` | 各线程已完成任务数（细分统计） |
| `bookkeeper_server_thread_executor_tasks_rejected` | 各线程被拒绝的任务数 |
| `bookkeeper_server_thread_executor_tasks_failed` | 各线程执行失败的任务数 |
| `bookkeeper_server_WRITE_THREAD_QUEUED_LATENCY` | 写线程任务在队列中的等待延迟分布 |

---

## 十二、Bookie 读写请求指标

| 指标名 | 含义说明 |
|--------|----------|
| `bookkeeper_server_ADD_ENTRY_IN_PROGRESS` | 当前正在处理的写入请求数 |
| `bookkeeper_server_ADD_ENTRY_BLOCKED` | 当前被阻塞的写入请求数 |
| `bookkeeper_server_ADD_ENTRY_BLOCKED_WAIT` | 写入请求被阻塞等待的延迟分布 |
| `bookkeeper_server_ADD_ENTRY` | 写入 Entry 的端到端延迟分布，单位毫秒 |
| `bookie_add_entry` | Bookie 内部处理写入 Entry 的底层延迟分布 |
| `bookkeeper_server_ADD_ENTRY_REQUEST` | 写入 Entry 请求处理耗时分布 |
| `bookkeeper_server_ADD_ENTRY_REJECTED` | 被拒绝的写入请求数 |
| `bookkeeper_server_READ_ENTRY_IN_PROGRESS` | 当前正在处理的读取请求数 |
| `bookkeeper_server_READ_ENTRY_BLOCKED` | 当前被阻塞的读取请求数 |
| `bookkeeper_server_READ_ENTRY_BLOCKED_WAIT` | 读取请求被阻塞等待的延迟分布 |
| `bookkeeper_server_READ_ENTRY` | 读取 Entry 的端到端延迟分布，单位毫秒 |
| `bookkeeper_server_READ_ENTRY_REQUEST` | 读取 Entry 请求处理耗时分布 |
| `bookkeeper_server_READ_ENTRY_REJECTED` | 被拒绝的读取请求数 |
| `bookkeeper_server_READ_ENTRY_SCHEDULING_DELAY` | 读取请求调度延迟分布 |
| `bookkeeper_server_READ_ENTRY_LONG_POLL_REQUEST` | 长轮询读取请求总耗时分布 |
| `bookkeeper_server_READ_ENTRY_LONG_POLL_PRE_WAIT` | 长轮询读取请求预等待耗时分布 |
| `bookkeeper_server_READ_ENTRY_LONG_POLL_WAIT` | 长轮询等待耗时分布 |
| `bookkeeper_server_READ_ENTRY_LONG_POLL_READ` | 长轮询实际读取耗时分布 |
| `bookkeeper_server_READ_ENTRY_FENCE_REQUEST` | Fence 读取请求耗时分布 |
| `bookkeeper_server_READ_ENTRY_FENCE_READ` | Fence 读取数据耗时分布 |
| `bookkeeper_server_READ_ENTRY_FENCE_WAIT` | Fence 读取等待耗时分布 |
| `bookkeeper_server_READ_LAST_ENTRY_NOENTRY_ERROR` | 读取最后 Entry 时返回 NoEntry 错误的次数 |
| `bookkeeper_server_FORCE_LEDGER` | 强制刷盘操作的延迟分布 |
| `bookkeeper_server_FORCE_LEDGER_REQUEST` | 强制刷盘请求处理耗时分布 |
| `bookkeeper_server_WRITE_LAC` | 写入 LAC（Last Add Confirmed）的耗时分布 |
| `bookkeeper_server_WRITE_LAC_REQUEST` | 写入 LAC 请求的耗时分布 |
| `bookkeeper_server_READ_LAC` | 读取 LAC 的耗时分布 |
| `bookkeeper_server_READ_LAC_REQUEST` | 读取 LAC 请求的耗时分布 |
| `bookkeeper_server_CHANNEL_WRITE` | 网络通道写入的耗时分布 |
| `bookkeeper_server_GET_BOOKIE_INFO` | 获取 Bookie 信息请求的延迟分布 |
| `bookkeeper_server_GET_BOOKIE_INFO_REQUEST` | 获取 Bookie 信息请求处理耗时分布 |
| `bookkeeper_server_GET_LIST_OF_ENTRIES_OF_LEDGER` | 获取账本 Entry 列表的延迟分布 |
| `bookkeeper_server_GET_LIST_OF_ENTRIES_OF_LEDGER_REQUEST` | 获取账本 Entry 列表请求处理耗时分布 |

---

## 十三、Bookie 刷盘与索引指标

| 指标名 | 含义说明 |
|--------|----------|
| `bookie_flush` | Bookie 账本刷盘操作的耗时/延迟分布 |
| `bookie_flush_size` | Bookie 单次刷盘操作的数据量分布 |
| `bookie_flush_entrylog` | 刷写 EntryLog 文件的延迟分布，单位毫秒 |
| `bookie_flush_ledger_index` | 刷写账本索引的延迟分布，单位毫秒 |
| `bookie_flush_locations_index` | 刷写 Entry 位置索引的延迟分布，单位毫秒 |
| `bookie_sync_thread_time` | 同步线程运行耗时，单位毫秒 |
| `bookie_lookup_entry_location` | 查找 Entry 存储位置的耗时分布 |
| `bookie_read_locations_index_time` | 读取位置索引的耗时，单位毫秒 |
| `bookie_read_entrylog_time` | 从 EntryLog 文件读取数据的耗时，单位毫秒 |

---

## 十四、Bookie 预读（ReadAhead）指标

| 指标名 | 含义说明 |
|--------|----------|
| `bookie_readahead_max_batch_size` | 预读操作的最大批次大小 |
| `bookie_readahead_time` | 各线程预读操作的累计耗时，单位毫秒 |
| `bookie_readahead_batch_size` | 每次预读批次实际大小的分布 |
| `bookie_readahead_batch_count` | 预读批次数量统计 |

---

## 十五、副本复制（Replication Worker）指标

| 指标名 | 含义说明 |
|--------|----------|
| `replication_replication_worker_NUM_ENTRIES_READ` | 复制 Worker 读取的 Entry 总数 |
| `replication_replication_worker_NUM_ENTRIES_WRITTEN` | 复制 Worker 写入的 Entry 总数 |
| `replication_replication_worker_NUM_BYTES_READ` | 复制 Worker 读取的字节数分布 |
| `replication_replication_worker_NUM_BYTES_WRITTEN` | 复制 Worker 写入的字节数分布 |
| `replication_replication_worker_NUM_FULL_OR_PARTIAL_LEDGERS_REPLICATED` | 完整或部分复制的账本累计数量 |
| `replication_replication_worker_NUM_NOT_ADHERING_PLACEMENT_LEDGERS_REPLICATED` | 不符合放置策略而被复制的账本数量 |
| `replication_replication_worker_NUM_DEFER_LEDGER_LOCK_RELEASE_OF_FAILED_LEDGER` | 因失败账本延迟释放锁的次数 |
| `replication_replication_worker_NUM_ENTRIES_UNABLE_TO_READ_FOR_REPLICATION` | 复制过程中无法读取的 Entry 数量 |
| `replication_replication_worker_READ_DATA_LATENCY` | 复制读取数据的延迟分布 |
| `replication_replication_worker_WRITE_DATA_LATENCY` | 复制写入数据的延迟分布 |
| `replication_replication_worker_rereplicate` | 重复复制操作的耗时分布 |
| `replication_replication_worker_exceptions_BKNoSuchLedgerExistsOnMetadataServerException` | 复制时遇到账本元数据不存在异常的累计次数 |

---

## 十六、复制客户端（BookKeeper Client）指标

| 指标名 | 含义说明 |
|--------|----------|
| `replication_bookkeeper_client_bookkeeper_client_NUM_WRITABLE_BOOKIES_IN_DEFAULT_RACK` | 默认机架中可写 Bookie 节点数量 |
| `replication_bookkeeper_client_bookkeeper_client_NUM_PENDING_ADD` | 待确认的写入请求数量 |
| `replication_bookkeeper_client_bookkeeper_client_ADD_ENTRY` | 客户端写入 Entry 的延迟分布 |
| `replication_bookkeeper_client_bookkeeper_client_ADD_ENTRY_UR` | 客户端写入时发生 Under Replication 的次数 |
| `replication_bookkeeper_client_bookkeeper_client_READ_ENTRY` | 客户端读取 Entry 的延迟分布 |
| `replication_bookkeeper_client_bookkeeper_client_READ_ENTRY_DM` | 客户端读取 Entry 时发生 Digest Mismatch 的次数 |
| `replication_bookkeeper_client_bookkeeper_client_LEDGER_CREATE` | 客户端创建账本的延迟分布 |
| `replication_bookkeeper_client_bookkeeper_client_LEDGER_DELETE` | 客户端删除账本的延迟分布 |
| `replication_bookkeeper_client_bookkeeper_client_LEDGER_OPEN` | 客户端打开账本的延迟分布 |
| `replication_bookkeeper_client_bookkeeper_client_LEDGER_RECOVER` | 客户端恢复账本的延迟分布 |
| `replication_bookkeeper_client_bookkeeper_client_LEDGER_RECOVER_ADD_ENTRIES` | 账本恢复过程中写入 Entry 的延迟分布 |
| `replication_bookkeeper_client_bookkeeper_client_LEDGER_RECOVER_READ_ENTRIES` | 账本恢复过程中读取 Entry 的延迟分布 |
| `replication_bookkeeper_client_bookkeeper_client_WRITE_LAC` | 客户端写入 LAC 的延迟分布 |
| `replication_bookkeeper_client_bookkeeper_client_READ_LAC` | 客户端读取 LAC 的延迟分布 |
| `replication_bookkeeper_client_bookkeeper_client_FORCE` | 客户端强制刷盘操作的延迟分布 |
| `replication_bookkeeper_client_bookkeeper_client_LAC_UPDATE_HITS` | LAC 更新命中缓存的次数 |
| `replication_bookkeeper_client_bookkeeper_client_LAC_UPDATE_MISSES` | LAC 更新未命中缓存的次数 |
| `replication_bookkeeper_client_bookkeeper_client_NUM_ENSEMBLE_CHANGE` | 账本 Ensemble 变更次数（Bookie 节点集合变化） |
| `replication_bookkeeper_client_bookkeeper_client_READ_REQUESTS_REORDERED` | 被重新排序的读取请求数量分布 |
| `replication_bookkeeper_client_bookkeeper_client_READ_LAST_CONFIRMED_AND_ENTRY` | 读取最后确认及 Entry 的耗时分布 |
| `replication_bookkeeper_client_bookkeeper_client_READ_LAST_CONFIRMED_AND_ENTRY_RESPONSE` | 读取最后确认及 Entry 的响应时间分布 |
| `replication_bookkeeper_client_bookkeeper_client_BOOKIES_JOINED` | 新加入集群的 Bookie 数量事件分布 |
| `replication_bookkeeper_client_bookkeeper_client_BOOKIES_LEFT` | 离开集群的 Bookie 数量事件分布 |
| `replication_bookkeeper_client_bookkeeper_client_CLIENT_CHANNEL_WRITE_WAIT` | 客户端通道写入等待时间分布 |
| `replication_bookkeeper_client_bookkeeper_client_WRITE_DELAYED_DUE_TO_NOT_ENOUGH_FAULT_DOMAINS` | 因容错域不足导致写入延迟的次数 |
| `replication_bookkeeper_client_bookkeeper_client_WRITE_DELAYED_DUE_TO_NOT_ENOUGH_FAULT_DOMAINS_LATENCY` | 因容错域不足导致写入延迟的延迟分布 |
| `replication_bookkeeper_client_bookkeeper_client_WRITE_TIME_OUT_DUE_TO_NOT_ENOUGH_FAULT_DOMAINS` | 因容错域不足导致写入超时的次数 |
| `replication_bookkeeper_client_bookkeeper_client_bookie_watcher_NEW_ENSEMBLE_TIME` | 创建新 Ensemble 所消耗的时间分布 |
| `replication_bookkeeper_client_bookkeeper_client_bookie_watcher_REPLACE_BOOKIE_TIME` | 替换 Bookie 节点所消耗的时间分布 |
| `replication_bookkeeper_client_BookKeeperClientWorker_threads` | 复制客户端工作线程数量 |
| `replication_bookkeeper_client_BookKeeperClientWorker_max_queue_size` | 复制客户端工作线程最大队列大小 |
| `replication_bookkeeper_client_BookKeeperClientWorker_task_queued` | 复制客户端工作线程任务排队等待时间分布 |
| `replication_bookkeeper_client_BookKeeperClientWorker_task_execution` | 复制客户端工作线程任务执行耗时分布 |
| `replication_bookkeeper_client_thread_executor_queue` | 复制客户端各线程的任务队列长度 |
| `replication_bookkeeper_client_thread_executor_completed` | 复制客户端各线程累计完成任务数 |
| `replication_bookkeeper_client_thread_executor_tasks_completed` | 复制客户端各线程已完成任务数（细分） |
| `replication_bookkeeper_client_thread_executor_tasks_rejected` | 复制客户端各线程被拒绝的任务数 |
| `replication_bookkeeper_client_thread_executor_tasks_failed` | 复制客户端各线程执行失败的任务数 |
| `replication_bookkeeper_client_watcher_state_SyncConnected` | 复制客户端与 DCS 建立同步连接的次数 |
| `replication_bookkeeper_client_dcs_sync` | 复制客户端 DCS 同步操作的延迟分布 |
| `replication_bookkeeper_client_dcs_create` | 复制客户端在 DCS 创建节点的延迟分布 |
| `replication_bookkeeper_client_dcs_create_client` | 复制客户端创建 DCS 客户端的延迟分布 |
| `replication_bookkeeper_client_dcs_delete` | 复制客户端在 DCS 删除节点的延迟分布 |
| `replication_bookkeeper_client_dcs_exists` | 复制客户端检查 DCS 节点存在性的延迟分布 |
| `replication_bookkeeper_client_dcs_get_acl` | 复制客户端获取 DCS ACL 的延迟分布 |
| `replication_bookkeeper_client_dcs_set_acl` | 复制客户端设置 DCS ACL 的延迟分布 |
| `replication_bookkeeper_client_dcs_get_children` | 复制客户端获取 DCS 子节点列表的延迟分布 |
| `replication_bookkeeper_client_dcs_get_data` | 复制客户端从 DCS 读取数据的延迟分布 |
| `replication_bookkeeper_client_dcs_set_data` | 复制客户端在 DCS 写入数据的延迟分布 |
| `replication_bookkeeper_client_dcs_multi` | 复制客户端执行 DCS 批量操作的延迟分布 |

---

## 十七、Bookie DCS 客户端指标

> Bookie 自身连接 DCS（分布式协调服务）所产生的操作延迟指标。

| 指标名 | 含义说明 |
|--------|----------|
| `bookie_bookie_dcs_create` | Bookie DCS 客户端创建节点的延迟分布 |
| `bookie_bookie_dcs_create_client` | Bookie 创建 DCS 客户端连接的延迟分布 |
| `bookie_bookie_dcs_delete` | Bookie DCS 客户端删除节点的延迟分布 |
| `bookie_bookie_dcs_exists` | Bookie DCS 客户端检查节点是否存在的延迟分布 |
| `bookie_bookie_dcs_get_acl` | Bookie DCS 客户端获取节点 ACL 的延迟分布 |
| `bookie_bookie_dcs_set_acl` | Bookie DCS 客户端设置节点 ACL 的延迟分布 |
| `bookie_bookie_dcs_get_children` | Bookie DCS 客户端获取子节点列表的延迟分布 |
| `bookie_bookie_dcs_get_data` | Bookie DCS 客户端读取节点数据的延迟分布 |
| `bookie_bookie_dcs_set_data` | Bookie DCS 客户端写入节点数据的延迟分布 |
| `bookie_bookie_dcs_multi` | Bookie DCS 客户端执行批量操作的延迟分布 |
| `bookie_bookie_dcs_sync` | Bookie DCS 客户端同步操作的延迟分布 |
| `bookie_bookie_watcher_state_SyncConnected` | Bookie DCS Watcher 建立 SyncConnected 连接状态的次数 |
| `replication_bookkeeper_client_bookkeeper_client_bookie_watcher_ENSEMBLE_NOT_ADHERING_TO_PLACEMENT_POLICY_TOTAL` | 不符合放置策略的 Ensemble 累计次数 |
| `replication_bookkeeper_client_bookkeeper_client_FAILED_TO_RESOLVE_NETWORK_LOCATION_TOTAL` | 解析网络位置失败的累计次数 |
| `replication_bookkeeper_client_bookkeeper_client_SPECULATIVE_READ_COUNT` | 投机读取（Speculative Read）操作次数 |
