# 任务管理 API 文档

## 获取任务列表

获取当前用户的所有扫描任务。

### 请求

```http
GET /api/v1/task
Authorization: Bearer <token>

Query Parameters:
- status: string[]      // 任务状态列表
- page: integer         // 页码，默认1
- page_size: integer    // 每页记录数，默认10
```

### 响应

成功响应 (200):
```json
{
    "jobs": [
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
    ],
    "total": "integer",      // 总记录数
    "page": "integer",       // 当前页码
    "page_size": "integer"   // 每页记录数
}
```

错误响应 (500):
```json
{
    "error": "string"  // 错误信息
}
```

### 说明

- 只返回当前用户的任务
- 支持按状态过滤
- 按开始时间倒序排序
- 支持分页查询

## 创建扫描任务

创建新的扫描任务。

### 请求

```http
POST /api/v1/task
Authorization: Bearer <token>
Content-Type: application/json

{
    "subnet_ids": ["integer"],  // 子网ID列表
    "policy_id": "integer"      // 扫描策略ID
}
```

### 响应

成功响应 (201):
```json
{
    "message": "Scan jobs created successfully",
    "jobs": [
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

错误响应 (400/500):
```json
{
    "error": "string"  // 错误信息
}
```

### 说明

- 需要指定有效的子网ID和策略ID
- 策略必须属于当前用户
- 子网必须属于当前用户
- 会为每个子网创建单独的任务

## 获取任务状态

获取指定任务的详细状态。

### 请求

```http
GET /api/v1/task/{job_id}
Authorization: Bearer <token>
```

### 响应

成功响应 (200):
```json
{
    "job_id": "string",
    "status": {
        "status": "string",         // 任务状态
        "progress": "integer",      // 进度百分比
        "machines_found": "integer", // 发现的机器数量
        "error": "string"           // 错误信息
    },
    "job": {
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
}
```

错误响应 (404/500):
```json
{
    "error": "string"  // 错误信息
}
```

### 说明

- 只能查看自己的任务
- 返回实时任务状态和进度
- 包含任务的基本信息

## 取消任务

取消正在运行的扫描任务。

### 请求

```http
POST /api/v1/task/{job_id}/cancel
Authorization: Bearer <token>
```

### 响应

成功响应 (200):
```json
{
    "message": "Job cancelled successfully"
}
```

错误响应 (400/404/500):
```json
{
    "error": "string"  // 错误信息
}
```

### 说明

- 只能取消自己的任务
- 只能取消待处理或运行中的任务
- 取消后会更新任务状态和结束时间

## 获取任务结果

获取指定任务的扫描结果。

### 请求

```http
GET /api/v1/task/{job_id}/results
Authorization: Bearer <token>
```

### 响应

成功响应 (200):
```json
[
    {
        "id": "integer",
        "job_id": "integer",
        "ip_address": "string",
        "port": "integer",
        "protocol": "string",
        "service": "string",
        "version": "string",
        "os_info": "string",
        "status": "string",
        "banner": "string",
        "raw_data": "string",
        "created_at": "string",
        "updated_at": "string"
    }
]
```

错误响应 (403/404):
```json
{
    "error": "string"  // 错误信息
}
```

### 说明

- 只有管理员或任务所有者可以访问结果
- 返回该任务的所有扫描结果
- 结果按创建时间排序 