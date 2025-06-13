export default {
  dashboard: {
    title: 'Dashboard',
    stats: {
      total_ips: '总IP地址',
      claimed_ips: '已认领IP地址',
      unclaimed_ips: '未认领IP地址',
      user_claimed_ips: '用户已认领IP地址',
      total_policies: '总策略',
      running_jobs: '运行中的任务',
      failed_jobs: '失败的任务',
      successful_jobs: '成功的任务',
      cpu_usage: 'CPU使用率',
      memory_usage: '内存使用率',
      disk_usage: '磁盘使用率',
    },
    resources: {
      audit: '审计资源',
      columns: {
        id: 'ID',
        action: '操作',
        details: '详情',
        created_at: '创建时间',
        source_ip: '源IP'
      }
    },
    recentJobs: {
      title: '最近扫描任务',
      columns: {
        id: 'ID',
        status: '状态',
        result: '结果',
        created_at: '创建时间',
        machines_found: '扫描主机数量'
      }
    },
    refresh: {
      off: '关闭自动刷新',
      '1s': '每 1 秒',
      '5s': '每 5 秒',
      '10s': '每 10 秒',
      '30s': '每 30 秒',
      '60s': '每分钟'
    }
  },
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
    refresh: '刷新',
    autoRefresh: '自动刷新',
    enabled: '启用',
    disabled: '禁用',
    view: '查看详情',
    stop: '停止',
  },
  menu: {
    home: '首页',
    ipManagement: '主机管理',
    scanConfig: '配置扫描',
    task: '任务管理',
    settings: '系统设置',
    userManagement: '用户管理',
    notifications: '通知历史',
    notificationSettings: '通知配置'
  },
  auth: {
    login: '登录',
    logout: '退出登录',
    register: '立即注册',
    username: '用户名',
    password: '密码',
    email: '邮箱',
    loginSuccess: '登录成功',
    loginError: '登录失败',
    invalidUsernameOrPassword: '用户名或密码错误',
    tokenExpired: '登录过期，请重新登录',
    invalidCaptcha: '验证码错误或过期',
    title: 'IPAM系统平台',
    subtitle: '轻松监控和管理您的网络',
    registerSubtitle: '创建一个账户来管理您的网络',
    noAccount: '还没有账号？',
    hasAccount: '已经有账号？',
    confirmPassword: '确认密码',
    confirmPasswordPlaceholder: '请再次输入密码',
    registerSuccess: '注册成功',
    registerError: '注册失败',
    validation: {
      username: '请输入用户名',
      usernameLength: '用户名长度至少为3个字符',
      email: {
        required: '请输入邮箱',
        invalid: '请输入有效的邮箱地址'
      },
      password: '请输入密码',
      passwordLength: '密码长度至少为6个字符',
      confirmPassword: '请确认密码',
      passwordMismatch: '两次输入的密码不一致',
      captchaRequired: '请输入验证码',
      captchaInvalid: '验证码错误'
    },
    captcha: '验证码',
    captchaPlaceholder: '请输入验证码',
    captchaError: '获取验证码失败',
    captchaRefresh: '刷新验证码',
    message: {
      noPermisstions: '权限不足',
    }
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
      myResources: '我的资源',
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
    changePassword: '修改密码',
    editProfile: '编辑资料',
    editDialogTitle: '编辑个人资料',
    wechatPlaceholder: '待补充',
    changePasswordTitle: '修改密码',
    role: {
      admin: '管理员',
      user: '用户'
    },
    fields: {
      id: 'ID',
      username: '用户名',
      email: '邮箱',
      wechatId: '微信号',
      createdAt: '创建时间',
      oldPassword: '旧密码',
      newPassword: '新密码',
      confirmPassword: '确认密码'
    },
    validation: {
      emailRequired: '邮箱不能为空',
      emailFormat: '请输入有效的邮箱地址',
      wechatIdRequired: '微信号不能为空',
      wechatIdLength: '微信号长度至少为2个字符',
      oldPasswordRequired: '旧密码不能为空',
      newPasswordRequired: '新密码不能为空',
      confirmPasswordRequired: '确认密码不能为空',
      passwordMismatch: '新密码与确认密码不匹配',
      passwordLength: '密码长度至少为6个字符'
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
      invalidFileType: '只支持JPG, JPEG, PNG和GIF格式图片',
      fileTooLarge: '文件大小超过2MB限制',
      passwordSuccess: '密码修改成功',
      passwordFailed: '修改密码失败',
      passwordSuccessRedirect: '密码修改成功，5秒后将返回登录页面...',
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
      subnetsPlaceholder: '请选择要扫描的网段',
      description: '策略描述',
      descriptionPlaceholder: '请输入策略描述',
      threads: '线程数',
      threadsPlaceholder: '请输入线程数',
      schedules: '扫描计划',
      addSchedule: '添加扫描计划',
      removeSchedule: '移除扫描计划',
      type: '策略类型',
      typeRequired: '请选择策略类型',
      subnets: '网段',
      startTimePlaceholder: '请输入计划开始时间',
      scanParams: {
        title: "扫描参数配置",
        help: "配置扫描策略，不同的扫描类型适用于不同的场景：<br>- 默认扫描：适合日常网络监控<br>- 快速扫描：适合快速了解网络状态<br>- 深度扫描：适合详细分析网络情况<br>- 漏洞扫描：适合安全审计",
        scanType: "扫描类型",
        scanTypeHelp: "选择不同的扫描类型来满足不同的扫描需求",
        ports: "端口配置",
        enableCustomPorts: "启用自定义端口",
        portsPlaceholder: "例如: 80,443,8080-8090",
        portsHelp: "支持以下格式：<br>- 单个端口: 80<br>- 端口范围: 80-100<br>- 多个端口: 80,443,8080<br>- 组合: 80,443,8080-8090",
        portsHelpDisplay: "支持以下格式：\n- 单个端口: 80\n- 端口范围: 80-100\n- 多个端口: 80,443,8080\n- 组合: 80,443,8080-8090",
        types: {
          default: {
            label: "默认扫描",
            tag: "基础",
            description: "使用基本的扫描参数，可以自定义端口范围。适合一般用途的扫描。"
          },
          quick: {
            label: "快速扫描",
            tag: "快速",
            description: "只扫描最常见的100个端口，扫描速度快。适合快速了解网络状态。"
          },
          intense: {
            label: "深度扫描",
            tag: "全面",
            description: "进行全面的扫描，包括操作系统检测和版本检测。可以选择是否限制端口范围。"
          },
          vulnerability: {
            label: "漏洞扫描",
            tag: "安全",
            description: "在深度扫描的基础上，增加漏洞检测。可以选择是否限制端口范围。"
          }
        }
      },
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
      execute: {
        title: '执行扫描',
        policyName: '策略名称',
        selectSubnets: '选择要扫描的网段',
        confirm: '确认执行扫描',
        noSubnets: '请选择至少一个网段',
        success: '扫描执行成功',
        failed: '执行扫描失败'
      },
      show: {
        title: '扫描策略',
        add: '添加策略',
        schedulerJobs: '定时任务',
        columns: {
          name: '策略名称',
          description: '策略描述',
          strategy: '执行计划',
          startTime: '开始时间',
          threads: '线程数',
          createdAt: '创建时间',
          subnets: '扫描网段',
          scan_params: '扫描参数',
          scan_type: '扫描类型',
          nextRunTime: '下次执行时间',
          trigger: '触发器',
          jobType: '任务类型',
          startJob: '启动任务',
          cronJob: '定时任务',
          status: {
            title: '状态',
            active: '已启用',
            inactive: '已禁用',
            running: '运行中',
            completed: '已完成',
            failed: '失败',
            pending: '等待中',
            cancelled: '已取消',
          },
          actions: {
            title: '操作',
            enable: '启用',
            disable: '禁用',
            edit: '编辑',
            delete: '删除',
            scan: '扫描'
          }
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
          updateSuccess: '策略更新成功',
          fetchFailed: '获取策略列表失败',
          deleteFailed: '策略删除失败',
          updateFailed: '更新策略失败',
          editFailed: '编辑策略失败',
          statusUpdateSuccess: '策略状态更新成功',
          statusUpdateFailed: '策略状态更新失败'
        }
      },
      policyDescription: {
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
      },
      jobs: {
        title: '扫描任务',
        jobId: '任务ID',
        subnet: '网段',
        status: '状态',
        machinesFound: '发现主机数',
        progress: '进度',
        startTime: '开始时间',
        endTime: '结束时间',
        errorMessage: '任务执行结果',
        actions: '操作',
        cancel: '取消',
        viewResults: '查看结果',
        cancelSuccess: "任务已取消",
        cancelFailed: '取消任务失败',
        fetchError: '获取任务列表失败',
        refresh: {
          off: '关闭自动刷新',
          '1s': '每 1 秒',
          '5s': '每 5 秒',
          '10s': '每 10 秒',
          '30s': '每 30 秒',
          '60s': '每分钟'
        }
      },
      cron: {
        "everyMinute": "每分钟执行一次, ",
        "everyXMinutes": "每隔 {interval} 分钟执行一次, ",
        "atMinutes": "在 {minutes} 执行, ",
        "betweenMinutes": "从 {start} 分到 {end} 分每分钟执行一次, ",
        "everyHour": "每小时执行一次, ",
        "everyXHours": "每隔 {interval} 小时执行一次, ",
        "atHours": "在 {hours} 执行, ",
        "betweenHours": "从 {start} 点到 {end} 点每小时执行一次, ",
        "everyDay": "每天执行一次, ",
        "everyXDays": "每隔 {interval} 天执行一次, ",
        "atDays": "在每月 {days} 执行, ",
        "betweenDays": "从每月 {start} 日到 {end} 日每天执行一次, ",
        "everyMonth": "每月执行一次, ",
        "everyXMonths": "每隔 {interval} 个月执行一次, ",
        "atMonths": "在 {months} 执行, ",
        "betweenMonths": "从 {start} 月到 {end} 月每月执行一次, ",
        "everyWeekday": "每周每天执行一次, ",
        "everyXWeeks": "每隔 {interval} 周执行一次, ",
        "atWeekdays": "在 {weekdays} 执行, ",
        "betweenWeekdays": "从 {start} 到 {end} 每天执行一次, "
      },
      scheduler: {
        totalJobs: '总任务数',
        startJobs: '启动任务',
        cronJobs: '定时任务',
        nextRunTime: '下次执行时间',
        trigger: '触发方式',
        jobType: '任务类型',
        startJob: '启动任务',
        cronJob: '定时任务'
      }
    },
    execution: {
      title: '执行扫描',
      selectSubnet: '选择网段',
      execute: '执行扫描'
    },
    form: {
      confirm: {
        title: '确认保存',
        saveContent: '您即将保存以下数据：',
        subnets: '网段: {count}',
        policies: '策略: {count}',
        save: '确认保存当前配置？',
        execute: '确认执行扫描？',
        delete: '确认删除？'
      },
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
        updatePolicy: '测试更新成功',
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
    },
    results: {
      title: '扫描结果',
      ipAddress: 'IP地址',
      openPorts: '开放端口',
      createdAt: '创建时间',
      updatedAt: '更新时间',
      searchPlaceholder: '搜索IP地址',
      hostCount: '主机数: {count}',
      resourceId: '资源ID',
      jobId: '任务ID',
      noData: '暂无数据'
    },
    scheduler: {
      totalJobs: '总任务数',
      startJobs: '启动任务',
      cronJobs: '定时任务',
      nextRunTime: '下次执行时间',
      trigger: '触发方式',
      jobType: '任务类型',
      startJob: '启动任务',
      cronJob: '定时任务'
    }
  },
  settings: {
    title: '系统设置',
    subtitle: '在这里您可以配置您的系统偏好设置，包括主题、语言等',
    sections: {
      basic: '基本设置',
      interface: '界面设置',
      account: '账户设置',
      notification: '通知设置'
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
        off: '关',
        email: {
          title: '邮件通知',
          enabled: '启用邮件通知',
          disabled: '禁用邮件通知',
          smtp: {
            title: 'SMTP 服务器配置',
            host: 'SMTP 服务器地址',
            port: 'SMTP 端口',
            username: 'SMTP 用户名',
            password: 'SMTP 密码',
            from: '发件人邮箱',
            to: '收件人邮箱',
            test: '测试邮件配置'
          }
        },
        wechat: {
          title: '微信通知',
          enabled: '启用微信通知',
          disabled: '禁用微信通知',
          config: {
            title: '微信配置',
            appId: '微信 AppID',
            appSecret: '微信 AppSecret',
            templateId: '模板消息 ID',
            test: '测试微信配置'
          }
        },
        events: {
          title: '通知事件',
          scan: {
            title: '扫描事件',
            start: '扫描开始',
            complete: '扫描完成',
            error: '扫描错误'
          },
          ip: {
            title: 'IP 事件',
            claim: 'IP 认领',
            release: 'IP 释放',
            update: 'IP 更新'
          },
          system: {
            title: '系统事件',
            error: '系统错误',
            warning: '系统警告',
            info: '系统信息'
          }
        }
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
      confirmPassword: '请确认新密码',
      smtp: {
        host: '请输入 SMTP 服务器地址',
        port: '请输入 SMTP 端口',
        username: '请输入 SMTP 用户名',
        password: '请输入 SMTP 密码',
        from: '请输入发件人邮箱',
        to: '请输入收件人邮箱'
      },
      wechat: {
        appId: '请输入微信 AppID',
        appSecret: '请输入微信 AppSecret',
        templateId: '请输入模板消息 ID'
      }
    },
    messages: {
      addUserFailed: '添加用户失败: {error}',
      saveSuccess: '设置已保存',
      passwordMismatch: '新密码与确认密码不匹配',
      passwordSuccess: '密码修改成功',
      passwordSuccessRedirect: '密码修改成功，5秒后将返回登录页面...',
      passwordFailed: '修改密码失败',
      updateUserFailed: '更新用户信息失败: {error}',
      fetchUsersFailed: '获取用户列表失败',
      emailAlreadyExists: '邮箱已存在',
      usernameAlreadyExists: '用户名已存在',
      unsavedChanges: '您有未保存的更改，确定要放弃这些更改吗？',
      confirmSave: '确定要保存当前设置吗？',
      notification: {
        testEmailSuccess: '测试邮件发送成功',
        testEmailFailed: '测试邮件发送失败',
        testWechatSuccess: '测试微信消息发送成功',
        testWechatFailed: '测试微信消息发送失败',
        saveSuccess: '通知设置保存成功',
        saveFailed: '通知设置保存失败'
      }
    },
    buttons: {
      save: '保存设置',
      cancel: '取 消',
      confirm: '确 定',
      test: '测试配置'
    }
  },
  notifications: {
    label: '通知开关',
    on: '开',
    off: '关',
    email: {
      title: '邮件通知',
      enabled: '启用邮件通知',
      disabled: '禁用邮件通知',
      smtp: {
        title: 'SMTP 服务器配置',
        host: 'SMTP 服务器地址',
        port: 'SMTP 端口',
        username: 'SMTP 用户名',
        password: 'SMTP 密码',
        from: '发件人邮箱',
        to: '收件人邮箱',
        test: '测试邮件配置'
      }
    },
    wechat: {
      title: '微信通知',
      enabled: '启用微信通知',
      disabled: '禁用微信通知',
      config: {
        title: '微信配置',
        appId: '微信 AppID',
        appSecret: '微信 AppSecret',
        templateId: '模板消息 ID',
        test: '测试微信配置'
      }
    },
    events: {
      title: '通知事件',
      scan: {
        title: '扫描事件',
        start: '扫描开始',
        complete: '扫描完成',
        error: '扫描错误'
      },
      ip: {
        title: 'IP 事件',
        claim: 'IP 认领',
        release: 'IP 释放',
        update: 'IP 更新'
      },
      system: {
        title: '系统事件',
        error: '系统错误',
        warning: '系统警告',
        info: '系统信息'
      }
    },
    history: {
      title: '通知历史',
      subtitle: '查看和管理系统通知',
      actions: {
        markAllAsRead: '全部标记为已读',
        clearAll: '清空所有通知'
      },
      columns: {
        title: '标题',
        content: '内容',
        type: '类型',
        status: '状态',
        createdAt: '创建时间',
        actions: '操作'
      },
      status: {
        read: '已读',
        unread: '未读'
      },
      types: {
        scan: '扫描',
        ip: 'IP',
        policy: '策略'
      },
      messages: {
        markAsReadSuccess: '标记已读成功',
        markAsReadFailed: '标记已读失败',
        markAllAsReadSuccess: '全部标记已读成功',
        markAllAsReadFailed: '全部标记已读失败',
        deleteSuccess: '删除成功',
        deleteFailed: '删除失败',
        clearAllSuccess: '清空成功',
        clearAllFailed: '清空失败',
        fetchFailed: '获取通知历史失败'
      }
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
  errors: {
    database: {
      connection: '数据库连接失败，请检查网络连接或联系管理员'
    },
    network: '网络连接失败，请检查网络设置',
    unknown: '发生未知错误，请稍后重试'
  },
  tasks: {
    title: '任务管理',
    subtitle: '查看和管理所有任务及扫描结果',
    tabs: {
      running: '运行中',
      history: '历史记录'
    },
    refresh: {
      off: '关闭自动刷新',
      '1s': '1 秒',
      '5s': '5 秒',
      '10s': '10 秒',
      '30s': '30 秒',
      '60s': '1 分钟'
    },
    table: {
      name: '任务名称',
      type: '类型',
      status: '状态',
      progress: '进度',
      startTime: '开始时间',
      endTime: '结束时间',
      actions: '操作',
      machines_found: '发现主机数',
      error_message: '任务执行结果',
      policy: {
        name: '策略名称',
        strategies: '扫描策略',
        description: '策略描述',
        type: '策略类型',
        createTime: '创建时间'
      }
    },
    types: {
      scan: '扫描任务',
      backup: '备份任务',
      sync: '同步任务',
      other: '其他任务'
    },
    status: {
      running: '运行中',
      completed: '已完成',
      failed: '失败',
      stopped: '已停止',
      pending: '等待中',
      cancelled: '已取消',
    },
    scanStatus: {
      success: '成功',
      failed: '失败',
      warning: '警告',
      info: '信息',
      up: '开启',
    },
    details: {
      title: '任务详情',
      name: '任务名称',
      type: '任务类型',
      status: '任务状态',
      progress: '任务进度',
      startTime: '开始时间',
      endTime: '结束时间',
      scanResults: '扫描结果',
      ip: 'IP 地址',
      resultStatus: '状态',
      details: '详细信息',
      scanTime: '扫描时间'
    },
    actions: {
      create: '创建任务'
    },
    messages: {
      confirmStop: '确定要停止该任务吗？',
      stopSuccess: '任务已停止',
      stopFailed: '停止任务失败',
      loadFailed: '加载任务列表失败'
    }
  },
};