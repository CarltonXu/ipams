<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElMessage } from 'element-plus';
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
const customFileName = ref('');

const loading = ref(false);

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
});

// 按分类组织字段
const categorizedFields = computed(() => {
  const categories = new Map<string, ExportField[]>();
  
  fields.value.forEach(field => {
    if (!categories.has(field.category)) {
      categories.set(field.category, []);
    }
    categories.get(field.category)!.push(field);
  });
  
  return categories;
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
  } catch (error) {
    ElMessage.error(t('common.fetchError'));
  }
};

const handleTemplateChange = () => {
  if (selectedTemplate.value) {
    const template = templates.value.find(t => t.id === selectedTemplate.value);
    if (template) {
      // 根据模板预设字段
      selectedFields.value = template.fields || [];
    }
  }
};

const toggleField = (field: string) => {
  const index = selectedFields.value.indexOf(field);
  if (index > -1) {
    selectedFields.value.splice(index, 1);
  } else {
    selectedFields.value.push(field);
  }
};

const toggleAllInCategory = (categoryFields: ExportField[]) => {
  const allSelected = categoryFields.every(f => selectedFields.value.includes(f.field));
  
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

const handleClose = () => {
  visible.value = false;
  selectedFields.value = [];
  selectedTemplate.value = '';
  customFileName.value = '';
};
</script>

<template>
  <el-dialog
    v-model="visible"
    :title="$t('export.title')"
    width="600px"
    @close="handleClose"
  >
    <div class="export-config">
      <!-- 模板选择 -->
      <div class="config-section">
        <div class="section-title">{{ $t('export.selectTemplate') }}</div>
        <el-radio-group v-model="selectedTemplate" @change="handleTemplateChange">
          <el-radio
            v-for="template in templates"
            :key="template.id"
            :label="template.id"
          >
            {{ template.name }} ({{ template.field_count }} {{ $t('common.fields') || '字段' }})
          </el-radio>
        </el-radio-group>
      </div>

      <!-- 字段选择 -->
      <div class="config-section">
        <div class="section-title">{{ $t('export.selectFields') }}</div>
        <el-scrollbar height="300px">
          <div
            v-for="[category, categoryFields] in categorizedFields"
            :key="category"
            class="field-category"
          >
            <div class="category-header">
              <el-checkbox
                :model-value="categoryFields.every(f => selectedFields.includes(f.field))"
                :indeterminate="categoryFields.some(f => selectedFields.includes(f.field)) && !categoryFields.every(f => selectedFields.includes(f.field))"
                @change="toggleAllInCategory(categoryFields)"
              >
                {{ $t(`export.fieldCategories.${category}`) }}
              </el-checkbox>
            </div>
            <div class="category-fields">
              <el-checkbox
                v-for="field in categoryFields"
                :key="field.field"
                :model-value="selectedFields.includes(field.field)"
                :label="field.field"
                @change="toggleField(field.field)"
              >
                {{ field.label }}
              </el-checkbox>
            </div>
          </div>
        </el-scrollbar>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">{{ $t('common.cancel') }}</el-button>
        <el-button type="primary" @click="handleExport" :loading="loading">
          {{ $t('export.actions.export') }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<style scoped>
.export-config {
  padding: 10px 0;
}

.config-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--el-text-color-primary);
}

.field-category {
  margin-bottom: 16px;
}

.category-header {
  margin-bottom: 8px;
}

.category-fields {
  padding-left: 24px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>

