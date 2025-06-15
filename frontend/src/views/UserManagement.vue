<template>
  <div class="user-management">
    <el-card class="box-card">
      <div class="toolbar">
        <div class="toolbar-header">
          <h2 class="title">{{ $t('user.management.title') }}</h2>
          <p class="subtitle">{{ $t('user.management.subtitle') }}</p>
        </div>
        <div class="filters">
          <div class="batch-actions" v-if="selectedUsers.length > 0">
            <el-button 
              type="danger" 
              @click="handleBatchDelete"
              :disabled="!canBatchDelete"
            >
              <el-icon><Delete /></el-icon> 
              {{ $t('user.management.buttons.batchDelete', { count: selectedUsers.length }) }}
            </el-button>
          </div>
          <el-select
            v-model="searchColumn"
            class="column-filter"
            :placeholder="$t('user.management.search.selectColumn')"
          >
            <el-option value="all" :label="$t('user.management.search.allColumns')" />
            <el-option value="uuid" :label="$t('user.management.table.columns.uuid')" />
            <el-option value="username" :label="$t('user.management.table.columns.username')" />
            <el-option value="email" :label="$t('user.management.table.columns.email')" />
          </el-select>
          
          <el-input
            v-model="searchQuery"
            :placeholder="searchColumn === 'all' ? $t('user.management.search.all') : $t('user.management.search.specific', { column: $t(`user.management.table.columns.${searchColumn}`) })"
            :prefix-icon="Search"
            clearable
            class="search-input"
          />
          
          <el-select 
            v-model="adminFilter" 
            class="admin-filter"
            :placeholder="$t('user.management.search.adminStatus')"
          >
            <el-option :label="$t('user.management.search.allUsers')" value="all" />
            <el-option :label="$t('user.management.search.adminOnly')" value="true" />
            <el-option :label="$t('user.management.search.normalOnly')" value="false" />
          </el-select>

          <el-button v-if="isAdmin" type="primary" @click="openUserDialog">
            <el-icon><Edit /></el-icon> {{ $t('user.management.button.add') }}
          </el-button>
        </div>
      </div>


      <!-- 用户列表表格 -->
      <el-table
        :data="tableData"
        border
        stripe
        @selection-change="handleSelectionChange"
        v-loading="pagination.loading"
        class="user-table"
        :empty-text="$t('user.management.table.noData')"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" :label="$t('user.management.table.columns.uuid')" />
        <el-table-column prop="username" :label="$t('user.management.table.columns.username')" />
        <el-table-column prop="email" :label="$t('user.management.table.columns.email')" />
        <el-table-column prop="created_at" :label="$t('user.management.table.columns.createdAt')" />
        <el-table-column prop="is_admin" :label="$t('user.management.table.columns.isAdmin')" width="100">
          <template v-slot="scope">
            <el-switch v-model="scope.row.is_admin" disabled />
          </template>
        </el-table-column>
        <el-table-column prop="is_active" :label="$t('user.management.table.columns.isActive')" width="120">
          <template v-slot="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
              {{ scope.row.is_active ? t('user.management.status.active') : t('user.management.status.disable') }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="$t('user.management.table.columns.actions')" width="280">
          <template v-slot="scope">
            <el-button
              @click="openUserDialog(scope.row)"
              size="small"
              type="primary"
            >
              <el-icon><Edit /></el-icon> {{ $t('user.management.buttons.edit') }}
            </el-button>
            <el-button
              @click="toggleUserStatus(scope.row)"
              size="small"
              :type="scope.row.is_active ? 'warning' : 'success'"
              :disabled="scope.row.id === authStore.user?.id"
            >
              <el-icon><Switch /></el-icon>
              {{ scope.row.is_active ? t('user.management.buttons.deactivate') : t('user.management.buttons.activate') }}
            </el-button>
            <el-button
              @click="deleteUser(scope.row)"
              size="small"
              type="danger"
              :disabled="scope.row.id === authStore.user?.id"
            >
              <el-icon><Delete /></el-icon> {{ $t('user.management.buttons.delete') }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页组件 -->
      <el-pagination
        v-model:current-page="pagination.currentPage"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        background
        layout="total, sizes, prev, pager, next, jumper"
        :prev-text="$t('pagination.prev')"
        :next-text="$t('pagination.next')"
        :total-template="`${$t('pagination.total', { total: pagination.total })}`"
        :page-size-template="`{size}${$t('pagination.pageSize')}`"
        :jumper-template="`${$t('pagination.jumper')}${$t('pagination.page')}`"
        :sizes-text="$t('pagination.pageSize')"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
        class="pagination"
      />
    </el-card>

    <!-- 用户编辑/添加对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="$t('user.management.dialog.title')" 
      width="500px" 
      :close-on-click-modal="false"
    >
      <el-form :model="currentUser" label-width="100px" ref="userForm" :rules="formRules">
        <el-form-item :label="$t('user.management.dialog.labels.username')" prop="username">
          <el-input 
            v-model="currentUser.username" 
            :placeholder="$t('user.management.dialog.placeholders.username')" 
          />
        </el-form-item>
        <el-form-item :label="$t('user.management.dialog.labels.email')" prop="email">
          <el-input 
            v-model="currentUser.email" 
            :placeholder="$t('user.management.dialog.placeholders.email')" 
          />
        </el-form-item>
        <el-form-item 
          v-if="!currentUser.id" 
          :label="$t('user.management.dialog.labels.password')" 
          prop="password"
        >
          <el-input 
            v-model="currentUser.password" 
            type="password" 
            :placeholder="$t('user.management.dialog.placeholders.password')" 
          />
        </el-form-item>
        <el-form-item :label="$t('user.management.dialog.labels.wechatId')" prop="wechat_id">
          <el-input 
            v-model="currentUser.wechat_id" 
            :placeholder="$t('user.management.dialog.placeholders.wechatId')" 
          />
        </el-form-item>
        <el-form-item :label="$t('user.management.dialog.labels.isAdmin')" prop="is_admin">
          <el-switch v-model="currentUser.is_admin" />
        </el-form-item>
        <el-form-item :label="$t('user.management.dialog.labels.isActive')" prop="is_active">
          <el-switch v-model="currentUser.is_active" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">
          {{ $t('user.management.buttons.cancel') }}
        </el-button>
        <el-button type="primary" @click="saveUser">
          {{ $t('user.management.buttons.save') }}
        </el-button>
      </div>
    </el-dialog>

    <!-- 添加批量删除确认对话框 -->
    <el-dialog
      v-model="batchDeleteDialogVisible"
      :title="$t('user.management.dialog.batchDelete.title')"
      width="600px"
    >
      <div v-if="usersWithIPs.length > 0">
        <el-alert
          :title="$t('user.management.dialog.batchDelete.warning')"
          type="warning"
          :description="$t('user.management.dialog.batchDelete.description')"
          show-icon
          class="mb-4"
        />
        <div v-for="user in usersWithIPs" :key="user.id" class="user-ips-info">
          <h4>
            <span>{{ user.username }}</span>
            <span class="user-id">({{ user.id }})</span>
          </h4>
          <div class="ip-tags-container">
            <el-tag 
              v-for="ip in user.ips" 
              :key="ip.id"
              type="info"
            >
              {{ ip.ip_address }}
            </el-tag>
          </div>
        </div>
      </div>
      <div v-else>
        <div class="batch-delete-confirm">
          <p class="confirm-title">
            {{ $t('user.management.dialog.batchDelete.confirm', { count: selectedUsers.length }) }}
          </p>
          <div class="users-list">
            <div v-for="user in selectedUsers" :key="user.id" class="user-item">
              <span class="user-name">{{ user.username }}</span>
              <span class="user-id">({{ user.id }})</span>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="batchDeleteDialogVisible = false">
          {{ $t('common.cancel') }}
        </el-button>
        <el-button type="danger" @click="confirmBatchDelete" :loading="batchDeleteLoading">
          {{ $t('common.confirm') }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { reactive, computed, onMounted, ref, watch, h } from 'vue';
import { useUserStore } from '../stores/user';
import { useAuthStore } from '../stores/auth';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Edit, Delete, Search, Switch } from '@element-plus/icons-vue';
import { useI18n } from 'vue-i18n';
import { debounce } from 'lodash';

const { t } = useI18n();

// Store 引用
const userStore = useUserStore();
const authStore = useAuthStore();
const isAdmin = computed(() => authStore.user.is_admin);

// 搜索和过滤条件
const searchQuery = ref('');
const searchColumn = ref('all');
const adminFilter = ref('all');

// UI 状态
const dialogVisible = ref(false);
const currentUser = reactive({
  id: '',
  username: '',
  email: '',
  password: '',
  wechat_id: '',
  is_admin: false,
  is_active: true
});

// 表单验证规则
const formRules = {
  username: [{ required: true, message: t('user.management.validation.username'), trigger: 'blur' }],
  email: [
    { required: true, message: t('user.management.validation.email.required'), trigger: 'blur' },
    { type: 'email', message: t('user.management.validation.email.invalid'), trigger: 'blur' },
  ],
  password: [{ required: true, message: t('user.management.validation.password'), trigger: 'blur', min: 6 }],
  is_active: [{ required: true, message: t('user.management.validation.status'), trigger: 'change' }]
};

// 分页相关状态
const pagination = ref({
  currentPage: 1,
  pageSize: 10,
  total: 0,
  loading: false
});

// 表格数据
const tableData = ref([]);

// 定义接口
interface User {
  id: string;
  username: string;
  email: string;
  wechat_id?: string;
  is_admin: boolean;
  is_active: boolean;
}

interface IP {
  id: string;
  ip_address: string;
}

// 加载用户数据
const loadUsersData = async () => {
  pagination.value.loading = true;
  try {
    const response = await userStore.fetchFilteredUsers({
      page: pagination.value.currentPage,
      pageSize: pagination.value.pageSize,
      query: searchQuery.value,
      column: searchColumn.value,
      isAdmin: adminFilter.value === 'all' ? undefined : adminFilter.value === 'true'
    });
    
    if (!response || !response.users) {
      throw new Error(t('common.fetchError'));
    }

    tableData.value = response.users;
    pagination.value.total = response.total;
  } catch (error: any) {
    ElMessage.error(error.message || t('common.fetchError'));
    tableData.value = [];
    pagination.value.total = 0;
  } finally {
    pagination.value.loading = false;
  }
};

// 处理搜索
const handleSearch = debounce(() => {
  pagination.value.currentPage = 1; // 重置到第一页
  loadUsersData();
}, 300);

// 监听搜索条件变化
watch([
  () => searchQuery.value,
  () => searchColumn.value,
  () => adminFilter.value
], () => {
  handleSearch();
});

// 处理分页变化
const handlePageChange = async (page: number) => {
  pagination.value.currentPage = page;
  await loadUsersData();
};

// 处理每页条数变化
const handleSizeChange = async (size: number) => {
  pagination.value.pageSize = size;
  pagination.value.currentPage = 1;
  await loadUsersData();
};

// 初始化
onMounted(() => {
  loadUsersData();
});

// 公共方法：重置用户表单
const resetUserForm = (user?: any) => {
  Object.assign(currentUser, user || {
    id: '',
    username: '',
    email: '',
    password: '',
    wechat_id: '',
    is_admin: false,
    is_active: true
  });
};

// 打开用户对话框
const openUserDialog = (user?: any) => {
  resetUserForm(user);
  dialogVisible.value = true;
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
    loadUsersData();
  } catch (error: any) {
    ElMessage.error(error.message || t('user.management.messages.saveError'));
  }
};

// 批量删除相关状态
const selectedUsers = ref<User[]>([]);
const batchDeleteDialogVisible = ref(false);
const batchDeleteLoading = ref(false);
const usersWithIPs = ref<Array<{ id: string; username: string; ips: IP[] }>>([]);

// 处理表格选择变化
const handleSelectionChange = (selection: User[]) => {
  selectedUsers.value = selection;
};

// 判断是否可以批量删除
const canBatchDelete = computed(() => {
  return selectedUsers.value.length > 0 && 
         !selectedUsers.value.some(user => user.id === authStore.user?.id); // 不能删除自己
});

// 单个删除用户
const deleteUser = async (user: User) => {
  if (user.id === authStore.user?.id) {
    ElMessage.error(t('user.management.messages.deleteSelfError'));
    return;
  }
  await deleteUsers([user], false);
};

// 抽象删除用户的公共逻辑
const deleteUsers = async (users: User[], isBatch: boolean = false) => {
  try {
    // 检查用户是否有关联的 IP
    const response = await userStore.checkUsersIPs(users.map(u => u.id));
    
    if (response.usersWithIPs && response.usersWithIPs.length > 0) {
      // 如果有关联的 IP，显示带有 IP 信息的确认对话框
      usersWithIPs.value = response.usersWithIPs;
      if (isBatch) {
        // 批量删除时使用批量删除对话框
        batchDeleteDialogVisible.value = true;
      } else {
        // 单个删除时显示用户的 IP 信息
        const userWithIPs = response.usersWithIPs[0];
        ElMessageBox.alert(
          h('div', { class: 'batch-delete-confirm' }, [
            h('p', { class: 'confirm-title' }, t('user.management.messages.hasAssociatedIPs')),
            h('div', { class: 'user-ips-info' }, [
              h('h4', [
                h('span', userWithIPs.username),
                h('span', { class: 'user-id' }, `(${userWithIPs.id})`)
              ]),
              h('div', { class: 'ip-tags-container' }, 
                userWithIPs.ips.map((ip: any) => 
                  h('el-tag', { 
                    key: ip.id,
                    type: 'info',
                    class: 'mb-1'
                  }, ip.ip_address)
                )
              )
            ])
          ]),
          {
            title: t('common.warning'),
            type: 'warning',
            showClose: false,
            confirmButtonText: t('common.confirm')
          }
        );
      }
      return;
    }

    // 如果没有关联的 IP，显示确认对话框
    try {
      await ElMessageBox.confirm(
        h('div', { class: 'batch-delete-confirm' }, [
          h('p', { class: 'confirm-title' }, 
            isBatch 
              ? t('user.management.messages.batchDeleteConfirm', { count: users.length })
              : t('user.management.messages.deleteConfirm', { username: users[0].username })
          ),
          h('div', { class: 'users-list' }, 
            users.map(user => 
              h('div', { class: 'user-item' }, [
                h('span', { class: 'user-name' }, user.username),
                h('span', { class: 'user-id' }, `(${user.id})`)
              ])
            )
          )
        ]),
        {
          title: t('common.warning'),
          confirmButtonText: t('common.confirm'),
          cancelButtonText: t('common.cancel'),
          type: 'warning',
          customClass: 'batch-delete-dialog'
        }
      );

      // 执行删除操作
      batchDeleteLoading.value = true;
      await userStore.batchDeleteUsers(users.map(u => u.id));
      ElMessage.success(t('user.management.messages.deleteSuccess'));
      await loadUsersData();
      
      // 只在批量删除时更新选中状态
      if (isBatch) {
        selectedUsers.value = [];
      }
      
    } catch (error: any) {
      if (error === 'cancel') {
        return;
      }
      throw error;
    } finally {
      batchDeleteLoading.value = false;
    }
  } catch (error: any) {
    ElMessage.error(error.message || t('user.management.messages.deleteError'));
  }
};

// 批量删除用户
const handleBatchDelete = async () => {
  if (!canBatchDelete.value) return;
  await deleteUsers(selectedUsers.value, true);
};

// 确认批量删除
const confirmBatchDelete = async () => {
  batchDeleteLoading.value = true;
  try {
    await userStore.batchDeleteUsers(selectedUsers.value.map(u => u.id));
    ElMessage.success(t('user.management.messages.deleteSuccess'));
    batchDeleteDialogVisible.value = false;
    await loadUsersData();
    // 清理选中状态
    selectedUsers.value = [];
  } catch (error: any) {
    ElMessage.error(error.message || t('user.management.messages.deleteError'));
  } finally {
    batchDeleteLoading.value = false;
  }
};

// 切换用户状态
const toggleUserStatus = async (user: any) => {
  try {
    const newStatus = !user.is_active;
    const confirmMessage = newStatus 
      ? t('user.management.messages.confirmActivate', { username: user.username })
      : t('user.management.messages.confirmDeactivate', { username: user.username });

    await ElMessageBox.confirm(
      confirmMessage,
      t('common.warning'),
      {
        confirmButtonText: t('common.confirm'),
        cancelButtonText: t('common.cancel'),
        type: 'warning'
      }
    );

    await userStore.updateUserStatus(user.id, newStatus);
    ElMessage.success(t('user.management.messages.statusUpdateSuccess'));
    await loadUsersData();
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || t('user.management.messages.statusUpdateError'));
    }
  }
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

