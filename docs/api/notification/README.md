# 通知系统 API 文档

## 获取通知配置

获取当前用户的通知配置。

### 请求

```http
GET /api/v1/notification/config
Authorization: Bearer <token>
```

### 响应

成功响应 (200):
```json
{
    "email": {
        "enabled": boolean,
        "smtpServer": "string",
        "smtpUsername": "string",
        "smtpFrom": "string"
    },
    "wechat": {
        "enabled": boolean,
        "webhookUrl": "string"
    }
}
```

错误响应 (500):
```json
{
    "error": "string"  // 错误信息
}
```

## 更新通知配置

更新当前用户的通知配置。

### 请求

```http
PUT /api/v1/notification/config
Authorization: Bearer <token>
Content-Type: application/json

{
    "email": {
        "enabled": boolean,
        "smtpServer": "string",
        "smtpUsername": "string",
        "smtpPassword": "string",
        "smtpFrom": "string"
    },
    "wechat": {
        "enabled": boolean,
        "webhookUrl": "string"
    }
}
```

### 响应

成功响应 (200):
```json
{
    "message": "配置更新成功"
}
```

错误响应 (500):
```json
{
    "error": "string"  // 错误信息
}
```

## 测试通知配置

测试通知配置是否有效。

### 请求

```http
POST /api/v1/notification/test
Authorization: Bearer <token>
Content-Type: application/json

{
    "type": "string",  // email 或 wechat
    "config": {
        // 邮件配置
        "smtpServer": "string",
        "smtpUsername": "string",
        "smtpPassword": "string",
        "smtpFrom": "string",
        // 或微信配置
        "webhookUrl": "string"
    }
}
```

### 响应

成功响应 (200):
```json
{
    "message": "测试发送成功"
}
```

错误响应 (400/500):
```json
{
    "error": "string"  // 错误信息
}
```

### 说明

- 邮件测试会发送一封测试邮件到用户邮箱
- 微信测试会发送一条测试消息到配置的 webhook
- 会验证配置的有效性

## 获取通知历史

获取通知历史记录。

### 请求

```http
GET /api/v1/notification/history
Authorization: Bearer <token>

Query Parameters:
- page: integer         // 页码，默认1
- per_page: integer     // 每页记录数，默认10
- type: string         // 通知类型
- status: string       // 通知状态（read/unread）
```

### 响应

成功响应 (200):
```json
{
    "notifications": [
        {
            "id": "string",
            "user_id": "integer",
            "type": "string",
            "title": "string",
            "content": "string",
            "read": boolean,
            "created_at": "string",
            "updated_at": "string"
        }
    ],
    "total": "integer"  // 总记录数
}
```

错误响应 (500):
```json
{
    "error": "string"  // 错误信息
}
```

## 标记通知为已读

标记指定通知为已读。

### 请求

```http
PUT /api/v1/notification/{id}/read
Authorization: Bearer <token>
```

### 响应

成功响应 (200):
```json
{
    "message": "标记已读成功"
}
```

错误响应 (404/500):
```json
{
    "error": "string"  // 错误信息
}
```

## 标记所有通知为已读

标记所有通知为已读。

### 请求

```http
PUT /api/v1/notification/read-all
Authorization: Bearer <token>
```

### 响应

成功响应 (200):
```json
{
    "message": "全部标记已读成功"
}
```

错误响应 (500):
```json
{
    "error": "string"  // 错误信息
}
```

## 删除通知

删除指定的通知。

### 请求

```http
DELETE /api/v1/notification/{id}
Authorization: Bearer <token>
```

### 响应

成功响应 (200):
```json
{
    "message": "删除成功"
}
```

错误响应 (404/500):
```json
{
    "error": "string"  // 错误信息
}
```

## 清空所有通知

清空所有通知。

### 请求

```http
DELETE /api/v1/notification/clear-all
Authorization: Bearer <token>
```

### 响应

成功响应 (200):
```json
{
    "message": "清空成功"
}
```

错误响应 (500):
```json
{
    "error": "string"  // 错误信息
}
```

## 获取未读通知数量

获取当前用户的未读通知数量。

### 请求

```http
GET /api/v1/notification/unread-count
Authorization: Bearer <token>
```

### 响应

成功响应 (200):
```json
{
    "count": "integer"  // 未读通知数量
}
```

错误响应 (500):
```json
{
    "error": "string"  // 错误信息
}
```