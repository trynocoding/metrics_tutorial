# CloudMQ DCS 组件指标说明

DCS（Distributed Coordination Service）是 CloudMQ 内置的 ZooKeeper 兼容协调服务，负责集群元数据管理、Leader 选举、分布式锁与 Watch 通知。

---

## 一、JVM 内存指标

| 指标名 | 类型 | 含义说明 |
|--------|------|----------|
| `jvm_memory_objects_pending_finalization` | gauge | 等待 GC 终结队列中的对象数量 |
| `jvm_memory_bytes_used` | gauge | JVM 各内存区域（heap/nonheap）当前使用量，单位字节 |
| `jvm_memory_bytes_committed` | gauge | JVM 各内存区域已提交大小，单位字节 |
| `jvm_memory_bytes_max` | gauge | JVM 各内存区域最大容量，单位字节 |
| `jvm_memory_bytes_init` | gauge | JVM 各内存区域初始大小，单位字节 |
| `jvm_memory_pool_bytes_used` | gauge | JVM 各内存池（ZHeap/Metaspace/CodeHeap 等）当前使用量，单位字节 |
| `jvm_memory_pool_bytes_committed` | gauge | JVM 各内存池已提交大小，单位字节 |
| `jvm_memory_pool_bytes_max` | gauge | JVM 各内存池最大容量，单位字节 |
| `jvm_memory_pool_bytes_init` | gauge | JVM 各内存池初始大小，单位字节 |
| `jvm_memory_pool_collection_used_bytes` | gauge | GC 后各内存池的使用量，单位字节 |
| `jvm_memory_pool_collection_committed_bytes` | gauge | GC 后各内存池已提交大小，单位字节 |
| `jvm_memory_pool_collection_max_bytes` | gauge | GC 后各内存池最大值，单位字节 |
| `jvm_memory_pool_collection_init_bytes` | gauge | GC 后各内存池初始值，单位字节 |
| `jvm_memory_pool_allocated_bytes` | counter | JVM 各内存池累计分配字节数（GC 后更新） |

---

## 二、JVM 线程与类指标

| 指标名 | 类型 | 含义说明 |
|--------|------|----------|
| `jvm_threads_current` | gauge | 当前 JVM 线程总数 |
| `jvm_threads_daemon` | gauge | 当前守护线程数 |
| `jvm_threads_peak` | gauge | JVM 启动以来线程数峰值 |
| `jvm_threads_started` | counter | JVM 启动以来累计创建的线程总数 |
| `jvm_threads_deadlocked` | gauge | 当前处于死锁状态的线程数（等待对象监视器或可拥有同步器） |
| `jvm_threads_deadlocked_monitor` | gauge | 因监视器（monitor）死锁的线程数 |
| `jvm_threads_state` | gauge | 各状态下的线程数（NEW/RUNNABLE/BLOCKED/WAITING/TIMED_WAITING/TERMINATED/UNKNOWN） |
| `jvm_classes_currently_loaded` | gauge | 当前 JVM 已加载的类数量 |
| `jvm_classes_loaded` | counter | JVM 启动以来累计加载的类总数 |
| `jvm_classes_unloaded` | counter | JVM 启动以来累计卸载的类总数 |

---

## 三、JVM GC 与 Buffer 指标

| 指标名 | 类型 | 含义说明 |
|--------|------|----------|
| `jvm_gc_collection_seconds` | summary | GC 周期耗时（count：GC 次数，sum：总耗时），支持 ZGC Cycles/Pauses |
| `jvm_pause_time_ms` | summary | JVM STW（Stop-The-World）停顿时长分布，单位毫秒 |
| `jvm_info` | gauge | JVM 基础信息（运行时、厂商、版本） |
| `jvm_buffer_pool_used_bytes` | gauge | JVM Buffer 池（direct/mapped）当前使用字节数 |
| `jvm_buffer_pool_capacity_bytes` | gauge | JVM Buffer 池容量，单位字节 |
| `jvm_buffer_pool_used_buffers` | gauge | JVM Buffer 池当前使用的 Buffer 数量 |

---

## 四、进程指标

| 指标名 | 类型 | 含义说明 |
|--------|------|----------|
| `process_cpu_seconds` | counter | 进程累计 CPU 使用时间，单位秒 |
| `process_start_time_seconds` | gauge | 进程启动时间（Unix 时间戳） |
| `process_open_fds` | gauge | 当前已打开的文件描述符数量 |
| `process_max_fds` | gauge | 系统允许的最大文件描述符数量 |
| `process_virtual_memory_bytes` | gauge | 进程虚拟内存大小，单位字节 |
| `process_resident_memory_bytes` | gauge | 进程常驻物理内存大小，单位字节 |

