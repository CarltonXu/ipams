export default {
  common: {
    success: 'Operation Successful',
    error: 'Operation Failed',
    fetchError: 'Failed to fetch data',
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
    invalidUsernameOrPassword: 'Invalid username or password',
    tokenExpired: 'Login expired, please login again',
    invalidCaptcha: 'Invalid or expired captcha',
    title: 'IPAM System Platform',
    subtitle: 'Monitor and manage your network with ease',
    registerSubtitle: 'Create an account to manage your network',
    noAccount: 'No account yet?',
    hasAccount: 'Already have an account?',
    confirmPassword: 'Confirm Password',
    confirmPasswordPlaceholder: 'Please enter password again',
    registerSuccess: 'Register Successful',
    registerError: 'Register Failed',
    validation: {
      username: 'Please enter username',
      usernameLength: 'Username must be at least 3 characters long',
      email: {
        required: 'Please enter email',
        invalid: 'Please enter a valid email address'
      },
      password: 'Please enter password',
      passwordLength: 'Password must be at least 6 characters long',
      confirmPassword: 'Please confirm password',
      passwordMismatch: 'Passwords do not match'
    },
    captcha: 'Captcha',
    captchaPlaceholder: 'Please enter captcha',
    captchaError: 'Failed to get captcha',
    captchaRefresh: 'Refresh Captcha',
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
      table: {
        columns: {
          uuid: 'UUID',
          username: 'Username',
          email: 'Email',
          createdAt: 'Created At',
          isAdmin: 'Admin',
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
          isAdmin: 'Admin'
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
        deleteSelfError: 'Cannot delete yourself'
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
    title: 'IP Address Management',
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
        execute: {
          title: 'Execute Scan',
          policyName: 'Policy Name',
          selectSubnets: 'Select Subnets',
          confirm: 'Confirm Execute Scan',
          noSubnets: 'Please select at least one subnet',
          success: 'Scan executed successfully',
          error: 'Failed to execute scan'
        },
        show: {
          columns: {
            name: 'Policy Name',
            description: 'Policy Description',
            strategy: 'Policy Execution Cron',
            startTime: 'Start Time',
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
            fetchFailed: 'Failed to fetch policy list',
            deleteFailed: 'Failed to delete policy',
            updateFailed: 'Failed to update policy'
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
  },
  settings: {
    title: 'System Settings',
    subtitle: 'Configure your system preferences including theme, language, etc.',
    sections: {
      basic: 'Basic Settings',
      interface: 'Interface Settings',
      account: 'Account Settings'
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
        off: 'Off'
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
      confirmPassword: 'Please confirm new password'
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
      usernameAlreadyExists: 'Username already exists'
    },
    buttons: {
      save: 'Save Settings',
      cancel: 'Cancel',
      confirm: 'Confirm'
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
};