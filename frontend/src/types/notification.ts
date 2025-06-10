export interface NotificationConfig {
  ENABLE_EMAIL_NOTIFICATION: string;
  SMTP_SERVER: string;
  SMTP_PORT: string;
  SMTP_USERNAME: string;
  SMTP_PASSWORD: string;
  SMTP_FROM: string;
  ENABLE_WECHAT_NOTIFICATION: string;
  WECHAT_WEBHOOK_URL: string;
  NOTIFY_SCAN_COMPLETED: string;
  NOTIFY_SCAN_FAILED: string;
  NOTIFY_IP_CLAIMED: string;
  NOTIFY_IP_RELEASED: string;
  NOTIFY_POLICY_CREATED: string;
  NOTIFY_POLICY_UPDATED: string;
  NOTIFY_POLICY_DELETED: string;
}

export interface Notification {
  id: number;
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