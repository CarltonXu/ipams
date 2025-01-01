<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <!-- 头部区域 -->
      <div class="profile-header">
        <div class="avatar-section">
          <el-avatar 
            :src="user.avatar" 
            :size="120"
            class="avatar"
          />
          <el-upload
            class="avatar-upload"
            :action="uploadUrl"
            :headers="uploadHeaders"
            :show-file-list="false"
            accept="image/*"
            :on-success="updateAvatar"
            :on-error="handleUploadError"
            :before-upload="beforeUpload"
          >
            <el-button type="primary" class="upload-btn" size="small">
              {{ $t('profile.changeAvatar') }}
            </el-button>
          </el-upload>
        </div>
        
        <div class="user-basic-info">
          <h1 class="username">{{ user.username }}</h1>
          <span class="role-tag">
            <el-tag :type="user.is_admin ? 'danger' : 'info'" size="small">
              {{ user.is_admin ? $t('profile.role.admin') : $t('profile.role.user') }}
            </el-tag>
          </span>
        </div>
      </div>

      <!-- 信息卡片区域 -->
      <div class="info-section">
        <el-descriptions :column="1" border>
          <el-descriptions-item :label="$t('profile.fields.id')">
            {{ user.id }}
          </el-descriptions-item>
          <el-descriptions-item :label="$t('profile.fields.email')">
            {{ user.email }}
          </el-descriptions-item>
          <el-descriptions-item :label="$t('profile.fields.wechatId')">
            {{ user.wechat_id || $t('profile.wechatPlaceholder') }}
          </el-descriptions-item>
          <el-descriptions-item :label="$t('profile.fields.createdAt')">
            {{ formatDate(user.created_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 操作按钮区域 -->
      <div class="action-section">
        <el-button type="primary" @click="editProfile" class="edit-btn">
          <el-icon><Edit /></el-icon>
          {{ $t('profile.editProfile') }}
        </el-button>
        <el-button @click="changePassword" class="password-btn">
          <el-icon><Lock /></el-icon>
          {{ $t('profile.changePassword') }}
        </el-button>
      </div>
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog 
      :title="$t('profile.editDialogTitle')" 
      v-model="isEditing" 
      width="500px"
      destroy-on-close
    >
      <el-form 
        :model="form" 
        :rules="rules"
        ref="formRef"
        label-position="top"
      >
        <el-form-item :label="$t('profile.fields.username')" prop="username">
          <el-input v-model="form.username" disabled />
        </el-form-item>
        <el-form-item :label="$t('profile.fields.email')" prop="email">
          <el-input v-model="form.email" type="email" />
        </el-form-item>
        <el-form-item :label="$t('profile.fields.wechatId')" prop="wechat_id">
          <el-input v-model="form.wechat_id" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="isEditing = false">
          {{ $t('profile.buttons.cancel') }}
        </el-button>
        <el-button type="primary" @click="saveProfile">
          {{ $t('profile.buttons.save') }}
        </el-button>
      </template>
    </el-dialog>

    <el-dialog 
      :title="$t('profile.changePasswordTitle')" 
      v-model="isChangingPassword" 
      width="500px"
      destroy-on-close
    >
      <el-form 
        :model="passwordForm" 
        :rules="passwordRules"
        ref="passwordFormRef"
        label-position="top"
      >
        <el-form-item :label="$t('profile.fields.oldPassword')" prop="oldPassword">
          <el-input 
            v-model="passwordForm.oldPassword" 
            type="password" 
            :show-password="true"
          />
        </el-form-item>
        <el-form-item :label="$t('profile.fields.newPassword')" prop="newPassword">
          <el-input 
            v-model="passwordForm.newPassword" 
            type="password" 
            :show-password="true"
          />
        </el-form-item>
        <el-form-item :label="$t('profile.fields.confirmPassword')" prop="confirmPassword">
          <el-input 
            v-model="passwordForm.confirmPassword" 
            type="password" 
            :show-password="true"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="isChangingPassword = false">
          {{ $t('profile.buttons.cancel') }}
        </el-button>
        <el-button type="primary" @click="handleChangePassword">
          {{ $t('profile.buttons.save') }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useUserStore } from '../stores/user'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Edit, Lock } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { useRouter } from 'vue-router'

const { t } = useI18n()
const authStore = useAuthStore()
const userStore = useUserStore()
const router = useRouter()
const user = computed(() => authStore.user)
const isEditing = ref(false)
const formRef = ref()
const isChangingPassword = ref(false)
const passwordFormRef = ref()
const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const uploadUrl = '/api/users/upload-avatar'

const form = ref({
  username: '',
  email: '',
  wechat_id: ''
})

const rules = {
  email: [
    { required: true, message: t('profile.validation.emailRequired'), trigger: 'blur' },
    { type: 'email', message: t('profile.validation.emailFormat'), trigger: 'blur' }
  ],
  wechat_id: [
    { required: true, message: t('profile.validation.wechatIdRequired'), trigger: 'blur' },
    { min: 2, max: 20, message: t('profile.validation.wechatIdLength'), trigger: 'blur' }
  ]
}

const passwordRules = {
  oldPassword: [
    { required: true, message: t('profile.validation.oldPasswordRequired'), trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: t('profile.validation.newPasswordRequired'), trigger: 'blur' },
    { min: 6, message: t('profile.validation.passwordLength'), trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: t('profile.validation.confirmPasswordRequired'), trigger: 'blur' },
    {
      validator: (rule: any, value: string, callback: Function) => {
        if (value !== passwordForm.value.newPassword) {
          callback(new Error(t('profile.validation.passwordMismatch')))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const formatDate = (date: string) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

const uploadHeaders = computed(() => {
  return {
    Authorization: `Bearer ${authStore.token}`
  }
})

const editProfile = () => {
  form.value = { 
    username: user.value.username,
    email: user.value.email,
    wechat_id: user.value.wechat_id || ''
  }
  isEditing.value = true
}

const saveProfile = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        await authStore.updateUserInfo({
          email: form.value.email,
          wechat_id: form.value.wechat_id
        })
        isEditing.value = false
        ElMessage.success(t('profile.messages.updateSuccess'))
      } catch (error) {
        ElMessage.error(t('profile.messages.updateFailed'))
      }
    }
  })
}

const updateAvatar = async (response: any) => {
  try {
    // 使用 store 的方法更新用户信息
    authStore.updateUserInfo({
      avatar: response.url
    })
    ElMessage.success(t('profile.messages.avatarSuccess'))
  } catch (error) {
    ElMessage.error(t('profile.messages.avatarFailed'))
  }
}

const handleUploadError = (err: any, file: any) => {
  let errorMessage = t('profile.messages.avatarFailed');
  
  // 处理错误响应
  if (err.response) {
    try {
      const response = JSON.parse(err.response);
      errorMessage = response.error || errorMessage;
    } catch (e) {
      // 如果解析失败，尝试直接获取错误信息
      errorMessage = err.response.error || errorMessage;
    }
  }
  
  ElMessage.error(errorMessage);
};

// 添加上传前的验证
const beforeUpload = (file: File) => {
  // 验证文件类型
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
  if (!allowedTypes.includes(file.type)) {
    ElMessage.error(t('profile.messages.invalidFileType'));
    return false;
  }
  
  // 验证文件大小（例如：2MB）
  const maxSize = 2 * 1024 * 1024;
  if (file.size > maxSize) {
    ElMessage.error(t('profile.messages.fileTooLarge'));
    return false;
  }
  
  return true;
};

const changePassword = () => {
  isChangingPassword.value = true
  passwordForm.value = {
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  }
}

const handleChangePassword = async () => {
  if (!passwordFormRef.value) return
  
  await passwordFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        await userStore.updatePassword(
          user.id,
          passwordForm.value.oldPassword,
          passwordForm.value.newPassword
        )
        isChangingPassword.value = false
        ElMessage.success(t('profile.messages.passwordSuccess'))

        // 显示提示信息并倒计时
        ElMessage({
          type: 'success',
          message: t('profile.messages.passwordSuccessRedirect'),
          duration: 5000  // 显示5秒
        });

        // 密码修改成功后，5秒后登出并跳转到登录页
        setTimeout(async () => {
          await authStore.logout()
          router.push('/login')
        }, 5000)
        
      } catch (error: any) {
        ElMessage.error(error.message || t('profile.messages.passwordFailed'))
      }
    }
  })
}
</script>

<style scoped>
.profile-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.profile-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 40px;
  padding: 20px 0;
  border-bottom: 1px solid var(--el-border-color-light);
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.avatar {
  border: 4px solid var(--el-color-primary-light-8);
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
  transition: transform 0.3s ease;
}

.avatar:hover {
  transform: scale(1.05);
}

.user-basic-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.username {
  margin: 0;
  font-size: 24px;
  color: var(--el-text-color-primary);
}

.role-tag {
  margin-top: 4px;
}

.info-section {
  padding: 24px 0;
}

.action-section {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding-top: 20px;
  border-top: 1px solid var(--el-border-color-light);
}

.edit-btn, .password-btn {
  display: flex;
  align-items: center;
  gap: 8px;
}

:deep(.el-descriptions__label) {
  width: 120px;
}

:deep(.el-dialog__body) {
  padding-top: 20px;
}
</style>
