# 用户管理 API 文档

## 添加用户

管理员添加新用户。

### 请求

```http
POST /api/v1/user
Authorization: Bearer <token>
Content-Type: application/json

{
    "username": "string",    // 用户名
    "email": "string",       // 电子邮箱
    "password": "string",    // 密码
    "is_admin": boolean      // 是否为管理员
}
```

### 响应

成功响应 (201):
```json
{
    "message": "User added successfully",
    "user": {
        "id": "integer",
        "username": "string",
        "email": "string",
        "is_admin": boolean,
        "avatar": "string",
        "created_at": "string",
        "updated_at": "string"
    }
}
```

错误响应 (400):
```json
{
    "error": "string"  // 错误信息
}
```

### 说明

- 需要管理员权限
- 用户名和邮箱必须唯一
- 邮箱格式必须有效
- 所有字段都是必填的

## 上传头像

上传用户头像。

### 请求

```http
POST /api/v1/user/avatar
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <file>  // 图片文件
```

### 响应

成功响应 (200):
```json
{
    "message": "Avatar uploaded successfully",
    "url": "string"  // 头像URL
}
```

错误响应 (400/500):
```json
{
    "error": "string"  // 错误信息
}
```

### 说明

- 支持的文件格式：PNG、JPG、JPEG、GIF
- 文件大小限制：10MB
- 头像URL格式：/uploads/avatars/{uuid}.{ext}

## 删除用户

删除指定用户。

### 请求

```http
DELETE /api/v1/user/{user_id}
Authorization: Bearer <token>
```

### 响应

成功响应 (200):
```json
{
    "message": "User {user_id} deleted successfully"
}
```

错误响应 (403/404):
```json
{
    "error": "string"  // 错误信息
}
```

### 说明

- 需要管理员权限
- 执行软删除，不会真正从数据库中删除记录

## 获取用户列表

获取用户列表，支持分页、搜索和排序。

### 请求

```http
GET /api/v1/user
Authorization: Bearer <token>

Query Parameters:
- page: integer          // 页码，默认1
- page_size: integer     // 每页记录数，默认10
- query: string          // 搜索关键词
- column: string         // 搜索字段（username/email/id/is_admin/wechat_id）
- is_admin: boolean      // 按管理员状态筛选
- sort_by: string        // 排序字段
- sort_order: string     // 排序方向（asc/desc）
- no_pagination: boolean // 是否不分页
```

### 响应

成功响应 (200):
```json
{
    "users": [
        {
            "id": "integer",
            "username": "string",
            "email": "string",
            "is_admin": boolean,
            "avatar": "string",
            "created_at": "string",
            "updated_at": "string"
        }
    ],
    "total": "integer"  // 总记录数
}
```

### 说明

- 支持多字段搜索
- 支持多字段排序
- 可选择是否分页

## 获取当前用户信息

获取当前登录用户的信息。

### 请求

```http
GET /api/v1/user/me
Authorization: Bearer <token>
```

### 响应

成功响应 (200):
```json
{
    "id": "integer",
    "username": "string",
    "email": "string",
    "is_admin": boolean,
    "avatar": "string",
    "created_at": "string",
    "updated_at": "string"
}
```

## 修改密码

修改当前用户的密码。

### 请求

```http
POST /api/v1/user/change-password
Authorization: Bearer <token>
Content-Type: application/json

{
    "old_password": "string",  // 旧密码
    "new_password": "string"   // 新密码
}
```

### 响应

成功响应 (200):
```json
{
    "message": "Password changed successfully"
}
```

错误响应 (400):
```json
{
    "error": "string"  // 错误信息
}
```

## 更新用户信息

更新指定用户的信息。

### 请求

```http
PUT /api/v1/user/{user_id}
Authorization: Bearer <token>
Content-Type: application/json

{
    "username": "string",    // 用户名
    "email": "string",       // 电子邮箱
    "is_admin": boolean,     // 是否为管理员
    "wechat_id": "string"    // 微信ID
}
```

### 响应

成功响应 (200):
```json
{
    "message": "User updated successfully",
    "user": {
        "id": "integer",
        "username": "string",
        "email": "string",
        "is_admin": boolean,
        "avatar": "string",
        "wechat_id": "string",
        "created_at": "string",
        "updated_at": "string"
    }
}
```

错误响应 (400/403/404):
```json
{
    "error": "string"  // 错误信息
}
```

### 说明

- 需要管理员权限
- 用户名和邮箱必须唯一
- 邮箱格式必须有效

## 批量删除用户

批量删除多个用户。

### 请求

```http
POST /api/v1/user/batch-delete
Authorization: Bearer <token>
Content-Type: application/json

{
    "user_ids": ["string"]  // 用户ID列表
}
```

### 响应

成功响应 (200):
```json
{
    "message": "Users deleted successfully",
    "deleted_count": "integer"  // 成功删除的用户数量
}
```

错误响应 (400/403):
```json
{
    "error": "string"  // 错误信息
}
```

### 说明

- 需要管理员权限
- 执行软删除
- 返回成功删除的用户数量 