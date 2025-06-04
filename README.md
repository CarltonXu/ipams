# IPAMS (IP Address Management System)

IPAMS 是一个基于 Web 的 IP 地址管理系统，旨在解决手动配置 IP 地址导致的管理难题。通过提供自动扫描网络、IP 地址标注、所有者信息管理等功能，帮助企业高效地维护和管理其内部网络资源。

## 功能特性

### 核心功能

- **网络扫描**：定期扫描网络，发现新设备和未使用的 IP 地址
- **IP 地址标注**：用户可以标注 IP 地址的用途及设备信息
- **所有者管理**：允许用户认领 IP 地址并关联设备用途
- **权限控制**：支持普通用户和管理员角色的分离，确保数据安全
- **多语言支持**：内置中英文界面，方便不同语言用户使用

### 技术架构

- **前端**：Vue 3 + TypeScript + Vite + Element Plus
- **后端**：Python 3 + Flask + SQLAlchemy
- **数据库**：MySQL
- **任务队列**：Celery（用于异步网络扫描任务）

---

## 项目结构

```plaintext
IPAMS/
├── src/                # 前端代码（Vue 3 项目）
│   ├── assets/         # 静态资源
│   ├── components/     # 复用组件
│   ├── composables/    # 组合式函数
│   ├── i18n/           # 国际化配置
│   ├── locales/        # 语言文件
│   ├── routers/        # 路由配置
│   ├── stores/         # Pinia 状态管理
│   ├── types/          # TypeScript 类型定义
│   ├── utils/          # 工具函数
│   ├── views/          # 页面视图
│   ├── App.vue         # 根组件
│   ├── main.ts         # 入口文件
│   └── style.css       # 全局样式
├── backend/            # 后端代码（Flask 项目）
│   ├── app/            # 应用主目录
│   │   ├── models/     # 数据库模型
│   │   ├── routes/     # 路由定义
│   │   ├── services/   # 核心业务逻辑
│   │   └── utils/      # 工具模块
│   ├── migrations/     # 数据库迁移文件
│   ├── uploads/        # 上传文件存储
│   ├── .env            # 环境变量配置
│   ├── celery_worker.py # Celery 工作进程
│   ├── create_user.py  # 用户创建脚本
│   ├── requirements.txt # Python 依赖
│   └── run.py          # 应用入口
├── .vscode/            # VS Code 配置
├── .venv/              # Python 虚拟环境
├── node_modules/       # Node.js 依赖
├── .gitignore          # Git 忽略文件
├── index.html          # HTML 入口
├── package.json        # 前端依赖配置
├── tsconfig.json       # TypeScript 配置
├── vite.config.ts      # Vite 配置
└── README.md           # 项目说明文档
```

## 环境要求

- 前端

  - Node.js 16+
  - npm 或 yarn

- 后端

  - Python 3.8+
  - Flask 2.0+
  - MySQL 8.0+
  - Redis 6.0+（用于 Celery 和缓存）

- 系统
  - Linux/Mac/Windows

---

## 安装与运行

### 1. 克隆代码库

```bash
git clone https://github.com/your-username/ipams.git
cd ipams
```

### 2. 前端设置

```bash
# 安装依赖
npm install

# 开发模式运行
npm run dev

# 构建生产版本
npm run build
```

前端服务将在 http://localhost:5173 运行（开发模式）。

### 3. 后端设置

- 创建并激活虚拟环境

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows 用户执行 .venv\Scripts\activate
```

- 安装依赖

```bash
pip install -r requirements.txt
```

- 配置环境变量

复制 `.env.example` 到 `.env` 并修改配置：

```bash
cp .env.example .env
# 编辑 .env 文件，设置数据库连接等信息
```

- 安装并启动 Redis

```bash
# macOS (使用 Homebrew)
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Windows
# 下载 Redis for Windows: https://github.com/microsoftarchive/redis/releases
# 安装并启动 Redis 服务
```

- 初始化数据库

```bash
flask db upgrade
```

- 创建管理员用户

```bash
python create_user.py
```

- 启动服务

```bash
# 启动 Flask 应用
python run.py

# 启动 Celery 工作进程（新终端）
python start_celery.py
```

后端服务默认将在 http://127.0.0.1:5000 运行。

---

## 使用指南

1. 打开浏览器访问 http://localhost:5173（开发模式）
2. 登录系统：

   - 使用管理员账户登录（通过 create_user.py 创建）
   - 普通用户可通过管理员在系统中创建

3. 开始添加、标注和管理 IP 地址资源

---

## 开发计划

- [x] IP 地址扫描功能
- [x] IP 地址认领和标注
- [x] 用户权限管理
- [x] 多语言支持
- [x] 高级搜索和过滤功能
- [ ] 支持导入/导出 IP 地址数据
- [ ] 网络流量监控和可视化
- [ ] API 文档自动生成

## 贡献指南

欢迎对 IPAMS 项目提出意见或参与开发：

1. Fork 本项目
2. 创建特性分支：`git checkout -b feature/your-feature-name`
3. 提交更改：`git commit -m 'Add some feature'`
4. 推送到分支：`git push origin feature/your-feature-name`
5. 提交 Pull Request

提交 Pull Request 前，请确保：

- 代码通过 Lint 检查
- 包含充分的单元测试
- 更新相关文档

---

## 联系我们

如果在使用中遇到问题，欢迎通过以下方式联系我们：

- 提交 Issue：GitHub Issues
- 邮件：support@yourcompany.com

---

## 开源协议

IPAMS 遵循 Apache License 2 开源协议。
