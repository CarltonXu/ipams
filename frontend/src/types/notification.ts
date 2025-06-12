export interface NotificationConfig {
  emailConfig: {
    enabled: boolean;
    smtpServer: string;
    smtpPort: number;
    smtpUsername: string;
    smtpPassword: string;
    smtpFrom: string;
  };
  wechatConfig: {
    enabled: boolean;
    webhookUrl: string;
  };
  eventConfig: {
    scanCompleted: boolean;
    scanFailed: boolean;
    ipClaimed: boolean;
    ipReleased: boolean;
    policyCreated: boolean;
    policyUpdated: boolean;
    policyDeleted: boolean;
  };
}

export interface Notification {
  id: string;
  title: string;
  content: string;
  type: 'scan' | 'ip' | 'policy';
  read: boolean;
  created_at: string;
  updated_at: string;
}

export interface NotificationFilters {
  type?: 'scan' | 'ip' | 'policy';
  status?: 'read' | 'unread';
  dateRange?: [Date, Date];
  page: number;
  per_page: number;
}

export interface NotificationResponse {
  data: Notification[];
  total: number;
} 