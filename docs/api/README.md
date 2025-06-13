# IPAMS API 文档

## 目录

1. [认证接口](./auth/README.md)
   - 用户注册
   - 用户登录
   - 令牌刷新

2. [用户管理](./user/README.md)
   - 用户列表
   - 用户创建
   - 用户更新
   - 用户删除

3. [IP 地址管理](./ip/README.md)
   - IP 地址列表
   - IP 地址分配
   - IP 地址更新
   - IP 地址删除

4. [子网管理](./subnet/README.md)
   - 子网列表
   - 子网创建
   - 子网更新
   - 子网删除

5. [网络扫描](./scan/README.md)
   - 扫描任务
   - 扫描结果
   - 设备发现

6. [任务管理](./task/README.md)
   - 任务列表
   - 任务创建
   - 任务状态
   - 任务历史

7. [通知系统](./notification/README.md)
   - 通知列表
   - 通知配置
   - 通知模板

8. [系统配置](./config/README.md)
   - 基础配置
   - 扫描配置
   - 系统参数

9. [策略管理](./policy/README.md)
   - 访问策略
   - 扫描策略
   - 通知策略

10. [仪表盘](./dashboard/README.md)
    - 资源统计
    - 状态概览
    - 告警信息

## API 规范

### 基础 URL
```
http://localhost:5000/api/v1
```

### 认证方式
所有 API 请求需要在 Header 中携带 JWT Token：
```
Authorization: Bearer <token>
```

### 响应格式
```json
{
    "code": 200,
    "message": "success",
    "data": {}
}
```

### 错误码
- 200: 成功
- 400: 请求参数错误
- 401: 未认证
- 403: 无权限
- 404: 资源不存在
- 500: 服务器错误 