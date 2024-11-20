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
          <el-button type="text" class="upload-btn">更换头像</el-button>
        </el-upload>
      </div>
      <div class="user-details">
        <p class="username">{{ user.username }}</p>
        <p class="email">{{ user.email }}</p>
        <p class="wechat_id">{{ user.wechat_id || "待补充" }}</p>
      </div>
      <el-button type="primary" @click="editProfile" class="edit-btn">编辑资料</el-button>
    </el-card>

    <el-dialog title="编辑个人资料" v-model="isEditing" class="edit-dialog">
      <el-form :model="form" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" />
        </el-form-item>
        <el-form-item label="Wechat ID">
          <el-input v-model="form.wechat_id" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="isEditing = false">取消</el-button>
        <el-button type="primary" @click="saveProfile">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
  
<script setup lang="ts">
import { ref, computed } from 'vue';
import { useAuthStore } from '../stores/auth';

const authStore = useAuthStore();
const user = computed(() => authStore.user);

const isEditing = ref(false);
const form = ref({ username: user.value.username, email: user.value.email });

const uploadUrl = '/api/upload-avatar'; // 替换为实际上传地址

const editProfile = () => {
  form.value = { ...user.value };
  isEditing.value = true;
};

const saveProfile = () => {
  authStore.updateUser(form.value);
  isEditing.value = false;
};

const updateAvatar = (response: any) => {
  authStore.updateUser({ avatar: response.url });
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
