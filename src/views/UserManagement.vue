<template>
  <div class="user-management">
    <el-card class="box-card">
      <el-row justify="space-between" align="middle" class="header-row">
        <h2>用户管理</h2>
        <el-button v-if="isAdmin" type="primary" size="medium" @click="openUserDialog">
          <i class="el-icon-plus"></i> 添加用户
        </el-button>
      </el-row>
      <el-table
        :data="paginatedUsers"
        border
        stripe
        style="width: 100%"
        v-loading="loading"
        class="user-table"
      >
        <el-table-column prop="id" label="UUID" />
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="created_at" label="创建时间" />
        <el-table-column prop="is_admin" label="管理员" width="100">
          <template v-slot="scope">
            <el-switch
              v-model="scope.row.is_admin"
              disabled
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220">
          <template v-slot="scope">
            <el-button
              @click="openUserDialog(scope.row)"
              size="mini"
              type="primary">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button
              @click="deleteUser(scope.row)"
              size="mini"
              type="danger">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page.sync="currentPage"
        :page-size.sync="pageSize"
        :total="userStore.getAllUsers.length"
        layout="prev, pager, next, sizes, jumper"
        background
        @size-change="handleSizeChange"
        class="pagination"
      />
    </el-card>

    <!-- 编辑/添加用户对话框 -->
    <el-dialog v-model="dialogVisible" title="用户信息" width="500px" :close-on-click-modal="false">
      <el-form :model="currentUser" label-width="100px" ref="userForm" :rules="formRules">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="currentUser.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="currentUser.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!currentUser.id">
          <el-input
            v-model="currentUser.password"
            type="password"
            placeholder="请输入密码"
          />
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
import { ref, reactive, computed, onMounted } from 'vue';
import { useUserStore } from '../stores/user';
import { ElMessageBox, ElMessage } from 'element-plus';
import { Edit, Delete } from '@element-plus/icons-vue';  // 引入 Element Plus 的图标

const userStore = useUserStore();
const isAdmin = computed(() => userStore.isAdmin); // 当前登录用户权限
const loading = ref(false);
const dialogVisible = ref(false);
const currentPage = ref(1);
const pageSize = ref(10);

const currentUser = reactive({
  id: '',
  username: '',
  email: '',
  password: '',
  wechat_id: '',
  is_admin: false,
});

const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return userStore.getAllUsers.slice(start, end);
});

const handleSizeChange = (page: number) => {
  pageSize.value = page;
};

const formRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' },
  ],
  password: [{ required: true, message: '请输入密码', trigger: 'blur', min: 6 }],
};

// 加载用户列表
onMounted(() => {
  loading.value = true;
  userStore.fetchUsers().finally(() => {
    loading.value = false;
  });
});

// 打开用户对话框
const openUserDialog = (user?: any) => {
  if (user) {
    Object.assign(currentUser, user);
  } else {
    Object.assign(currentUser, {
      id: '',
      username: '',
      email: '',
      password: '',
      wechat_id: '',
      is_admin: false,
    });
  }
  dialogVisible.value = true;
};

// 保存用户
const saveUser = async () => {
  try {
    if (currentUser.id) {
      await userStore.updateUser(currentUser);
    } else {
      await userStore.addUser(currentUser);
    }
    ElMessage.success('用户保存成功');
    dialogVisible.value = false;
  } catch (error: any) {
    ElMessage.error(error.message || '用户保存失败');
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