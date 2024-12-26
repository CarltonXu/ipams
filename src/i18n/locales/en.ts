export default {
  common: {
    success: 'Operation Successful',
    error: 'Operation Failed',
    confirm: 'Confirm',
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
  },
  menu: {
    home: 'Home',
    ipManagement: 'IP Management',
    scanConfig: 'Scan Config',
    settings: 'Settings',
    userManagement: 'User Management',
  },
  auth: {
    login: 'Login',
    logout: 'Logout',
    register: 'Register',
    username: 'Username',
    password: 'Password',
    email: 'Email',
    loginSuccess: 'Login Successful',
    loginError: 'Login Failed',
    tokenExpired: 'Login expired, please login again',
  },
  user: {
    profile: 'Profile',
    settings: 'Settings',
    account: 'Account',
    changePassword: 'Change Password',
    currentUser: 'Current User',
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
    title: 'IP Address Management',
    subtitle: 'Easily manage your IP addresses with filters and search functionality',
    search: 'Search IPs, devices, or purpose',
    status: {
      all: 'All Status',
      active: 'Active',
      inactive: 'Inactive',
      unclaimed: 'Unclaimed',
      description: {
        active: 'This IP is currently active',
        inactive: 'This IP is not in use',
        unclaimed: 'This IP is available for claiming',
        danger: 'Unknown status'
      }
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
      updateSuccess: 'Successfully updated IP: {ip}'
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
        required: 'Required',
      }
    }
  },
  profile: {
    title: 'Profile',
    changeAvatar: 'Change Avatar',
    editProfile: 'Edit Profile',
    editDialogTitle: 'Edit Profile',
    wechatPlaceholder: 'Not Set',
    fields: {
      username: 'Username',
      email: 'Email',
      wechatId: 'WeChat ID',
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
      confirm: {
        save: 'Confirm to save current configuration?',
        execute: 'Confirm to execute scan?'
      },
      tips: {
        weekDays: 'Please select at least one weekday',
        monthDays: 'Please select at least one day',
        customCron: 'Cron expression format: minute hour day month weekday'
      }
    },
    policy: {
        title: 'Scan Policy Configuration',
        name: 'Policy Name',
        namePlaceholder: 'Please enter policy name',
        type: 'Policy Type',
        typeRequired: 'Please select policy type',
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
        description: {
          everyMinute: 'Every {minutes} minutes, starting from {time}',
          everyHour: 'Every {hours} hours, starting from {time}',
          everyDay: 'Every {days} days, starting from {time}',
          everyWeek: 'Every {weekdays}, starting from {time}',
          everyMonth: 'Every month on {days}, starting from {time}',
          custom: 'Custom execution: {cron}'
        },
        show: {
          columns: {
            name: 'Policy Name',
            description: 'Policy Description',
            createdAt: 'Created At',
            subnets: 'Scan Subnets',
            status: {
                title: 'Status',
                active: 'Active',
                inactive: 'Inactive'
            },
            actions: {
              title: 'Actions',
              enable: 'Enable',
              disable: 'Disable',
              edit: 'Edit',
              delete: 'Delete'
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
            updateSuccess: 'Policy updated successfully'
          }
        }
      },
    messages: {
      success: {
        addPolicy: 'Policy added successfully',
        savePolicy: 'Policy saved successfully',
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
  }
};