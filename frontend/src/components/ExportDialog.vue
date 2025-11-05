<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElMessage } from 'element-plus';
import { Search, Select, Document, ArrowRight } from '@element-plus/icons-vue';
import { useHostInfoStore } from '../stores/hostInfo';
import type { ExportField } from '../types/hostInfo';

const { t } = useI18n();
const hostInfoStore = useHostInfoStore();

interface Props {
  modelValue: boolean;
  selectedHosts: string[];
}

const props = defineProps<Props>();
const emit = defineEmits(['update:modelValue']);

const templates = ref<any[]>([]);
const fields = ref<ExportField[]>([]);
const selectedFields = ref<string[]>([]);
const selectedTemplate = ref<string>('');
const searchQuery = ref('');
const expandedCategories = ref<Set<string>>(new Set());

const loading = ref(false);

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
});

// 按分类组织字段
const categorizedFields = computed(() => {
  const categories = new Map<string, ExportField[]>();
  
  let filteredFields = fields.value;
  
  // 如果有搜索关键词，过滤字段
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase();
    filteredFields = fields.value.filter(field => 
      field.label.toLowerCase().includes(query) || 
      field.field.toLowerCase().includes(query) ||
      field.category.toLowerCase().includes(query)
    );
  }
  
  filteredFields.forEach(field => {
    if (!categories.has(field.category)) {
      categories.set(field.category, []);
    }
    categories.get(field.category)!.push(field);
  });
  
  return categories;
});

// 统计信息
const stats = computed(() => {
  const totalFields = fields.value.length;
  const selectedCount = selectedFields.value.length;
  const categories = Array.from(categorizedFields.value.keys());
  
  return {
    totalFields,
    selectedCount,
    categoriesCount: categories.length
  };
});

// 检查分类是否全部选中
const isCategorySelected = (categoryFields: ExportField[]): boolean => {
  return categoryFields.every(f => selectedFields.value.includes(f.field));
};

// 检查分类是否部分选中
const isCategoryIndeterminate = (categoryFields: ExportField[]): boolean => {
  const selected = categoryFields.filter(f => selectedFields.value.includes(f.field));
  return selected.length > 0 && selected.length < categoryFields.length;
};

// 切换分类选择
const toggleCategory = (categoryFields: ExportField[]) => {
  const allSelected = isCategorySelected(categoryFields);
  
  if (allSelected) {
    // 取消选择该分类的所有字段
    categoryFields.forEach(f => {
      const index = selectedFields.value.indexOf(f.field);
      if (index > -1) {
        selectedFields.value.splice(index, 1);
      }
    });
  } else {
    // 选择该分类的所有字段
    categoryFields.forEach(f => {
      if (!selectedFields.value.includes(f.field)) {
        selectedFields.value.push(f.field);
      }
    });
  }
};

// 切换单个字段
const toggleField = (field: string) => {
  const index = selectedFields.value.indexOf(field);
  if (index > -1) {
    selectedFields.value.splice(index, 1);
  } else {
    selectedFields.value.push(field);
  }
};

// 全选所有字段
const selectAll = () => {
  selectedFields.value = fields.value.map(f => f.field);
};

// 取消全选
const deselectAll = () => {
  selectedFields.value = [];
};

// 切换分类展开/折叠
const toggleCategoryExpand = (category: string) => {
  if (expandedCategories.value.has(category)) {
    expandedCategories.value.delete(category);
  } else {
    expandedCategories.value.add(category);
  }
};

// 展开所有分类
const expandAll = () => {
  categorizedFields.value.forEach((_, category) => {
    expandedCategories.value.add(category);
  });
};

// 折叠所有分类
const collapseAll = () => {
  expandedCategories.value.clear();
};

// 处理模板选择
const handleTemplateSelect = (templateId: string) => {
  if (selectedTemplate.value === templateId) {
    // 如果点击已选中的模板，取消选择
    selectedTemplate.value = '';
    selectedFields.value = [];
  } else {
    selectedTemplate.value = templateId;
    const template = templates.value.find(t => t.id === templateId);
    if (template && template.fields && template.fields.length > 0) {
      // 使用模板的字段列表
      selectedFields.value = [...template.fields];
      // 自动展开包含选中字段的分类
      fields.value.forEach(field => {
        if (template.fields!.includes(field.field)) {
          expandedCategories.value.add(field.category);
        }
      });
    } else {
      // 如果模板没有fields字段，尝试从TEMPLATES配置中获取（兼容旧版本）
      ElMessage.warning(t('export.messages.templateFieldsNotFound'));
    }
  }
};


