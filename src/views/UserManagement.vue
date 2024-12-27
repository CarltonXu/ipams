<template>
  <div class="user-management">
    <el-card class="box-card">
      <div class="toolbar">
        <div class="toolbar-header">
          <h2 class="title">{{ t('user.management.title') }}</h2>
          <p class="subtitle">{{ t('user.management.subtitle') }}</p>
        </div>
        <el-button v-if="isAdmin" type="primary" size="medium" @click="openUserDialog">
          <el-icon><Edit /></el-icon> {{ t('user.management.button.add') }}
        </el-button>
      </div>

      <!-- 用户列表表格 -->
      <el-table
        :data="userStore.users"
        border
        stripe
        style="width: 100%"
        v-loading="userStore.loading"
        class="user-table"
        :empty-text="t('user.management.table.noData')"
      >
        <el-table-column prop="id" :label="t('user.management.table.columns.uuid')" />
        <el-table-column prop="username" :label="t('user.management.table.columns.username')" />
        <el-table-column prop="email" :label="t('user.management.table.columns.email')" />
        <el-table-column prop="created_at" :label="t('user.management.table.columns.createdAt')" />
        <el-table-column prop="is_admin" :label="t('user.management.table.columns.isAdmin')" width="100">
          <template v-slot="scope">
            <el-switch v-model="scope.row.is_admin" disabled />
          </template>
        </el-table-column>
        <el-table-column :label="t('user.management.table.columns.actions')" width="220">
          <template v-slot="scope">
            <el-button
              @click="openUserDialog(scope.row)"
              size="mini"
              type="primary"
            >
              <el-icon><Edit /></el-icon> {{ t('user.management.buttons.edit') }}
            </el-button>
            <el-button
              @click="deleteUser(scope.row)"
              size="mini"
              type="danger"
            >
              <el-icon><Delete /></el-icon> {{ t('user.management.buttons.delete') }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页组件 -->
      <el-pagination
        v-model:current-page="userStore.currentPage"
        v-model:page-size="userStore.pageSize"
        :total="userStore.total"
        :page-sizes="[10, 20, 50, 100]"
        background
        layout="total, sizes, prev, pager, next, jumper"
        :prev-text="t('pagination.prev')"
        :next-text="t('pagination.next')"
        :total-template="`${t('pagination.total', { total: userStore.total })}`"
        :page-size-template="`{size}${t('pagination.pageSize')}`"
        :jumper-template="`${t('pagination.jumper')}${t('pagination.page')}`"
        :sizes-text="t('pagination.pageSize')"
        @size-change="fetchUsers"
        @current-change="fetchUsers"
        class="pagination"
      />
    </el-card>

    <!-- 用户编辑/添加对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="t('user.management.dialog.title')" 
      width="500px" 
      :close-on-click-modal="false"
    >
      <el-form :model="currentUser" label-width="100px" ref="userForm" :rules="formRules">
        <el-form-item :label="t('user.management.dialog.labels.username')" prop="username">
          <el-input 
            v-model="currentUser.username" 
            :placeholder="t('user.management.dialog.placeholders.username')" 
          />
        </el-form-item>
        <el-form-item :label="t('user.management.dialog.labels.email')" prop="email">
          <el-input 
            v-model="currentUser.email" 
            :placeholder="t('user.management.dialog.placeholders.email')" 
          />
        </el-form-item>
        <el-form-item 
          v-if="!currentUser.id" 
          :label="t('user.management.dialog.labels.password')" 
          prop="password"
        >
          <el-input 
            v-model="currentUser.password" 
            type="password" 
            :placeholder="t('user.management.dialog.placeholders.password')" 
          />
        </el-form-item>
        <el-form-item :label="t('user.management.dialog.labels.wechatId')" prop="wechat_id">
          <el-input 
            v-model="currentUser.wechat_id" 
            :placeholder="t('user.management.dialog.placeholders.wechatId')" 
          />
        </el-form-item>
        <el-form-item :label="t('user.management.dialog.labels.isAdmin')" prop="is_admin">
          <el-switch v-model="currentUser.is_admin" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">
          {{ t('user.management.buttons.cancel') }}
        </el-button>
        <el-button type="primary" @click="saveUser">
          {{ t('user.management.buttons.save') }}
        </el-button>
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
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

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
  username: [{ required: true, message: t('user.management.validation.username'), trigger: 'blur' }],
  email: [
    { required: true, message: t('user.management.validation.email.required'), trigger: 'blur' },
    { type: 'email', message: t('user.management.validation.email.invalid'), trigger: 'blur' },
  ],
  password: [{ required: true, message: t('user.management.validation.password'), trigger: 'blur', min: 6 }],
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
    ElMessage.error(error.message || t('user.management.messages.fetchError'));
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
    ElMessage.success(t('user.management.messages.saveSuccess'));
    dialogVisible.value = false;
    fetchUsers();
  } catch (error: any) {
    ElMessage.error(error.message || t('user.management.messages.saveError'));
  }
};

// 删除用户
const deleteUser = async (user: any) => {
  ElMessageBox.confirm(
    t('user.management.messages.deleteConfirm', { username: user.username }), 
    t('common.warning'),
    {
      confirmButtonText: t('user.management.buttons.delete'),
      cancelButtonText: t('user.management.buttons.cancel'),
      type: 'warning',
    }
  )
    .then(async () => {
      await userStore.deleteUser(user.id);
      ElMessage.success(t('user.management.messages.deleteSuccess'));
      fetchUsers();
    })
    .catch(() => {});
};
</script>

<style scoped>
.user-management {
  padding: 20px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.toolbar-header h2 {
  font-size: 24px;
  margin: 0;
  color: #333;
}

.toolbar-header .subtitle {
  color: #666;
  margin: 5px 0 0;
  font-size: 14px;
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

.dialog-footer {
  margin-left: 315px;
}
</style>