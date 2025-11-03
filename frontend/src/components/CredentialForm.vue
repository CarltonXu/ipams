<script setup lang="ts">
import { ref, computed } from 'vue';
import type { CredentialType } from '../types/credential';
import { useI18n } from 'vue-i18n';
import { View, Hide } from '@element-plus/icons-vue';

const { t } = useI18n();

interface Props {
  modelValue: any;
  editMode?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  editMode: false
});

const emit = defineEmits(['update:modelValue']);

const credentialTypes: { value: CredentialType; label: string }[] = [
  { value: 'linux', label: t('credential.types.linux') },
  { value: 'windows', label: t('credential.types.windows') },
  { value: 'vmware', label: t('credential.types.vmware') }
];

const form = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
});

const showPassword = ref(false);
const showPrivateKey = ref(true);

const isLinux = computed(() => form.value?.credential_type === 'linux');
const isVmware = computed(() => form.value?.credential_type === 'vmware');

const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value;
};
</script>

<template>
  <el-form :model="form" label-position="top" class="credential-form">
    <el-form-item :label="$t('credential.name')" required>
      <el-input 
        v-model="form.name" 
        :placeholder="$t('credential.placeholder.name')"
      />
    </el-form-item>

    <el-form-item :label="$t('credential.type')" required>
      <el-select 
        v-model="form.credential_type" 
        :placeholder="$t('credential.type')"
        style="width: 100%"
      >
        <el-option
          v-for="type in credentialTypes"
          :key="type.value"
          :label="type.label"
          :value="type.value"
        />
      </el-select>
    </el-form-item>

    <el-form-item :label="$t('credential.username')" required>
      <el-input 
        v-model="form.username" 
        :placeholder="$t('credential.placeholder.username')"
      />
    </el-form-item>

    <el-form-item 
      :label="$t('credential.password')" 
      :required="!isLinux || !form.private_key"
    >
      <el-input 
        v-model="form.password" 
        :type="showPassword ? 'text' : 'password'"
        :placeholder="$t('credential.placeholder.password')"
      >
        <template #suffix>
          <el-icon 
            :class="['password-icon', { active: showPassword }]"
            @click="togglePasswordVisibility"
          >
            <View v-if="showPassword" />
            <Hide v-else />
          </el-icon>
        </template>
      </el-input>
    </el-form-item>

    <el-form-item 
      v-if="isLinux" 
      :label="$t('credential.privateKey')"
    >
      <el-input 
        v-model="form.private_key" 
        type="textarea" 
        :rows="4"
        :placeholder="$t('credential.placeholder.privateKey')"
        show-word-limit
      />
    </el-form-item>

    <el-form-item>
      <el-checkbox v-model="form.is_default">
        {{ $t('credential.isDefault') }}
      </el-checkbox>
    </el-form-item>
  </el-form>
</template>

<style scoped>
.credential-form {
  padding: 10px 20px;
}

.password-icon {
  cursor: pointer;
  color: #909399;
  transition: color 0.3s;
}

.password-icon:hover {
  color: #409eff;
}

.password-icon.active {
  color: #409eff;
}
</style>

