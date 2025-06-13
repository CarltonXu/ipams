# 认证 API 文档

## 获取验证码

获取登录所需的验证码图片。

### 请求

```http
GET /api/v1/auth/captcha
```

### 响应

```json
{
    "captchaKey": "string",  // 验证码的唯一标识
    "captchaImage": "string" // Base64 编码的验证码图片
}
```

### 说明

- 验证码有效期为 5 分钟
- 验证码图片为 Base64 编码的 PNG 格式图片
- 验证码不区分大小写

## 用户注册

注册新用户。

### 请求

```http
POST /api/v1/auth/register
Content-Type: application/json

{
    "username": "string",  // 用户名
    "email": "string",     // 电子邮箱
    "password": "string"   // 密码
}
```

### 响应

成功响应 (201):
```json
{
    "id": "integer",
    "username": "string",
    "email": "string",
    "created_at": "string",
    "updated_at": "string"
}
```

错误响应 (400):
```json
{
    "message": "string"  // 错误信息
}
```

### 说明

- 用户名和邮箱必须唯一
- 邮箱格式必须有效
- 所有字段都是必填的

## 用户登录

用户登录并获取访问令牌。

### 请求

```http
POST /api/v1/auth/login
Content-Type: application/json

{
    "username": "string",    // 用户名
    "password": "string",    // 密码
    "captcha": "string",     // 验证码
    "captchaKey": "string"   // 验证码标识
}
```

### 响应

成功响应 (200):
```json
{
    "token": "string",  // JWT 访问令牌
    "user": {
        "id": "integer",
        "username": "string",
        "email": "string",
        "created_at": "string",
        "updated_at": "string"
    }
}
```

错误响应 (401):
```json
{
    "message": "string"  // 错误信息
}
```

### 说明

- 验证码必须与之前获取的验证码匹配
- 验证码不区分大小写
- 登录成功后会记录日志
- 登录失败也会记录日志

## 用户登出

用户登出系统。

### 请求

```http
POST /api/v1/auth/logout
Authorization: Bearer <token>
```

### 响应

成功响应 (200):
```json
{
    "message": "Successfully logged out"
}
```

### 说明

- 需要有效的 JWT 令牌
- 登出后会记录日志

## 刷新令牌

刷新访问令牌。

### 请求

```http
POST /api/v1/auth/refresh
Authorization: Bearer <token>
```

### 响应

成功响应 (200):
```json
{
    "token": "string"  // 新的 JWT 访问令牌
}
```

### 说明

- 需要有效的 JWT 令牌
- 新令牌的有效期与原始令牌相同 