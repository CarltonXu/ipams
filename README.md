# IPAMS (IP Address Management System)

IPAMS 是一个基于 Web 的 IP 地址管理系统，旨在解决手动配置 IP 地址导致的管理难题。通过提供自动扫描网络、IP 地址标注、所有者信息管理等功能，帮助企业高效地维护和管理其内部网络资源。

## 功能特性

### 核心功能

- **用户认证与授权**
  - 用户注册与登录
  - 基于角色的权限控制
  - 用户管理界面

- **IP 地址管理**
  - 子网划分与管理
  - IP 地址分配与追踪
  - 使用状态监控

- **网络扫描**
  - 定时自动扫描
  - 设备发现与识别
  - 扫描结果管理

- **任务调度**
  - 定时任务管理
  - 任务执行监控
  - 历史记录追踪

- **通知系统**
  - 系统通知管理
  - 通知模板配置
  - 通知历史记录

- **系统配置**
  - 基础参数配置
  - 扫描策略设置
  - 通知规则配置

### 技术架构

- **前端**：Vue 3 + TypeScript + Vite + Element Plus
- **后端**：Python 3 + Flask + SQLAlchemy
- **数据库**：MySQL
- **缓存**：Redis
- **部署**：Docker + Docker Compose

---

## 项目结构

```plaintext
IPAMS/
├── frontend/                # 前端代码（Vue 3 项目）
│   ├── src/                # 源代码
│   │   ├── assets/        # 静态资源
│   │   ├── components/    # 通用组件
│   │   ├── composables/   # 组合式函数
│   │   ├── config/        # 配置文件
│   │   ├── i18n/          # 国际化配置
│   │   ├── routers/       # 路由配置
│   │   ├── stores/        # Pinia 状态管理
│   │   ├── types/         # TypeScript 类型定义
│   │   ├── utils/         # 工具函数
│   │   ├── views/         # 页面视图
│   │   ├── App.vue        # 根组件
│   │   ├── main.ts        # 入口文件
│   │   └── style.css      # 全局样式
│   └── public/            # 公共资源
├── backend/               # 后端代码（Flask 项目）
│   ├── app/              # 应用主目录
│   │   ├── api/         # API 路由
│   │   ├── core/        # 核心功能
│   │   │   ├── config/  # 配置管理
│   │   │   ├── errors/  # 错误处理
│   │   │   └── middleware/ # 中间件
│   │   ├── models/      # 数据库模型
│   │   ├── scripts/     # 脚本工具
│   │   ├── services/    # 业务服务
│   │   │   ├── redis/   # Redis 服务
│   │   │   └── scan/    # 网络扫描服务
│   │   └── tasks/       # 定时任务
│   └── uploads/         # 上传文件存储
├── deploy/              # 部署相关配置
│   ├── docker/         # Docker 相关配置
│   │   ├── frontend/   # 前端 Docker 配置
│   │   │   ├── Dockerfile
│   │   │   └── nginx.conf
│   │   └── backend/    # 后端 Docker 配置
│   │       └── Dockerfile
│   ├── docker-compose/ # Docker Compose 配置
│   │   ├── docker-compose.yml        # 基础配置
│   │   ├── docker-compose.dev.yml    # 开发环境
│   │   └── docker-compose.prod.yml   # 生产环境
│   └── scripts/        # 部署脚本
│       ├── init.sh     # 初始化脚本
│       └── backup.sh   # 备份脚本
├── docs/               # 项目文档
│   ├── api/           # API 文档
│   ├── deployment/    # 部署文档
│   └── development/   # 开发文档
└── README.md          # 项目说明文档
```

## 环境要求

### 开发环境

- Node.js 16+
- Python 3.8+
- MySQL 8.0+
- Redis 6.0+

### 生产环境

- Docker 20.10.0+
- Docker Compose 2.0.0+
- 至少 4GB RAM
- 至少 20GB 可用磁盘空间

---

## 快速开始

### 使用 Docker 部署（推荐）

1. 克隆代码库
```bash
git clone https://github.com/CarltonXu/ipams.git
cd ipams
```

2. 配置环境变量
```bash
# 复制并修改环境变量配置
cp backend/.env.example backend/.env
```

3. 选择部署环境

#### 开发环境
```bash
# 启动开发环境
docker-compose -f deploy/docker-compose/docker-compose.dev.yml up -d

# 查看服务状态
docker-compose -f deploy/docker-compose/docker-compose.dev.yml ps

# 查看服务日志
docker-compose -f deploy/docker-compose/docker-compose.dev.yml logs -f
```

#### 生产环境
```bash
# 进入部署脚本目录
cd deploy/scripts

# 添加执行权限
chmod +x init.sh backup.sh

# 初始化环境
./init.sh
```

4. 访问服务
- 前端：http://localhost
- 后端 API：http://localhost:5000

### 维护操作

#### 数据备份
```bash
cd deploy/scripts
./backup.sh
```

#### 服务管理
```bash
# 开发环境
# 重启服务
docker-compose -f deploy/docker-compose/docker-compose.dev.yml restart

# 停止服务
docker-compose -f deploy/docker-compose/docker-compose.dev.yml down

# 生产环境
# 重启服务
docker-compose -f deploy/docker-compose/docker-compose.prod.yml restart

# 停止服务
docker-compose -f deploy/docker-compose/docker-compose.prod.yml down
```

### 手动部署

#### 前端设置
```bash
cd frontend

# 安装依赖
npm install

# 开发模式运行
npm run dev

# 构建生产版本
npm run build
```

#### 后端设置
```bash
cd backend

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 初始化数据库
flask db upgrade

# 创建管理员用户
python create_user.py

# 启动服务
python run.py
```

---

## 项目文档

详细的文档可以在 `docs` 目录下找到：

- `docs/api/` - API 接口文档
- `docs/deployment/` - 部署相关文档
- `docs/development/` - 开发指南

## 开发计划

### 已完成功能
- [x] 用户认证与授权
  - 用户注册登录
  - 角色权限管理
  - 用户管理界面
- [x] IP 地址管理
  - 子网管理
  - IP 地址分配
  - 使用状态追踪
- [x] 网络扫描
  - 定时扫描任务
  - 扫描结果管理
  - 设备发现
- [x] 系统配置
  - 基础配置管理
  - 扫描策略配置
  - 通知设置
- [x] 任务管理
  - 任务创建与调度
  - 任务执行状态
  - 任务历史记录
- [x] 通知系统
  - 通知历史记录
  - 通知配置
  - 通知模板

### 开发中功能
- [ ] 仪表盘
  - 资源使用统计
  - 网络状态概览
  - 告警信息展示
- [ ] 策略管理
  - 访问控制策略
  - 扫描策略
  - 通知策略
- [ ] 高级搜索
  - 多条件组合查询
  - 结果导出
  - 自定义过滤

### 计划功能
- [ ] 数据可视化
  - 网络拓扑图
  - 资源使用趋势
  - 性能监控图表
- [ ] 批量操作
  - 批量导入导出
  - 批量配置下发
  - 模板管理
- [ ] API 文档
  - Swagger 集成
  - 接口测试工具
  - 使用示例

## 贡献指南

欢迎对 IPAMS 项目提出意见或参与开发：

1. Fork 本项目
2. 创建特性分支：`git checkout -b feature/your-feature-name`
3. 提交更改：`git commit -m 'Add some feature'`
4. 推送到分支：`git push origin feature/your-feature-name`
5. 提交 Pull Request

## 联系我们

- 提交 Issue：GitHub Issues
- 邮件：support@yourcompany.com

## 开源协议

IPAMS 遵循 Apache License 2 开源协议。
