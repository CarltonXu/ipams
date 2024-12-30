export default {
  common: {
    success: '操作成功',
    error: '操作失败',
    fetchError: '获取数据失败',
    confirm: '确认',
    warning: '警告',
    cancel: '取消',
    save: '保存',
    delete: '删除',
    edit: '编辑',
    add: '添加',
    search: '搜索',
    reset: '重置',
    loading: '加载中...',
    more: '更多',
    yes: '是',
    no: '否',
    actions: '操作',
  },
  menu: {
    home: '首页',
    ipManagement: '主机管理',
    scanConfig: '配置扫描',
    settings: '系统设置',
    userManagement: '用户管理',
  },
  auth: {
    login: '登录',
    logout: '退出登录',
    register: '注册',
    username: '用户名',
    password: '密码',
    email: '邮箱',
    loginSuccess: '登录成功',
    loginError: '登录失败',
    tokenExpired: '登录已过期，请重新登录',
  },
  user: {
    profile: '个人中心',
    settings: '个人设置',
    account: '账号信息',
    changePassword: '修改密码',
    currentUser: '当前用户',
    management: {
      title: '用户管理',
      subtitle: '管理系统用户及其权限',
      button: {
        add: '添加用户'
      },
      table: {
        columns: {
          uuid: 'UUID',
          username: '用户名',
          email: '邮箱',
          createdAt: '创建时间',
          isAdmin: '管理员',
          actions: '操作'
        },
        noData: '暂无用户数据'
      },
      dialog: {
        title: '用户信息',
        labels: {
          username: '用户名',
          email: '邮箱',
          password: '密码',
          wechatId: '微信 ID',
          isAdmin: '管理员'
        },
        placeholders: {
          username: '请输入用户名',
          email: '请输入邮箱',
          password: '请输入密码',
          wechatId: '请输入微信 ID'
        },
        batchDelete: {
          title: '批量删除 {count} 用户',
          confirm: '确定删除 {count} 用户吗？',
          success: '用户删除成功',
          error: '删除用户失败',
          warning: '这是一个危险操作，请谨慎操作',
          description: '用户仍与IP地址关联，请先收回IP地址，然后删除用户'
        }
      },
      buttons: {
        edit: '编辑',
        delete: '删除',
        save: '保存',
        cancel: '取消',
        add: '添加用户',
        batchDelete: '批量删除 {count} 用户',
        batchDeleteConfirm: '确定删除 {count} 用户吗？'
      },
      messages: {
        deleteConfirm: '确定删除用户 {username} 吗？',
        deleteSuccess: '用户删除成功',
        saveSuccess: '用户保存成功',
        fetchError: '获取用户列表失败',
        saveError: '保存用户失败',
        hasAssociatedIPs: '用户仍与IP地址关联，请先收回IP地址，然后删除用户',
        batchDeleteConfirm: '确定删除 {count} 用户吗？',
        batchDeleteSuccess: '用户删除成功',
        deleteSelfError: '不能删除自己',
      },
      validation: {
        username: '请输入用户名',
        email: {
          required: '请输入邮箱',
          invalid: '请输入有效的邮箱地址'
        },
        password: '请输入密码'
      },
      search: {
        selectColumn: '选择搜索列',
        allColumns: '所有列',
        all: '搜索所有列...',
        specific: '搜索 {column}...',
        adminStatus: '管理员状态',
        allUsers: '所有用户',
        adminOnly: '管理员',
        normalOnly: '普通用户'
      }
    }
  },
  theme: {
    title: '主题设置',
    light: '浅色模式',
    dark: '深色模式',
    system: '跟随系统',
  },
  language: {
    title: '语言设置',
    zh: '中文',
    en: '英文',
  },
  ip: {
    title: 'IP地址管理',
    subtitle: '使用过滤器和搜索功能轻松管理您的IP地址',
    status: {
      all: '所有状态',
      active: '活跃',
      inactive: '未使用',
      unclaimed: '未认领',
      unassigned: '未分配',
      description: {
        active: '此IP当前处于活跃状态',
        inactive: '此IP未在使用',
        unclaimed: '此IP可供认领',
        unassigned: '此IP未分配',
        danger: '未知状态',
        undefined: '未知状态'
      },
    },
    search: {
      title: '搜索IP、设备或用途',
      selectColumn: '选择搜索列',
      allColumns: '所有列',
      all: '搜索所有列...',
      specific: '搜索 {column}...'
    },
    columns: {
      hostUUID: '主机UUID',
      ipAddress: 'IP地址',
      osVersion: '操作系统',
      status: '状态',
      deviceName: '设备名称',
      deviceType: '设备类型',
      architecture: '架构',
      model: '型号',
      owningUser: '所属用户',
      purpose: '用途',
      lastScanned: '最后扫描时间'
    },
    actions: {
      claim: '认领',
      edit: '编辑',
      claimSuccess: '成功认领IP：{ip}',
      updateSuccess: '成功更新IP：{ip}',
      batchClaim: '批量认领',
      batchUpdate: '批量更新',
      batchClaimSuccess: '成功批量认领IP：{ip}',
      batchUpdateSuccess: '成功批量更新IP：{ip}'
    },
    noData: '未找到IP地址',
    dialog: {
      claim: {
        title: '认领IP地址',
        hostUUID: '主机UUID',
        hostIP: '主机IP',
        assignUser: '分配给用户',
        selectUser: '选择用户',
        deviceName: '设备名称',
        deviceNamePlaceholder: '输入设备名称，如(Nginx, Other)',
        osType: '操作系统',
        osTypeTip: '选择设备运行的操作系统(如Linux, Windows, Other)',
        deviceType: '设备类型',
        deviceTypeTip: '指定使用此IP的设备类型(如Router, Switch, Server)',
        manufacturer: '制造商',
        manufacturerTip: '指定设备部署位置(如VMware, OpenStack, Physical)',
        model: '型号',
        modelTip: '提供设备型号(如PowerEdge R730, DELL R720)',
        purpose: '用途',
        purposePlaceholder: '描述此IP地址的用途',
        confirmClaim: '确认认领',
        confirmUpdate: "确认更新",
        required: '必填',
        success: 'IP认领成功',
        updateSuccess: 'IP认领更新成功',
        error: '认领 IP 失败: {error}',
        deviceNameRequired: '设备名称不能为空',
        purposeRequired: '用途不能为空',
      },
      batchClaim: {
        title: '批量认领IP地址',
        commonConfig: '通用配置',
        applyToAll: '批量设置',
        individualConfig: '单个配置',
        selectIPs: '选择要认领的IP地址',
        confirmClaim: '确认认领',
        success: 'IP批量认领成功',
        error: '批量认领IP失败: {error}',
        validation: '请填写所有必填字段'
      },
      update: {
        title: '更新IP地址',
        success: 'IP更新成功',
        error: '更新IP失败: {error}',
      }
    }
  },
  profile: {
    title: '个人资料',
    changeAvatar: '更换头像',
    editProfile: '编辑资料',
    editDialogTitle: '编辑个人资料',
    wechatPlaceholder: '待补充',
    fields: {
      username: '用户名',
      email: '邮箱',
      wechatId: '微信号',
    },
    buttons: {
      save: '保存',
      cancel: '取消',
    },
    messages: {
      updateSuccess: '个人资料更新成功',
      updateFailed: '更新失败',
      avatarSuccess: '头像更新成功',
      avatarFailed: '头像更新失败',
    }
  },
  scan: {
    title: '扫描配置',
    subtitle: '管理扫描网段和策略配置',
    subnet: {
      title: '添加扫描网段',
      name: '网段名称',
      namePlaceholder: '请输入网段名称',
      range: '网段',
      rangePlaceholder: '请输入扫描网段 (例如: 192.168.0.0/24)',
      add: '添加',
      list: '已添加网段',
      columns: {
        name: '网段名称',
        subnet: '网段',
        createdAt: '创建时间',
        actions: '操作'
      },
      noData: '暂无网段数据',
      delete: '删除'
    },
    policy: {
      title: '扫描策略配置',
      subtitle: '管理您的扫描策略及其配置',
      name: '策略名称',
      namePlaceholder: '请输入策略名称',
      type: '策略类型',
      typeRequired: '请选择策略类型',
      types: {
        everyMinute: '每分钟',
        everyHour: '每小时',
        everyDay: '每天',
        everyWeek: '每周',
        everyMonth: '每月',
        custom: '自定义'
      },
      interval: {
        minute: '间隔N分钟',
        hour: '间隔N小时',
        day: '间隔N天'
      },
      startTime: '开始时间',
      startTimeRequired: '请选择开始时间',
      weekdays: {
        mon: '周一',
        tue: '周二',
        wed: '周三',
        thu: '周四',
        fri: '周五',
        sat: '周六',
        sun: '周日'
      },
      monthDays: '日期',
      monthDaysRequired: '请选择日期',
      lastDay: '月末',
      time: '时间',
      cronExpression: 'Cron 表达式',
      cronPlaceholder: '输入 Cron 表达式',
      add: '添加策略',
      list: '已添加策略',
      save: '保存策略',
      columns: {
        name: '策略名称',
        description: '策略描述',
        createdAt: '创建时间',
        actions: '操作'
      },
      noData: '暂无策略数据',
      show: {
        columns: {
          name: '策略名称',
          description: '策略描述', 
          strategy: '策略执行Cron',
          startTime: '开始时间',
          createdAt: '创建时间',
          subnets: '扫描网段',
          status: {
            title: '状态',
            active: '活跃',
            inactive: '未使用'
          },
          actions: {
            title: '操作',
            enable: '启用',
            disable: '禁用',
            edit: '编辑',
            delete: '删除'
          },
        },
        noData: '暂无策略数据',
        dialog: {
          addTitle: '添加策略',
          editTitle: '编辑策略',
          deleteConfirm: '确定要删除此策略吗？',
          deleteTitle: '删除策略'
        },
        messages: {
          addSuccess: '策略添加成功',
          saveSuccess: '策略保存成功',
          deleteSuccess: '策略删除成功',
          updateSuccess: '策略更新成功'
        }
      },
      description: {
        everyMinute: '每隔 {minutes} 分钟，从 {time} 开始执行',
        everyHour: '每隔 {hours} 小时，从 {time} 开始执行',
        everyDay: '每隔 {days} 天，从 {time} 开始执行',
        everyWeek: '每 {weekdays}，从 {time} 开始执行',
        everyMonth: '每月 {days}，从 {time} 开始执行',
        custom: '自定义执行: {cron}'
      },
      weekDays: {
        0: '周日',
        1: '周一',
        2: '周二',
        3: '周三',
        4: '周四',
        5: '周五',
        6: '周六'
      }
    },
    execution: {
      title: '执行扫描',
      selectSubnet: '选择网段',
      execute: '执行扫描'
    },
    form: {
      interval: {
        minutes: '间隔N分钟',
        hours: '间隔N小时',
        days: '间隔N天',
        selectTime: '请选择时间'
      },
      time: {
        start: '开始时间',
        execution: '开始执行时间',
        select: '选择时间',
        weekly: '每周执行时间',
        monthly: '每月执行时间',
        daily: '每日执行时间'
      },
      cron: {
        label: 'Cron 表达式',
        placeholder: '输入 Cron 表达式'
      },
      validation: {
        invalidSubnet: '请输入有效的网段！',
        subnetNameRequired: '网段名称不能为空!',
        invalidIPFormat: '无效的 IP 地址格式！',
        invalidSubnetFormat: '无效的网段格式，正确格式为：IP/掩码（如：192.168.0.0/24）',
        weeklyConfig: '请完整配置每周执行时间和日期',
        monthlyConfig: '请完整配置每月执行时间和日期',
        cronRequired: '请输入 cron 表达式和开始时间',
        subnetRequired: '请选择要扫描的网段',
        strategyName: '请输入策略名称',
        strategyDescription: '请输入策略描述',
        selectStartTime: '请选择执行时间',
        selectInterval: '请选择周期时间',
      },
      monthDays: {
        last: '月末',
        select: '选择日期'
      },
      cronExpression: {
        label: 'Cron 表达式',
        placeholder: '请输入 Cron 表达式',
        time: '执行时间'
      },
      buttons: {
        add: '添加策略',
        save: '保存配置',
        execute: '执行扫描',
        delete: '删除'
      },
      table: {
        noData: '暂无数据'
      },
      status: {
        loading: '加载中...',
        executing: '正在执行扫描...',
        saving: '正在保存...'
      },
      confirm: {
        save: '确认保存当前配置？',
        execute: '确认执行扫描？',
        delete: '确认删除？'
      },
      tips: {
        weekDays: '请至少选择一个星期',
        monthDays: '请至少选择一个日期',
        customCron: 'Cron表达式格式：分 时 日 月 星期 (*/1 * * * *)'
      },
      types: {
        everyMinute: '每隔N分钟',
        everyHour: '每隔N小时',
        everyDay: '每隔N天',
        everyWeek: '每周',
        everyMonth: '每月',
        custom: '自定义'
      }
    },
    messages: {
      success: {
        addPolicy: '策略添加成功',
        savePolicy: '策略保存成功',
        addSubnet: '网段添加成功',
        deleteSubnet: '网段删除成功',
        deletePolicy: '策略删除成功'
      },
      confirm: {
        deleteSubnet: '确定要删除该网段吗？',
        deletePolicy: '确定要删除该策略吗？'
      }
    },
    validation: {
      subnetName: '请输入网段名称',
      subnetRange: '请输入网段范围',
      selectExecutionTime: '请选择执行时间',
      strategyName: '请输入策略名称',
      strategyDescription: '请输入策略描述',
      noSubnets: '请至少添加一个扫描网段',
      noPolicy: '请至少添加一个扫描策略',
      invalidIPFormat: '请输入有效的IP地址',
      invalidSubnetFormat: '请输入有效的网段格式，正确格式为：IP/掩码（如：192.168.0.0/24）'
    }
  },
  settings: {
    title: '系统设置',
    subtitle: '在这里您可以配置您的系统偏好设置，包括主题、语言等',
    sections: {
      basic: '基本设置',
      interface: '界面设置',
      account: '账户设置'
    },
    form: {
      language: {
        label: '语言',
        placeholder: '选择语言',
        options: {
          zh: '中文',
          en: '英文'
        }
      },
      theme: {
        label: '主题',
        placeholder: '选择主题',
        options: {
          light: '浅色',
          dark: '深色'
        }
      },
      notifications: {
        label: '通知开关',
        on: '开',
        off: '关'
      },
      timeFormat: {
        label: '时间格式',
        placeholder: '选择时间格式',
        options: {
          '12h': '12小时制',
          '24h': '24小时制'
        }
      },
      password: {
        label: '修改密码',
        button: '修改密码',
        dialog: {
          title: '修改密码',
          old: '旧密码',
          new: '新密码',
          confirm: '确认密码'
        }
      }
    },
    validation: {
      language: '请选择语言',
      theme: '请选择主题',
      oldPassword: '请输入旧密码',
      newPassword: '请输入新密码',
      confirmPassword: '请确认新密码'
    },
    messages: {
      saveSuccess: '设置已保存',
      passwordMismatch: '新密码与确认密码不匹配',
      passwordSuccess: '密码修改成功',
      passwordSuccessRedirect: '密码修改成功，5秒后将返回登录页面...',
      passwordFailed: '修改密码失败',
      updateUserFailed: '更新用户信息失败: {error}',
      fetchUsersFailed: '获取用户列表失败'
    },
    buttons: {
      save: '保存设置',
      cancel: '取 消',
      confirm: '确 定'
    }
  },
  pagination: {
    total: '共 {total} 条',
    pageSize: '条/页',
    jumper: '前往',
    page: '页',
    prev: '上一页',
    next: '下一页',
  },
};