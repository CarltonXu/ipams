export interface IP {
  id: string;
  ip_address: string;
  os_version: string;
  status: 'active' | 'inactive' | 'unclaimed';
  assigned_user_id: string | null;
  device_name: string;
  purpose: string;
  last_scanned: string;
  updated_at: string;
}

export interface User {
  id: string;
  username: string;
  email: string;
  wechat_id: string;
}