<template>
  <div class="profile-page">
    <el-card class="profile-card">
      <div class="profile-header">
        <el-avatar 
          :src="user.avatar" 
          size="large" 
          class="avatar"
          @click="changeAvatar"
        />
        <el-upload
          class="upload-avatar"
          :action="uploadUrl"
          accept="image/*"
          show-file-list="false"
          @success="updateAvatar"
        >
          <el-button type="text" class="upload-btn">{{ $t('profile.changeAvatar') }}</el-button>
        </el-upload>
      </div>
      <div class="user-details">
        <p class="username">{{ user.username }}</p>
        <p class="email">{{ user.email }}</p>
        <p class="wechat_id">{{ user.wechat_id || $t('profile.wechatPlaceholder') }}</p>
      </div>
      <el-button type="primary" @click="editProfile" class="edit-btn">
        {{ $t('profile.editProfile') }}
      </el-button>
    </el-card>

    <el-dialog :title="$t('profile.editDialogTitle')" v-model="isEditing" class="edit-dialog">
      <el-form :model="form" label-width="80px">
        <el-form-item :label="$t('profile.fields.username')">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item :label="$t('profile.fields.email')">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item :label="$t('profile.fields.wechatId')">
          <el-input v-model="form.wechat_id" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="isEditing = false">{{ $t('profile.buttons.cancel') }}</el-button>
        <el-button type="primary" @click="saveProfile">{{ $t('profile.buttons.save') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>
  
<script setup lang="ts">
import { ref, computed } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useI18n } from 'vue-i18n';
import { ElMessage } from 'element-plus';

const { t } = useI18n();
const authStore = useAuthStore();
const user = computed(() => authStore.user);

const isEditing = ref(false);
const form = ref({ username: user.value.username, email: user.value.email });

const uploadUrl = '/api/upload-avatar';

const editProfile = () => {
  form.value = { ...user.value };
  isEditing.value = true;
};

const saveProfile = async () => {
  try {
    await authStore.updateUser(form.value);
    isEditing.value = false;
    ElMessage.success(t('profile.messages.updateSuccess'));
  } catch (error) {
    ElMessage.error(t('profile.messages.updateFailed'));
  }
};

const updateAvatar = async (response: any) => {
  try {
    await authStore.updateUser({ avatar: response.url });
    ElMessage.success(t('profile.messages.avatarSuccess'));
  } catch (error) {
    ElMessage.error(t('profile.messages.avatarFailed'));
  }
};
</script>

<style scoped>
.profile-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f5f7fa;
  padding: 20px;
}

.profile-card {
  max-width: 400px;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  text-align: center;
  background: white;
}

.profile-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
  gap: 10px;
}

.avatar {
  cursor: pointer;
  border: 2px solid #409eff;
  transition: transform 0.3s;
}

.avatar:hover {
  transform: scale(1.1);
}

.upload-avatar {
  margin-top: 10px;
}

.upload-btn {
  font-size: 12px;
  color: #409eff;
  padding: 0;
}

.user-details {
  margin-bottom: 20px;
}

.username {
  font-size: 18px;
  font-weight: 500;
  margin-bottom: 5px;
}

.email, .wechat_id {
  font-size: 14px;
  color: #888;
}

.edit-btn {
  width: 100%;
}

::v-deep(.edit-dialog) {
  width: 20%;
}
</style>
