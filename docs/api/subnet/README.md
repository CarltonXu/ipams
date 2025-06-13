# 子网管理 API 文档

## 获取子网列表

获取当前用户的所有扫描子网。

### 请求

```http
GET /api/v1/subnet
Authorization: Bearer <token>
```

### 响应

成功响应 (200):
```json
[
    {
        "id": "integer",
        "user_id": "integer",
        "name": "string",     // 子网名称
        "subnet": "string",   // 子网地址
        "created_at": "string",
        "updated_at": "string"
    }
]
```

### 说明

- 只返回当前用户的子网
- 不返回已删除的子网

## 添加子网

添加新的扫描子网。

### 请求

```http
POST /api/v1/subnet
Authorization: Bearer <token>
Content-Type: application/json

{
    "name": "string",    // 子网名称
    "subnet": "string"   // 子网地址
}
```

### 响应

成功响应 (201):
```json
{
    "message": "Subnet added successfully",
    "subnet": {
        "id": "integer",
        "user_id": "integer",
        "name": "string",
        "subnet": "string",
        "created_at": "string",
        "updated_at": "string"
    }
}
```

### 说明

- 子网名称和地址都是必填的
- 子网地址必须是有效的 CIDR 格式

## 更新子网

更新现有子网的信息。

### 请求

```http
PUT /api/v1/subnet/{subnet_id}
Authorization: Bearer <token>
Content-Type: application/json

{
    "name": "string",    // 子网名称
    "subnet": "string"   // 子网地址
}
```

### 响应

成功响应 (200):
```json
{
    "message": "Subnet updated successfully",
    "subnet": {
        "id": "integer",
        "user_id": "integer",
        "name": "string",
        "subnet": "string",
        "created_at": "string",
        "updated_at": "string"
    }
}
```

错误响应 (404):
```json
{
    "error": "Subnet not found"
}
```

### 说明

- 只能更新自己的子网
- 不能更新已删除的子网
- 所有字段都是可选的，未提供的字段保持原值

## 删除子网

软删除指定的子网。

### 请求

```http
DELETE /api/v1/subnet/{subnet_id}
Authorization: Bearer <token>
```

### 响应

成功响应 (200):
```json
{
    "message": "Subnet deleted successfully"
}
```

错误响应 (404):
```json
{
    "error": "Subnet not found"
}
```

### 说明

- 只能删除自己的子网
- 执行软删除，不会真正从数据库中删除记录
- 删除后的子网不会在列表中显示 