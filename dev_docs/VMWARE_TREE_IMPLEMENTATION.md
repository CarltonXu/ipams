# VMware树形结构实现说明

## 架构设计

### 数据模型

```
HostInfo (主机信息表)
├── id (主键)
├── ip_id (关联IP表，外键)
├── parent_host_id (父主机ID，自关联) ← 新增字段
├── host_type (主机类型: physical/vmware/other_virtualization)
├── hostname (主机名)
├── vmware_info (JSON字段，存储VM详细信息)
└── ... 其他字段

关系：
- parent_host_id → HostInfo.id (一对多)
- 一个vCenter可以有多个VM作为子主机
```

### 数据流程

1. **标记主机类型**: 用户在采集前手动标记主机为`vmware`类型
2. **采集vCenter**: 系统调用pyvmomi连接到vCenter
3. **批量采集VM**: 获取所有虚拟机信息
4. **创建子记录**: 为每个VM创建HostInfo子记录
5. **关联关系**: 设置parent_host_id指向vCenter主机
6. **树形展示**: 前端使用Element Plus Table的tree-props功能

### API返回结构

```json
{
  "hosts": [
    {
      "id": "vcenter-host-id",
      "hostname": "vCenter-192.168.1.10",
      "host_type": "vmware",
      "child_hosts": [
        {
          "id": "vm-1-id",
          "hostname": "VM-01",
          "parent_host_id": "vcenter-host-id",
          "vmware_info": {
            "vm_uuid": "vmware-uuid",
            "vm_name": "VM-01",
            "power_state": "poweredOn"
          }
        },
        {
          "id": "vm-2-id",
          "hostname": "VM-02",
          "parent_host_id": "vcenter-host-id",
          "vmware_info": {...}
        }
      ]
    }
  ]
}
```

## 后端实现

### 1. 数据库迁移

```python
# 添加parent_host_id字段
parent_host_id = db.Column(db.String(36), db.ForeignKey('host_infos.id', ondelete='CASCADE'), nullable=True)

# 添加父子关系
parent_host = db.relationship('HostInfo', remote_side=[id], backref='child_hosts')
```

### 2. 采集流程

```python
# collector_manager.py
def collect_single_host():
    # 1. 执行采集
    result = self._execute_collection(host_info, credential)
    
    # 2. 如果是VMware批量采集
    if result['success'] and 'vms' in result['data']:
        # 3. 创建子主机记录
        self._create_vm_child_records(host_info, result['data']['vms'])

def _create_vm_child_records(parent_host, vm_list):
    for vm_info in vm_list:
        # 检查是否已存在（通过vm_uuid匹配）
        existing_child = find_by_uuid(parent_host, vm_uuid)
        
        if existing_child:
            # 更新
            self._update_host_info(existing_child, vm_info)
        else:
            # 创建
            child_host = HostInfo(
                ip_id=parent_host.ip_id,  # 共享父主机IP
                parent_host_id=parent_host.id,
                host_type='vmware'
            )
            self._update_host_info(child_host, vm_info)
```

### 3. API查询

```python
# host.py
def get_hosts():
    # 只查询根主机（parent_host_id IS NULL）
    hosts_query = HostInfo.query.filter_by(
        deleted=False, 
        parent_host_id=None
    )
    
    # 包含子主机
    host_dict = host.to_dict(include_children=True)
```

## 前端实现

### 1. Tree Table

```vue
<el-table
  :data="tableData"
  :tree-props="{children: 'child_hosts', hasChildren: 'hasChildren'}"
>
  <el-table-column type="selection" :selectable="isSelectable" />
  <!-- 子主机不可选 -->
</el-table>

<script>
const isSelectable = (row) => {
  return !row.parent_host_id;  // 子主机不可选
};
</script>
```

### 2. 数据显示

- **父节点（vCenter）**: 显示真实IP地址
- **子节点（VM）**: 显示"-"或VM名称
- **层级关系**: 自动展开/折叠

### 3. 操作逻辑

- **批量选择**: 只能选择父节点
- **批量采集**: 只采集父节点
- **批量绑定**: 只绑定父节点
- **查看详情**: 所有节点可查看

## 使用流程

### 完整流程

1. **扫描IP**: 扫描发现vCenter IP
2. **认领IP**: 认领vCenter的IP地址
3. **标记类型**: 在主机列表中将该主机标记为`vmware`类型
4. **创建凭证**: 创建VMware类型凭证
5. **绑定凭证**: 将该凭证绑定到vCenter主机
6. **执行采集**: 点击"采集"按钮
7. **自动处理**: 系统自动：
   - 连接到vCenter
   - 批量采集所有VM信息
   - 创建子主机记录
   - 建立树形关系
8. **查看结果**: 前端自动树形展示

### 页面效果

```
vCenter (192.168.1.10) [vmware] [采集成功]
  ├─ VM-01 [poweredOn] [采集成功]
  ├─ VM-02 [poweredOff] [采集成功]
  └─ VM-03 [poweredOn] [采集成功]

物理主机1 (192.168.1.20) [physical] [采集成功]
物理主机2 (192.168.1.21) [physical] [待采集]
```

## 关键特性

### 1. 数据一致性
- 使用`vm_uuid`匹配，避免重复创建
- 更新时保留历史记录

### 2. IP共享
- 所有VM共享vCenter的IP记录
- 简化数据库设计

### 3. 树形查询
- 自动递归加载子主机
- 支持无限层级（目前2层）

### 4. 批量操作
- 只能操作父节点
- 自动关联子节点

## 限制说明

1. **层级深度**: 当前仅支持2层（vCenter → VM）
2. **IP地址**: VM不显示独立IP（使用父主机IP）
3. **分页**: 树形模式下分页统计基于父节点
4. **搜索**: 搜索时也基于父节点

## 后续优化

1. 支持多层级树形结构
2. 每个VM显示独立IP地址
3. 支持仅搜索VM子节点
4. 支持VM级别的单独操作

## API端点

### 主机列表（支持树形）
```http
GET /api/v1/host
```

**响应**: 返回所有根主机，每个主机包含child_hosts数组

### 单个采集（自动创建子记录）
```http
POST /api/v1/host/<host_id>/collect
```

**VMware类型**: 自动创建所有VM作为子记录

## 数据库查询示例

```sql
-- 查询所有vCenter及其VM
SELECT h1.*, h2.*
FROM host_infos h1
LEFT JOIN host_infos h2 ON h2.parent_host_id = h1.id
WHERE h1.host_type = 'vmware' 
  AND h1.parent_host_id IS NULL;

-- 查询特定vCenter的VM列表
SELECT *
FROM host_infos
WHERE parent_host_id = 'vcenter-host-id';
```

## 注意事项

1. **首次采集**: 会自动创建所有VM记录
2. **重复采集**: 更新已有VM记录，不创建重复
3. **删除vCenter**: CASCADE删除所有子记录
4. **标记类型**: 用户必须手动标记主机类型