---

## 五、日志指标

| 指标名 | 类型 | 含义说明 |
|--------|------|----------|
| `log4j2_appender` | counter | 各日志级别（debug/info/warn/error/fatal/trace）的累计日志输出条数 |

---

## 六、服务运行状态指标

| 指标名 | 类型 | 含义说明 |
|--------|------|----------|
| `uptime` | gauge | DCS 服务已运行时长，单位毫秒 |
| `quorum_size` | gauge | 当前 Quorum（法定人数）节点数 |
| `synced_observers` | gauge | 当前已同步的 Observer 节点数 |
| `auth_failed_count` | gauge | 客户端认证失败的累计次数 |
| `open_file_descriptor_count` | gauge | DCS 进程当前打开的文件描述符数量 |
| `max_file_descriptor_count` | gauge | DCS 进程允许的最大文件描述符数量 |
| `outstanding_tls_handshake` | gauge | 当前正在进行中的 TLS 握手数量 |
| `non_mtls_local_conn_count` | gauge | 当前非 mTLS 本地连接数量 |
| `non_mtls_remote_conn_count` | gauge | 当前非 mTLS 远端连接数量 |
| `unavailable_time` | summary | 服务不可用时长分布，单位毫秒 |

---

## 七、客户端连接指标

| 指标名 | 类型 | 含义说明 |
|--------|------|----------|
| `num_alive_connections` | gauge | 当前活跃的客户端连接数 |
| `packets_received` | gauge | 累计接收的网络数据包数量 |
| `packets_sent` | gauge | 累计发送的网络数据包数量 |
| `bytes_received_count` | counter | 累计接收的字节总数 |
| `response_bytes` | counter | 累计发送的响应字节总数 |
| `connection_request_count` | counter | 累计收到的连接请求次数 |
| `connection_drop_count` | counter | 因服务端主动断开而丢弃的连接数 |
| `connection_drop_probability` | gauge | 当前连接丢弃概率（用于负载控制） |
| `connection_rejected` | counter | 被拒绝的连接请求数（超出限制） |
| `connection_revalidate_count` | counter | 连接重新验证（Session 恢复）的累计次数 |
| `revalidate_count` | counter | 累计 Session 重验证次数 |
| `connection_token_deficit` | summary | 连接令牌不足事件的时长分布（速率限制） |
| `cnxn_closed_without_dcs_server_running` | counter | 服务尚未就绪时关闭连接的累计次数 |
| `sessionless_connections_expired` | counter | 无会话连接因超时过期的次数 |
| `tls_handshake_exceeded` | counter | TLS 握手超时的累计次数 |
| `unsuccessful_handshake` | counter | TLS/连接握手失败的累计次数 |
| `insecure_admin_count` | counter | 通过非安全通道执行 Admin 操作的累计次数 |

---

## 八、会话（Session）指标

| 指标名 | 类型 | 含义说明 |
|--------|------|----------|
| `global_sessions` | gauge | 当前全局 Session 数量（含本地与远端） |
| `local_sessions` | gauge | 当前本地 Session 数量 |
| `session_queues_drained` | summary | Session 请求队列排空操作的耗时分布，单位毫秒 |
| `pending_session_queue_size` | summary | 待处理 Session 队列的当前长度分布 |
| `stale_sessions_expired` | counter | 已过期（stale）的 Session 数量 |

---

## 九、数据节点（ZNode）与 Watch 指标

| 指标名 | 类型 | 含义说明 |
|--------|------|----------|
| `znode_count` | gauge | 数据树中当前 ZNode 总数 |
| `ephemerals_count` | gauge | 当前临时节点（Ephemeral ZNode）数量 |
| `approximate_data_size` | gauge | 数据树中所有节点数据的近似总字节数 |
| `watch_count` | gauge | 当前活跃的 Watch 数量 |
| `watch_bytes` | counter | Watch 事件累计发送的字节总数 |
| `dead_watchers_queued` | counter | 死亡 Watcher 入队等待清理的累计次数 |
| `dead_watchers_cleared` | counter | 已成功清理的死亡 Watcher 累计数量 |
| `dead_watchers_cleaner_latency` | summary | 死亡 Watcher 清理操作的延迟分布，单位毫秒 |
| `add_dead_watcher_stall_time` | counter | 添加死亡 Watcher 时发生停顿的累计时间，单位毫秒 |
| `node_created_watch_count` | summary | 节点创建事件触发的 Watch 数量分布 |
| `node_deleted_watch_count` | summary | 节点删除事件触发的 Watch 数量分布 |
| `node_changed_watch_count` | summary | 节点数据变更事件触发的 Watch 数量分布 |
| `node_children_watch_count` | summary | 节点子节点变更事件触发的 Watch 数量分布 |