.filters {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
  margin-top: 1rem;
}

.column-filter {
  width: 150px;
}

.search-input {
  width: 300px;
}

.admin-filter {
  width: 150px;
}

.batch-actions {
  margin-left: auto;
  display: flex;
  gap: 1rem;
}

.user-ips-info {
  margin-bottom: 1rem;
  padding: 0.5rem;
  border-bottom: 1px solid #eee;
}

.user-ips-info h4 {
  margin: 0 0 0.5rem 0;
}

.user-ips-info .el-tag {
  margin-right: 0.5rem;
  margin-bottom: 0.5rem;
}

.mb-4 {
  margin-bottom: 1rem;
}

/* 批量删除确认对话框样式 */
.batch-delete-dialog .el-message-box__content {
  max-height: 400px;
  overflow-y: auto;
}

.batch-delete-confirm {
  padding: 10px 0;
}

.confirm-title {
  margin-bottom: 15px;
  font-weight: 500;
  color: #606266;
}

.users-list {
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #EBEEF5;
  border-radius: 4px;
  padding: 8px;
}

.user-item {
  padding: 8px;
  margin: 4px 0;
  background: #F5F7FA;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-name {
  font-weight: 500;
  color: #303133;
}

.user-id {
  color: #909399;
  font-size: 0.9em;
}

/* 带有 IP 的用户列表样式 */
.user-ips-info {
  margin-bottom: 1rem;
  padding: 1rem;
  background: #F5F7FA;
  border-radius: 4px;
}

.user-ips-info h4 {
  margin: 0 0 0.5rem 0;
  color: #303133;
  display: flex;
  align-items: center;
}

.user-ips-info .user-id {
  font-size: 0.9em;
  color: #909399;
  font-weight: normal;
}

.user-ips-info .el-tag {
  margin-right: 0.5rem;
  margin-bottom: 0.5rem;
}

.ip-tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.el-tag {
  text-transform: capitalize;
}
</style>