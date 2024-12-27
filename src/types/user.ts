export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterCredentials {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export interface User {
  id: string;
  username: string;
  email: string;
  avatar?: string;
  wechat_id?: string;
  created_at: string;
  is_admin: boolean;
}

export interface AuthState {
  user: User | null;
  token: string | null;
}

export interface updatePassword {
  id: string;
  old_password: string;
  new_password: string;
}

export interface UpdateUser {
  id: string;
  username: string;
  email: string;
  avator: string;
  wechat_id: string;
}