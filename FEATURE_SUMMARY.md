# IPAMS 凭证和主机信息管理功能总结

## 一、功能实现概览

### 核心功能 ✅
1. **凭证管理** - 完整的CRUD操作，支持Linux/Windows/VMware三种类型
2. **主机信息采集** - 使用Ansible收集Linux/Windows主机信息
3. **VMware支持** - 使用pyvmomi采集虚拟机信息
4. **凭证绑定** - 多对多关系，支持一个主机绑定多个凭证
5. **数据导出** - Excel导出支持模板和自定义字段

### 增强功能 ✅
1. **凭证详情查看** - 查看解密后的用户名、密码、私钥
2. **凭证绑定查询** - 查看凭证绑定的所有主机列表
3. **连接测试** - 支持指定主机IP测试SSH/WinRM连接
4. **一键复制** - 用户名密码一键复制到剪贴板
5. **密码可见性切换** - 显示/隐藏密码
6. **主机自动创建** - 认领IP后自动创建HostInfo记录
7. **批量绑定/解绑** - 凭证和主机双向批量操作
8. **自定义凭证采集** - 支持临时凭证和自定义端口
9. **VMware树形结构** - parent_host_id字段支持父子关系
10. **绑定信息显示** - 主机列表自动加载凭证绑定信息

## 二、后端实现

### 数据库模型
- `Credential` - 凭证模型（加密存储）
- `HostInfo` - 主机详细信息模型（支持树形结构）
- `HostCredentialBinding` - 绑定关系模型（多对多）
- `CollectionTask` - 采集任务模型

**新增字段**:
- `HostInfo.parent_host_id` - 父主机ID，用于VMware树形结构
- `HostInfo.child_hosts` - 子主机关系

### API端点
```
凭证管理:
GET  /api/v1/credential                   # 获取凭证列表
POST /api/v1/credential                   # 创建凭证
GET  /api/v1/credential/<id>              # 获取凭证详情
GET  /api/v1/credential/<id>/detail       # 获取凭证详情（含密码）
GET  /api/v1/credential/<id>/bindings     # 查看绑定主机
POST /api/v1/credential/<id>/batch-bind   # 批量绑定主机
POST /api/v1/credential/<id>/batch-unbind # 批量解绑主机
PUT  /api/v1/credential/<id>              # 更新凭证
DELETE /api/v1/credential/<id>            # 删除凭证
POST /api/v1/credential/<id>/test         # 测试连接（支持host_ip）

主机管理:
GET  /api/v1/host                         # 获取主机列表
GET  /api/v1/host/<id>                    # 获取主机详情
PUT  /api/v1/host/<id>                    # 更新主机信息
POST /api/v1/host/<id>/bind-credential    # 绑定凭证
DELETE /api/v1/host/<id>/unbind-credential # 解绑凭证
POST /api/v1/host/<id>/collect            # 单个采集（支持自定义凭证）
POST /api/v1/host/batch-collect           # 批量采集
POST /api/v1/host/batch-bind              # 批量绑定凭证
POST /api/v1/host/batch-unbind            # 批量解绑凭证
GET  /api/v1/host/<id>/collection-history # 采集历史
POST /api/v1/host/export                  # 导出数据
GET  /api/v1/host/export/templates        # 导出模板
GET  /api/v1/host/export/fields           # 导出字段
```

### 关键服务
1. **encryption.py** - AES加密/解密服务
2. **ansible_collector.py** - Ansible采集器
3. **vmware_collector.py** - VMware采集器
4. **collector_manager.py** - 采集任务管理器（并发控制）
5. **excel_exporter.py** - Excel导出服务

## 三、前端实现

### 页面和组件
1. **CredentialManagement.vue** - 凭证管理主页面
2. **CredentialForm.vue** - 凭证表单组件
3. **HostManagement.vue** - 主机信息管理页面
4. **BindCredentialDialog.vue** - 绑定凭证对话框
5. **ExportDialog.vue** - 导出配置对话框

### 状态管理（Pinia）
1. **credential.ts** - 凭证状态管理
2. **hostInfo.ts** - 主机信息状态管理

### TypeScript类型
1. **credential.ts** - 凭证相关类型
2. **hostInfo.ts** - 主机信息相关类型

### 国际化
- 完整的中英文翻译
- 支持语言切换

## 四、技术栈

### 后端
- Flask + SQLAlchemy
- Ansible (ansible-runner)
- pyvmomi (VMware)
- paramiko (SSH)
- openpyxl (Excel导出)
- cryptography (AES加密)
- PyJWT (认证)

### 前端
- Vue 3 + TypeScript
- Pinia (状态管理)
- Element Plus (UI组件)
- Vue Router (路由)
- Vue I18n (国际化)
- Axios (HTTP请求)

## 五、数据流程

```
┌─────────────┐
│  扫描发现   │
│  主机IP     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  认领IP     │
│  (Claim)    │
└──────┬──────┘
       │ 自动创建HostInfo
       ▼
┌─────────────┐
│  创建凭证   │
│  (Encrypt)  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  绑定凭证   │
│  (Bind)     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  采集信息   │
│  (Collect)  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  查看/导出  │
│  (View/Export)
└─────────────┘
```

## 六、安全特性

1. **凭证加密** - AES对称加密存储用户名/密码/私钥
2. **权限控制** - 每个用户只能管理自己的凭证
3. **软删除** - 所有删除操作都是软删除
4. **HTTPS支持** - 生产环境建议使用HTTPS
5. **认证保护** - 所有API都需要JWT token认证

## 七、部署要求

### 环境依赖
- Python 3.9+
- MySQL 5.7+
- Redis
- Node.js 18+

### Python包
- ansible==9.8.0
- ansible-runner==2.3.4
- pyvmomi==8.0.1.0.2
- paramiko==3.4.0
- openpyxl==3.1.2
- cryptography==43.0.3

### 配置要求
```bash
# .env 文件必需配置
ENCRYPTION_KEY=your-generated-key-here  # AES加密密钥
ANSIBLE_HOST_KEY_CHECKING=False
ANSIBLE_TIMEOUT=30
COLLECTION_MAX_CONCURRENT=5
COLLECTION_TIMEOUT=300
EXPORT_FILE_EXPIRY=3600
```

## 八、使用技巧

### 凭证管理
- 为不同环境创建不同的凭证模板
- 使用"测试连接"验证凭证正确性
- 定期查看"绑定列表"清理无用绑定

### 主机采集
- 先小批量测试，确认无误后批量采集
- 查看采集历史诊断失败原因
- 使用导出功能备份重要数据

### 故障排查
- Linux: 检查SSH服务和防火墙
- Windows: 检查WinRM服务状态
- 查看采集错误日志定位问题

## 九、待优化项

1. 支持更多操作系统类型
2. 采集计划任务（定时自动采集）
3. 凭证定期轮换提醒
4. 采集结果对比分析
5. WebSocket实时推送采集状态

## 十、技术支持

详细使用文档：`QUICK_START.md`
API文档：待补充Swagger文档