---

## 十、请求处理延迟指标

> 以下指标反映客户端读写请求在 DCS 服务端的处理耗时，覆盖从接收到返回的全链路各阶段。

| 指标名 | 类型 | 含义说明 |
|--------|------|----------|
| `avg_latency` | gauge | 请求处理平均延迟，单位毫秒 |
| `min_latency` | gauge | 请求处理最小延迟，单位毫秒 |
| `max_latency` | gauge | 请求处理最大延迟，单位毫秒 |
| `readlatency` | summary | 读请求端到端延迟分布，单位毫秒 |
| `updatelatency` | summary | 写请求（update）端到端延迟分布，单位毫秒 |
| `min_client_response_size` | gauge | 响应报文的最小大小，单位字节 |
| `max_client_response_size` | gauge | 响应报文的最大大小，单位字节 |
| `last_client_response_size` | gauge | 最近一次响应报文的大小，单位字节 |
| `outstanding_requests` | gauge | 当前挂起（尚未处理完成）的请求数量 |
| `close_session_prep_time` | summary | 关闭 Session 前预处理阶段的耗时分布，单位毫秒 |
| `socket_closing_time` | summary | 关闭 Socket 连接的耗时分布，单位毫秒 |

---

## 十一、请求队列与限流指标

| 指标名 | 类型 | 含义说明 |
|--------|------|----------|
| `requests_in_session_queue` | summary | Session 队列中积压的请求数量分布 |
| `reads_after_write_in_session_queue` | summary | Session 队列中写请求之后积压读请求数量分布 |
| `reads_issued_from_session_queue` | summary | 从 Session 队列发出的读请求数量分布 |
| `request_throttle_wait_count` | counter | 请求因限流而等待的累计次数 |
| `request_throttle_queue_time_ms` | summary | 请求在限流队列中等待的时长分布，单位毫秒 |
| `large_requests_rejected` | counter | 因超过大小限制被拒绝的请求累计次数 |
| `throttled_ops` | counter | 累计被限流的操作次数 |
| `stale_requests` | counter | 过期（stale）请求的累计数量 |
| `stale_requests_dropped` | counter | 被丢弃的过期请求累计数量 |
| `stale_replies` | counter | 过期回复（stale reply）的累计数量 |
| `requests_not_forwarded_to_commit_processor` | counter | 未被转发到 CommitProcessor 的请求累计次数 |
| `netty_queued_buffer_capacity` | summary | Netty 输出队列缓冲区的当前容量分布，单位字节 |

---

## 十二、Prep/Sync/Commit 处理器链指标

> 这组指标反映写请求在三阶段处理器流水线（PrepProcessor → SyncProcessor → CommitProcessor）各阶段的队列长度与耗时，是 ZooKeeper 写路径性能分析的核心指标。

| 指标名 | 类型 | 含义说明 |
|--------|------|----------|
| `prep_processor_request_queued` | counter | PrepProcessor 累计入队的请求数量 |
| `prep_processor_queue_size` | summary | PrepProcessor 队列当前长度分布 |
| `prep_processor_queue_time_ms` | summary | 请求在 PrepProcessor 队列中等待的时长分布，单位毫秒 |
| `prep_process_time` | summary | PrepProcessor 处理单个请求的耗时分布，单位毫秒 |
| `sync_processor_request_queued` | counter | SyncProcessor 累计入队的请求数量 |
| `sync_processor_queue_size` | summary | SyncProcessor 队列当前长度分布 |
| `sync_processor_queue_time_ms` | summary | 请求在 SyncProcessor 队列中等待的时长分布，单位毫秒 |
| `sync_processor_queue_flush_time_ms` | summary | SyncProcessor 队列刷盘（flush）操作耗时分布，单位毫秒 |
| `sync_processor_queue_and_flush_time_ms` | summary | SyncProcessor 单次处理（排队+刷盘）总耗时分布，单位毫秒 |
| `sync_processor_batch_size` | summary | SyncProcessor 每批次处理的请求数量分布 |
| `fsynctime` | summary | 事务日志 fsync 操作的耗时分布，单位毫秒 |
| `request_commit_queued` | counter | 提交（commit）请求的累计入队次数 |
| `commit_process_time` | summary | CommitProcessor 处理提交请求的耗时分布，单位毫秒 |
| `commit_commit_proc_req_queued` | summary | CommitProcessor 提交队列中积压的请求数量分布 |
| `concurrent_request_processing_in_commit_processor` | summary | CommitProcessor 并发处理请求数量分布 |
| `write_batch_time_in_commit_processor` | summary | CommitProcessor 处理一批写请求的总耗时分布，单位毫秒 |
| `time_waiting_empty_pool_in_commit_processor_read_ms` | summary | CommitProcessor 因读请求等待空闲线程池的时长分布，单位毫秒 |

