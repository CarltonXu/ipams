# 策略管理 API 文档

## 获取策略列表

获取当前用户的所有扫描策略。

### 请求

```http
GET /api/v1/policy
Authorization: Bearer <token>
```

### 响应

成功响应 (200):
```json
[
    {
        "id": "integer",
        "name": "string",           // 策略名称
        "description": "string",    // 策略描述
        "strategies": [             // 扫描策略列表
            {
                "cron": "string",           // 定时表达式
                "start_time": "string",     // 开始时间
                "subnet_ids": ["string"],   // 子网ID列表
                "scan_params": {            // 扫描参数
                    "enable_custom_ports": boolean,
                    "ports": "string",
                    "enable_custom_scan_type": boolean,
                    "scan_type": "string"
                }
            }
        ],
        "threads": "integer",       // 线程数
        "status": "string",         // 策略状态
        "created_at": "string",
        "subnets": [                // 关联的子网列表
            {
                "id": "integer",
                "name": "string",
                "subnet": "string"
            }
        ]
    }
]
```

错误响应 (500):
```json
{
    "error": "string"  // 错误信息
}
```

### 说明

- 只返回当前用户的策略
- 不返回已删除的策略
- 包含策略关联的子网信息

## 创建策略

创建新的扫描策略。

### 请求

```http
POST /api/v1/policy
Authorization: Bearer <token>
Content-Type: application/json

{
    "subnets": [                    // 子网列表
        {
            "name": "string",       // 子网名称
            "subnet": "string"      // 子网地址
        }
    ],
    "policies": [                   // 策略列表
        {
            "name": "string",       // 策略名称
            "description": "string", // 策略描述
            "threads": "integer",   // 线程数
            "strategies": [         // 扫描策略列表
                {
                    "cron": "string",           // 定时表达式
                    "start_time": "string",     // 开始时间
                    "scan_params": {            // 扫描参数
                        "enable_custom_ports": boolean,
                        "ports": "string",
                        "enable_custom_scan_type": boolean,
                        "scan_type": "string"
                    }
                }
            ]
        }
    ]
}
```

### 响应

成功响应 (200):
```json
{
    "message": "Configuration saved successfully",
    "policies": [
        {
            "id": "integer",
            "name": "string",
            "description": "string",
            "strategies": [
                {
                    "cron": "string",
                    "start_time": "string",
                    "subnet_ids": ["string"],
                    "scan_params": {
                        "enable_custom_ports": boolean,
                        "ports": "string",
                        "enable_custom_scan_type": boolean,
                        "scan_type": "string"
                    }
                }
            ],
            "threads": "integer",
            "status": "string",
            "created_at": "string",
            "subnets": [
                {
                    "id": "integer",
                    "name": "string",
                    "subnet": "string"
                }
            ]
        }
    ]
}
```

错误响应 (400/500):
```json
{
    "error": "string"  // 错误信息
}
```

### 说明

- 支持批量创建策略
- 支持创建或更新子网
- 会自动建立策略和子网的关联关系
- 会更新调度器
- 会发送通知

## 更新策略

更新现有扫描策略。

### 请求

```http
PUT /api/v1/policy/{policy_id}
Authorization: Bearer <token>
Content-Type: application/json

{
    "name": "string",           // 策略名称
    "description": "string",    // 策略描述
    "threads": "integer",       // 线程数
    "strategies": [             // 扫描策略列表
        {
            "cron": "string",           // 定时表达式
            "start_time": "string",     // 开始时间
            "scan_params": {            // 扫描参数
                "enable_custom_ports": boolean,
                "ports": "string",
                "enable_custom_scan_type": boolean,
                "scan_type": "string"
            }
        }
    ]
}
```

### 响应

成功响应 (200):
```json
{
    "id": "integer",
    "name": "string",
    "description": "string",
    "strategies": [
        {
            "cron": "string",
            "start_time": "string",
            "subnet_ids": ["string"],
            "scan_params": {
                "enable_custom_ports": boolean,
                "ports": "string",
                "enable_custom_scan_type": boolean,
                "scan_type": "string"
            }
        }
    ],
    "threads": "integer",
    "status": "string",
    "created_at": "string",
    "subnets": [
        {
            "id": "integer",
            "name": "string",
            "subnet": "string"
        }
    ]
}
```

错误响应 (404/500):
```json
{
    "error": "string"  // 错误信息
}
```

### 说明

- 只能更新自己的策略
- 会更新调度器
- 会记录操作日志

## 删除策略

删除指定的扫描策略。

### 请求

```http
DELETE /api/v1/policy/{policy_id}
Authorization: Bearer <token>
```

### 响应

成功响应 (200):
```json
{
    "message": "Policy deleted successfully"
}
```

错误响应 (404/500):
```json
{
    "error": "string"  // 错误信息
}
```

### 说明

- 只能删除自己的策略
- 执行软删除
- 会更新调度器
- 会记录操作日志

## 获取策略任务

获取指定策略的扫描任务列表。

### 请求

```http
GET /api/v1/policy/{policy_id}/jobs
Authorization: Bearer <token>
```

### 响应

成功响应 (200):
```json
[
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
```

错误响应 (404/500):
```json
{
    "error": "string"  // 错误信息
}
```

### 说明

- 只能查看自己的策略任务
- 按创建时间倒序排序

## 获取调度任务

获取所有调度任务。

### 请求

```http
GET /api/v1/policy/scheduler/jobs
Authorization: Bearer <token>
```

### 响应

成功响应 (200):
```json
[
    {
        "id": "string",
        "name": "string",
        "func": "string",
        "args": ["string"],
        "kwargs": {},
        "trigger": "string",
        "next_run_time": "string"
    }
]
```

错误响应 (500):
```json
{
    "error": "string"  // 错误信息
}
```

### 说明

- 返回所有调度任务的详细信息
- 包含下次运行时间

## 更新策略状态

更新策略的启用状态。

### 请求

```http
PUT /api/v1/policy/{policy_id}/status
Authorization: Bearer <token>
Content-Type: application/json

{
    "status": "string"  // enabled 或 disabled
}
```

### 响应

成功响应 (200):
```json
{
    "message": "Policy status updated successfully"
}
```

错误响应 (400/404/500):
```json
{
    "error": "string"  // 错误信息
}
```

### 说明

- 只能更新自己的策略状态
- 会更新调度器
- 会记录操作日志