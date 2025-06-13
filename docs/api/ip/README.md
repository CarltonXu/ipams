# IP 地址管理 API 文档

## 获取 IP 列表

获取 IP 地址列表，支持分页、搜索和排序。

### 请求

```http
GET /api/v1/ip
Authorization: Bearer <token>

Query Parameters:
- page: integer          // 页码
- page_size: integer     // 每页记录数
- query: string          // 搜索关键词
- column: string         // 搜索字段（ip_address/assigned_user.username/device_type/device_name/manufacturer/model/os_type/purpose）
- status: string         // 状态筛选（all/mine/active/inactive）
- sort_by: string        // 排序字段
- sort_order: string     // 排序方向（asc/desc）
```

### 响应

成功响应 (200):
```json
{
    "ips": [
        {
            "id": "integer",
            "ip_address": "string",
            "assigned_user": {
                "id": "integer",
                "username": "string"
            },
            "device_name": "string",
            "device_type": "string",
            "manufacturer": "string",
            "model": "string",
            "os_type": "string",
            "purpose": "string",
            "status": "string",
            "created_at": "string",
            "updated_at": "string"
        }
    ],
    "total": "integer",      // 总记录数
    "pages": "integer",      // 总页数
    "page_size": "integer",  // 每页记录数
    "current_page": "integer" // 当前页码
}
```

错误响应 (500):
```json
{
    "error": "string"  // 错误信息
}
```

### 说明

- 支持多字段搜索
- 支持多字段排序
- 支持按状态筛选
- 支持分页查询

## 认领 IP 地址

认领或分配 IP 地址。

### 请求

```http
POST /api/v1/ip/{ip_id}/claim
Authorization: Bearer <token>
Content-Type: application/json

{
    "assigned_user_id": "string",  // 可选，管理员分配用户时使用
    "device_name": "string",       // 设备名称
    "device_type": "string",       // 设备类型
    "manufacturer": "string",      // 制造商
    "model": "string",            // 型号
    "purpose": "string"           // 用途
}
```

### 响应

成功响应 (200):
```json
{
    "id": "integer",
    "ip_address": "string",
    "assigned_user": {
        "id": "integer",
        "username": "string"
    },
    "device_name": "string",
    "device_type": "string",
    "manufacturer": "string",
    "model": "string",
    "os_type": "string",
    "purpose": "string",
    "status": "string",
    "created_at": "string",
    "updated_at": "string"
}
```

错误响应 (404):
```json
{
    "error": "string"  // 错误信息
}
```

### 说明

- 管理员可以指定分配用户
- 普通用户只能认领给自己
- 认领后状态自动设置为 active
- 会发送通知给相关用户

## 更新 IP 地址信息

更新 IP 地址的详细信息。

### 请求

```http
POST /api/v1/ip/{ip_id}
Authorization: Bearer <token>
Content-Type: application/json

{
    "assigned_user_id": "string",  // 可选，分配用户
    "device_name": "string",       // 设备名称
    "device_type": "string",       // 设备类型
    "os_type": "string",          // 操作系统类型
    "manufacturer": "string",      // 制造商
    "model": "string",            // 型号
    "purpose": "string"           // 用途
}
```

### 响应

成功响应 (200):
```json
{
    "id": "integer",
    "ip_address": "string",
    "assigned_user": {
        "id": "integer",
        "username": "string"
    },
    "device_name": "string",
    "device_type": "string",
    "manufacturer": "string",
    "model": "string",
    "os_type": "string",
    "purpose": "string",
    "status": "string",
    "created_at": "string",
    "updated_at": "string"
}
```

错误响应 (400/403/404):
```json
{
    "error": "string"  // 错误信息
}
```

### 说明

- 普通用户只能更新分配给自己的 IP
- 管理员可以更新任何 IP
- 更新后状态自动设置为 active
- 会记录更新日志 