---

## 十三、读写 CommitProc 流程指标

| 指标名 | 类型 | 含义说明 |
|--------|------|----------|
| `read_commit_proc_req_queued` | summary | CommitProcessor 读队列积压请求数量分布 |
| `read_commit_proc_issued` | summary | CommitProcessor 实际发出处理的读请求数量分布 |
| `read_commitproc_time_ms` | summary | 读请求从进入 CommitProcessor 到处理完成的耗时分布，单位毫秒 |
| `read_final_proc_time_ms` | summary | 读请求在 FinalProcessor 中处理的耗时分布，单位毫秒 |
| `write_commit_proc_req_queued` | summary | CommitProcessor 写队列积压请求数量分布 |
| `write_commit_proc_issued` | summary | CommitProcessor 实际发出处理的写请求数量分布 |
| `write_commitproc_time_ms` | summary | 写请求从进入 CommitProcessor 到处理完成的耗时分布，单位毫秒 |
| `write_final_proc_time_ms` | summary | 写请求在 FinalProcessor 中处理的耗时分布，单位毫秒 |
| `local_write_committed_time_ms` | summary | 本地写请求提交（commit）的耗时分布，单位毫秒 |
| `server_write_committed_time_ms` | summary | 服务端写请求提交的耗时分布，单位毫秒 |
| `outstanding_changes_queued` | counter | 未应用到数据树的变更（OutstandingChange）累计入队次数 |
| `outstanding_changes_removed` | counter | 已移除（应用或取消）的 OutstandingChange 累计次数 |

---

## 十四、Leader 选举与集群同步指标

| 指标名 | 类型 | 含义说明 |
|--------|------|----------|
| `election_time` | summary | Leader 选举耗时分布，单位毫秒 |
| `looking_count` | counter | 进入 LOOKING 状态（触发选举）的累计次数 |
| `leader_unavailable_time` | summary | Leader 不可用持续时长分布，单位毫秒 |
| `quit_leading_due_to_disloyal_voter` | counter | 因 Follower 投票异常导致 Leader 主动退位的累计次数 |
| `follower_sync_time` | summary | Follower 与 Leader 完成数据同步的耗时分布，单位毫秒 |
| `observer_sync_time` | summary | Observer 与 Leader 完成数据同步的耗时分布，单位毫秒 |
| `synced_followers` | gauge | 当前已同步的 Follower 节点数 |
| `synced_non_voting_followers` | gauge | 当前已同步的非投票 Follower 节点数 |
| `pending_syncs` | gauge | 当前挂起的同步请求数 |
| `learners` | gauge | 当前连接的 Learner（Follower/Observer）总数 |
| `leader_uptime` | gauge | Leader 服务已运行时长，单位毫秒 |

---

## 十五、提案（Proposal）与日志提交指标

| 指标名 | 类型 | 含义说明 |
|--------|------|----------|
| `proposal_count` | counter | Leader 发出的提案（Proposal）累计数量 |
| `min_proposal_size` | gauge | 最小提案内容大小，单位字节 |
| `max_proposal_size` | gauge | 最大提案内容大小，单位字节 |
| `last_proposal_size` | gauge | 最近一次提案内容大小，单位字节 |
| `proposal_latency` | summary | 提案从发出到被集群确认的延迟分布，单位毫秒 |
| `proposal_process_time` | summary | Leader 处理提案的耗时分布，单位毫秒 |
| `proposal_ack_creation_latency` | summary | Leader 创建提案 ACK 的耗时分布，单位毫秒 |
| `commit_count` | counter | 已提交的事务累计数量 |
| `commit_propagation_latency` | summary | 提案从 commit 到传播至所有节点的延迟分布，单位毫秒 |
| `propagation_latency` | summary | 提案从 Leader 发出到 Follower 确认的传播延迟分布，单位毫秒 |
| `quorum_ack_latency` | summary | Leader 等待 Quorum ACK 的延迟分布，单位毫秒 |
| `learner_commit_received_count` | counter | Learner（Follower/Observer）收到 commit 消息的累计次数 |
| `learner_proposal_received_count` | counter | Learner 收到 Leader 提案的累计次数 |
| `sync_process_time` | summary | Follower SyncProcessor 处理提案的耗时分布，单位毫秒 |
| `om_proposal_process_time_ms` | summary | Observer Manager 处理提案的耗时分布，单位毫秒 |
| `om_commit_process_time_ms` | summary | Observer Manager 处理提交的耗时分布，单位毫秒 |
| `ack_latency` | summary | 请求确认（ACK）的延迟分布，单位毫秒 |

