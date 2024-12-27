import { computed } from 'vue';
import { useThemeStore } from '../stores/theme';

export function useTheme() {
  const store = useThemeStore();
  
  const theme = computed(() => store.currentTheme);
  
  const toggleTheme = (newTheme: 'light' | 'dark') => {
    store.setTheme(newTheme);
  };

  return {
    theme,
    toggleTheme,
  };
} 