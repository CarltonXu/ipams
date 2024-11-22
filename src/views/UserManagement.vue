<template>
  <div class="user-management">
    <el-card class="box-card">
      <el-row justify="space-between" align="middle" class="header-row">
        <h2>用户管理</h2>
        <el-button v-if="isAdmin" type="primary" size="medium" @click="openUserDialog">
          <el-icon><Edit /></el-icon> 添加用户
        </el-button>
      </el-row>

      <!-- 用户列表表格 -->
      <el-table
        :data="userStore.users"
        border
        stripe
        style="width: 100%"
        v-loading="userStore.loading"
        class="user-table"
        empty-text="暂无用户数据">
        <el-table-column prop="id" label="UUID" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="created_at" label="创建时间" />
        <el-table-column prop="is_admin" label="管理员" width="100">
          <template v-slot="scope">
            <el-switch v-model="scope.row.is_admin" disabled />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220">
          <template v-slot="scope">
            <el-button
              @click="openUserDialog(scope.row)"
              size="mini"
              type="primary">
              <el-icon><Edit /></el-icon> 编辑
            </el-button>
            <el-button
              @click="deleteUser(scope.row)"
              size="mini"
              type="danger">
              <el-icon><Delete /></el-icon> 删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页组件 -->
      <el-pagination
        v-model:current-page="userStore.currentPage"
        v-model:page-size="userStore.pageSize"
        :total="userStore.total"
        layout="prev, pager, next, sizes, jumper"
        background
        @size-change="fetchUsers"
        @current-change="fetchUsers"
        class="pagination" />
    </el-card>

    <!-- 用户编辑/添加对话框 -->
    <el-dialog v-model="dialogVisible" title="用户信息" width="500px" :close-on-click-modal="false">
      <el-form :model="currentUser" label-width="100px" ref="userForm" :rules="formRules">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="currentUser.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="currentUser.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item v-if="!currentUser.id" label="密码" prop="password">
          <el-input v-model="currentUser.password" type="password" placeholder="请输入密码" />
        </el-form-item>
        <el-form-item label="微信 ID" prop="wechat_id">
          <el-input v-model="currentUser.wechat_id" placeholder="请输入微信 ID" />
        </el-form-item>
        <el-form-item label="管理员" prop="is_admin">
          <el-switch v-model="currentUser.is_admin" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveUser">保存</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { reactive, computed, onMounted, ref } from 'vue';
import { useUserStore } from '../stores/user';
import { useAuthStore } from '../stores/auth';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Edit, Delete } from '@element-plus/icons-vue';

// Store 引用
const userStore = useUserStore();
const authStore = useAuthStore();
const isAdmin = computed(() => authStore.user.is_admin);

// UI 状态
const dialogVisible = ref(false);
const currentUser = reactive({
  id: '',
  username: '',
  email: '',
  password: '',
  wechat_id: '',
  is_admin: false,
});

// 表单验证规则
const formRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' },
  ],
  password: [{ required: true, message: '请输入密码', trigger: 'blur', min: 6 }],
};

// 初始化加载用户列表
onMounted(() => fetchUsers());

// 公共方法：重置用户表单
const resetUserForm = (user?: any) => {
  Object.assign(currentUser, user || {
    id: '',
    username: '',
    email: '',
    password: '',
    wechat_id: '',
    is_admin: false,
  });
};

// 打开用户对话框
const openUserDialog = (user?: any) => {
  resetUserForm(user);
  dialogVisible.value = true;
};

// 获取用户列表
const fetchUsers = () => {
  userStore.fetchUsers().catch((error) => {
    ElMessage.error(error.message || '获取用户列表失败');
  });
};

// 保存用户信息
const saveUser = async () => {
  try {
    if (currentUser.id) {
      await userStore.updateUser(currentUser);
    } else {
      await userStore.addUser(currentUser);
    }
    ElMessage.success('用户保存成功');
    dialogVisible.value = false;
    fetchUsers();
  } catch (error: any) {
    ElMessage.error(error.message || '保存用户失败');
  }
};

// 删除用户
const deleteUser = async (user: any) => {
  ElMessageBox.confirm(`确定删除用户 ${user.username} 吗？`, '警告', {
    confirmButtonText: '删除',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(async () => {
      await userStore.deleteUser(user.id);
      ElMessage.success('用户删除成功');
      fetchUsers();
    })
    .catch(() => {});
};
</script>

<style scoped>
.user-management {
  padding: 20px;
}

.header-row {
  margin-bottom: 20px;
}

.user-table {
  margin-top: 20px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}

.el-icon {
  margin-right: 5px;
}
</style>