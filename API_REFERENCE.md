# IPAMS 凭证和主机信息管理 API 参考

## 凭证管理API

### 1. 获取凭证列表
```http
GET /api/v1/credential
```

**响应示例**:
```json
{
  "credentials": [
    {
      "id": "...",
      "name": "Production Linux",
      "credential_type": "linux",
      "username": "***",
      "is_default": false,
      "created_at": "2025-11-03T10:00:00Z"
    }
  ]
}
```

### 2. 获取凭证详情（含密码）
```http
GET /api/v1/credential/<id>/detail
```

**响应示例**:
```json
{
  "credential": {
    "id": "...",
    "name": "Production Linux",
    "username_plain": "root",
    "password_plain": "password123",
    "private_key_plain": null
  }
}
```

### 3. 查看凭证绑定的主机
```http
GET /api/v1/credential/<id>/bindings
```

**响应示例**:
```json
{
  "credential_id": "...",
  "credential_name": "Production Linux",
  "total": 5,
  "hosts": [
    {
      "binding_id": "...",
      "host": {
        "id": "...",
        "ip": { "ip_address": "192.168.1.10" },
        "hostname": "server1"
      },
      "bound_at": "2025-11-03T10:00:00Z"
    }
  ]
}
```

### 4. 批量绑定主机到凭证
```http
POST /api/v1/credential/<id>/batch-bind
Content-Type: application/json

{
  "host_ids": ["host1", "host2", "host3"]
}
```

**响应示例**:
```json
{
  "message": "Batch bind completed: 3 bound, 0 skipped",
  "bound_count": 3,
  "skipped_count": 0
}
```

### 5. 批量解绑主机
```http
POST /api/v1/credential/<id>/batch-unbind
Content-Type: application/json

{
  "host_ids": ["host1", "host2"]
}
```

### 6. 测试连接
```http
POST /api/v1/credential/<id>/test
Content-Type: application/json

{
  "host_ip": "192.168.1.10"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "SSH connection successful"
}
```

## 主机管理API

### 1. 获取主机列表
```http
GET /api/v1/host?page=1&page_size=20&host_type=physical&collection_status=success
```

**查询参数**:
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认20）
- `host_type`: 主机类型（physical/vmware/other_virtualization/all）
- `collection_status`: 采集状态（pending/collecting/success/failed/all）
- `query`: 搜索关键词（主机名/IP地址）

### 2. 单个采集
```http
POST /api/v1/host/<host_id>/collect
Content-Type: application/json

{
  "credential_id": "cred123"
}

# 或使用自定义凭证
{
  "username": "root",
  "password": "password123",
  "credential_type": "linux",
  "port": 2222
}
```

### 3. 批量采集
```http
POST /api/v1/host/batch-collect
Content-Type: application/json

{
  "host_ids": ["host1", "host2", "host3"]
}
```

**响应示例**:
```json
{
  "message": "Batch collection started",
  "task_id": "task-123"
}
```

### 4. 批量绑定凭证
```http
POST /api/v1/host/batch-bind
Content-Type: application/json

{
  "host_ids": ["host1", "host2"],
  "credential_id": "cred123"
}
```

### 5. 批量解绑凭证
```http
POST /api/v1/host/batch-unbind
Content-Type: application/json

{
  "host_ids": ["host1", "host2"],
  "credential_id": "cred123"
}
```

### 6. 导出数据
```http
POST /api/v1/host/export
Content-Type: application/json

{
  "host_ids": ["host1", "host2"],
  "template": "detailed"
}

# 或自定义字段
{
  "host_ids": ["host1", "host2"],
  "fields": [
    "ip.ip_address",
    "hostname",
    "os_name",
    "cpu_cores",
    "memory_total"
  ]
}
```

**响应**: 文件下载

## 认证

所有API请求需要携带JWT Token:

```http
Authorization: Bearer <your-jwt-token>
```

## 错误响应

```json
{
  "error": "错误信息描述"
}
```

**常见HTTP状态码**:
- `200`: 成功
- `201`: 创建成功
- `400`: 请求错误
- `401`: 未认证
- `403`: 权限不足
- `404`: 资源不存在
- `500`: 服务器错误

## 完整示例

### 完整的采集流程

```bash
# 1. 创建凭证
curl -X POST http://localhost:5000/api/v1/credential \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Production Linux",
    "credential_type": "linux",
    "username": "root",
    "password": "password123",
    "is_default": true
  }'

# 2. 批量绑定主机
curl -X POST http://localhost:5000/api/v1/host/batch-bind \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "host_ids": ["host1", "host2"],
    "credential_id": "credential_id_from_step1"
  }'

# 3. 批量采集
curl -X POST http://localhost:5000/api/v1/host/batch-collect \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "host_ids": ["host1", "host2"]
  }'

# 4. 查看采集结果
curl http://localhost:5000/api/v1/host/host1 \
  -H "Authorization: Bearer $TOKEN"

# 5. 导出数据
curl -X POST http://localhost:5000/api/v1/host/export \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "host_ids": ["host1", "host2"],
    "template": "detailed"
  }' \
  --output hosts.xlsx
```

## 注意事项

1. 所有密码都经过AES加密存储
2. 凭证详情API返回的是解密后的明文
3. 批量操作支持最多100个主机
4. 采集任务异步执行，需要轮询查看状态
5. 导出文件24小时后自动清理

