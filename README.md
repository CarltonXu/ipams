# IPAMS (IP Address Management System)

IPAMS 是一个基于 Web 的 IP 地址管理系统，旨在解决手动配置 IP 地址导致的管理难题。通过提供自动扫描网络、IP 地址标注、所有者信息管理等功能，帮助企业高效地维护和管理其内部网络资源。

## 功能特性

### 核心功能
- **网络扫描**：定期扫描网络，发现新设备和未使用的 IP 地址。
- **IP 地址标注**：用户可以标注 IP 地址的用途及设备信息。
- **所有者管理**：允许用户认领 IP 地址并关联设备用途。
- **权限控制**：支持普通用户和管理员角色的分离，确保数据安全。

### 技术架构
- **前端**：Vue 3 + Element Plus
- **后端**：Python 3 + Flask
- **数据库**：MySQL

---

## 项目结构

```plaintext
IPAMS/
├── frontend/         # 前端代码（Vue 3 项目）
│   ├── src/
│   │   ├── components/   # 复用组件
│   │   ├── views/        # 页面视图
│   │   ├── stores/       # Pinia 状态管理
│   │   └── utils/        # 工具函数和全局设置
├── backend/          # 后端代码（Flask 项目）
│   ├── app/
│   │   ├── models/       # 数据库模型
│   │   ├── routes/       # 路由定义
│   │   ├── services/     # 核心业务逻辑
│   │   └── utils/        # 工具模块
│   ├── config.py         # 配置文件
│   └── app.py            # 项目入口
├── database/         # 数据库初始化脚本和迁移文件
└── README.md         # 项目说明文档
```

## 环境要求
- 前端
  - Node.js 16+
  - Yarn

- 后端
  - Python 3.8+
  - Flask 2.0+
  - MySQL 8.0+
- 系统
  - Linux/Mac/Windows

---

## 安装与运行

### 1. 克隆代码库

```
git clone https://github.com/your-username/ipams.git
cd ipams
```

### 2. 启动前端

```
cd ipams
npm install
npm run serve
```

前端服务将在 http://localhost:8080 运行。

### 3. 启动后端

- 创建虚拟环境

```
cd backend
python3 -m venv venv
source venv/bin/activate   # Windows 用户执行 venv\Scripts\activate
```

- 安装依赖

```
pip install -r requirements.txt
```

- 初始化数据库

确保 MySQL 服务已启动，并更新 config.py 中的数据库配置：

```
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://username:password@localhost/ipams"
```

然后运行：

```
flask db init
flask db migrate -m "initial database."
flask db upgrade
```

- 启动服务

```
python app.py
```

后端服务将在 http://localhost:5000 运行。

---

## 使用指南

1. 打开浏览器访问 http://localhost:8080。
2. 登录系统：
 - 管理员账户：admin / password（首次登录后请修改密码）。
 - 普通用户可通过管理员创建账户。

3. 开始添加、标注和管理 IP 地址资源。

---

## 开发计划
- [x] IP 地址扫描功能
- [x] IP 地址认领和标注
- [x] 用户权限管理
- [] 高级搜索和过滤功能
- [] 支持导入/导出 IP 地址数据
- [] 网络流量监控和可视化

## 贡献指南
欢迎对 IPAMS 项目提出意见或参与开发：

1. Fork 本项目
2. 提交 Pull Request 前，请确保代码符合以下要求：
 - 代码通过 Lint 检查。
 - 包含充分的单元测试。

---

## 联系我们
如果在使用中遇到问题，欢迎通过以下方式联系我们：

 - 邮箱：support@yourcompany.com
 - 提交 Issue：GitHub Issues

---

## 开源协议
IPAMS 遵循 Apache License 2 开源协议。