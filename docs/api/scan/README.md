# 网络扫描 API 文档

## 获取扫描结果列表

获取扫描结果列表，支持分页和过滤。

### 请求

```http
GET /api/v1/scan/results
Authorization: Bearer <token>

Query Parameters:
- job_id: string        // 扫描任务ID
- ip_address: string    // IP地址
- open_ports: string    // 开放端口
- service: string       // 服务名称
- page: integer         // 页码，默认1
- per_page: integer     // 每页记录数，默认20
```

### 响应

成功响应 (200):
```json
{
    "total": "integer",      // 总记录数
    "pages": "integer",      // 总页数
    "current_page": "integer", // 当前页码
    "results": [
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
}
```

错误响应 (500):
```json
{
    "error": "string"  // 错误信息
}
```

### 说明

- 只返回当前用户的扫描结果
- 按创建时间倒序排序
- 支持多条件过滤
- 支持分页查询

## 获取扫描结果详情

获取单个扫描结果的详细信息。

### 请求

```http
GET /api/v1/scan/results/{result_id}
Authorization: Bearer <token>
```

### 响应

成功响应 (200):
```json
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
```

错误响应 (404/500):
```json
{
    "error": "string"  // 错误信息
}
```

### 说明

- 只能查看自己的扫描结果
- 不能查看已删除的结果

## 批量创建扫描结果

批量创建扫描结果记录。

### 请求

```http
POST /api/v1/scan/results/batch
Authorization: Bearer <token>
Content-Type: application/json

{
    "job_id": "integer",  // 扫描任务ID
    "results": [
        {
            "ip_address": "string",    // IP地址
            "port": "integer",         // 端口号
            "protocol": "string",      // 协议
            "service": "string",       // 服务名称
            "version": "string",       // 版本信息
            "os_info": "string",       // 操作系统信息
            "status": "string",        // 状态
            "banner": "string",        // 服务横幅
            "raw_data": "string"       // 原始数据
        }
    ]
}
```

### 响应

成功响应 (200):
```json
{
    "message": "扫描结果保存成功",
    "count": "integer"  // 保存的记录数
}
```

错误响应 (400/404/500):
```json
{
    "error": "string"  // 错误信息
}
```

### 说明

- 需要指定有效的扫描任务ID
- 任务必须属于当前用户
- 支持批量创建多条记录
- 使用事务确保数据一致性

## 删除扫描结果

删除指定的扫描结果。

### 请求

```http
DELETE /api/v1/scan/results/{result_id}
Authorization: Bearer <token>
```

### 响应

成功响应 (200):
```json
{
    "message": "扫描结果删除成功"
}
```

错误响应 (404/500):
```json
{
    "error": "string"  // 错误信息
}
```

### 说明

- 只能删除自己的扫描结果
- 执行软删除，不会真正从数据库中删除记录
- 记录删除时间
- 使用事务确保数据一致性