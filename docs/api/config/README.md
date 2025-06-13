# 系统配置 API 文档

## 获取系统配置

获取所有系统配置。

### 请求

```http
GET /api/v1/config
Authorization: Bearer <token>
```

### 响应

成功响应 (200):
```json
{
    "configs": [
        {
            "key": "string",         // 配置键
            "value": "string",       // 配置值
            "description": "string", // 配置描述
            "is_public": boolean,    // 是否公开
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

- 管理员可以看到所有配置
- 普通用户只能看到公开配置

## 获取指定配置

获取指定配置项的详细信息。

### 请求

```http
GET /api/v1/config/{key}
Authorization: Bearer <token>
```

### 响应

成功响应 (200):
```json
{
    "key": "string",         // 配置键
    "value": "string",       // 配置值
    "description": "string", // 配置描述
    "is_public": boolean,    // 是否公开
    "created_at": "string",
    "updated_at": "string"
}
```

错误响应 (403/404/500):
```json
{
    "error": "string"  // 错误信息
}
```

### 说明

- 管理员可以查看任何配置
- 普通用户只能查看公开配置

## 创建配置

创建新的系统配置项。

### 请求

```http
POST /api/v1/config
Authorization: Bearer <token>
Content-Type: application/json

{
    "key": "string",         // 配置键
    "value": "string",       // 配置值
    "description": "string", // 配置描述
    "is_public": boolean     // 是否公开
}
```

### 响应

成功响应 (201):
```json
{
    "key": "string",         // 配置键
    "value": "string",       // 配置值
    "description": "string", // 配置描述
    "is_public": boolean,    // 是否公开
    "created_at": "string",
    "updated_at": "string"
}
```

错误响应 (400/500):
```json
{
    "error": "string"  // 错误信息
}
```

### 说明

- 需要管理员权限
- 配置键必须唯一
- 配置键、值和描述是必填的
- 会记录操作日志

## 更新配置

更新现有配置项。

### 请求

```http
PUT /api/v1/config/{key}
Authorization: Bearer <token>
Content-Type: application/json

{
    "value": "string",       // 配置值
    "description": "string", // 配置描述
    "is_public": boolean     // 是否公开
}
```

### 响应

成功响应 (200):
```json
{
    "key": "string",         // 配置键
    "value": "string",       // 配置值
    "description": "string", // 配置描述
    "is_public": boolean,    // 是否公开
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

- 需要管理员权限
- 所有字段都是可选的
- 会记录操作日志

## 删除配置

删除指定的配置项。

### 请求

```http
DELETE /api/v1/config/{key}
Authorization: Bearer <token>
```

### 响应

成功响应 (200):
```json
{
    "message": "Configuration deleted successfully"
}
```

错误响应 (404/500):
```json
{
    "error": "string"  // 错误信息
}
```

### 说明

- 需要管理员权限
- 会记录操作日志
- 删除后无法恢复 