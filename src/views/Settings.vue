<!-- src/views/Settings.vue -->
<template>
  <div class="settings">
    <el-form :model="settings" label-width="120px" @submit.prevent="saveSettings">
      <el-form-item label="语言" :rules="[{ required: true, message: '请选择语言' }]">
        <el-select v-model="settings.language" placeholder="选择语言">
          <el-option label="中文" value="zh"></el-option>
          <el-option label="英文" value="en"></el-option>
        </el-select>
      </el-form-item>

      <el-form-item label="主题" :rules="[{ required: true, message: '请选择主题' }]">
        <el-select v-model="settings.theme" placeholder="选择主题">
          <el-option label="浅色" value="light"></el-option>
          <el-option label="深色" value="dark"></el-option>
        </el-select>
      </el-form-item>

      <el-form-item label="修改密码">
        <el-button @click="showChangePasswordDialog" type="primary">修改密码</el-button>
      </el-form-item>

      <el-button type="primary" @click="saveSettings">保存设置</el-button>
    </el-form>

    <!-- 修改密码对话框 -->
    <el-dialog :visible.sync="changePasswordDialogVisible" title="修改密码" width="400px">
      <el-form :model="passwordForm">
        <el-form-item label="旧密码" :rules="[{ required: true, message: '请输入旧密码' }]">
          <el-input v-model="passwordForm.oldPassword" type="password" />
        </el-form-item>
        <el-form-item label="新密码" :rules="[{ required: true, message: '请输入新密码' }]">
          <el-input v-model="passwordForm.newPassword" type="password" />
        </el-form-item>
        <el-form-item label="确认密码" :rules="[{ required: true, message: '请确认新密码' }]">
          <el-input v-model="passwordForm.confirmPassword" type="password" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="changePasswordDialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="changePassword">确 定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { ElMessage } from 'element-plus';

// 系统设置的数据模型
const settings = ref({
  language: 'zh',
  theme: 'light'
});

// 修改密码的表单数据
const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
});

// 控制修改密码对话框显示
const changePasswordDialogVisible = ref(false);

// 保存系统设置
const saveSettings = () => {
  // 假设有 API 请求保存设置
  ElMessage.success('设置已保存');
};

// 显示修改密码对话框
const showChangePasswordDialog = () => {
  changePasswordDialogVisible.value = true;
};

// 执行修改密码操作
const changePassword = () => {
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    ElMessage.error('新密码与确认密码不匹配');
    return;
  }
  
  // 假设有修改密码的 API 请求
  ElMessage.success('密码修改成功');
  changePasswordDialogVisible.value = false;
};
</script>

<style scoped>
.settings {
  padding: 20px;
}

.dialog-footer {
  text-align: right;
}
</style>