export interface LoginCredentials {
  username: string;
  password: string;
  captcha: string;      // 用户输入的验证码
  captchaKey: string;   // 验证码标识
}

export interface CaptchaResponse {
  captchaKey: string;    // 验证码唯一标识
  captchaImage: string;  // Base64 编码的验证码图片
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
  status: 'active' | 'inactive' | 'suspended';
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

export interface UpdateUserAvatar {
  id: string;
  avatar: File;
}

export interface UserResponse {
  users: User[];
  total: number;
  page: number;
  pages: number;
}