---

## 十六、Learner 处理器指标

| 指标名 | 类型 | 含义说明 |
|--------|------|----------|
| `learner_request_processor_queue_size` | summary | Learner 请求处理器队列当前长度分布 |
| `learner_handler_qp_size` | summary | LearnerHandler 消息队列当前长度分布 |
| `learner_handler_qp_time_ms` | summary | LearnerHandler 消息队列等待时长分布，单位毫秒 |
| `skip_learner_request_to_next_processor_count` | counter | Learner 跳过请求直接转发至下一处理器的累计次数 |

---

## 十七、快照与差量同步指标

| 指标名 | 类型 | 含义说明 |
|--------|------|----------|
| `snapshottime` | summary | 快照生成（序列化）耗时分布，单位毫秒 |
| `snap_count` | counter | 累计生成快照的次数 |
| `dbinittime` | summary | 数据库（数据树）初始化耗时分布，单位毫秒 |
| `startup_snap_load_time` | summary | 启动时加载快照文件的耗时分布，单位毫秒 |
| `startup_txns_load_time` | summary | 启动时重放事务日志的耗时分布，单位毫秒 |
| `startup_txns_loaded` | summary | 启动时重放的事务日志条目数量分布 |
| `diff_count` | counter | 执行差量同步（diff sync）的累计次数 |
| `inflight_diff_count` | summary | 当前正在进行的差量同步数量分布 |
| `inflight_snap_count` | summary | 当前正在进行的全量快照同步数量分布 |

---

## 十八、响应包缓存指标

| 指标名 | 类型 | 含义说明 |
|--------|------|----------|
| `response_packet_cache_hits` | counter | 响应包缓存命中的累计次数 |
| `response_packet_cache_misses` | counter | 响应包缓存未命中的累计次数 |
| `response_packet_get_children_cache_hits` | counter | getChildren 请求响应包缓存命中的累计次数 |
| `response_packet_get_children_cache_misses` | counter | getChildren 请求响应包缓存未命中的累计次数 |

---

## 十九、集群认证与 Ensemble 指标

| 指标名 | 类型 | 含义说明 |
|--------|------|----------|
| `ensemble_auth_success` | counter | Ensemble 成员间认证成功的累计次数 |
| `ensemble_auth_fail` | counter | Ensemble 成员间认证失败的累计次数 |
| `ensemble_auth_skip` | counter | Ensemble 认证被跳过的累计次数 |
| `digest_mismatches_count` | counter | 数据摘要（digest）校验失败的累计次数 |
| `unrecoverable_error_count` | counter | 发生不可恢复错误的累计次数 |

---

## 二十、Quota（配额）指标

| 指标名 | 类型 | 含义说明 |
|--------|------|----------|
| `quota_bytes_limit_per_namespace` | gauge | 各命名空间配置的字节数上限（0 表示未配置） |
| `quota_bytes_usage_per_namespace` | gauge | 各命名空间当前使用的字节数 |
| `quota_count_limit_per_namespace` | gauge | 各命名空间配置的节点数量上限（0 表示未配置） |
| `quota_count_usage_per_namespace` | gauge | 各命名空间当前节点数量 |
| `quota_exceeded_error_per_namespace` | counter | 各命名空间触发配额超限错误的累计次数 |

---

## 二十一、命名空间读写延迟指标

> 按命名空间（key）维度统计操作延迟，覆盖 CloudMQ 各组件（loadbalance/ledgers/admin/namespace 等）的 DCS 访问模式。

| 指标名 | 类型 | 含义说明 |
|--------|------|----------|
| `write_per_namespace` | summary | 各命名空间写操作延迟分布（按 key 标签区分），单位毫秒 |
| `read_per_namespace` | summary | 各命名空间读操作延迟分布（按 key 标签区分），单位毫秒 |