// 处理导出
const handleExport = async () => {
  if (selectedFields.value.length === 0) {
    ElMessage.warning(t('export.messages.noFieldsSelected'));
    return;
  }
  
  loading.value = true;
  try {
    await hostInfoStore.exportHosts({
      host_ids: props.selectedHosts,
      fields: selectedFields.value,
      template: selectedTemplate.value || undefined
    });
    ElMessage.success(t('export.messages.exportSuccess'));
    visible.value = false;
  } catch (error) {
    ElMessage.error(t('export.messages.exportFailed'));
  } finally {
    loading.value = false;
  }
};

// 关闭对话框
const handleClose = () => {
  visible.value = false;
  selectedFields.value = [];
  selectedTemplate.value = '';
  searchQuery.value = '';
  expandedCategories.value.clear();
};

const getFieldLabel = (field: ExportField): string => {
  let i18nKey = `export.fieldLabels.${field.field}`;
  let translated = t(i18nKey);
  
  if (translated === i18nKey && field.field.includes('.')) {
    const fieldNameWithoutDot = field.field.split('.').pop();
    if (fieldNameWithoutDot) {
      i18nKey = `export.fieldLabels.${fieldNameWithoutDot}`;
      translated = t(i18nKey);
    }
  }
  
  if (translated && translated !== i18nKey) {
    return translated;
  }
  return field.label;
};

const getTemplateName = (template: any): string => {
  if (template.id) {
    const i18nKey = `export.templateNames.${template.id}`;
    const translated = t(i18nKey);
    if (translated && translated !== i18nKey) {
      return translated;
    }
  }
  return template.name || '';
};

// 监听对话框打开，自动展开所有分类
watch(visible, (newVal) => {
  if (newVal) {
    expandAll();
  }
});

onMounted(async () => {
  await Promise.all([
    loadTemplates(),
    loadFields()
  ]);
});

const loadTemplates = async () => {
  try {
    templates.value = await hostInfoStore.fetchExportTemplates();
  } catch (error) {
    ElMessage.error(t('common.fetchError'));
  }
};

const loadFields = async () => {
  try {
    fields.value = await hostInfoStore.fetchExportFields();
    // 默认展开所有分类
    expandAll();
  } catch (error) {
    ElMessage.error(t('common.fetchError'));
  }
};
</script>

