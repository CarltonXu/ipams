/**
 * 凭证管理相关类型定义
 */

export type CredentialType = 'linux' | 'windows' | 'vmware';

export interface Credential {
  id: string;
  user_id: string;
  name: string;
  credential_type: CredentialType;
  username: string;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

export interface CredentialFormData {
  name: string;
  credential_type: CredentialType;
  username: string;
  password?: string;
  private_key?: string;
  is_default?: boolean;
}

export interface CredentialCreateRequest {
  name: string;
  credential_type: CredentialType;
  username: string;
  password?: string;
  private_key?: string;
  is_default?: boolean;
}

export interface CredentialUpdateRequest {
  name?: string;
  credential_type?: CredentialType;
  username?: string;
  password?: string;
  private_key?: string;
  is_default?: boolean;
}

export interface CredentialResponse {
  credentials: Credential[];
}

export interface CredentialTestRequest {
  host_ip?: string;
  vcenter_host?: string;
}

export interface CredentialTestResponse {
  success: boolean;
  message: string;
}

export interface CredentialBindRequest {
  host_ids: string[];
}

export interface CredentialUnbindRequest {
  host_ids: string[];
}
