# IPAMS 更新日志

## [Unreleased] - 2025-11-03

### 🎉 新增功能

#### 凭证管理
- ✨ 凭证详情查看：显示解密后的用户名密码
- ✨ 查看绑定主机：显示凭证关联的所有主机
- ✨ 连接测试：支持指定主机IP测试SSH/WinRM连接
- ✨ 批量绑定主机：从凭证侧批量绑定主机
- ✨ 批量解绑主机：从凭证侧批量解绑主机
- ✨ 一键复制：用户名密码快速复制

#### 主机信息管理
- ✨ 自动创建HostInfo：认领IP后自动创建记录
- ✨ 批量绑定凭证：从主机侧批量绑定凭证
- ✨ 批量解绑凭证：从主机侧批量解绑凭证
- ✨ 显示绑定信息：主机列表自动显示绑定凭证
- ✨ 自定义凭证采集：支持临时凭证和自定义端口
- ✨ 树形数据模型：支持VMware父子关系

#### VMware支持
- ✨ 批量采集所有虚拟机
- ✨ 树形数据存储
- ✨ vCenter管理支持

#### 数据导出
- ✨ Excel导出功能
- ✨ 预设导出模板
- ✨ 自定义字段选择

### 🔧 改进

- 🔧 Ansible playbook优化：使用combine filter避免数据覆盖
- 🔧 批量操作性能优化：并发控制和错误处理
- 🔧 数据库查询优化：批量加载关联数据

### 🐛 Bug修复

- 🐛 修复Ansible采集时使用Python API而非shell命令
- 🐛 修复winrm导入错误：改用socket检测
- 🐛 修复凭证密码加密缺失问题

### 📚 文档

- 📚 添加QUICK_START.md快速开始指南
- 📚 添加USAGE_GUIDE.md使用指南
- 📚 添加FEATURE_SUMMARY.md功能总结
- 📚 添加PROGRESS_SUMMARY.md实现进度
- 📚 更新README.md API端点说明

### 🔄 技术更新

- ⬆️ 新增依赖：ansible==9.8.0
- ⬆️ 新增依赖：ansible-runner==2.3.4
- ⬆️ 新增依赖：pyvmomi==8.0.1.0.2
- ⬆️ 新增依赖：openpyxl==3.1.2
- ⬆️ 新增依赖：paramiko==3.4.0

### 🎯 数据库变更

- ➕ 新增字段：HostInfo.parent_host_id
- ➕ 新增关系：HostInfo.parent_host / child_hosts
- ✅ 数据库迁移文件已创建

### ⚠️ 已知问题

- VMware树形展示前端UI待实现
- VMware批量采集子记录创建流程待完善
- 大量数据场景性能测试待补充

### 🔜 计划中

- 前端批量操作对话框UI实现
- Element Plus Tree Table组件集成
- 自动化测试覆盖
- API Swagger文档生成

---

**开发者**: AI Assistant  
**完成日期**: 2025-11-03  
**版本**: v1.1.0-beta