<template>
  <el-dialog
    v-model="visible"
    :title="$t('export.title')"
    width="900px"
    @close="handleClose"
    class="export-dialog"
  >
    <div class="export-container">
      <!-- 顶部信息栏和操作 -->
      <div class="export-header">
        <div class="header-left">
          <el-tag type="info" size="default">
            {{ $t('export.selectedHosts', { count: selectedHosts.length }) }}
          </el-tag>
          <el-tag type="success" size="default" v-if="stats.selectedCount > 0">
            {{ $t('export.selectedFields', { count: stats.selectedCount }) }}
          </el-tag>
        </div>
        <div class="header-right">
          <el-button-group size="small">
            <el-button @click="selectAll" :icon="Select">
              {{ $t('export.actions.selectAll') }}
            </el-button>
            <el-button @click="deselectAll">
              {{ $t('export.actions.deselectAll') }}
            </el-button>
            <el-button @click="expandAll">
              {{ $t('export.actions.expandAll') }}
            </el-button>
            <el-button @click="collapseAll">
              {{ $t('export.actions.collapseAll') }}
            </el-button>
          </el-button-group>
        </div>
      </div>

      <!-- 搜索和模板区域 -->
      <div class="top-section">
        <div class="search-wrapper">
          <el-input
            v-model="searchQuery"
            :placeholder="$t('export.searchPlaceholder')"
            clearable
            size="default"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
        <div class="templates-section" v-if="templates.length > 0">
          <div class="templates-horizontal">
            <div
              v-for="template in templates"
              :key="template.id"
              :class="['template-item', { 'is-selected': selectedTemplate === template.id }]"
              @click="handleTemplateSelect(template.id)"
            >
              <el-icon class="template-icon"><Document /></el-icon>
              <span class="template-name">{{ getTemplateName(template) }}</span>
              <el-tag v-if="selectedTemplate === template.id" type="success" size="small" class="selected-badge">
                {{ $t('export.selected') }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>

      <!-- 字段选择区域 -->
      <div class="fields-section">
        <div class="section-header">
          <span class="section-label">
            {{ $t('export.selectFields') }}
            <span class="section-count" v-if="stats.selectedCount > 0">
              ({{ stats.selectedCount }}/{{ stats.totalFields }})
            </span>
          </span>
        </div>
        <el-scrollbar class="fields-scrollbar">
          <div class="fields-container">
            <div
              v-for="[category, categoryFields] in categorizedFields"
              :key="category"
              class="category-card"
            >
              <div
                class="category-header"
                @click="toggleCategoryExpand(category)"
              >
                <div class="category-header-left">
                  <el-icon class="expand-icon" :class="{ 'is-expanded': expandedCategories.has(category) }">
                    <ArrowRight />
                  </el-icon>
                  <el-checkbox
                    :model-value="isCategorySelected(categoryFields)"
                    :indeterminate="isCategoryIndeterminate(categoryFields)"
                    @click.stop="toggleCategory(categoryFields)"
                    class="category-checkbox"
                  >
                    <span class="category-name">{{ $t(`export.fieldCategories.${category}`) }}</span>
                  </el-checkbox>
                  <el-tag size="small" type="info" class="category-count">
                    {{ categoryFields.length }}
                  </el-tag>
                </div>
              </div>
              <el-collapse-transition>
                <div v-show="expandedCategories.has(category)" class="category-fields">
                  <div class="fields-grid">
                    <el-checkbox
                      v-for="field in categoryFields"
                      :key="field.field"
                      :model-value="selectedFields.includes(field.field)"
                      @change="toggleField(field.field)"
                      class="field-checkbox"
                    >
                      {{ getFieldLabel(field) }}
                    </el-checkbox>
                  </div>
                </div>
              </el-collapse-transition>
            </div>
          </div>
        </el-scrollbar>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <div class="footer-info">
          <span v-if="stats.selectedCount > 0" class="selected-info">
            {{ $t('export.selectedFields', { count: stats.selectedCount }) }}
          </span>
        </div>
        <div class="footer-actions">
          <el-button @click="handleClose">{{ $t('common.cancel') }}</el-button>
          <el-button
            type="primary"
            @click="handleExport"
            :loading="loading"
            :disabled="stats.selectedCount === 0"
          >
            {{ $t('export.actions.export') }}
          </el-button>
        </div>
      </div>
    </template>
  </el-dialog>
</template>


<style scoped>
.export-dialog {
  --el-dialog-border-radius: 12px;
  margin-top: 80px;
}

.export-container {
  padding: 0;
}

/* 顶部信息栏 */
.export-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  margin-bottom: 12px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.header-left {
  display: flex;
  gap: 8px;
  align-items: center;
}

.header-right {
  display: flex;
  gap: 0;
}

/* 搜索和模板区域 */
.top-section {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  align-items: flex-start;
}

.search-wrapper {
  flex: 1;
  min-width: 0;
}

/* 模板选择区域 - 横向布局 */
.templates-section {
  flex-shrink: 0;
}

.templates-horizontal {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.template-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--el-bg-color);
  white-space: nowrap;
}

.template-item:hover {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

.template-item.is-selected {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

.template-icon {
  font-size: 16px;
  color: var(--el-color-primary);
}

.template-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.section-header {
  margin-bottom: 8px;
}

.section-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  display: flex;
  align-items: center;
  gap: 8px;
}

.section-count {
  font-size: 12px;
  font-weight: normal;
  color: var(--el-text-color-regular);
}

.selected-badge {
  margin-left: 4px;
}

/* 字段选择区域 */
.fields-section {
  margin-bottom: 16px;
}

.fields-scrollbar {
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 8px;
  height: 65vh;
}

.fields-container {
  padding: 8px;
}

.category-card {
  margin-bottom: 12px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  overflow: hidden;
  background: var(--el-bg-color);
  transition: all 0.3s;
}

.category-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.category-header {
  padding: 12px 16px;
  background: var(--el-fill-color-light);
  cursor: pointer;
  user-select: none;
  transition: background 0.2s;
}

.category-header:hover {
  background: var(--el-fill-color);
}

.category-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.expand-icon {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  transition: transform 0.3s;
}

.expand-icon.is-expanded {
  transform: rotate(90deg);
}

.category-checkbox {
  flex: 1;
}

.category-name {
  font-weight: 600;
  font-size: 14px;
  color: var(--el-text-color-primary);
}

.category-count {
  margin-left: 8px;
}

.category-fields {
  padding: 12px 16px;
  background: var(--el-bg-color);
}

.fields-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.field-checkbox {
  font-size: 13px;
  color: var(--el-text-color-regular);
}

.field-checkbox:hover {
  color: var(--el-color-primary);
}

/* 底部 */
.dialog-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.footer-info {
  flex: 1;
}

.selected-info {
  font-size: 14px;
  color: var(--el-text-color-regular);
}

.footer-actions {
  display: flex;
  gap: 12px;
}

/* 响应式 */
@media (max-width: 768px) {
  .templates-grid {
    grid-template-columns: 1fr;
  }
  
  .fields-grid {
    grid-template-columns: 1fr;
  }
  
  .header-actions {
    flex-wrap: wrap;
  }
}
</style>