/**
 * 主机信息相关类型定义
 */

export type HostType = 'physical' | 'vmware' | 'other_virtualization';

export type CollectionStatus = 'pending' | 'collecting' | 'success' | 'failed';

export interface HostInfo {
  id: string;
  ip_id: string;
  scan_result_id?: string;
  parent_host_id?: string;
  host_type?: HostType;
  hostname?: string;
  os_name?: string;
  os_version?: string;
  kernel_version?: string;
  cpu_model?: string;
  cpu_cores?: number;
  memory_total?: number;
  disk_info?: any;
  network_interfaces?: any;
  vmware_info?: any;
  collection_status: CollectionStatus;
  collection_error?: string;
  last_collected_at?: string;
  raw_data?: any;
  created_at: string;
  updated_at: string;
  ip?: {
    id: string;
    ip_address: string;
    status: string;
    device_name?: string;
    os_type?: string;
  };
  child_hosts?: HostInfo[];  // 子主机列表（树形结构）
  credential_bindings?: HostInfoBinding[];  // 绑定的凭证
}

export interface HostInfoBinding {
  id: string;
  host_id: string;
  credential_id: string;
  created_at: string;
  credential?: any;
}

export interface HostInfoListResponse {
  hosts: HostInfo[];
  total: number;
  pages: number;
  page_size: number;
  current_page: number;
}

export interface HostInfoBindCredentialRequest {
  credential_id: string;
}

export interface HostInfoCollectRequest {
  credential_id?: string;
  username?: string;
  password?: string;
  private_key?: string;
  port?: number;
}

export interface HostInfoCollectResponse {
  message: string;
  result?: any;
  error?: string;
}

export interface HostInfoBatchCollectRequest {
  host_ids: string[];
}

export interface HostInfoBatchCollectResponse {
  message: string;
  task_id: string;
}

export interface HostInfoCollectionHistory {
  last_collected_at?: string;
  collection_status: CollectionStatus;
  collection_error?: string;
}

export interface ExportTemplate {
  id: string;
  name: string;
  field_count: number;
}

export interface ExportField {
  field: string;
  label: string;
  category: string;
}

export interface ExportRequest {
  host_ids: string[];
  fields?: string[];
  template?: string;
}

export interface ExportTemplatesResponse {
  templates: ExportTemplate[];
}

export interface ExportFieldsResponse {
  fields: ExportField[];
}

export interface HostInfoBatchBindRequest {
  host_ids: string[];
  credential_id: string;
}

export interface HostInfoBatchUnbindRequest {
  host_ids: string[];
  credential_id: string;
}

