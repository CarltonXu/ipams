# 仪表盘 API 文档

## 获取仪表盘数据

获取仪表盘所需的所有统计数据。

### 请求

```http
GET /api/v1/dashboard
Authorization: Bearer <token>
```

### 响应

成功响应 (200):
```json
{
    "stats": {
        "total_ips": "integer",        // IP地址总数
        "claimed_ips": "integer",      // 已分配IP数量
        "unclaimed_ips": "integer",    // 未分配IP数量
        "user_claimed_ips": "integer", // 当前用户分配的IP数量
        "total_policies": "integer",   // 扫描策略总数
        "running_jobs": "integer",     // 运行中的任务数
        "failed_jobs": "integer",      // 失败的任务数
        "successful_jobs": "integer",  // 成功的任务数
        "cpu_usage": "float",          // CPU使用率
        "memory_usage": "float",       // 内存使用率
        "disk_usage": "float"          // 磁盘使用率
    },
    "resources": {
        "audit_resources": [           // 审计资源列表
            {
                "id": "integer",
                "user_id": "integer",
                "action": "string",
                "target": "string",
                "details": "string",
                "created_at": "string"
            }
        ]
    },
    "recent_jobs": [                   // 最近的任务列表
        {
            "id": "integer",
            "user_id": "integer",
            "policy_id": "integer",
            "subnet_id": "integer",
            "status": "string",
            "start_time": "string",
            "end_time": "string",
            "created_at": "string",
            "updated_at": "string"
        }
    ]
}
```

错误响应 (500):
```json
{
    "error": "string"  // 错误信息
}
```

### 说明

- 返回系统整体运行状况的统计数据
- 包含 IP 地址分配情况
- 包含扫描任务执行情况
- 包含系统资源使用情况
- 包含最近的审计记录
- 包含最近的任务记录 