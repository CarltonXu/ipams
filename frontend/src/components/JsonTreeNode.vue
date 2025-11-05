<template>
  <div class="json-tree-node" :style="{ paddingLeft: `${level * 5}px` }">
    <div class="json-tree-node-header" @click="toggleExpand" v-if="hasChildren">
      <span class="json-tree-expand-icon">
        {{ isExpanded ? '−' : '+' }}
      </span>
      <span class="json-tree-key" :class="getKeyClass()">{{ keyName || 'root' }}:</span>
      <span class="json-tree-type">{{ getTypeLabel() }}</span>
    </div>
    <div class="json-tree-node-header" v-else>
      <span class="json-tree-key" :class="getKeyClass()">{{ keyName }}:</span>
      <span class="json-tree-value" :class="getValueClass()">{{ formatValue() }}</span>
    </div>
    <div v-if="isExpanded && hasChildren" class="json-tree-children">
      <template v-if="isArray">
        <JsonTreeNode
          v-for="(childValue, index) in data"
          :key="index"
          :data="childValue"
          :key-name="String(index)"
          :level="level + 1"
        />
      </template>
      <template v-else>
        <JsonTreeNode
          v-for="(childValue, childKey) in data"
          :key="childKey"
          :data="childValue"
          :key-name="String(childKey)"
          :level="level + 1"
        />
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

const props = defineProps<{
  data: any;
  keyName: string;
  level: number;
}>();

const isExpanded = ref(props.level < 2); // 默认展开前2层

const hasChildren = computed(() => {
  const value = props.data;
  return value !== null && 
         value !== undefined && 
         (typeof value === 'object' && !(value instanceof Date));
});

const isArray = computed(() => Array.isArray(props.data));

const toggleExpand = () => {
  if (hasChildren.value) {
    isExpanded.value = !isExpanded.value;
  }
};

const getTypeLabel = () => {
  if (!hasChildren.value) return '';
  if (isArray.value) return `Array[${Object.keys(props.data).length}]`;
  return `Object{${Object.keys(props.data).length}}`;
};

const getKeyClass = () => {
  if (isArray.value) {
    return 'json-tree-key-array';
  }
  return 'json-tree-key-object';
};

const getValueClass = () => {
  const value = props.data;
  if (value === null) return 'json-tree-value-null';
  if (typeof value === 'number') return 'json-tree-value-number';
  if (typeof value === 'boolean') return 'json-tree-value-boolean';
  if (typeof value === 'string') return 'json-tree-value-string';
  return '';
};

const formatValue = () => {
  const value = props.data;
  if (value === null) return 'null';
  if (value === undefined) return 'undefined';
  if (typeof value === 'string') {
    // 如果字符串太长，截断显示
    if (value.length > 100) {
      return `"${value.substring(0, 100)}..."`;
    }
    return `"${value}"`;
  }
  if (typeof value === 'number') return value;
  if (typeof value === 'boolean') return value ? 'true' : 'false';
  return String(value);
};
</script>

<style scoped>
.json-tree-node {
  margin: 2px 0;
}

.json-tree-node-header {
  display: flex;
  align-items: center;
  cursor: pointer;
  user-select: none;
  padding: 4px 0;
  transition: background-color 0.2s;
}

.json-tree-node-header:hover {
  background-color: var(--el-fill-color-light);
  border-radius: 3px;
}

.json-tree-expand-icon {
  display: inline-block;
  width: 20px;
  text-align: center;
  font-weight: bold;
  color: var(--el-text-color-secondary);
  font-size: 14px;
  line-height: 1;
}

.json-tree-key {
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-right: 8px;
}

.json-tree-key-array {
  color: #905;
}

.json-tree-key-object {
  color: #07a;
}

.json-tree-type {
  color: var(--el-text-color-secondary);
  font-size: 11px;
  font-style: italic;
  margin-left: 8px;
}

.json-tree-value {
  color: var(--el-text-color-regular);
  word-break: break-word;
}

.json-tree-value-string {
  color: #690;
}

.json-tree-value-number {
  color: #905;
}

.json-tree-value-boolean {
  color: #07a;
}

.json-tree-value-null {
  color: var(--el-text-color-placeholder);
  font-style: italic;
}

.json-tree-children {
  margin-left: 0;
  border-left: 1px solid var(--el-border-color-lighter);
  padding-left: 10px;
}
</style>

