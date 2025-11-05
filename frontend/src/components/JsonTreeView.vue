<template>
  <div class="json-tree-view">
    <JsonTreeNode :data="data" :key-name="''" :level="0" />
  </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';
import JsonTreeNode from './JsonTreeNode.vue';

defineProps<{
  data: any;
}>();
</script>

<style scoped>
.json-tree-view {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace;
  font-size: 13px;
  line-height: 1.6;
  background-color: var(--el-bg-color-page);
  padding: 15px;
  border-radius: 4px;
  max-height: 600px;
  overflow-y: auto;
}
</style>

