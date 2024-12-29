export interface IP {
  id: string;
  ip_address: string;
  status: 'active' | 'inactive' | 'unclaimed';
  assigned_user_id: string | null;
  device_name: string;
  device_type: string;
  manufacturer: string;
  model: string;
  os_type: string;
  purpose: string;
  location: string;
  last_scanned: string;
  updated_at: string;
  assigned_user?: User | null;
}

export interface User {
  id: string;
  username: string;
  email: string;
  wechat_id: string;
}