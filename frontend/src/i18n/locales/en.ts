export default {
  dashboard: {
    title: 'Dashboard',
    subtitle: 'System Overview',
    viewAll: 'View All',
    autoRefresh: 'Auto Refresh',
    systemInfo: {
      title: 'System Information',
      hostname: 'hostname',
      ipaddress: 'IP Address',
      platform: 'Operating platform',
      platform_version: 'System Version',
      processor: 'Processor',
      python_version: 'Python Version',
      uptime: 'Uptime',
      days: 'days',
      hours: 'hours',
      minutes: 'minutes'
    },
    charts: {
      resourceUsage: "Resource Usage Trend",
      jobStatus: "Task Status Distribution",
      IPStatus: 'IP Status Distribution',
      line: "Line chart",
      bar: "Bar chart"
    },
    stats: {
      total_ips: 'Total IPs',
      claimed_ips: 'Claimed IPs',
      unclaimed_ips: 'Unclaimed IPs',
      user_claimed_ips: 'User Claimed IPs',
      total_policies: 'Total Policies',
      total_jobs: 'Total Jobs',
      running_jobs: 'Running Jobs',
      failed_jobs: 'Failed Jobs',
      successful_jobs: 'Successful Jobs',
      cpu_usage: 'CPU Usage',
      memory_usage: 'Memory Usage',
      disk_usage: 'Disk Usage',
    },
    resources: {
      audit: 'Audit Resources',
      columns: {
        id: 'ID',
        action: 'Action',
        details: 'Details',
        created_at: 'Created At',
        source_ip: 'Source IP'
      }
    },
    IPs: {
      status: {
        total: 'Total IPs',
        claim: 'Claim IPs',
        unclaim: 'Unclaim IPs',
      }
    },
    recentJobs: {
      title: 'Recent Scan Jobs',
      columns: {
        id: 'ID',
        status: 'Status',
        result: 'Result',
        created_at: 'Created At',
        machines_found: 'Machines Found',
      },
      status: {
        running: 'Running',
        completed: 'Completed',
        failed: 'Failed',
        pending: 'Pending',
        cancelled: 'Cancelled',
      }
    },
    refresh: {
      off: 'Auto Refresh Off',
      '1s': 'Every 1 second',
      '5s': 'Every 5 seconds',
      '10s': 'Every 10 seconds',
      '30s': 'Every 30 seconds',
      '60s': 'Every minute'
    }
  },
  common: {
    success: 'Operation Successful',
    error: 'Operation Failed',
    fetchError: 'Failed to fetch data',
    createError: 'Create failed',
    updateError: 'Update failed',
    deleteError: 'Delete failed',
    testError: 'Test failed',
    exportError: 'Export failed',
    collectError: 'Collection failed',
    batchCollectError: 'Batch collection failed',
    bindError: 'Bind failed',
    unbindError: 'Unbind failed',
    unknownError: 'Unknown error',
    fields: 'Fields',
    confirm: 'Confirm',
    warning: 'Warning',
    cancel: 'Cancel',
    save: 'Save',
    delete: 'Delete',
    edit: 'Edit',
    add: 'Add',
    search: 'Search',
    reset: 'Reset',
    loading: 'Loading...',
    more: 'More',
    yes: 'Yes',
    no: 'No',
    actions: 'Actions',
    refresh: 'Refresh',
    autoRefresh: 'Auto Refresh',
    enabled: 'Enabled',
    disabled: 'Disabled',
    view: 'View Details',
    stop: 'Stop',
    createdAt: 'Created At',
    updatedAt: 'Updated At',
    cores: 'Cores',
    close: 'Close',
    second: 's',
    operationFailed: 'Operation failed',
  },
  menu: {
    home: 'Home',
    ipManagement: 'IP Management', // Keep old key for compatibility
    ipAddressManagement: 'IP Management',
    credentials: 'Credentials',
    hostInfo: 'Host Information', // Keep old key for compatibility
    hostManagement: 'Host Management', // Keep old key for compatibility
    hostCollection: 'Host Collection',
    resourceCollection: 'Resource Collection', // Keep old key for compatibility
    scanConfig: 'Scan Config',
    task: 'Task Management',
    settings: 'Settings',
    monitor: 'Resource Monitor',
    userManagement: 'User Management',
    notifications: 'Notification History',
    notificationSettings: 'Notification Settings',
    category: {
      resourceManagement: 'Resource Management',
      networkScan: 'Network Scan',
      systemManagement: 'System Management'
    }
  },
  auth: {
    login: 'Login',
    logout: 'Logout',
    register: 'Register Now',
    username: 'Username',
    password: 'Password',
    email: 'Email',
    loginSuccess: 'Login successful',
    loginError: 'Login failed',
    invalidUsernameOrPassword: 'Invalid username or password',
    tokenExpired: 'Login expired, please login again',
    invalidCaptcha: 'Invalid or expired captcha',
    accountDisabled: 'Account has been disabled, please contact administrator',
    title: 'IPAM System Platform',
    subtitle: 'Easily monitor and manage your network',
    registerSubtitle: 'Create an account to manage your network',
    noAccount: 'No account?',
    hasAccount: 'Already have an account?',
    confirmPassword: 'Confirm Password',
    confirmPasswordPlaceholder: 'Please enter password again',
    registerSuccess: 'Registration successful',
    registerError: 'Registration failed',
    validation: {
      missingFields: 'Please fill in all required fields',
      captchaRequired: 'Please enter the captcha',
      usernameRequired: 'Please enter username',
      usernameLength: 'Username must be at least 3 characters',
      passwordRequired: 'Please enter password',
      emailRequired: 'Please enter email',
      emailInvalid: 'Please enter a valid email address',
      passwordMismatch: 'Passwords do not match',
      passwordLength: 'Password must be at least 6 characters',
      PasswordConfirm: 'Password input again',
    },
    captcha: 'Captcha',
    captchaPlaceholder: 'Please enter captcha',
    captchaError: 'Failed to get captcha',
    captchaRefresh: 'Refresh Captcha',
    message: {
      noPermisstions: 'Insufficient permissions',
    }
  },
  user: {
    profile: 'Profile',
    settings: 'Settings',
    account: 'Account',
    changePassword: 'Change Password',
    currentUser: 'Current User',
    management: {
      title: 'User Management',
      subtitle: 'Manage system users and their permissions',
      button: {
        add: 'Add User'
      },
      status: {
        active: 'active',
        disable: 'disabled',
      },
      table: {
        columns: {
          uuid: 'UUID',
          username: 'Username',
          email: 'Email',
          createdAt: 'Created At',
          isAdmin: 'Admin',
          isActive: 'Status',
          actions: 'Actions'
        },
        noData: 'No user data'
      },
      dialog: {
        title: 'User Information',
        labels: {
          username: 'Username',
          email: 'Email',
          password: 'Password',
          wechatId: 'WeChat ID',
          isAdmin: 'Admin',
          isActive: 'Active',
        },
        placeholders: {
          username: 'Enter username',
          email: 'Enter email',
          password: 'Enter password',
          wechatId: 'Enter WeChat ID'
        },
        batchDelete: {
          title: 'Batch Delete {count} Users',
          confirm: 'Are you sure to delete {count} users?',
          success: 'Users deleted successfully',
          error: 'Failed to delete users',
          warning: 'This is a dangerous operation, please be careful!!!',
          description: 'Users are still associated with IP addresses, please reclaim the IP addresses first, and then delete the users.'
        }
      },
      buttons: {
        edit: 'Edit',
        delete: 'Delete',
        save: 'Save',
        cancel: 'Cancel',
        add: 'Add User',
        deactivate: 'disable',
        activate: 'active',
        batchDelete: 'Batch Delete {count} Users',
        batchDeleteConfirm: 'Are you sure to delete {count} users?'
      },
      messages: {
        deleteConfirm: 'Are you sure to delete user {username}?',
        deleteSuccess: 'User deleted successfully',
        saveSuccess: 'User saved successfully',
        fetchError: 'Failed to fetch user list',
        saveError: 'Failed to save user',
        hasAssociatedIPs: 'Users are still associated with IP addresses, please reclaim the IP addresses first, and then delete the users.',
        batchDeleteConfirm: 'Are you sure to delete {count} users?',
        batchDeleteSuccess: 'Users deleted successfully',
        deleteSelfError: 'Cannot delete yourself',
        confirmActivate: 'Are you sure to acitve user {username}?',
        confirmDeactivate: 'Are you sure to disable user {username}?',
        statusUpdateSuccess: 'User status updated successfully',
        statusUpdatefailed: 'User status update failed'
      },
      validation: {
        username: 'Username is required',
        email: {
          required: 'Email is required',
          invalid: 'Please enter a valid email address'
        },
        password: 'Password is required'
      },
      search: {
        selectColumn: 'Select Search Column',
        allColumns: 'All Columns',
        all: 'Search All Columns...',
        specific: 'Search {column}...',
        adminStatus: 'Admin Status',
        allUsers: 'All Users',
        adminOnly: 'Admin Only',
        normalOnly: 'Normal Only'
      }
    }
  },
  theme: {
    title: 'Theme',
    light: 'Light',
    dark: 'Dark',
    system: 'System',
  },
  language: {
    title: 'Language',
    zh: 'Chinese',
    en: 'English',
  },
  ip: {
    title: 'IP Management',
    subtitle: 'Easily manage your IP addresses with filters and search functionality',
    status: {
      all: 'All Status',
      active: 'Active',
      inactive: 'Inactive',
      unclaimed: 'Unclaimed',
      unassigned: 'Unassigned',
      myResources: 'My Resources',
      description: {
        active: 'This IP is currently active',
        inactive: 'This IP is not in use',
        unclaimed: 'This IP is available for claiming',
        unassigned: 'This IP is unassigned',
        danger: 'Unknown status',
        undefined: 'Unknown status',
      },
    },
    search: {
      title: 'Search IP, Device or Purpose',
      selectColumn: 'Select Search Column',
      allColumns: 'All Columns',
      all: 'Search All Columns...',
      specific: 'Search {column}...'
    },
    columns: {
      hostUUID: 'Host UUID',
      ipAddress: 'IP Address',
      osVersion: 'OS Version',
      status: 'Status',
      deviceName: 'Device Name',
      deviceType: 'Device Type',
      architecture: 'Architecture',
      model: 'Model',
      owningUser: 'Owning User',
      purpose: 'Purpose',
      lastScanned: 'Last Scanned'
    },
    actions: {
      claim: 'Claim',
      edit: 'Edit',
      claimSuccess: 'Successfully claimed IP: {ip}',
      updateSuccess: 'Successfully updated IP: {ip}',
      batchClaim: 'Batch Claim',
      batchUpdate: 'Batch Update',
      batchClaimSuccess: 'Successfully batch claimed IP: {ip}',
      batchUpdateSuccess: 'Successfully batch updated IP: {ip}'
    },
    noData: 'No IP addresses found',
    dialog: {
      claim: {
        title: 'Claim IP Address',
        hostUUID: 'Host UUID',
        hostIP: 'Host IP',
        assignUser: 'Assign to User',
        selectUser: 'Select a user',
        deviceName: 'Device Name',
        deviceNamePlaceholder: 'Enter your device name, Like (e.g., Nginx, Other)',
        hostType: 'Host Type',
        hostTypeTip: 'Select host type (Physical, VMware, etc.)',
        hostTypeOptions: {
          physical: 'Physical',
          vmware: 'VMware',
          other: 'Other Virtualization'
        },
        osType: 'OS Type',
        osTypeTip: 'Select the operating system running on this device (e.g., Linux, Windows, Other)',
        deviceType: 'Device Type',
        deviceTypeTip: 'Specify the type of device using this IP (e.g., Router, Switch, Server)',
        manufacturer: 'Manufacturer',
        manufacturerTip: 'Indicate where the device is deployed (e.g., VMware, OpenStack, Physical)',
        model: 'Model',
        modelTip: 'Provide the device model (e.g., PowerEdge R730, DELL R720)',
        purpose: 'Purpose',
        purposePlaceholder: 'Describe the purpose of this IP address',
        confirmClaim: 'Confirm Claim',
        confirmUpdate: 'Confirm Update',
        required: 'Required',
        success: 'IP claimed successfully',
        updateSuccess: 'IP updated successfully',
        error: 'Failed to claim IP: {error}',
        deviceNameRequired: 'Device Name is required',
        purposeRequired: 'Purpose is required',
      },
      batchClaim: {
        title: 'Batch Claim IP Address',
        commonConfig: 'Common Config',
        applyToAll: 'Apply to All',
        individualConfig: 'Individual Config',
        selectIPs: 'Select IP Address',
        confirmClaim: 'Confirm Claim',
        success: 'IP batch claimed successfully',
        error: 'Batch claim IP failed: {error}',
        validation: 'Please fill in all required fields'
      },
      update: {
        title: 'Update IP Address',
        success: 'IP updated successfully',
        error: 'Update IP failed: {error}',
      }
    }
  },
  profile: {
    title: 'Profile',
    changeAvatar: 'Change Avatar',
    changePassword: 'Change Password',
    editProfile: 'Edit Profile',
    editDialogTitle: 'Edit Profile',
    wechatPlaceholder: 'Not Set',
    changePasswordTitle: 'Change Password',
    role: {
      admin: 'Admin',
      user: 'User'
    },
    fields: {
      id: 'ID',
      username: 'Username',
      email: 'Email',
      wechatId: 'WeChat ID',
      createdAt: 'Created At',
      oldPassword: 'Old Password',
      newPassword: 'New Password',
      confirmPassword: 'Confirm Password'
    },
    validation: {
      emailRequired: 'Email is required',
      emailFormat: 'Please enter a valid email address',
      wechatIdRequired: 'WeChat ID is required',
      wechatIdLength: 'WeChat ID must be at least 2 characters long',
      oldPasswordRequired: 'Old password is required',
      newPasswordRequired: 'New password is required',
      confirmPasswordRequired: 'Confirm password is required',
      passwordMismatch: 'New password and confirm password do not match',
      passwordLength: 'Password must be at least 6 characters long'
    },
    buttons: {
      save: 'Save',
      cancel: 'Cancel',
    },
    messages: {
      updateSuccess: 'Profile updated successfully',
      updateFailed: 'Failed to update profile',
      avatarSuccess: 'Avatar updated successfully',
      avatarFailed: 'Failed to update avatar',
      invalidFileType: 'Only JPG, JPEG, PNG and GIF format images are supported',
      fileTooLarge: 'File size exceeds the limit of 2MB',
      passwordSuccess: 'Password updated successfully',
      passwordFailed: 'Failed to update password',
      passwordSuccessRedirect: 'Password updated successfully, 5 seconds will return to the login page...',
    }
  },
  scan: {
    title: 'Scan Configuration',
    subtitle: 'Manage scan subnets and policy configurations',
    subnet: {
        title: 'Add Scan Subnet',
        name: 'Subnet Name',
        namePlaceholder: 'Please enter subnet name',
        range: 'Subnet',
        rangePlaceholder: 'Please enter scan subnet (e.g.: 192.168.0.0/24)',
        add: 'Add',
        list: 'Added Subnets',
        columns: {
          name: 'Subnet Name',
          subnet: 'Subnet',
          createdAt: 'Created At',
          actions: 'Actions'
        },
        noData: 'No subnet data',
        delete: 'Delete'
    },
    form: {
      confirm: {
        title: 'Confirm to save',
        saveContent: 'You are about to save the following data:',
        subnets: 'Subnets: {count}',
        policies: 'Policies: {count}',
        save: 'Confirm to save current configuration?',
        execute: 'Confirm to execute scan?'
      },
      interval: {
        minutes: 'Interval (Minutes)',
        hours: 'Interval (Hours)',
        days: 'Interval (Days)',
        selectTime: 'Please select time'
      },
      time: {
        start: 'Start Time',
        execution: 'Execution Start Time',
        select: 'Select Time',
        weekly: 'Weekly Execution Time',
        monthly: 'Monthly Execution Time',
        daily: 'Daily Execution Time'
      },
      cron: {
        label: 'Cron Expression',
        placeholder: 'Enter Cron Expression'
      },
      validation: {
        invalidSubnet: 'Please enter a valid subnet!',
        subnetNameRequired: 'Subnet name cannot be empty!',
        invalidIPFormat: 'Invalid IP address format!',
        invalidSubnetFormat: 'Invalid subnet format, correct format is: IP/mask (e.g., 192.168.0.0/24)'
      },
      weekdays: {
        mon: 'Monday',
        tue: 'Tuesday',
        wed: 'Wednesday',
        thu: 'Thursday',
        fri: 'Friday',
        sat: 'Saturday',
        sun: 'Sunday'
      },
      types: {
        everyMinute: 'Every Minute',
        everyHour: 'Every Hour',
        everyDay: 'Every Day',
        everyWeek: 'Every Week',
        everyMonth: 'Every Month',
        custom: 'Custom'
      },
      monthDays: {
        last: 'Last Day',
        select: 'Select Days'
      },
      cronExpression: {
        label: 'Cron Expression',
        placeholder: 'Please enter Cron expression',
        time: 'Execution Time'
      },
      buttons: {
        add: 'Add',
        save: 'Save',
        execute: 'Execute Scan'
      },
      table: {
        noData: 'No Data'
      },
      status: {
        loading: 'Processing...',
        executing: 'Executing scan...'
      },
      tips: {
        weekDays: 'Please select at least one weekday',
        monthDays: 'Please select at least one day',
        customCron: 'Cron expression format: minute hour day month weekday'
      }
    },
    policy: {
      title: 'Scan Policy Configuration',
      subtitle: 'Manage your scan policies and their configurations',
      name: 'Policy Name',
      namePlaceholder: 'Please enter policy name',
      subnetsPlaceholder: 'Please select subnets to scan',
      description: 'Policy Description',
      descriptionPlaceholder: 'Please enter policy description',
      threads: 'Threads',
      threadsPlaceholder: 'Please enter number of threads',
      schedules: 'Scan Schedules',
      addSchedule: 'Add Scan Schedule',
      removeSchedule: 'Remove Scan Schedule',
      type: 'Policy Type',
      typeRequired: 'Please select policy type',
      subnets: 'Subnets',
      startTimePlaceholder: 'Please select the start time for schedule task',
      details: 'Policy Details',
      scanParams: {
        title: "Scan Parameters",
        help: "Configure scan strategy, different scan types are suitable for different scenarios:<br>- Default Scan: Suitable for daily network monitoring<br>- Quick Scan: Suitable for quick network status overview<br>- Intense Scan: Suitable for detailed network analysis<br>- Vulnerability Scan: Suitable for security auditing",
        scanType: "Scan Type",
        scanTypeHelp: "Choose different scan types to meet different scanning needs",
        ports: "Port Configuration",
        enableCustomPorts: "Enable Custom Ports",
        portsPlaceholder: "Example: 80,443,8080-8090",
        portsHelp: "Supported formats:<br>- Single port: 80<br>- Port range: 80-100<br>- Multiple ports: 80,443,8080<br>- Combined: 80,443,8080-8090",
        portsHelpDisplay: "Supported formats:\n- Single port: 80\n- Port range: 80-100\n- Multiple ports: 80,443,8080\n- Combined: 80,443,8080-8090",
        types: {
          default: {
            label: "Default Scan",
            tag: "Basic",
            description: "Uses basic scan parameters with customizable port ranges. Suitable for general purpose scanning."
          },
          quick: {
            label: "Quick Scan",
            tag: "Fast",
            description: "Scans only the most common 100 ports for quick network status overview."
          },
          intense: {
            label: "Intense Scan",
            tag: "Comprehensive",
            description: "Performs comprehensive scanning including OS detection and version detection. Port range can be customized."
          },
          vulnerability: {
            label: "Vulnerability Scan",
            tag: "Security",
            description: "Adds vulnerability detection to intense scanning. Port range can be customized."
          }
        }
      },
      types: {
        everyMinute: 'Every Minute',
        everyHour: 'Every Hour', 
        everyDay: 'Every Day',
        everyWeek: 'Every Week',
        everyMonth: 'Every Month',
        custom: 'Custom'
      },
      interval: {
        minute: 'Interval Minutes',
        hour: 'Interval Hours',
        day: 'Interval Days'
      },
      startTime: 'Start Time',
      startTimeRequired: 'Please select start time',
      weekDays: {
        0: 'Sunday',
        1: 'Monday', 
        2: 'Tuesday',
        3: 'Wednesday',
        4: 'Thursday',
        5: 'Friday',
        6: 'Saturday'
      },
      monthDays: 'Days',
      monthDaysRequired: 'Please select days',
      lastDay: 'Last Day',
      time: 'Time',
      cronExpression: 'Cron Expression',
      cronPlaceholder: 'Enter Cron expression',
      add: 'Add Policy',
      list: 'Added Policies',
      save: 'Save Policy',
      columns: {
        name: 'Policy Name',
        description: 'Policy Description',
        createdAt: 'Created At',
        actions: 'Actions'
      },
      noData: 'No policy data',
      policyDescription: {
        everyMinute: 'Every {minutes} minutes, starting from {time}',
        everyHour: 'Every {hours} hours, starting from {time}',
        everyDay: 'Every {days} days, starting from {time}',
        everyWeek: 'Every {weekdays}, starting from {time}',
        everyMonth: 'Every month on {days}, starting from {time}',
        custom: 'Custom execution: {cron}'
      },
      execute: {
        title: 'Execute Scan',
        policyName: 'Policy Name',
        selectSubnets: 'Select Subnets',
        confirm: 'Confirm Execute Scan',
        noSubnets: 'Please select at least one subnet',
        success: 'Scan executed successfully',
        failed: 'Failed to execute scan'
      },
      show: {
        title: 'Scan Policies',
        add: 'Add Policy',
        schedulerJobs: 'Scheduled Jobs',
        columns: {
          name: 'Policy Name',
          description: 'Policy Description',
          strategy: 'Execution Schedule',
          startTime: 'Start Time',
          threads: 'Thread Count',
          createdAt: 'Created At',
          subnets: 'Scan Subnets',
          scan_params: 'Scan Parameters',
          scan_type: 'Scan Type',
          nextRunTime: 'Next Run Time',
          trigger: 'Trigger',
          jobType: 'Job Type',
          startJob: 'Start Job',
          cronJob: 'Cron Job',
          status: {
            title: 'Status',
            active: 'Enabled',
            inactive: 'Disabled',
            running: 'Running',
            completed: 'Completed',
            failed: 'Failed',
            pending: 'Pending',
            cancelled: 'Cancelled',
          },
          actions: {
            title: 'Actions',
            enable: 'Enable',
            disable: 'Disable',
            edit: 'Edit',
            delete: 'Delete',
            scan: 'Scan'
          }
        },
        noData: 'No policy data',
        dialog: {
          addTitle: 'Add Policy',
          editTitle: 'Edit Policy',
          deleteConfirm: 'Are you sure you want to delete this policy?',
          deleteTitle: 'Delete Policy'
        },
        messages: {
          addSuccess: 'Policy added successfully',
          saveSuccess: 'Policy saved successfully',
          deleteSuccess: 'Policy deleted successfully',
          updateSuccess: 'Policy updated successfully',
          fetchFailed: 'Failed to fetch policies',
          deleteFailed: 'Failed to delete policy',
          editFailed: 'Failed to edit policy',
          statusUpdateSuccess: 'Policy status updated successfully',
          statusUpdateFailed: 'Failed to update policy status'
        }
      },
      jobs: {
        title: 'Scan Jobs',
        jobId: 'Jobs ID',
        subnet: 'Subnet',
        status: 'Status',
        machinesFound: 'Discovery Hosts Count',
        progress: 'Progress',
        startTime: 'Start Time',
        endTime: 'End Time',
        errorMessage: 'Task Results',
        actions: 'Actions',
        cancel: 'Cancel',
        viewResults: 'View Results',
        cancelSuccess: 'Job cancelled successfully',
        cancelFailed: 'Failed to cancel job',
        fetchError: 'Failed to fetch jobs',
        refresh: {
          off: 'Auto-refresh Off',
          '1s': "Refresh every 1s",
          '5s': 'Refresh every 5s',
          '10s': 'Refresh every 10s',
          '30s': 'Refresh every 30s',
          '60s': 'Refresh every 60s'
        }
      },
      cron: {
        "everyMinute": "Execute every minute, ",
        "everyXMinutes": "Execute every {interval} minutes, ",
        "atMinutes": "Execute at {minutes}, ",
        "betweenMinutes": "Execute every minute from {start} to {end}, ",
        "everyHour": "Execute every hour, ",
        "everyXHours": "Execute every {interval} hours, ",
        "atHours": "Execute at {hours}, ",
        "betweenHours": "Execute every hour from {start} to {end}, ",
        "everyDay": "Execute every day, ",
        "everyXDays": "Execute every {interval} days, ",
        "atDays": "Execute on {days}, ",
        "betweenDays": "Execute every day from {start} to {end}, ",
        "everyMonth": "Execute every month, ",
        "everyXMonths": "Execute every {interval} months, ",
        "atMonths": "Execute in {months}, ",
        "betweenMonths": "Execute every month from {start} to {end}, ",
        "everyWeekday": "Execute every weekday, ",
        "everyXWeeks": "Execute every {interval} weeks, ",
        "atWeekdays": "Execute on {weekdays}, ",
        "betweenWeekdays": "Execute every day from {start} to {end}, "
      },
      scheduler: {
        totalJobs: 'Total Jobs',
        startJobs: 'Start Jobs',
        cronJobs: 'Cron Jobs',
        nextRunTime: 'Next Run Time',
        trigger: 'Trigger',
        jobType: 'Job Type',
        startJob: 'Start Job',
        cronJob: 'Cron Job'
      }
    },
    messages: {
      success: {
        addPolicy: 'Policy added successfully',
        savePolicy: 'Policy saved successfully',
        updatePolicy: 'Policy updated successfully',
        addSubnet: 'Subnet added successfully',
        deleteSubnet: 'Subnet deleted successfully',
        deletePolicy: 'Policy deleted successfully'
      },
      confirm: {
        deleteSubnet: 'Are you sure you want to delete this subnet?',
        deletePolicy: 'Are you sure you want to delete this policy?'
      }
    },
    validation: {
      subnetName: 'Please enter subnet name',
      subnetRange: 'Please enter subnet range',
      selectExecutionTime: 'Please select execution time'
    },
    execution: {
        title: 'Execute Scan',
        selectSubnet: 'Select Subnet',
        execute: 'Execute Scan'
    },
    results: {
      title: 'Scan Results',
      ipAddress: 'IP Address',
      openPorts: 'Open Ports',
      createdAt: 'Created At',
      updatedAt: 'Updated At',
      searchPlaceholder: 'Search IP Address',
      hostCount: 'Host Count: {count}',
      resourceId: 'Resource ID',
      jobId: 'Job ID',
      noData: 'No data'
    },
  },
  settings: {
    title: 'System Settings',
    subtitle: 'Configure your system preferences including theme, language, etc.',
    sections: {
      basic: 'Basic Settings',
      interface: 'Interface Settings',
      account: 'Account Settings',
      notification: 'Notification Settings'
    },
    form: {
      language: {
        label: 'Language',
        placeholder: 'Select language',
        options: {
          zh: 'Chinese',
          en: 'English'
        }
      },
      theme: {
        label: 'Theme',
        placeholder: 'Select theme',
        options: {
          light: 'Light',
          dark: 'Dark'
        }
      },
      notifications: {
        label: 'Notifications',
        on: 'On',
        off: 'Off',
        email: {
          title: 'Email Notifications',
          enabled: 'Enable Email Notifications',
          disabled: 'Disable Email Notifications',
          smtp: {
            title: 'SMTP Server Configuration',
            host: 'SMTP Server Address',
            port: 'SMTP Port',
            username: 'SMTP Username',
            password: 'SMTP Password',
            from: 'Sender Email',
            to: 'Recipient Email',
            test: 'Test Email Configuration'
          }
        },
        wechat: {
          title: 'WeChat Notifications',
          enabled: 'Enable WeChat Notifications',
          disabled: 'Disable WeChat Notifications',
          config: {
            title: 'WeChat Configuration',
            appId: 'WeChat AppID',
            appSecret: 'WeChat AppSecret',
            templateId: 'Template Message ID',
            test: 'Test WeChat Configuration'
          }
        },
        events: {
          title: 'Notification Events',
          scan: {
            title: 'Scan Events',
            start: 'Scan Start',
            complete: 'Scan Complete',
            error: 'Scan Error'
          },
          ip: {
            title: 'IP Events',
            claim: 'IP Claim',
            release: 'IP Release',
            update: 'IP Update'
          },
          system: {
            title: 'System Events',
            error: 'System Error',
            warning: 'System Warning',
            info: 'System Info'
          }
        }
      },
      timeFormat: {
        label: 'Time Format',
        placeholder: 'Select time format',
        options: {
          '12h': '12-hour',
          '24h': '24-hour'
        }
      },
      password: {
        label: 'Change Password',
        button: 'Change Password',
        dialog: {
          title: 'Change Password',
          old: 'Old Password',
          new: 'New Password',
          confirm: 'Confirm Password'
        }
      }
    },
    validation: {
      language: 'Please select a language',
      theme: 'Please select a theme',
      oldPassword: 'Please enter old password',
      newPassword: 'Please enter new password',
      confirmPassword: 'Please confirm new password',
      smtp: {
        host: 'Please enter SMTP server address',
        port: 'Please enter SMTP port',
        username: 'Please enter SMTP username',
        password: 'Please enter SMTP password',
        from: 'Please enter sender email',
        to: 'Please enter recipient email'
      },
      wechat: {
        appId: 'Please enter WeChat AppID',
        appSecret: 'Please enter WeChat AppSecret',
        templateId: 'Please enter template message ID'
      }
    },
    messages: {
      addUserFailed: 'Failed to add user: {error}',
      saveSuccess: 'Settings saved',
      passwordMismatch: 'New password and confirm password do not match',
      passwordSuccess: 'Password changed successfully',
      passwordSuccessRedirect: 'Password changed successfully, 5 seconds will return to the login page...',
      passwordFailed: 'Failed to change password',
      updateUserFailed: 'Failed to update user: {error}',
      fetchUsersFailed: 'Failed to fetch user list',
      emailAlreadyExists: 'Email already exists',
      usernameAlreadyExists: 'Username already exists',
      unsavedChanges: 'You have unsaved changes. Are you sure you want to discard them?',
      confirmSave: 'Are you sure you want to save the current settings?',
      notification: {
        testEmailSuccess: 'Test email sent successfully',
        testEmailFailed: 'Failed to send test email',
        testWechatSuccess: 'Test WeChat message sent successfully',
        testWechatFailed: 'Failed to send test WeChat message',
        saveSuccess: 'Notification settings saved successfully',
        saveFailed: 'Failed to save notification settings'
      }
    },
    buttons: {
      save: 'Save Settings',
      cancel: 'Cancel',
      confirm: 'Confirm',
      test: 'Test Configuration'
    }
  },
  pagination: {
    total: 'Total {total} items',
    pageSize: ' items/page',
    jumper: 'Go to',
    page: 'Page',
    prev: 'Previous',
    next: 'Next',
  },
  errors: {
    database: {
      connection: 'Database connection failed, please check network connection or contact administrator'
    },
    network: 'Network connection failed, please check network settings',
    unknown: 'An unknown error occurred, please try again later'
  },
  notifications: {
    history: {
      title: 'Notification History',
      subtitle: 'View and manage system notifications',
      actions: {
        markAllAsRead: 'Mark All as Read',
        clearAll: 'Clear All Notifications'
      },
      columns: {
        title: 'Title',
        content: 'Content',
        type: 'Type',
        status: 'Status',
        createdAt: 'Created At',
        actions: 'Actions'
      },
      status: {
        read: 'Read',
        unread: 'Unread'
      },
      types: {
        scan: 'Scan',
        ip: 'IP',
        policy: 'Policy'
      },
      messages: {
        markAsReadSuccess: 'Marked as read successfully',
        markAsReadFailed: 'Failed to mark as read',
        markAllAsReadSuccess: 'All notifications marked as read',
        markAllAsReadFailed: 'Failed to mark all as read',
        deleteSuccess: 'Notification deleted successfully',
        deleteFailed: 'Failed to delete notification',
        clearAllSuccess: 'All notifications cleared',
        clearAllFailed: 'Failed to clear all notifications',
        fetchFailed: 'Failed to fetch notifications'
      }
    },
  },
  tasks: {
    title: 'Task Management',
    subtitle: 'View and manage all tasks and scan results',
    tabs: {
      running: 'Running',
      history: 'History'
    },
    refresh: {
      off: 'Auto Refresh Off',
      '1s': '1 Second',
      '5s': '5 Seconds',
      '10s': '10 Seconds',
      '30s': '30 Seconds',
      '60s': '1 Minute'
    },
    table: {
      name: 'Task Name',
      type: 'Type',
      status: 'Status',
      progress: 'Progress',
      startTime: 'Start Time',
      endTime: 'End Time',
      actions: 'Actions',
      machines_found: 'Discovery Hosts',
      error_message: 'Task Results',
      policy: {
        name: 'Policy Name',
        strategies: 'Scan Strategies',
        description: 'Policy Description',
        type: 'Policy Type',
        createTime: 'Create Time'
      }
    },
    types: {
      scan: 'Scan Task',
      backup: 'Backup Task',
      sync: 'Sync Task',
      other: 'Other Task'
    },
    status: {
      running: 'Running',
      completed: 'Completed',
      failed: 'Failed',
      stopped: 'Stopped',
      pending: 'Pending',
      cancelled: 'cancelled',
    },
    scanStatus: {
      success: 'Success',
      failed: 'Failed',
      warning: 'Warning',
      info: 'Info',
      up: 'UP',
    },
    details: {
      title: 'Task Details',
      name: 'Task Name',
      type: 'Task Type',
      status: 'Task Status',
      progress: 'Task Progress',
      startTime: 'Start Time',
      endTime: 'End Time',
      scanResults: 'Scan Results',
      ip: 'IP Address',
      resultStatus: 'Status',
      details: 'Details',
      scanTime: 'Scan Time'
    },
    actions: {
      create: 'Create Task'
    },
    messages: {
      confirmStop: 'Are you sure you want to stop this task?',
      stopSuccess: 'Task stopped successfully',
      stopFailed: 'Failed to stop task',
      loadFailed: 'Failed to load task list'
    }
  },
  monitor: {
    title: 'Resource Monitor',
    cpu: {
      title: 'CPU Usage',
      cores: 'CPU Cores',
      loadAvg1min: '1 Min Load',
      loadAvg5min: '5 Min Load',
      loadAvg15min: '15 Min Load'
    },
    memory: {
      title: 'Memory Usage',
      total: 'Total Memory',
      used: 'Used Memory',
      free: 'Free Memory'
    },
    disk: {
      title: 'Disk Usage',
      io: 'Disk IO',
      read: 'Read Speed',
      write: 'Write Speed',
      iops: 'IOPS'
    },
    process: {
      title: 'Process Count',
      list: 'Process List',
      search: 'Search Process',
      pid: 'PID',
      name: 'Process Name',
      cpuUsage: 'CPU Usage',
      memoryUsage: 'Memory Usage',
      physicalMemory: 'Physical Memory',
      virtualMemory: 'Virtual Memory',
      status: 'Status',
      threads: 'Threads',
      createTime: 'Create Time'
    },
    network: {
      title: 'Network Traffic',
      sendSpeed: 'Send Speed',
      recvSpeed: 'Receive Speed',
      errors: 'Errors',
      drops: 'Drops'
    },
    charts: {
      resourceTrend: 'Resource Usage Trend',
      send: 'Send',
      recv: 'Receive',
      read: 'Read',
      write: 'Write'
    },
    timeRange: {
      '1h': '1 Hour',
      '6h': '6 Hours',
      '24h': '24 Hours'
    }
  },
  credential: {
    title: 'Credential Management',
    subtitle: 'Manage host access credentials',
    name: 'Credential Name',
    type: 'Credential Type',
    username: 'Username',
    password: 'Password',
    privateKey: 'SSH Private Key',
    isDefault: 'Default Credential',
    actions: {
      add: 'Add Credential',
      edit: 'Edit Credential',
      delete: 'Delete Credential',
      test: 'Test Connection',
      refresh: 'Refresh List',
      viewDetail: 'View Detail',
      viewBindings: 'View Bindings',
      viewHost: 'View Host',
      copy: 'Copy',
      batchBind: 'Batch Bind',
      batchUnbind: 'Batch Unbind'
    },
    types: {
      linux: 'Linux',
      windows: 'Windows',
      vmware: 'VMware'
    },
    placeholder: {
      name: 'Enter credential name',
      username: 'Enter username',
      password: 'Enter password',
      privateKey: 'Enter SSH private key (optional)'
    },
    messages: {
      createSuccess: 'Credential created successfully',
      updateSuccess: 'Credential updated successfully',
      deleteSuccess: 'Credential deleted successfully',
      deleteConfirm: 'Are you sure to delete this credential?',
      testSuccess: 'Connection test successful',
      testFailed: 'Connection test failed',
      alreadyExists: 'Credential already exists',
      noCredentials: 'No credentials',
      bindingsCount: 'Credential "{name}" is bound to {count} hosts',
      copySuccess: 'Copied to clipboard',
      copyFailed: 'Copy failed',
      unbindConfirm: 'Are you sure to unbind {count} hosts?',
      unbindSuccess: 'Unbind successful',
      unbindFailed: 'Unbind failed'
    },
    test: {
      hostIp: 'Test Host IP',
      hostIpPlaceholder: 'Enter the host IP address to test',
      hostIpRequired: 'Please enter test host IP'
    },
    boundAt: 'Bound At'
  },
  hostInfo: {
    title: 'Host Information',
    subtitle: 'Host information management',
    ip: 'IP Address',
    hostname: 'Hostname',
    hostType: 'Host Type',
    osType: 'OS Type',
    osName: 'Operating System',
    osVersion: 'Version',
    kernel: 'Kernel',
    cpu: 'CPU',
    memory: 'Memory',
    disk: 'Disk',
    network: 'Network',
    collectionStatus: 'Collection Status',
    lastCollected: 'Last Collected',
    types: {
      physical: 'Physical Machine',
      vmware: 'VMware Virtual Machine',
      other_virtualization: 'Other Virtualization'
    },
    status: {
      pending: 'Pending',
      collecting: 'Collecting',
      success: 'Success',
      failed: 'Failed'
    },
    filters: {
      all: 'All',
      search: 'Search Hosts'
    },
    collectionProgress: {
      title: 'Collection Progress',
      total: 'Total',
      completed: 'Completed',
      failed: 'Failed',
      currentStep: 'Current Step',
      error: 'Error Message',
      noData: 'No progress data',
      status: {
        running: 'Running',
        completed: 'Completed',
        failed: 'Failed',
        cancelled: 'Cancelled'
      }
    },
    credential: 'Credential',
    tabs: {
      basic: 'Basic Info',
      hardware: 'Hardware Info',
      network: 'Network Info',
      disk: 'Disk Info',
      vmware: 'VMware Info',
      raw: 'Raw Data',
      hostList: 'Host List',
      taskHistory: 'Collection Task History'
    },
    credentialInfo: {
      currentCredential: 'Current Credential',
      changeCredential: 'Change Credential',
      selectNewCredential: 'Select New Credential',
      sameCredential: 'Selected credential is the same as the current one',
      noMatchingCredential: 'No matching credentials (check host type and OS type)'
    },
    collectionTask: {
      taskId: 'Task ID',
      taskStatus: 'Task Status',
      progress: 'Progress',
      totalHosts: 'Total Hosts',
      successCount: 'Success',
      failedCount: 'Failed',
      createdAt: 'Created At',
      endTime: 'End Time',
      relatedHosts: 'Related Hosts',
      viewDetails: 'View Details',
      cancel: 'Cancel',
      cancelTask: 'Cancel Task',
      confirmCancel: 'Are you sure you want to cancel this collection task? You can restart it after cancellation.',
      cancelSuccess: 'Task cancelled successfully',
      cancelFailed: 'Failed to cancel task',
      autoRefresh: 'Auto Refresh',
      refreshInterval: 'Refresh Interval',
      tableView: 'Table View',
      timelineView: 'Timeline View',
      filterStatus: 'Filter Status',
      status: {
        pending: 'Pending',
        running: 'Running',
        completed: 'Completed',
        failed: 'Failed',
        cancelled: 'Cancelled'
      },
      errorMessage: 'Error Message'
    },
    actions: {
      refresh: 'Refresh',
      collect: 'Collect',
      batchCollect: 'Batch Collect',
      bindCredential: 'Bind Credential',
      batchBindCredential: 'Batch Bind Credential',
      unbindCredential: 'Unbind Credential',
      selectCredential: 'Select Credential',
      export: 'Export',
      batchExport: 'Batch Export',
      viewDetails: 'View Details',
      cancelCollection: 'Cancel Collection'
    },
    messages: {
      collectSuccess: 'Collection task started',
      collectFailed: 'Collection task start failed',
      collectStarted: 'Collection task started',
      bindSuccess: 'Credential bound successfully',
      bindFailed: 'Credential bind failed',
      unbindSuccess: 'Credential unbound successfully',
      exportSuccess: 'Export successful',
      exportFailed: 'Export failed',
      noHosts: 'No host information',
      credentialRequired: 'Please select a credential',
      credentialRequiredTitle: 'Credential Required',
      batchBindInfo: 'Will bind {count} hosts to the selected credential',
      noRunningTask: 'No running collection task found, list refreshed',
      loadChildrenFailed: 'Failed to load child nodes',
      noValidHostsForBind: 'No valid hosts for binding credentials (VMware child hosts cannot bind credentials)',
      someHostsSkipped: 'Skipped {count} VMware child hosts',
      credentialRequiredForCollection: 'Host {hostName} has no credential bound. Please bind a credential before collection.',
      vmwareChildNeedParentCredential: 'VMware child host requires parent host ({hostName}) credential for collection. Please bind credential to parent host first.',
      batchCollectCredentialRequired: 'The following hosts have no credentials bound. Please bind credentials before collection: {hostNames}',
      confirmBatchCollect: 'Confirm Batch Collection',
      batchCollectPartial: 'Only {count} hosts have credentials bound. Collect only these hosts?',
      noValidHostsForCollect: 'No valid hosts for collection (all hosts have no credentials bound)',
      loadDetailsFailed: 'Failed to load host details, showing basic information'
    },
    detail: {
      network: {
        interface: 'Interface',
        deviceName: 'Device Name',
        deviceId: 'Device ID',
        macAddress: 'MAC Address',
        ipAddress: 'IP Address',
        connectionStatus: 'Connection Status',
        connected: 'Connected',
        disconnected: 'Disconnected',
        networkName: 'Network Name',
        network: 'Network',
        addressType: 'Address Type',
        portgroup: 'Port Group',
        wakeOnLan: 'Wake-on-LAN',
        enabled: 'Enabled',
        disabled: 'Disabled',
        interfaceType: 'Interface Type',
        speed: 'Speed',
        state: 'State',
        noData: 'No network interface information'
      },
      disk: {
        disk: 'Disk',
        deviceName: 'Device Name',
        mountPoint: 'Mount Point',
        capacity: 'Capacity',
        capacityKB: 'Capacity (KB)',
        freeSpace: 'Free Space',
        usedSpace: 'Used Space',
        usageRate: 'Usage Rate',
        fileSystem: 'File System',
        volumeName: 'Volume Name',
        diskMode: 'Disk Mode',
        thinProvisioned: 'Thin Provisioned',
        yes: 'Yes',
        no: 'No',
        eagerlyScrub: 'Eagerly Scrub',
        uuid: 'UUID',
        fileName: 'File Name',
        datastore: 'Datastore',
        deviceType: 'Device Type',
        vendor: 'Vendor',
        model: 'Model',
        noData: 'No disk information'
      },
      raw: {
        noData: 'No raw data'
      }
    },
    driveTypes: {
      unknown: 'Unknown',
      noRoot: 'No Root Directory',
      removable: 'Removable Disk',
      fixed: 'Fixed Disk',
      network: 'Network Drive',
      cdrom: 'CD-ROM',
      ram: 'RAM Disk',
      type: 'Type'
    }
  },
  collection: {
    title: 'Collection Tasks',
    taskId: 'Task ID',
    triggerType: 'Trigger Type',
    status: 'Status',
    totalHosts: 'Total Hosts',
    successCount: 'Success',
    failedCount: 'Failed',
    startTime: 'Start Time',
    endTime: 'End Time',
    triggerTypes: {
      auto: 'Auto Trigger',
      manual: 'Manual Trigger'
    },
    statuses: {
      pending: 'Pending',
      running: 'Running',
      completed: 'Completed',
      failed: 'Failed'
    },
    messages: {
      noTasks: 'No collection tasks'
    }
  },
  export: {
    title: 'Batch Export Configuration',
    selectedHosts: 'Selected {count} hosts',
    selectedFields: 'Selected {count} fields',
    selectFields: 'Select Export Fields',
    selectTemplate: 'Quick Templates',
    searchPlaceholder: 'Search field names...',
    selected: 'Selected',
    templates: {
      basic: 'Basic Info',
      detailed: 'Detailed Info',
      full: 'Full Info'
    },
    templateNames: {
      basic: 'Basic Info',
      detailed: 'Detailed Info',
      full: 'Full Info'
    },
    fieldCategories: {
      basic: 'Basic',
      system: 'System',
      hardware: 'Hardware',
      network: 'Network',
      storage: 'Storage',
      vmware: 'VMware',
      status: 'Status'
    },
    fieldLabels: {
      'ip_address': 'IP Address',
      'hostname': 'Hostname',
      'host_type': 'Host Type',
      'os_name': 'Operating System',
      'os_version': 'OS Version',
      'kernel_version': 'Kernel Version',
      'cpu_model': 'CPU Model',
      'cpu_cores': 'CPU Cores',
      'memory_total': 'Total Memory (MB)',
      'network_interfaces': 'Network Interfaces',
      'disk_info': 'Disk Information',
      'vmware_info': 'VMware Information',
      'collection_status': 'Collection Status',
      'last_collected_at': 'Last Collected At',
      'collection_error': 'Collection Error'
    },
    actions: {
      export: 'Export',
      cancel: 'Cancel',
      selectAll: 'Select All',
      deselectAll: 'Clear All',
      expandAll: 'Expand All',
      collapseAll: 'Collapse All'
    },
    messages: {
      noFieldsSelected: 'Please select at least one field',
      exportSuccess: 'Export successful',
      exportFailed: 'Export failed'
    }
  }
};